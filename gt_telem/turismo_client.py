from __future__ import annotations

import copy
import logging
import socket
import threading
from time import sleep

from gt_telem.errors.playstation_errors import (PlayStationNotFoundError,
                                                PlayStatonOnStandbyError)
from gt_telem.models.helpers import SpanReader
from gt_telem.models.telemetry import Telemetry
from gt_telem.net.crypto import PDEncyption
from gt_telem.net.device_discover import get_ps_ip_type


class TurismoClient:
    RECEIVE_PORT = 33339
    BIND_PORT = 33340

    def __init__(self, is_gt7: bool = True, ps_ip: str = None, telem_update_callback=None, telem_update_callback_args=None):
        """
        Initialize TurismoClient.

        Parameters:
        - is_gt7 (bool): Flag indicating whether it's Gran Turismo 7. Default is True.
        - ps_ip (str): PlayStation IP address. If None, it will be discovered.
        """
        ip, ps = get_ps_ip_type()
        ip = ip or ps_ip
        if not ip:
            raise PlayStationNotFoundError()
        if ps and "STANDBY" in ps:
            raise PlayStatonOnStandbyError(ip)

        self.ip_addr: str = ip
        if is_gt7:
            self.RECEIVE_PORT += 400
            self.BIND_PORT += 400
        self._crypto: PDEncyption = PDEncyption(is_gt7)

        self._telem_lock: threading.Lock = threading.Lock()
        self._telem: Telemetry = None
        self._hb: threading.Thread = threading.Thread(
            target=self._send_heartbeat, daemon=True
        )
        self._l: threading.Thread = threading.Thread(target=self._listen, daemon=True)
        self._callback_exists = None

    @property
    def telemetry(self) -> Telemetry:
        """
        Get a copy of the telemetry data.

        Returns:
        Telemetry: A copy of the telemetry data.
        """
        if not self._telem:
            return None
        with self._telem_lock:
            cpy: Telemetry = copy.deepcopy(self._telem)
        return cpy

    @telemetry.setter
    def telemetry(self, value: Telemetry) -> None:
        """
        Set the telemetry data.

        Parameters:
        - value (Telemetry): Telemetry data to set.
        """
        with self._telem_lock:
            self._telem = value

        if self._callback_exists:
            alive = self._callback_thread.is_alive()
            if not alive:
                self._callback_thread.start()
            #with self._callback_lock:
                #self._callback(self._callback_args)

    @property
    def telem_dict(self) -> dict:
        """
        Get the telemetry data as a dictionary.

        Returns:
        dict: Telemetry data as a dictionary.
        """
        return self.telemetry.as_dict() if self.telemetry else {}

    def set_telemetry_update_callback(self, callback, callback_args):
        """
        Function callback when telemetry is updated. Function will
        be started on its own thread so as to not block the telemetry client.
        NOTE: updates happen very quickly, usually 60/s. If the callback function
        does not return before the next update arrives, a new callback will not be issued.
        """
        self._callback_exists = True
        self._callback_thread = threading.Thread(target=callback, args=callback_args, daemon=True)

    def run(self) -> None:
        """
        Start the TurismoClient threads.
        """
        self._hb.start()
        self._l.start()

    def _send_heartbeat(self) -> None:
        msg: bytes = b"A"
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                udp_socket.sendto(msg, (self.ip_addr, self.RECEIVE_PORT))
            sleep(10)

    def _listen(self) -> None:
        logging.info(f"Listening for data on {self.ip_addr}:{self.BIND_PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_socket.bind(("0.0.0.0", self.BIND_PORT))

            while True:
                data, addr = udp_socket.recvfrom(1024)
                self._handle_data(data)

    def _handle_data(self, data: bytes) -> None:
        try:
            message: bytes = self._crypto.decrypt(data)
        except Exception as e:
            logging.debug(f"Failed to decrypt. Error: {e}. Wrong system?")
            return
        # First 4 bytes are header and indicate which system this is
        try:
            header: str = message[:4].decode("ascii")
        except Exception as e:
            logging.debug(f"Not sure what this is \n{message[:4]}. Error: {e}")
            return
        message: bytes = message[4:]
        if not header in ["0S7G", "G6S0"]:
            # bad data
            logging.debug(f"Not sure what this is \n{header}")
            return
        if header == "0S7G":
            sr: SpanReader = SpanReader(message, "little")
        else:
            sr: SpanReader = SpanReader(message, "big")
        self._parse_telemetry(sr)

    def _parse_telemetry(self, sr: SpanReader) -> None:
        self.telemetry = Telemetry(
            position_x=sr.read_single(),
            position_y=sr.read_single(),
            position_z=sr.read_single(),
            velocity_x=sr.read_single(),
            velocity_y=sr.read_single(),
            velocity_z=sr.read_single(),
            rotation_x=sr.read_single(),
            rotation_y=sr.read_single(),
            rotation_z=sr.read_single(),
            orientation=sr.read_single(),
            ang_vel_x=sr.read_single(),
            ang_vel_y=sr.read_single(),
            ang_vel_z=sr.read_single(),
            body_height=sr.read_single(),
            engine_rpm=sr.read_single(),
            iv=sr.read_single(),
            fuel_level=sr.read_single(),
            fuel_capacity=sr.read_single(),
            speed_mps=sr.read_single(),
            boost_pressure=sr.read_single(),
            oil_pressure=sr.read_single(),
            water_temp=sr.read_single(),
            oil_temp=sr.read_single(),
            tire_fl_temp=sr.read_single(),
            tire_fr_temp=sr.read_single(),
            tire_rl_temp=sr.read_single(),
            tire_rr_temp=sr.read_single(),
            packet_id=sr.read_int32(),
            current_lap=sr.read_int16(),
            total_laps=sr.read_int16(),
            best_lap_time_ms=sr.read_int32(),
            last_lap_time_ms=sr.read_int32(),
            time_of_day_ms=sr.read_int32(),
            race_start_pos=sr.read_int16(),
            total_cars=sr.read_int16(),
            min_alert_rpm=sr.read_int16(),
            max_alert_rpm=sr.read_int16(),
            calc_max_speed=sr.read_int16(),
            flags=sr.read_int16(),
            bits=sr.read_byte(),
            throttle=sr.read_byte(),
            brake=sr.read_byte(),
            empty=sr.read_byte(),
            road_plane_x=sr.read_single(),
            road_plane_y=sr.read_single(),
            road_plane_z=sr.read_single(),
            road_plane_dist=sr.read_single(),
            wheel_fl_rps=sr.read_single(),
            wheel_fr_rps=sr.read_single(),
            wheel_rl_rps=sr.read_single(),
            wheel_rr_rps=sr.read_single(),
            tire_fl_radius=sr.read_single(),
            tire_fr_radius=sr.read_single(),
            tire_rl_radius=sr.read_single(),
            tire_rr_radius=sr.read_single(),
            tire_fl_sus_height=sr.read_single(),
            tire_fr_sus_height=sr.read_single(),
            tire_rl_sus_height=sr.read_single(),
            tire_rr_sus_height=sr.read_single(),
            unused1=sr.read_int32(),
            unused2=sr.read_int32(),
            unused3=sr.read_int32(),
            unused4=sr.read_int32(),
            unused5=sr.read_int32(),
            unused6=sr.read_int32(),
            unused7=sr.read_int32(),
            unused8=sr.read_int32(),
            clutch_pedal=sr.read_single(),
            clutch_engagement=sr.read_single(),
            trans_rpm=sr.read_single(),
            trans_top_speed=sr.read_single(),
            gear1=sr.read_single(),
            gear2=sr.read_single(),
            gear3=sr.read_single(),
            gear4=sr.read_single(),
            gear5=sr.read_single(),
            gear6=sr.read_single(),
            gear7=sr.read_single(),
            gear8=sr.read_single(),
            car_code=sr.read_int32(),
        )

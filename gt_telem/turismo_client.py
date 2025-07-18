import asyncio
import copy
import logging
import socket
import threading
from collections import deque
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

    def __init__(self, is_gt7: bool=True, ps_ip: str=None, heartbeat_type: str="A"):
        """
        Initialize TurismoClient.

        Parameters:
            - is_gt7 (bool): Flag indicating whether it's Gran Turismo 7. Default is True.
            - ps_ip (str): PlayStation IP address. If None, it will be discovered.
            - heartbeat_type (str): Heartbeat message type to use. Options: "A" (standard), 
                                  "B" (extended with motion data), "~" (extended with filtered data).
                                  Default is "A". Note: Only one type can be active per session.        """
        self._cancellation_token = None
        
        # Validate heartbeat type
        if heartbeat_type not in ["A", "B", "~"]:
            raise ValueError(f"Invalid heartbeat_type '{heartbeat_type}'. Must be 'A', 'B', or '~'")
        
        self.heartbeat_type = heartbeat_type
        
        ip, ps = get_ps_ip_type()
        ip = ip or ps_ip
        if not ip:
            raise PlayStationNotFoundError()
        if ps and "STANDBY" in ps:
            raise PlayStatonOnStandbyError(ip)

        logging.info(f"Using the {ps} at {ip} with heartbeat type '{heartbeat_type}'")
        self.ip_addr: str = ip

        if is_gt7:
            self.RECEIVE_PORT += 400
            self.BIND_PORT += 400
        self._crypto: PDEncyption = PDEncyption(is_gt7, heartbeat_type)

        self._telem_lock: threading.Lock = threading.Lock()
        # Thread for when run w/o wait:
        self._loop_thread = threading.Thread(target=self._run_forever_threaded)
        self._telem: Telemetry = None

        self._telem_update_callbacks = {}
        self._telem_callback_queue = asyncio.LifoQueue(maxsize=1)
        self._processing_callbacks = False

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
        Set the telemetry data and call any registered callbacks.

        Parameters:
            - value (Telemetry): Telemetry data to set.
        """
        with self._telem_lock:
            self._telem = value

        try:
            self._telem_callback_queue.put_nowait(value)
        except asyncio.QueueFull:
            self._telem_callback_queue.get_nowait()
            self._telem_callback_queue.put_nowait(value)
        if not self._processing_callbacks:
            asyncio.create_task(self._process_telemetry_callbacks())

    def register_callback(self, callback, args=None):
        """
        Register an awaitable callback to be invoked when new telemetry is received.

        The telemetry object is sent as the first parameter, and additional
        args can be passed if specified.

        Callbacks are executed off the main thread, potentially compromising
        state integrity (e.g., using `self.` within your callback won't work).
        To work around this limitation, declare your callback as a @staticmethod,
        pass the class instance (self) as an argument, and receive the context of
        the class in your parameters (after telemetry, which is the first).

        .. code-block:: python

            def __init__(self, tc: TurismoClient):
                tc.add_callback(MyClass.parse_telem, [self])

            @staticmethod
            async def parse_telem(t: Telemetry, context: MyClass):
                self = context


        Additionally, note that the game sends telemetry at the same frequency as
        the frame rate (~60/s). If your callback takes too long to process and exit,
        subsequent callbacks will not be invoked until it returns.
        """
        self._telem_update_callbacks[callback] = args

    def deregister_callback(self, callback):
        """
        Deregister a callback.

        Parameters:
            - callback: Callback to deregister.
        """
        self._telem_update_callbacks.pop(callback)

    def start(self):
        self._loop_thread.start()

    def stop(self):
        self._cancellation_token.set()
        self._loop_thread.join()

    def _run_forever_threaded(self, cancellation_token: asyncio.Event=None) -> None:
        """
        Start the telemetry client and return immediately. Must provide cancellation token.

        Parameters:
            - cancellation_token (asyncio.Event): Set token to shut down threads and return from run()
        """
        asyncio.run(self.run_async(cancellation_token))

    def run(self, cancellation_token: asyncio.Event=None) -> None:
        """
        Start the telemetry client and run the event loop. Blocking.

        Parameters:
            - cancellation_token (asyncio.Event): Set token to shut down threads and return from run()
        """
        self._cancellation_token = cancellation_token or asyncio.Event()
        loop = asyncio.get_event_loop()
        heartbeat_task = loop.create_task(self._send_heartbeat())
        listen_task = loop.create_task(self._listen(loop))

        # Run the tasks in the event loop
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
            self._cancellation_token.set()
        finally:
            # Clean up any resources here if needed
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    async def run_async(self, cancellation_token: asyncio.Event=None) -> None:
        """
        Asynchronously start the telemetry client and run the event loop.

        Parameters:
            - cancellation_token (asyncio.Event): Set token to shut down threads and return from run()
        """
        self._cancellation_token = cancellation_token or asyncio.Event()
        loop = asyncio.get_event_loop()
        heartbeat_task = loop.create_task(self._send_heartbeat())
        listen_task = loop.create_task(self._listen(loop))

        # Run the tasks in the event loop
        try:
            await asyncio.gather(heartbeat_task, listen_task)
        except KeyboardInterrupt:
            self._cancellation_token.set()
            loop.stop()
        finally:
            # Clean up any resources here if needed
            await loop.shutdown_asyncgens()
    async def _send_heartbeat(self) -> None:
        """
        Send heartbeat messages at regular intervals to keep the telemetry stream alive.
        Uses the configured heartbeat_type ("A", "B", or "~").
        """
        logging.info(f"Starting telemetry heartbeat with type '{self.heartbeat_type}'.")
        msg: bytes = self.heartbeat_type.encode('ascii')
        while not self._cancellation_token.is_set():
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(msg, (self.ip_addr, self.RECEIVE_PORT))
            udp_socket.close()
            await asyncio.sleep(10)

    async def _listen(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Listen for incoming telemetry data.

        Parameters:
            - loop: The asyncio event loop.
        """
        logging.info(f"Listening for data on {self.ip_addr}:{self.BIND_PORT}")

        class MyDatagramProtocol(asyncio.DatagramProtocol):
            def __init__(self, client):
                self.client = client

            def datagram_received(self, data, addr):
                self.client._handle_data(data)

        udp_socket, _ = await loop.create_datagram_endpoint(
            lambda: MyDatagramProtocol(self),
            local_addr=("0.0.0.0", self.BIND_PORT)
        )
        await self._cancellation_token.wait()
        udp_socket.close()

    async def _process_telemetry_callbacks(self):
        """
        Process telemetry callbacks.
        """
        self._processing_callbacks = True
        while True:
            try:
                # Wait for the next telemetry update callback
                telemetry_value = await self._telem_callback_queue.get()

                # Call the user-provided callback
                for cb, args in self._telem_update_callbacks.items():
                    if args:
                        await cb(telemetry_value, *args)
                    else:
                        await cb(telemetry_value)

                # Optionally introduce a delay here if needed
                await asyncio.sleep(1 / 60)  # 60 Hz update rate

            except asyncio.CancelledError:
                # The task is cancelled when the event loop is stopped
                break
            except Exception as e:
                # Handle exceptions during callback processing
                logging.error(f"Error processing telemetry {cb}: {e}")

        self._processing_callbacks = False

    def _handle_data(self, data: bytes) -> None:
        """
        Handle incoming telemetry data.

        Parameters:
            - data: Raw telemetry data.
        """
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
        """
        Parse telemetry data from SpanReader and update the telemetry property.
        Handles different packet sizes based on heartbeat type.

        Parameters:
            - sr: SpanReader containing telemetry data.
        """
        # Parse the standard fields (present in all heartbeat types)
        telemetry_data = {
            'position_x': sr.read_single(),
            'position_y': sr.read_single(),
            'position_z': sr.read_single(),
            'velocity_x': sr.read_single(),
            'velocity_y': sr.read_single(),
            'velocity_z': sr.read_single(),
            'rotation_x': sr.read_single(),
            'rotation_y': sr.read_single(),
            'rotation_z': sr.read_single(),
            'orientation': sr.read_single(),
            'ang_vel_x': sr.read_single(),
            'ang_vel_y': sr.read_single(),
            'ang_vel_z': sr.read_single(),
            'body_height': sr.read_single(),
            'engine_rpm': sr.read_single(),
            'iv': sr.read_single(),
            'fuel_level': sr.read_single(),
            'fuel_capacity': sr.read_single(),
            'speed_mps': sr.read_single(),
            'boost_pressure': sr.read_single(),
            'oil_pressure': sr.read_single(),
            'water_temp': sr.read_single(),
            'oil_temp': sr.read_single(),
            'tire_fl_temp': sr.read_single(),
            'tire_fr_temp': sr.read_single(),
            'tire_rl_temp': sr.read_single(),
            'tire_rr_temp': sr.read_single(),
            'packet_id': sr.read_int32(),
            'current_lap': sr.read_int16(),
            'total_laps': sr.read_int16(),
            'best_lap_time_ms': sr.read_int32(),
            'last_lap_time_ms': sr.read_int32(),
            'time_of_day_ms': sr.read_int32(),
            'race_start_pos': sr.read_int16(),
            'total_cars': sr.read_int16(),
            'min_alert_rpm': sr.read_int16(),
            'max_alert_rpm': sr.read_int16(),
            'calc_max_speed': sr.read_int16(),
            'flags': sr.read_int16(),
            'bits': sr.read_byte(),
            'throttle': sr.read_byte(),
            'brake': sr.read_byte(),
            'empty': sr.read_byte(),
            'road_plane_x': sr.read_single(),
            'road_plane_y': sr.read_single(),
            'road_plane_z': sr.read_single(),
            'road_plane_dist': sr.read_single(),
            'wheel_fl_rps': sr.read_single(),
            'wheel_fr_rps': sr.read_single(),
            'wheel_rl_rps': sr.read_single(),
            'wheel_rr_rps': sr.read_single(),
            'tire_fl_radius': sr.read_single(),
            'tire_fr_radius': sr.read_single(),
            'tire_rl_radius': sr.read_single(),
            'tire_rr_radius': sr.read_single(),
            'tire_fl_sus_height': sr.read_single(),
            'tire_fr_sus_height': sr.read_single(),
            'tire_rl_sus_height': sr.read_single(),
            'tire_rr_sus_height': sr.read_single(),
            'unused1': sr.read_int32(),
            'unused2': sr.read_int32(),
            'unused3': sr.read_int32(),
            'unused4': sr.read_int32(),
            'unused5': sr.read_int32(),
            'unused6': sr.read_int32(),
            'unused7': sr.read_int32(),
            'unused8': sr.read_int32(),
            'clutch_pedal': sr.read_single(),
            'clutch_engagement': sr.read_single(),
            'trans_rpm': sr.read_single(),
            'trans_top_speed': sr.read_single(),
            'gear1': sr.read_single(),
            'gear2': sr.read_single(),
            'gear3': sr.read_single(),
            'gear4': sr.read_single(),
            'gear5': sr.read_single(),
            'gear6': sr.read_single(),
            'gear7': sr.read_single(),
            'gear8': sr.read_single(),
            'car_code': sr.read_int32(),
        }
        
        # Parse additional fields based on heartbeat type
        if self.heartbeat_type == "B":
            # Heartbeat "B" adds 5 additional floats for motion data
            telemetry_data.update({
                'wheel_rotation_radians': sr.read_single(),
                'filler_float_fb': sr.read_single(),
                'sway': sr.read_single(),
                'heave': sr.read_single(),
                'surge': sr.read_single(),
            })
        elif self.heartbeat_type == "~":
            # Heartbeat "~" adds different extended data
            # Based on the GitHub issue, it includes filtered throttle/brake and energy recovery
            telemetry_data.update({
                'throttle_filtered': sr.read_byte(),
                'brake_filtered': sr.read_byte(),
                'unk_tilde_1': sr.read_byte(),
                'unk_tilde_2': sr.read_byte(),
            })
            # Skip some bytes for Vector4 that only Tomahawk seems to use
            sr.read_single()  # Skip Vec4 component 1
            sr.read_single()  # Skip Vec4 component 2
            sr.read_single()  # Skip Vec4 component 3
            sr.read_single()  # Skip Vec4 component 4
            # Add the remaining fields
            telemetry_data.update({
                'energy_recovery': sr.read_single(),
                'unk_tilde_3': sr.read_single(),
            })
        
        self.telemetry = Telemetry(**telemetry_data)

import asyncio
import copy
import logging
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from gt_telem.errors.playstation_errors import (PlayStationNotFoundError,
                                                PlayStatonOnStandbyError)
from gt_telem.models.helpers import SpanReader
from gt_telem.models.telemetry import Telemetry
from gt_telem.net.crypto import PDEncyption
from gt_telem.net.device_discover import get_ps_ip_type

class TurismoClient:
    RECEIVE_PORT = 33339
    BIND_PORT = 33340

    def __init__(self, is_gt7: bool=True, ps_ip: str=None, heartbeat_type: str="A", max_callback_workers: int=10):
        """
        Initialize TurismoClient.

        Parameters:
            - is_gt7 (bool): Flag indicating whether it's Gran Turismo 7. Default is True.
            - ps_ip (str): PlayStation IP address. If None, it will be discovered.
            - heartbeat_type (str): Heartbeat message type to use. Options: "A" (standard), 
                                  "B" (extended with motion data), "~" (extended with filtered data).
                                  Default is "A". Note: Only one type can be active per session.
            - max_callback_workers (int): Maximum number of threads for callback execution. Default is 10.
        """
        self._cancellation_token = None
        
        # Create logger for this instance
        self.logger = logging.getLogger(f"gt-telem.TurismoClient")
        
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

        self.logger.info(f"Using the {ps} at {ip} with heartbeat type '{heartbeat_type}'")
        self.ip_addr: str = ip

        if is_gt7:
            self.RECEIVE_PORT += 400
            self.BIND_PORT += 400
        self._crypto: PDEncyption = PDEncyption(is_gt7, heartbeat_type)

        self._telem_lock: threading.Lock = threading.Lock()
        # Thread for when run w/o wait:
        self._loop_thread = threading.Thread(target=self._run_forever_threaded)
        self._telem: Telemetry = None

        # Use a thread pool for callback execution
        self._callback_executor = ThreadPoolExecutor(
            max_workers=max_callback_workers, 
            thread_name_prefix="gt_callback"
        )
        self._telem_update_callbacks = {}

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
        Callbacks are executed asynchronously to avoid blocking telemetry reception.

        Parameters:
            - value (Telemetry): Telemetry data to set.
        """
        with self._telem_lock:
            self._telem = value

        # Fire callbacks without blocking - each callback gets its own thread
        if self._telem_update_callbacks:
            self._invoke_callbacks(value)

    def register_callback(self, callback, args=None):
        """
        Register a callback to be invoked when new telemetry is received.

        The telemetry object is sent as the first parameter, and additional
        args can be passed if specified.

        Callbacks are executed in a thread pool to ensure telemetry reception
        is never blocked. Both synchronous and asynchronous callbacks are supported.
        Multiple callbacks run concurrently for optimal performance.

        For thread safety with instance methods, declare your callback as a 
        @staticmethod and pass the class instance (self) as an argument:

        .. code-block:: python

            def __init__(self, tc: TurismoClient):
                tc.register_callback(MyClass.parse_telem, [self])

            @staticmethod
            async def parse_telem(t: Telemetry, context: MyClass):
                self = context
                # Your callback logic here...

        Parameters:
            - callback: The callback function (sync or async)
            - args: Optional list of additional arguments to pass to the callback

        Note: The game sends telemetry at 60Hz. Callbacks run in separate threads
        so slow callbacks won't drop telemetry frames, but very heavy processing
        may still impact overall performance.
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
        # Gracefully shutdown callback threads
        self._callback_executor.shutdown(wait=True, timeout=5.0)

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
        self.logger.info(f"Starting telemetry heartbeat with type '{self.heartbeat_type}'.")
        msg: bytes = self.heartbeat_type.encode('ascii')
        while not self._cancellation_token.is_set():
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(msg, (self.ip_addr, self.RECEIVE_PORT))
            udp_socket.close()
            await asyncio.sleep(10)
        self.logger.info("Stopping telemetry heartbeat.")

    async def _listen(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Listen for incoming telemetry data.

        Parameters:
            - loop: The asyncio event loop.
        """
        self.logger.info(f"Listening for data on {self.ip_addr}:{self.BIND_PORT}")

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
        self.logger.info("Stopping telemetry listener.")
        udp_socket.close()

    def _invoke_callbacks(self, telemetry_value: Telemetry) -> None:
        """
        Invoke all registered callbacks in a thread pool worker.
        Handles both sync and async callbacks properly.
        Each callback runs in its own thread for better resource utilization.
        """
        # Submit each callback to the thread pool individually
        for callback, args in self._telem_update_callbacks.items():
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Async callback - submit to thread pool
                    self._callback_executor.submit(self._run_async_callback, callback, telemetry_value, args)
                else:
                    # Sync callback - submit to thread pool
                    self._callback_executor.submit(self._run_sync_callback_threaded, callback, telemetry_value, args)
            except Exception as e:
                self.logger.error(f"Error submitting callback {callback.__name__}: {e}")

    def _run_async_callback(self, callback, telemetry_value, args):
        """
        Run an async callback in a thread pool worker.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if args:
                loop.run_until_complete(callback(telemetry_value, *args))
            else:
                loop.run_until_complete(callback(telemetry_value))
        except Exception as e:
            self.logger.error(f"Error in async callback {callback.__name__}: {e}")
        finally:
            loop.close()

    def _run_sync_callback_threaded(self, callback, telemetry_value, args):
        """
        Run a sync callback in a thread pool worker.
        """
        try:
            if args:
                callback(telemetry_value, *args)
            else:
                callback(telemetry_value)
        except Exception as e:
            self.logger.error(f"Error in sync callback {callback.__name__}: {e}")

    def _handle_data(self, data: bytes) -> None:
        """
        Handle incoming telemetry data.

        Parameters:
            - data: Raw telemetry data.
        """
        try:
            message: bytes = self._crypto.decrypt(data)
        except Exception as e:
            self.logger.debug(f"Failed to decrypt. Error: {e}. Wrong system?")
            return
        # First 4 bytes are header and indicate which system this is
        try:
            header: str = message[:4].decode("ascii")
        except Exception as e:
            self.logger.debug(f"Not sure what this is \n{message[:4]}. Error: {e}")
            return
        message: bytes = message[4:]
        if not header in ["0S7G", "G6S0"]:
            # bad data
            self.logger.debug(f"Not sure what this is \n{header}")
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

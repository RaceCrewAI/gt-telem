from typing import Callable, List

from gt_telem.turismo_client import TurismoClient


class DriverEvents:
    """
    DriverEvents class for tracking driver-related events in Gran Turismo using telemetry.

    Attributes:
        on_gear_change (List[Callable]): List of callbacks to be executed when the current gear changes.
        on_flash_lights (List[Callable]): List of callbacks to be executed when the high beams are activated.
        on_handbrake (List[Callable]): List of callbacks to be executed when the handbrake is activated.
        on_suggested_gear (List[Callable]): List of callbacks to be executed when the suggested gear changes.
        on_tcs (List[Callable]): List of callbacks to be executed when the Traction Control System (TCS) state changes.
        on_asm (List[Callable]): List of callbacks to be executed when the Anti-Spin Management (ASM) state changes.
        on_rev_limit (List[Callable]): List of callbacks to be executed when the engine reaches the rev limit.
        on_brake (List[Callable]): List of callbacks to be executed when the brake is applied.
        on_throttle (List[Callable]): List of callbacks to be executed when the throttle is applied.
        on_shift_light_low (List[Callable]): List of callbacks to be executed when the engine is in the low shift light range.
        on_shift_light_high (List[Callable]): List of callbacks to be executed when the engine is in the high shift light range.

    Methods:
        __init__(self, tc: TurismoClient):
            Initializes the DriverEvents instance and registers the _state_tracker callback with the provided TurismoClient.

        _state_tracker(t, context):
            Callback function to track driver-related events based on telemetry data.

    Usage:
        # Example usage:
        tc = TurismoClient()
        driver = DriverEvents(tc)
        driver.on_gear_change.append(lambda: print("Gear changed!"))
        driver.on_flash_lights.append(lambda: print("High beams activated!"))
        # Add more event callbacks as needed.

        # Start the TurismoClient
        tc.run()
    """

    on_gear_change: list[Callable] = []
    on_flash_lights: list[Callable] = []
    on_handbrake: list[Callable] = []
    on_suggested_gear: list[Callable] = []
    on_tcs: list[Callable] = []
    on_asm: list[Callable] = []
    on_rev_limit: list[Callable] = []
    on_brake: list[Callable] = []
    on_throttle: list[Callable] = []
    on_shift_light_low: list[Callable] = []
    on_shift_light_high: list[Callable] = []

    def __init__(self, tc: TurismoClient):
        """
        Initialize the DriverEvents instance.

        Parameters:
            tc (TurismoClient): The TurismoClient instance to track telemetry.
        """
        tc.register_callback(DriverEvents._state_tracker, [self])
        self.last = tc.telemetry
        self.above_min_alert_rpm = False
        self.above_max_alert_rpm = False

    @staticmethod
    async def _state_tracker(t, context):
        """
        Callback function to track driver-related events based on telemetry data.

        Parameters:
            t: Telemetry data.
            context: The DriverEvents instance.
        """
        self = context
        if not self.last:
            self.last = t
            return
        if self.last.current_gear != t.current_gear:
            [e() for e in self.on_gear_change]
        if not self.last.high_beams and t.high_beams:
            [e() for e in self.on_flash_lights]
        if not self.last.hand_brake_active and t.hand_brake_active:
            [x() for x in self.on_handbrake]
        if self.last.suggested_gear != t.suggested_gear:
            [x() for x in self.on_suggested_gear]
        if self.last.tcs_active != t.tcs_active:
            [x() for x in self.on_tcs]
        if self.last.asm_active != t.asm_active:
            [x() for x in self.on_asm]
        if self.last.rev_limit != t.rev_limit:
            [x() for x in self.on_rev_limit]
        if self.last.brake == 0 and t.brake > 0:
            [x() for x in self.on_brake]
        if self.last.throttle == 0 and t.throttle > 0:
            [x() for x in self.on_throttle]
        if t.engine_rpm > t.min_alert_rpm:
            if not self.above_min_alert_rpm:
                self.above_min_alert_rpm = True
                [x() for x in self.on_shift_light_low]
        elif self.above_min_alert_rpm:
            self.above_min_alert_rpm = False
        if t.engine_rpm > t.max_alert_rpm:
            if not self.above_max_alert_rpm:
                self.above_max_alert_rpm = True
                [x() for x in self.on_shift_light_high]
        elif self.above_max_alert_rpm:
            self.above_max_alert_rpm = False

        self.last = t

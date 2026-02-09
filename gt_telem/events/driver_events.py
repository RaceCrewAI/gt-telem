import asyncio
from typing import Callable, List

from gt_telem.turismo_client import TurismoClient


class DriverEvents:
    """
    DriverEvents class for tracking driver-related events in Gran Turismo using telemetry.

    Attributes:
        on_gear_change (List[Callable]): List of async callbacks to be executed when the current gear changes.
                                        Callbacks receive the new gear value as a parameter.
        on_flash_lights (List[Callable]): List of async callbacks to be executed when the high beams are activated.
                                         Callbacks receive the high beams state as a parameter.
        on_handbrake (List[Callable]): List of async callbacks to be executed when the handbrake is activated.
                                      Callbacks receive the handbrake state as a parameter.
        on_suggested_gear (List[Callable]): List of async callbacks to be executed when the suggested gear changes.
                                           Callbacks receive the suggested gear value as a parameter.
        on_tcs (List[Callable]): List of async callbacks to be executed when the Traction Control System (TCS) state changes.
                                Callbacks receive the TCS state as a parameter.
        on_asm (List[Callable]): List of async callbacks to be executed when the Anti-Spin Management (ASM) state changes.
                                Callbacks receive the ASM state as a parameter.
        on_rev_limit (List[Callable]): List of async callbacks to be executed when the engine reaches the rev limit.
                                      Callbacks receive the rev limit value as a parameter.
        on_brake (List[Callable]): List of async callbacks to be executed when the brake is applied (transitions from 0 to >0).
                                  Callbacks receive the brake value as a parameter.
        on_throttle (List[Callable]): List of async callbacks to be executed when the throttle is applied (transitions from 0 to >0).
                                     Callbacks receive the throttle value as a parameter.
        on_shift_light_low (List[Callable]): List of async callbacks to be executed when the engine RPM crosses above the minimum alert RPM.
                                           Callbacks receive the current engine RPM as a parameter.
        on_shift_light_high (List[Callable]): List of async callbacks to be executed when the engine RPM crosses above the maximum alert RPM.
                                            Callbacks receive the current engine RPM as a parameter.

    Methods:
        __init__(self, tc: TurismoClient):
            Initializes the DriverEvents instance and registers the _state_tracker callback with the provided TurismoClient.

        _state_tracker(t, context):
            Static async callback function to track driver-related events based on telemetry data.

    Usage:
        # Example usage:
        tc = TurismoClient()
        driver = DriverEvents(tc)

        # All callbacks are async and receive the relevant value as a parameter
        driver.on_gear_change.append(lambda gear: print(f"Gear changed to: {gear}"))
        driver.on_flash_lights.append(lambda state: print(f"High beams: {state}"))
        driver.on_brake.append(lambda brake_value: print(f"Brake applied: {brake_value}"))
        driver.on_shift_light_low.append(lambda rpm: print(f"Low shift light at RPM: {rpm}"))

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
        Static async callback function to track driver-related events based on telemetry data.

        This method compares the current telemetry data with the previous state to detect
        changes and trigger appropriate event callbacks. All callbacks are awaited and
        receive the relevant telemetry value as a parameter.

        Parameters:
            t: Current telemetry data object containing all vehicle state information.
            context: The DriverEvents instance (passed as context since this is a static method).

        Events Triggered:
            - on_gear_change: When current_gear changes from previous value
            - on_flash_lights: When high_beams transitions from False to True
            - on_handbrake: When hand_brake_active transitions from False to True
            - on_suggested_gear: When suggested_gear changes from previous value
            - on_tcs: When tcs_active state changes
            - on_asm: When asm_active state changes
            - on_rev_limit: When rev_limit value changes
            - on_brake: When brake transitions from 0 to any value > 0
            - on_throttle: When throttle transitions from 0 to any value > 0
            - on_shift_light_low: When engine_rpm crosses above min_alert_rpm threshold
            - on_shift_light_high: When engine_rpm crosses above max_alert_rpm threshold
        """
        self = context
        if not self.last:
            self.last = t
            return
        if self.last.current_gear != t.current_gear:
            for x in self.on_gear_change:
                if asyncio.iscoroutinefunction(x):
                    await x(t.current_gear)
                else:
                    x(t.current_gear)
        if not self.last.high_beams and t.high_beams:
            for x in self.on_flash_lights:
                if asyncio.iscoroutinefunction(x):
                    await x(t.high_beams)
                else:
                    x(t.high_beams)
        if not self.last.hand_brake_active and t.hand_brake_active:
            for x in self.on_handbrake:
                if asyncio.iscoroutinefunction(x):
                    await x(t.hand_brake_active)
                else:
                    x(t.hand_brake_active)
        if self.last.suggested_gear != t.suggested_gear:
            for x in self.on_suggested_gear:
                if asyncio.iscoroutinefunction(x):
                    await x(t.suggested_gear)
                else:
                    x(t.suggested_gear)
        if self.last.tcs_active != t.tcs_active:
            for x in self.on_tcs:
                if asyncio.iscoroutinefunction(x):
                    await x(t.tcs_active)
                else:
                    x(t.tcs_active)
        if self.last.asm_active != t.asm_active:
            for x in self.on_asm:
                if asyncio.iscoroutinefunction(x):
                    await x(t.asm_active)
                else:
                    x(t.asm_active)
        if self.last.rev_limit != t.rev_limit:
            for x in self.on_rev_limit:
                if asyncio.iscoroutinefunction(x):
                    await x(t.rev_limit)
                else:
                    x(t.rev_limit)
        if self.last.brake == 0 and t.brake > 0:
            for x in self.on_brake:
                if asyncio.iscoroutinefunction(x):
                    await x(t.brake)
                else:
                    x(t.brake)
        if self.last.throttle == 0 and t.throttle > 0:
            for x in self.on_throttle:
                if asyncio.iscoroutinefunction(x):
                    await x(t.throttle)
                else:
                    x(t.throttle)
        if t.engine_rpm > t.min_alert_rpm:
            if not self.above_min_alert_rpm:
                self.above_min_alert_rpm = True
                for x in self.on_shift_light_low:
                    if asyncio.iscoroutinefunction(x):
                        await x(t.engine_rpm)
                    else:
                        x(t.engine_rpm)
        elif self.above_min_alert_rpm:
            self.above_min_alert_rpm = False
        if t.engine_rpm > t.max_alert_rpm:
            if not self.above_max_alert_rpm:
                self.above_max_alert_rpm = True
                for x in self.on_shift_light_high:
                    if asyncio.iscoroutinefunction(x):
                        await x(t.engine_rpm)
                    else:
                        x(t.engine_rpm)
        elif self.above_max_alert_rpm:
            self.above_max_alert_rpm = False

        self.last = t

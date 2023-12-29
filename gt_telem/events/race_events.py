from typing import Callable, List

from gt_telem.turismo_client import TurismoClient


class RaceEvents:
    """
    RaceEvents class for tracking race events in Gran Turismo using telemetry.

    Attributes:
        on_race_start (List[Callable]): List of callbacks to be executed when a race starts.
        on_lap_change (List[Callable]): List of callbacks to be executed when the lap changes.
        on_best_lap_time (List[Callable]): List of callbacks to be executed when the best lap time changes.
        on_last_lap_time (List[Callable]): List of callbacks to be executed when the last lap time changes.

    Methods:
        __init__(self, tc: TurismoClient):
            Initializes the RaceEvents instance and registers the _state_tracker callback with the provided TurismoClient.

        _state_tracker(t, context):
            Callback function to track race events based on telemetry data.

    Usage:
        # Example usage:
        tc = TurismoClient()
        race = RaceEvents(tc)
        race.on_race_start.append(lambda: print("Race started!"))
        race.on_lap_change.append(lambda: print("Lap changed!"))
        race.on_best_lap_time.append(lambda: print("Best lap time changed!"))
        race.on_last_lap_time.append(lambda: print("Last lap time changed!"))

        # Start the TurismoClient
        asyncio.run(tc.run())
    """

    on_race_start: list[Callable] = []
    on_lap_change: list[Callable] = []
    on_best_lap_time: list[Callable] = []
    on_last_lap_time: list[Callable] = []

    def __init__(self, tc: TurismoClient):
        """
        Initialize the RaceEvents instance.

        Parameters:
            tc (TurismoClient): The TurismoClient instance to track telemetry.
        """
        tc.register_callback(RaceEvents._state_tracker, [self])
        self.last = tc.telemetry

    @staticmethod
    async def _state_tracker(t, context):
        """
        Callback function to track race events based on telemetry data.

        Parameters:
            t: Telemetry data.
            context: The RaceEvents instance.
        """
        self = context
        if self.last.lap == 0 and t.lap == 1:
            [e() for e in self.on_race_start]
        if self.last.lap != t.lap:
            [e() for e in self.on_lap_change]
        if self.last.best_lap_time != t.best_lap_time:
            [x() for x in self.on_best_lap_time]
        if self.last.last_lap_time != t.last_lap_time:
            [x() for x in self.on_last_lap_time]

        self.last = t.telemetry

from __future__ import annotations

import asyncio
import logging
from enum import Enum
from typing import Callable, List

from gt_telem.turismo_client import TurismoClient


class GameState(Enum):
    NOT_RUNNING = 0,
    RUNNING = 1,
    IN_MENU = 2,
    AT_TRACK = 3,
    IN_RACE = 4,
    PAUSED = 5,
    END_RACE = 6


class TurismoGame:
    on_running: list[Callable] = []
    on_in_game_menu: list[Callable] = []
    on_at_track: list[Callable] = []
    on_in_race: list[Callable] = []
    on_paused: list[Callable] = []
    on_race_end: list[Callable] = []

    def __init__(self, tc: TurismoClient):
        self.game_state: GameState = GameState.NOT_RUNNING
        self.check_next = 0
        self.tod = tc.telemetry.time_of_day_ms if tc.telemetry else 0
        tc.add_callback(TurismoGame._state_tracker, [self])

    def _change_state(self, state: GameState):
        events = None
        match state:
            case GameState.RUNNING:
                events = self.on_running
            case GameState.IN_MENU:
                events = self.on_in_game_menu
            case GameState.AT_TRACK:
                events = self.on_at_track
            case GameState.IN_RACE:
                events = self.on_in_race
            case GameState.PAUSED:
                events = self.on_paused
            case GameState.END_RACE:
                events = self.on_race_end
            case _:
                events = []
        for event in events:
            event()
        self.game_state = state

    @staticmethod
    async def _state_tracker(t, context):
        """
        Try to keep track of what the game is doing. This is remarkably challenging
        and probably not reliable. Things like replays, licenses and non-standard race events
        aren't handled well.
        """
        self = context
        if self.game_state == GameState.NOT_RUNNING:
            if t is None:
                return
            self._change_state(GameState.RUNNING)
            logging.debug("Game is running.")
        last = self.game_state

        match self.game_state:
            case GameState.RUNNING:
                if t.cars_on_track:
                    if t.is_paused:
                        logging.debug("Race is paused.")
                        self._change_state(GameState.PAUSED)
                    if t.current_lap == -1:
                        logging.debug("End of a Race.")
                        self._change_state(GameState.END_RACE)
                    else:
                        logging.debug("In a Race.")
                        self._change_state(GameState.IN_RACE)
                else:
                    if t.current_lap > -1:
                        logging.debug("At a track")
                        self._change_state(GameState.AT_TRACK)
                    else:
                        logging.debug("In a menu.")
                        self._change_state(GameState.IN_MENU)

            case GameState.IN_MENU:
                if t.current_lap > -1:
                    logging.debug("At a track")
                    self._change_state(GameState.AT_TRACK)

            case GameState.AT_TRACK:
                if t.cars_on_track:
                    logging.debug("In a Race.")
                    self._change_state(GameState.IN_RACE)
                elif t.current_lap == -1:
                    logging.debug("In a menu.")
                    self._change_state(GameState.IN_MENU)

            case GameState.IN_RACE:
                if t.is_paused:
                    logging.debug("Race is paused.")
                    self._change_state(GameState.PAUSED)
                elif t.current_lap == -1:
                    logging.debug("Race ended.")
                    self._change_state(GameState.END_RACE)

            case GameState.PAUSED:
                if not t.is_paused:
                    # The only way to really tell if they're resuming or exiting
                    # is to compare two frames. Engine RPM is a good candidate to
                    # test if the simulation is still running because even when stopped
                    # it fluctuates. This means losing a few frames but if that's a
                    # problem, don't pause the game :)
                    if self.check_next == 0:
                        self.check_next = 2
                    else:
                        if self.check_next > 1:
                            self.engine_rpm = t.engine_rpm
                            self.check_next -= 1
                            return
                        else:
                            self.check_next = 0
                            if t.engine_rpm != self.engine_rpm:
                                logging.debug("Resuming Race")
                                self._change_state(GameState.IN_RACE)
                            else:
                                logging.debug("Quit Race")
                                self._change_state(GameState.END_RACE)

            case GameState.END_RACE:
                if not t.is_loading:
                    logging.debug("At a track")
                    self._change_state(GameState.AT_TRACK)

            case _:
                logging.debug(f"Unhandled state: {self.game_state}")

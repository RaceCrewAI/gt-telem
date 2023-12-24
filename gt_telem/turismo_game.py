from __future__ import annotations

import logging
from enum import Enum

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
    def __init__(self, is_gt7=True, ps_ip=None):
        self.game_state: GameState = GameState.NOT_RUNNING
        self.tc = TurismoClient(is_gt7, ps_ip)
        self.tc.set_telemetry_update_callback(self._state_watcher, [])
        self.tc.run()
        self.tod = self.tc.telemetry.time_of_day_ms if self.tc.telemetry else 0
        self.check_next = 0

    def _state_watcher(self):
        """
        Try to keep track of what the game is doing. This is remarkably challenging
        and probably not reliable. Things like replays, licenses and non-standard race events
        aren't handled well.
        """
        if self.game_state == GameState.NOT_RUNNING:
            if self.tc.telemetry is None:
                return
            self.game_state = GameState.RUNNING
            logging.info("Game is running.")
        last = self.game_state
        t = self.tc.telemetry

        match self.game_state:
            case GameState.RUNNING:
                if t.cars_on_track:
                    if t.is_paused:
                        logging.info("Race is paused.")
                        self.game_state = GameState.PAUSED
                    if t.current_lap == -1:
                        logging.info("End of a Race.")
                        self.game_state = GameState.END_RACE
                    else:
                        logging.info("In a Race.")
                        self.game_state = GameState.IN_RACE
                else:
                    if t.current_lap > -1:
                        logging.info("At a track")
                        self.game_state = GameState.AT_TRACK
                    else:
                        logging.info("In a menu.")
                        self.game_state = GameState.IN_MENU

            case GameState.IN_MENU:
                if t.current_lap > -1:
                    logging.info("At a track")
                    self.game_state = GameState.AT_TRACK

            case GameState.AT_TRACK:
                if t.cars_on_track:
                    logging.info("In a Race.")
                    self.game_state = GameState.IN_RACE
                elif t.current_lap == -1:
                    logging.info("In a menu.")
                    self.game_state = GameState.IN_MENU

            case GameState.IN_RACE:
                if t.is_paused:
                    logging.info("Race is paused.")
                    self.game_state = GameState.PAUSED
                elif t.current_lap == -1:
                    logging.info("Race ended.")
                    self.game_state = GameState.END_RACE

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
                                logging.info("Resuming Race")
                                self.game_state = GameState.IN_RACE
                            else:
                                logging.info("Quit Race")
                                self.game_state = GameState.END_RACE

            case GameState.END_RACE:
                if not t.is_loading:
                    logging.info("At a track")
                    self.game_state = GameState.AT_TRACK

            case _:
                logging.debug(f"Unhandled state: {self.game_state}")

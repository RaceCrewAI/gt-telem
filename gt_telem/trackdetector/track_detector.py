# Portions of this file are adapted from gt7telemetry by Bornhall:
#   https://github.com/Bornhall/gt7telemetry/blob/main/gt7trackdetect.py

import csv
from importlib.resources import files
from gt_telem.models import Telemetry
from gt_telem.trackdetector.utils import TrackBounds, find_matching_track

PROBABILITY_THRESHOLD = 95


class TrackDetector:
    """
    Analyses telemetry packets received during a race to detect a track.

    The track is detected by computing a track rectangle based on vehicle position during 1 lap and matching it to tracks database.
    """
    track_id: int

    def __init__(self) -> None:
        self.track_id: int = None
        self._old_xyz: tuple[float, float] = None
        self._maxX = self._maxY = -999999.9
        self._minX = self._minY = 999999.9
        self._track_bounds = self._read_track_bounds()

    def detect_track(self, telemetry: Telemetry) -> int:
        """
        Detect a track from the telemetry data.
        """
        if telemetry.is_loading or telemetry.is_paused:
            return self.track_id
        if self.track_id and telemetry.cars_on_track:
            return self.track_id
        self.track_id = self._detect_track(telemetry)
        return self.track_id

    def _detect_track(self, telemetry: Telemetry) -> None:
        if not telemetry.cars_on_track:
            self._old_xyz = None
            self._maxX = self._maxY = -999999.9
            self._minX = self._minY = 999999.9
            return None

        new_xyz = [telemetry.position.x, telemetry.position.z]
        self._maxX = max(self._maxX, telemetry.position.x)
        self._minX = min(self._minX, telemetry.position.x)
        self._maxY = max(self._maxY, telemetry.position.z)
        self._minY = min(self._minY, telemetry.position.z)
        track_id = None
        if telemetry.current_lap > 1 and self._old_xyz is not None:
            matches = find_matching_track(self._old_xyz[0], self._old_xyz[1], new_xyz[0], new_xyz[1], self._minX, self._minY, self._maxX, self._maxY, self._track_bounds)
            if matches:
                best_match = matches[0]
                probability, _track_id = best_match[0], best_match[1]
                probability_percentage = round(probability * 100, 1)
                if probability_percentage >= PROBABILITY_THRESHOLD:
                    track_id = _track_id

        self._old_xyz = new_xyz
        return track_id

    def _read_track_bounds(self):
        csv_data = files('gt_telem.data').joinpath('gt7trackdetect.csv').read_text()
        rows = list(csv.DictReader(csv_data.splitlines()))
        return [TrackBounds(**row) for row in rows]

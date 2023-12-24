from __future__ import annotations

import logging
from time import sleep

from gt_telem.turismo_client import TurismoClient
from gt_telem.turismo_game import TurismoGame

logging.basicConfig(level=logging.DEBUG)

def handle_at_track():
    logging.info("I'm at the track")

def handle_race_end():
    logging.info("Hope it was a good one")

if __name__ == "__main__":
    logging.info("Starting...")
    tc = TurismoClient()
    tg = TurismoGame(tc)
    tg.on_at_track.append(handle_at_track)
    tg.on_race_end.append(handle_race_end)
    tc.run()

from __future__ import annotations

import logging
from time import sleep

from gt_telem.turismo_game import TurismoGame

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    logging.info("Starting...")
    tg = TurismoGame()

    while True:
        sleep(1)

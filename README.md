# Gran Turismo Telemetry
Python library for interfacing with Polyphony Digital's telemetry service for motion rigs in GT6/GTS/GT7 (maybe older?)

## Features
* Playstation IP Address discovery
* Asynchronous callbacks
* Game event observer
* Telemetry as an object or a dictionary

## Installation
Install with pip:
`pip install gt-telem`

## Usage

Getting telemetry is fairly straightforward. Here's a simple example:
```python
import json

from gt_telem import TurismoClient
from gt_telem.models import Telemetry

async def print_telem(t: Telemetry):
    print(json.dumps(t.as_dict, indent=4))

tc = TurismoClient()
tc.register_callback(print_telem)
tc.run()
```

`print_telem()` is invoked with each frame rendered (60hz). This tends to produces a lot of noise, especially when in menus, or even if the race is paused.

The full list of telemetry is available [here](https://github.com/RaceCrewAI/gt-telem/blob/main/gt_telem/models/telemetry.py).

## Events
The following events are currently supported:
* gt_telem.events.GameEvents
  * on_running - The game has started/is running
  * on_in_game_menu - Outside of a race or track screen
  * on_at_track - Player has entered a track screen
  * on_in_race - Fired when the simulation starts, before player control
  * on_paused - When the player pauses the race
  * on_race_end - Fires when a player leaves the simulation
* gt_telem.events.RaceEvents
  * on_race_start - Fired at the beginning of Lap 1
  * on_race_finish - Fired when the last lap is completed (checkered flag)
  * on_lap_change - Fires when the lap counter changes (including 0->1)
  * on_best_lap_time - A new best lap is set
  * on_last_lap_time - A new last lap time is available
* gt_telem.events.DriverEvents
  * on_gear_change - A gear has changed
  * on_flash_lights - High Beams have been activated
  * on_handbrake - Player has utilized handbrake
  * on_suggested_gear - Fires when the game suggests a gear change
  * on_tcs - Traction Control System activated
  * on_asm - Active Stability Management activated
  * on_rev_limit - Engine revs exceed threshold
  * on_brake - Player depresses brake
  * on_throttle - Player depresses throttle
  * on_shift_light_low - Engine revs entered lower bound for shift light
  * on_shift_light_high - Engine revs exceed upper bound for shift light

## Example using Events
Here's a more complex example of a telemetry recorder that hooks into race start, pause, and race end:

```python
from gt_telem import TurismoClient
from gt_telem.events import GameEvents
from gt_telem.errors.playstation_errors import *

class MySimpleTelemetryRecorder():
    def __init__(self, tc: TurismoClient):
        self.tc = tc
        self.storage = []

    def start(self):
        self.tc.register_callback(MySimpleTelemetryRecorder.receive_telem, [self])

    def stop(self):
        self.tc.deregister_callback(MySimpleTelemetryRecorder.receive_telem)
        # save self.storage somewhere

    @staticmethod
    async def receive_telem(t, context):
        context.storage.append(t)
        print(f"{t.engine_rpm}RPM - {t.boost_pressure}kPa")
        print(f"Best: {t.best_lap_time}\tLast: {t.last_lap_time}")


if __name__ == "__main__":
    try:
        tc = TurismoClient()
    except PlayStatonOnStandbyError as e:
        print("Turn the playstation on")
        print(e)
    except PlayStationNotFoundError:
        print("Maybe I'm on the wrong network")
        print(e)
    else:
        ge = GameEvents(tc)
        mstr = MySimpleTelemetryRecorder(tc)
        ge.on_in_race.append(mstr.start)
        ge.on_race_end.append(mstr.stop)
        ge.on_paused.append(mstr.stop)
        print("Listening for telemetry. CTRL+C to stop")
        tc.run()
```

`TurismoClient.run()` is a blocking call, but does shut down gracefully when a keyboard interrupt is issued. It also accepts a cancellation token.

### Advanced Example
See [this jupyter notebook](https://gist.github.com/Jonpro03/5856bc6df506f4d3c7741d4cb42157f1) that displays a live race view and how to properly pass a token to shut down gracefully.

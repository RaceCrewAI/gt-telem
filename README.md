# Gran Turismo Telemetry
Python library for interfacing with Polyphony Digital's telemetry service for motion rigs in GT6/GTS/GT7 (maybe older?)

## Features
* Playstation IP Address discovery
* Synchronous and asynchronous callbacks with thread pool execution
* Game event observer
* Telemetry as an object or a dictionary
* Configurable callback worker threads for optimal performance

## Installation
Install with pip:
`pip install gt-telem`

**Note**: The GUI uses heartbeat type "B" to access motion data including steering wheel rotation.

**Requirements:**
- Gran Turismo 7 running on PlayStation
- Telemetry enabled in GT7 settings
- PlayStation and PC on the same network
- Python 3.7+ with tkinter (included with most Python installations)


## Usage

Getting telemetry is fairly straightforward. Here's a simple example that runs the client on a separate thread:
```python
from gt_telem import TurismoClient
from time import sleep

tc = TurismoClient()

tc.start()
for i in range(10):
    sleep(1)
    print(tc.telemetry.position)
tc.stop()
```

If you're working inside of an asynchronous framework, use run_async()
```python
from gt_telem import TurismoClient

class MyAsyncClass:
    def __init__(self, tc: TurismoClient):
        self.tc = tc
        self.cancel_tkn: asyncio.Event = None

    async def start_telem(self):
        await self.tc.run_async(self.cancel_tkn)
```

Otherwise run like this if you only care for callbacks:
```python
import json

from gt_telem import TurismoClient
from gt_telem.models import Telemetry

# Both sync and async callbacks are supported
async def print_telem_async(t: Telemetry):
    print(json.dumps(t.as_dict, indent=4))

def print_telem_sync(t: Telemetry):
    print(f"Speed: {t.speed_mps:.2f} m/s")

tc = TurismoClient()
tc.register_callback(print_telem_async)  # Async callback
tc.register_callback(print_telem_sync)   # Sync callback
tc.run()  # Blocking call
```

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
  * on_track_detected - Track has been detected
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
        # Configure with more workers for heavy telemetry processing
        tc = TurismoClient(max_callback_workers=18)
    except PlayStationOnStandbyError as e:
        print("Turn the playstation on")
        print(e)
        exit()
    except PlayStationNotFoundError as e:
        print("Maybe I'm on the wrong network")
        print(e)
        exit()
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

## Heartbeat Types

Gran Turismo 7 supports different heartbeat message types that provide additional telemetry data. You can specify the heartbeat type when creating a `TurismoClient`:

```python
from gt_telem import TurismoClient

# Standard heartbeat (default) - 296 bytes
tc_standard = TurismoClient(heartbeat_type="A")

# Motion data heartbeat - 316 bytes with additional motion fields
tc_motion = TurismoClient(heartbeat_type="B")

# Extended data heartbeat - includes filtered inputs and energy recovery
tc_extended = TurismoClient(heartbeat_type="~")
```

### Heartbeat Type "A" (Standard)
This is the default format that provides all the standard telemetry data. Compatible with most existing GT7 telemetry applications.

### Heartbeat Type "B" (Motion Data)
Adds 5 additional motion-related fields:
- `wheel_rotation_radians` - Wheel rotation in radians
- `filler_float_fb` - Possibly lateral slip angle or other motion data
- `sway` - Vehicle sway motion
- `heave` - Vehicle heave motion  
- `surge` - Vehicle surge motion

Access motion data using the `motion_data` property:
```python
telemetry = tc.telemetry
if telemetry and telemetry.motion_data:
    motion = telemetry.motion_data
    print(f"Sway: {motion['sway']:.3f}")
    print(f"Heave: {motion['heave']:.3f}")
    print(f"Surge: {motion['surge']:.3f}")
```

### Heartbeat Type "~" (Extended Data)
Provides additional fields including:
- `throttle_filtered` - Filtered throttle input
- `brake_filtered` - Filtered brake input
- `energy_recovery` - Energy recovery value
- Additional unknown fields for future expansion

Access extended data using the `extended_data` property:
```python
telemetry = tc.telemetry
if telemetry and telemetry.extended_data:
    extended = telemetry.extended_data
    print(f"Energy Recovery: {extended['energy_recovery']:.3f}")
    print(f"Filtered Throttle: {extended['throttle_filtered']}")
```

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

## Hooking into game events
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

from __future__ import annotations

import math
import struct


def format_time(milliseconds):
    milliseconds = max(0, int(milliseconds))
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"


def format_time_of_day(milliseconds, use_24hr=False):
    milliseconds = max(0, int(milliseconds))
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    if use_24hr:
        am_pm = "AM" if hours < 12 else "PM"
        hours = hours % 12 or 12
        return f"{hours:02}:{minutes:02}:{seconds:02} {am_pm}"
    else:
        return f"{hours:02}:{minutes:02}:{seconds:02}"


class SpanReader:
    def __init__(self, data, byte_order="little"):
        self.view = memoryview(data)
        self.byte_order = "<" if byte_order == "little" else ">"
        self.position = 0

    def read_int32(self):
        format_string = f"{self.byte_order}i"
        value = struct.unpack_from(format_string, self.view, self.position)[0]
        self.position += 4
        return value

    def read_int16(self):
        format_string = f"{self.byte_order}h"
        value = struct.unpack_from(format_string, self.view, self.position)[0]
        self.position += 2
        return value

    def read_single(self):
        format_string = f"{self.byte_order}f"
        value = struct.unpack_from(format_string, self.view, self.position)[0]
        self.position += 4
        return value

    def read_byte(self):
        value = struct.unpack_from("B", self.view, self.position)[0]
        self.position += 1
        return value

    def read_bytes(self, length):
        value = self.view[self.position : self.position + length].tobytes()
        self.position += length
        return value

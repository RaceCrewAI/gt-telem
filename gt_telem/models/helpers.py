import math
import struct
from typing import Tuple

from transforms3d import euler, quaternions


def format_time(milliseconds):
    """
    Format milliseconds into a time string (MM:SS.sss).

    Parameters:
        - milliseconds (int): Time in milliseconds.

    Returns:
        str: Formatted time string.
    """
    milliseconds = max(0, int(milliseconds))
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"


def format_time_of_day(milliseconds, use_24hr=False):
    """
    Format milliseconds into a time of day string.

    Parameters:
        - milliseconds (int): Time in milliseconds.
        - use_24hr (bool): Flag indicating whether to use 24-hour format. Default is False.

    Returns:
        str: Formatted time of day string.
    """
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


def loop_angle(angle, range_size):
    while angle < -range_size / 2:
        angle += range_size
    while angle >= range_size / 2:
        angle -= range_size
    return angle


def quaternion_to_euler(w, i, j, k) -> tuple[float, float, float]:
    # Convert quaternion to Euler angles (roll, pitch, yaw)
    euler_angles = euler.quat2euler([w, i, j, k], axes='sxyz')
    roll, pitch, yaw = euler_angles
    return roll, pitch, yaw

class SpanReader:
    """
    Utility class for reading binary data in a structured manner.
    """

    def __init__(self, data, byte_order="little"):
        """
        Initialize the SpanReader.

        Parameters:
            - data: Binary data to read.
            - byte_order (str): Byte order for interpreting binary data, 'little' or 'big'.
        """
        self.view = memoryview(data)
        self.byte_order = "<" if byte_order == "little" else ">"
        self.position = 0

    def read_int32(self):
        """
        Read a 32-bit signed integer from the binary data.

        Returns:
            int: The read integer value.
        """
        format_string = f"{self.byte_order}i"
        value = struct.unpack_from(format_string, self.view, self.position)[0]
        self.position += 4
        return value

    def read_int16(self):
        """
        Read a 16-bit signed integer from the binary data.

        Returns:
            int: The read integer value.
        """
        format_string = f"{self.byte_order}h"
        value = struct.unpack_from(format_string, self.view, self.position)[0]
        self.position += 2
        return value

    def read_single(self):
        """
        Read a 32-bit floating-point number from the binary data.

        Returns:
            float: The read floating-point value.
        """
        format_string = f"{self.byte_order}f"
        value = struct.unpack_from(format_string, self.view, self.position)[0]
        self.position += 4
        return value

    def read_byte(self):
        """
        Read a byte from the binary data.

        Returns:
            int: The read byte value.
        """
        value = struct.unpack_from("B", self.view, self.position)[0]
        self.position += 1
        return value

    def read_bytes(self, length):
        """
        Read a specified number of bytes from the binary data.

        Parameters:
            - length (int): Number of bytes to read.

        Returns:
            bytes: The read bytes.
        """
        value = self.view[self.position : self.position + length].tobytes()
        self.position += length
        return value

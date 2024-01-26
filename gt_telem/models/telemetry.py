import math
from datetime import datetime

from gt_telem.models.helpers import (format_time, format_time_of_day,
                                     loop_angle, quaternion_to_euler)
from gt_telem.models.models import Vector3D, WheelMetric
from gt_telem.models.telemetry_packet import TelemetryPacket


class Telemetry(TelemetryPacket):
    """
    Telemetry data from Gran Turismo

    Attributes:
    - position_x (float): X-coordinate of the position.
    - position_y (float): Y-coordinate of the position.
    - position_z (float): Z-coordinate of the position.
    - velocity_x (float): X-component of velocity.
    - velocity_y (float): Y-component of velocity.
    - velocity_z (float): Z-component of velocity.
    - rotation_i (float): I-component of rotation quaternion.
    - rotation_j (float): J-component of rotation quaternion.
    - rotation_k (float): K-component of rotation quaternion.
    - rotation_w (float): W-component of rotation quaternion.
    - ang_vel_x (float): X-component of angular velocity.
    - ang_vel_y (float): Y-component of angular velocity.
    - ang_vel_z (float): Z-component of angular velocity.
    - body_height (float): Height of the body.
    - engine_rpm (float): Engine RPM.
    - iv (float): IV, used for encryption.
    - fuel_level (float): Fuel level.
    - fuel_capacity (float): Fuel capacity.
    - speed_mps (float): Speed in meters per second.
    - boost_pressure (float): Boost pressure.
    - oil_pressure (float): Oil pressure.
    - water_temp (float): Water temperature.
    - oil_temp (float): Oil temperature.
    - tire_fl_temp (float): Front-left tire temperature.
    - tire_fr_temp (float): Front-right tire temperature.
    - tire_rl_temp (float): Rear-left tire temperature.
    - tire_rr_temp (float): Rear-right tire temperature.
    - packet_id (int): Packet ID.
    - current_lap (int): Current lap.
    - total_laps (int): Total laps.
    - best_lap_time_ms (int): Best lap time in milliseconds.
    - last_lap_time_ms (int): Last lap time in milliseconds.
    - time_of_day_ms (int): Time of day in milliseconds.
    - race_start_pos (int): Race start position.
    - total_cars (int): Total number of cars.
    - min_alert_rpm (int): Minimum alert RPM.
    - max_alert_rpm (int): Maximum alert RPM.
    - calc_max_speed (int): Calculated maximum speed.
    - flags (int): Byte that contains current/suggested gear.
    - bits (int): Collection of booleans - see properties.
    - throttle (int): Throttle.
    - brake (int): Brake.
    - empty (int): Unused.
    - road_plane_i (float): I-coordinate of the road plane quaternion.
    - road_plane_j (float): J-coordinate of the road plane quaternion.
    - road_plane_k (float): K-coordinate of the road plane quaternion.
    - road_plane_w (float): W-coordinate of the road plane quaternion.
    - wheel_fl_rps (float): Front-left wheel revolutions per second.
    - wheel_fr_rps (float): Front-right wheel revolutions per second.
    - wheel_rl_rps (float): Rear-left wheel revolutions per second.
    - wheel_rr_rps (float): Rear-right wheel revolutions per second.
    - tire_fl_radius (float): Front-left tire radius.
    - tire_fr_radius (float): Front-right tire radius.
    - tire_rl_radius (float): Rear-left tire radius.
    - tire_rr_radius (float): Rear-right tire radius.
    - tire_fl_sus_height (float): Front-left tire suspension height.
    - tire_fr_sus_height (float): Front-right tire suspension height.
    - tire_rl_sus_height (float): Rear-left tire suspension height.
    - tire_rr_sus_height (float): Rear-right tire suspension height.
    - unused1 (int): Unused variable 1.
    - unused2 (int): Unused variable 2.
    - unused3 (int): Unused variable 3.
    - unused4 (int): Unused variable 4.
    - unused5 (int): Unused variable 5.
    - unused6 (int): Unused variable 6.
    - unused7 (int): Unused variable 7.
    - unused8 (int): Unused variable 8.
    - clutch_pedal (float): Clutch pedal position.
    - clutch_engagement (float): Clutch engagement.
    - trans_rpm (float): Transmission RPM.
    - trans_top_speed (float): Transmission top speed.
    - gear1 (float): Gear 1.
    - gear2 (float): Gear 2.
    - gear3 (float): Gear 3.
    - gear4 (float): Gear 4.
    - gear5 (float): Gear 5.
    - gear6 (float): Gear 6.
    - gear7 (float): Gear 7.
    - gear8 (float): Gear 8.
    - car_code (int): Car code - on vehicles with more than 8 gears, this is corrupted.

    Properties:
    - position (Vector3D): Get the position as a Vector3D.
    - velocity (Vector3D): Get the velocity as a Vector3D.
    - angular_velocity (Vector3D): Get the angular velocity as a Vector3D.
    - tire_temp (WheelMetric): Get tire temperatures as a WheelMetric.
    - wheel_rps (WheelMetric): Get wheel revolutions per second as a WheelMetric.
    - tire_radius (WheelMetric): Get tire radii as a WheelMetric.
    - suspension_height (WheelMetric): Get suspension heights as a WheelMetric.
    - current_gear (int): Get the current gear.
    - suggested_gear (int): Get the suggested gear.
    - speed_kph (float): Get the speed in kilometers per hour.
    - speed_mph (float): Get the speed in miles per hour.
    - cars_on_track (bool): Check if there are cars on the track.
    - is_paused (bool): Check if the simulation is paused.
    - is_loading (bool): Check if the simulation is loading.
    - in_gear (bool): Check if the vehicle is in gear.
    - has_turbo (bool): Check if the vehicle has a turbo.
    - rev_limit (bool): Check if the vehicle is at the rev limit.
    - hand_brake_active (bool): Check if the hand brake is active.
    - lights_active (bool): Check if the lights are active.
    - high_beams (bool): Check if the high beams are active.
    - low_beams (bool): Check if the low beams are active.
    - asm_active (bool): Check if the ASM (Active Stability Management) is active.
    - tcs_active (bool): Check if the TCS (Traction Control System) is active.
    - unknown_bool_1 (bool): Purpose unknown.
    - unknown_bool_2 (bool): Purpose unknown.
    - unknown_bool_3 (bool): Purpose unknown.
    - unknown_bool_4 (bool): Purpose unknown.
    - best_lap_time (str): Get the formatted best lap time.
    - last_lap_time (str): Get the formatted last lap time.
    - time_of_day (str): Get the formatted time of day.
    - vehicle_roll (float): Roll in degrees.
    - vehicle_pitch (float): Pitch in degrees.
    - vehicle_yaw (float): Yaw in degrees.
    - vehicle_surge (float): Surge for simfeedback.
    - vehicle_heave (float): Heave for simfeedback.
    - plane_roll (float): Roll in degrees.
    - plane_pitch (float): Pitch in degrees.
    - plane_yaw (float): Yaw in degrees.

    Methods:
    - as_dict(): Get the state of the object in a dictionary format.
    - from_dict(): Get telemetry instance from the as_dict property.
    """

    @property
    def position(self) -> Vector3D:
        """
        Get the position as a Vector3D.
        """
        return Vector3D(self.position_x, self.position_y, self.position_z)

    @property
    def velocity(self) -> Vector3D:
        """
        Get the velocity as a Vector3D.
        """
        return Vector3D(self.velocity_x, self.velocity_y, self.velocity_z)

    @property
    def angular_velocity(self) -> Vector3D:
        """
        Get the angular velocity as a Vector3D.
        """
        return Vector3D(self.ang_vel_x, self.ang_vel_y, self.ang_vel_z)

    @property
    def tire_temp(self) -> WheelMetric:
        """
        Get tire temperatures as a WheelMetric.
        """
        return WheelMetric(
            self.tire_fl_temp, self.tire_fr_temp, self.tire_rl_temp, self.tire_rr_temp
        )

    @property
    def wheel_rps(self) -> WheelMetric:
        """
        Get wheel revolutions per second as a WheelMetric.
        """
        return WheelMetric(
            self.wheel_fl_rps, self.wheel_fr_rps, self.wheel_rl_rps, self.wheel_rr_rps
        )

    @property
    def tire_radius(self) -> WheelMetric:
        """
        Get tire radii as a WheelMetric.
        """
        return WheelMetric(
            self.tire_fl_radius,
            self.tire_fr_radius,
            self.tire_rl_radius,
            self.tire_rr_radius,
        )

    @property
    def suspension_height(self) -> WheelMetric:
        """
        Get suspension heights as a WheelMetric.
        """
        return WheelMetric(
            self.tire_fl_sus_height,
            self.tire_fr_sus_height,
            self.tire_rl_sus_height,
            self.tire_rr_sus_height,
        )

    @property
    def current_gear(self) -> int:
        """
        Get the current gear.
        """
        return self.bits & 0b1111

    @property
    def suggested_gear(self) -> int:
        """
        Get the suggested gear.
        """
        return self.bits >> 4

    @property
    def speed_kph(self) -> float:
        """
        Get the speed in kilometers per hour.
        """
        return self.speed_mps * 3.6

    @property
    def speed_mph(self) -> float:
        """
        Get the speed in miles per hour.
        """
        return self.speed_mps * 2.23694

    @property
    def cars_on_track(self) -> bool:
        """
        Check if there are cars on the track.
        """
        return bool(1<<0 & self.flags)

    @property
    def is_paused(self) -> bool:
        """
        Check if the simulation is paused.
        """
        return bool(1<<1 & self.flags)

    @property
    def is_loading(self) -> bool:
        """
        Check if the simulation is loading.
        """
        return bool(1<<2 & self.flags)

    @property
    def in_gear(self) -> bool:
        """
        Check if the vehicle is in gear.
        """
        return bool(1<<3 & self.flags)

    @property
    def has_turbo(self) -> bool:
        """
        Check if the vehicle has a turbo.
        """
        return bool(1<<4 & self.flags)

    @property
    def rev_limit(self) -> bool:
        """
        Check if the vehicle is at the rev limit.
        """
        return bool(1<<5 & self.flags)

    @property
    def hand_brake_active(self) -> bool:
        """
        Check if the hand brake is active.
        """
        return bool(1<<6 & self.flags)

    @property
    def lights_active(self) -> bool:
        """
        Check if the lights are active.
        """
        return bool(1<<7 & self.flags)

    @property
    def high_beams(self) -> bool:
        """
        Check if the high beams are active.
        """
        return bool(1<<8 & self.flags)

    @property
    def low_beams(self) -> bool:
        """
        Check if the low beams are active.
        """
        return bool(1<<9 & self.flags)

    @property
    def asm_active(self) -> bool:
        """
        Check if the ASM (Active Stability Management) is active.
        """
        return bool(1<<10 & self.flags)

    @property
    def tcs_active(self) -> bool:
        """
        Check if the TCS (Traction Control System) is active.
        """
        return bool(1<<11 & self.flags)

    @property
    def unknown_bool_1(self) -> bool:
        """
        Get the value of an unknown boolean flag.
        """
        return bool(1<<12 & self.flags)

    @property
    def unknown_bool_2(self) -> bool:
        """
        Not sure
        """
        return bool(1<<13 & self.flags)

    @property
    def unknown_bool_3(self) -> bool:
        """
        Get the value of another unknown boolean flag.
        """
        return bool(1<<14 & self.flags)

    @property
    def unknown_bool_4(self) -> bool:
        """
        Get the value of another unknown boolean flag.
        """
        return bool(1<<15 & self.flags)

    @property
    def best_lap_time(self) -> str:
        """
        Get the formatted best lap time.
        """
        if self.best_lap_time_ms == -1:
            return None
        return format_time(self.best_lap_time_ms)

    @property
    def last_lap_time(self) -> str:
        """
        Get the formatted last lap time.
        """
        if self.last_lap_time_ms == -1:
            return None
        return format_time(self.last_lap_time_ms)

    @property
    def time_of_day(self) -> str:
        """
        Get the formatted time of day.
        """
        if self.time_of_day_ms == -1:
            return None
        return format_time_of_day(self.time_of_day_ms)

    # for simfeedback
    @property
    def vehicle_roll(self) -> float:
        """
        Get the roll Euler angle in degrees.

        Returns:
            float: The roll Euler angle in degrees.
        """
        if not self.rotation_euler:
            self.rotation_euler = quaternion_to_euler(self.rotation_w, self.rotation_i, self.rotation_j, self.rotation_k)
        #return loop_angle(math.degrees(self.rotation_euler[0]), 180)
        return math.degrees(self.rotation_euler[0])

    @property
    def vehicle_pitch(self) -> float:
        """
        Get the pitch Euler angle in degrees.

        Returns:
            float: The pitch Euler angle in degrees.
        """
        if not self.rotation_euler:
            self.rotation_euler = quaternion_to_euler(self.rotation_w, self.rotation_i, self.rotation_j, self.rotation_k)
        return math.degrees(self.rotation_euler[1])

    @property
    def vehicle_yaw(self) -> float:
        """
        Get the yaw Euler angle in degrees.

        Returns:
            float: The yaw Euler angle in degrees.
        """
        if not self.rotation_euler:
            self.rotation_euler = quaternion_to_euler(self.rotation_w, self.rotation_i, self.rotation_j, self.rotation_k)
        return math.degrees(self.rotation_euler[2])

    @property
    def vehicle_surge(self) -> float:
        """
        Get the surge velocity.

        Returns:
            float: The surge velocity.
        """
        return velocity_x * 0.10197162129779

    @property
    def vehicle_heave(self) -> float:
        """
        Get the heave velocity.

        Returns:
            float: The heave velocity.
        """
        return velocity_y * 0.10197162129779

    @property
    def plane_roll(self) -> float:
        """
        Get the roll Euler angle in degrees.

        Returns:
            float: The roll Euler angle in degrees.
        """
        if not self.plane_euler:
            self.plane_euler = quaternion_to_euler(self.road_plane_w, self.road_plane_i, self.road_plane_j, self.road_plane_k)
        return loop_angle(math.degrees(self.plane_euler[0]), 180)

    @property
    def plane_pitch(self) -> float:
        """
        Get the pitch Euler angle in degrees.

        Returns:
            float: The pitch Euler angle in degrees.
        """
        if not self.plane_euler:
            self.plane_euler = quaternion_to_euler(self.road_plane_w, self.road_plane_i, self.road_plane_j, self.road_plane_k )
        return math.degrees(self.plane_euler[1])

    @property
    def plane_yaw(self) -> float:
        """
        Get the yaw Euler angle in degrees.

        Returns:
            float: The yaw Euler angle in degrees.
        """
        if not self.plane_euler:
            self.plane_euler = quaternion_to_euler(self.road_plane_w, self.road_plane_i, self.road_plane_j, self.road_plane_k)
        return math.degrees(self.plane_euler[2])

    @property
    def as_dict(self):
        """
        Returns a dictionary containing the state of the object.
        """
        remove_keys = [
            x
            for x in self.__dict__.keys()
            if any(
                ignore in x
                for ignore in [
                    "_x",
                    "_y",
                    "_z",
                    "flags",
                    "bits",
                    "empty",
                    "unused",
                    "_fl",
                    "_fr",
                    "_rl",
                    "_rr",
                ]
            )
        ]

        added = {
            "position": self.position,
            "velocity": self.velocity,
            "angular_velocity": self.angular_velocity,
            "tire_temp": self.tire_temp,
            "wheel_rps": self.wheel_rps,
            "tire_radius": self.tire_radius,
            "suspension_height": self.suspension_height,
            "current_gear": self.current_gear,
            "suggested_gear": self.suggested_gear,
            "speed_kph": self.speed_kph,
            "speed_mph": self.speed_mph,
            "cars_on_track": self.cars_on_track,
            "is_paused": self.is_paused,
            "is_loading": self.is_loading,
            "in_gear": self.in_gear,
            "has_turbo": self.has_turbo,
            "rev_limit": self.rev_limit,
            "hand_brake_active": self.hand_brake_active,
            "lights_active": self.lights_active,
            "high_beams": self.high_beams,
            "low_beams": self.low_beams,
            "asm_active": self.asm_active,
            "tcs_active": self.tcs_active,
            "unknown_bool_1": self.unknown_bool_1,
            "unknown_bool_2": self.unknown_bool_2,
            "unknown_bool_3": self.unknown_bool_3,
            "unknown_bool_4": self.unknown_bool_4,
            "best_lap_time": self.best_lap_time,
            "last_lap_time": self.last_lap_time,
            "time_of_day": self.time_of_day,
        }

        result = dict(self.__dict__, **added)
        for remove_key in remove_keys:
            result.pop(remove_key, None)

        return result

    @staticmethod
    def from_dict(d):
        """
        Get telemetry instance from the as_dict property
        Useful for replays
        """

        # pop the vector3s
        for vec3 in ["position", "velocity", "rotation", "angular_velocity", "road_plane"]:
            prop = d.pop(vec3)
            if vec3 == "angular_velocity":
                vec3 = "ang_vel"
            d[f"{vec3}_x"] = prop[0]
            d[f"{vec3}_y"] = prop[1]
            d[f"{vec3}_z"] = prop[2]
        # pop the corners
        for whmet, attr in {
            "tire_temp": "tire_{0}_temp",
            "wheel_rps": "wheel_{0}_rps",
            "tire_radius": "tire_{0}_radius",
            "suspension_height": "tire_{0}_sus_height"
        }.items():
            prop = d.pop(whmet)
            for i, k in {
                0: "fl",
                1: "fr",
                2: "rl",
                3: "rr"
            }.items():
                d[attr.format(k)] = prop[i]
        # rebuild the bits attr
        sg = d.pop("suggested_gear") & 0xF
        cg = d.pop("current_gear") & 0xF
        d["bits"] = (sg << 4) | cg

        # just remove these:
        for prop in ["speed_kph", "speed_mph", "best_lap_time", "last_lap_time", "time_of_day"]:
            d.pop(prop)

        # Add back ones removed:
        d["empty"] = 0
        for i in range(8):
            d[f"unused{i+1}"] = 0

        # rebuild flags
        d["flags"] = (
            (1<<0 if d.pop("cars_on_track") else 0) |
            (1<<1 if d.pop("is_paused") else 0) |
            (1<<2 if d.pop("is_loading") else 0) |
            (1<<3 if d.pop("in_gear") else 0) |
            (1<<4 if d.pop("has_turbo") else 0) |
            (1<<5 if d.pop("rev_limit") else 0) |
            (1<<6 if d.pop("hand_brake_active") else 0) |
            (1<<7 if d.pop("lights_active") else 0) |
            (1<<8 if d.pop("high_beams") else 0) |
            (1<<9 if d.pop("low_beams") else 0) |
            (1<<10 if d.pop("asm_active") else 0) |
            (1<<11 if d.pop("tcs_active") else 0) |
            (1<<12 if d.pop("unknown_bool_1", False) else 0) |
            (1<<13 if d.pop("clutch_out", False) else 0) |
            (1<<13 if d.pop("unknown_bool_2", False) else 0) |
            (1<<14 if d.pop("unknown_bool_3", False) else 0) |
            (1<<15 if d.pop("unknown_bool_4", False) else 0)
        )

        return Telemetry(**d)

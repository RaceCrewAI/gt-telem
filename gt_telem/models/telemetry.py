from datetime import datetime

from gt_telem.models.helpers import format_time, format_time_of_day
from gt_telem.models.models import Vector3D, WheelMetric
from gt_telem.models.telemetry_packet import TelemetryPacket


class Telemetry(TelemetryPacket):
    """
    Telemetry data from Gran Turismo

    Attributes:
    - position_x: float - X-coordinate of the position.
    - position_y: float - Y-coordinate of the position.
    - position_z: float - Z-coordinate of the position.
    - velocity_x: float - X-component of velocity.
    - velocity_y: float - Y-component of velocity.
    - velocity_z: float - Z-component of velocity.
    - rotation_x: float - X-component of rotation.
    - rotation_y: float - Y-component of rotation.
    - rotation_z: float - Z-component of rotation.
    - orientation: float - Orientation.
    - ang_vel_x: float - X-component of angular velocity.
    - ang_vel_y: float - Y-component of angular velocity.
    - ang_vel_z: float - Z-component of angular velocity.
    - body_height: float - Height of the body.
    - engine_rpm: float - Engine RPM.
    - iv: float - IV, used for encryption.
    - fuel_level: float - Fuel level.
    - fuel_capacity: float - Fuel capacity.
    - speed_mps: float - Speed in meters per second.
    - boost_pressure: float - Boost pressure.
    - oil_pressure: float - Oil pressure.
    - water_temp: float - Water temperature.
    - oil_temp: float - Oil temperature.
    - tire_fl_temp: float - Front-left tire temperature.
    - tire_fr_temp: float - Front-right tire temperature.
    - tire_rl_temp: float - Rear-left tire temperature.
    - tire_rr_temp: float - Rear-right tire temperature.
    - packet_id: int - Packet ID.
    - current_lap: int - Current lap.
    - total_laps: int - Total laps.
    - best_lap_time_ms: int - Best lap time in milliseconds.
    - last_lap_time_ms: int - Last lap time in milliseconds.
    - time_of_day_ms: int - Time of day in milliseconds.
    - race_start_pos: int - Race start position.
    - total_cars: int - Total number of cars.
    - min_alert_rpm: int - Minimum alert RPM.
    - max_alert_rpm: int - Maximum alert RPM.
    - calc_max_speed: int - Calculated maximum speed.
    - flags: int - byte that contains current/suggested gear.
    - bits: int - Collection of booleans - see properties.
    - throttle: int - Throttle.
    - brake: int - Brake.
    - empty: int - Unused.
    - road_plane_x: float - X-coordinate of the road plane.
    - road_plane_y: float - Y-coordinate of the road plane.
    - road_plane_z: float - Z-coordinate of the road plane.
    - road_plane_dist: float - Distance of the road plane. Not sure what this is.
    - wheel_fl_rps: float - Front-left wheel revolutions per second.
    - wheel_fr_rps: float - Front-right wheel revolutions per second.
    - wheel_rl_rps: float - Rear-left wheel revolutions per second.
    - wheel_rr_rps: float - Rear-right wheel revolutions per second.
    - tire_fl_radius: float - Front-left tire radius.
    - tire_fr_radius: float - Front-right tire radius.
    - tire_rl_radius: float - Rear-left tire radius.
    - tire_rr_radius: float - Rear-right tire radius.
    - tire_fl_sus_height: float - Front-left tire suspension height.
    - tire_fr_sus_height: float - Front-right tire suspension height.
    - tire_rl_sus_height: float - Rear-left tire suspension height.
    - tire_rr_sus_height: float - Rear-right tire suspension height.
    - unused1: int - Unused variable 1.
    - unused2: int - Unused variable 2.
    - unused3: int - Unused variable 3.
    - unused4: int - Unused variable 4.
    - unused5: int - Unused variable 5.
    - unused6: int - Unused variable 6.
    - unused7: int - Unused variable 7.
    - unused8: int - Unused variable 8.
    - clutch_pedal: float - Clutch pedal position.
    - clutch_engagement: float - Clutch engagement.
    - trans_rpm: float - Transmission RPM.
    - trans_top_speed: float - Transmission top speed.
    - gear1: float - Gear 1.
    - gear2: float - Gear 2.
    - gear3: float - Gear 3.
    - gear4: float - Gear 4.
    - gear5: float - Gear 5.
    - gear6: float - Gear 6.
    - gear7: float - Gear 7.
    - gear8: float - Gear 8.
    - car_code: int - Car code - on vehicles with more than 8 gears, this is corrupted.

    Properties:
    - position: Get the position as a Vector3D.
    - velocity: Get the velocity as a Vector3D.
    - rotation: Get the rotation as a Vector3D.
    - angular_velocity: Get the angular velocity as a Vector3D.
    - road_plane: Get the road plane coordinates as a Vector3D.
    - tire_temp: Get tire temperatures as a WheelMetric.
    - wheel_rps: Get wheel revolutions per second as a WheelMetric.
    - tire_radius: Get tire radii as a WheelMetric.
    - suspension_height: Get suspension heights as a WheelMetric.
    - current_gear: Get the current gear.
    - suggested_gear: Get the suggested gear.
    - speed_kph: Get the speed in kilometers per hour.
    - speed_mph: Get the speed in miles per hour.
    - cars_on_track: Check if there are cars on the track.
    - is_paused: Check if the simulation is paused.
    - is_loading: Check if the simulation is loading.
    - in_gear: Check if the vehicle is in gear.
    - has_turbo: Check if the vehicle has a turbo.
    - rev_limit: Check if the vehicle is at the rev limit.
    - hand_brake_active: Check if the hand brake is active.
    - lights_active: Check if the lights are active.
    - high_beams: Check if the high beams are active.
    - low_beams: Check if the low beams are active.
    - asm_active: Check if the ASM (Active Stability Management) is active.
    - tcs_active: Check if the TCS (Traction Control System) is active.
    - unknown_bool_1: Usually true. Purpose unknown.
    - clutch_out: Check if the clutch is out.
    - unknown_bool_3: Usually true. Purpose unknown.
    - best_lap_time: Get the formatted best lap time.
    - last_lap_time: Get the formatted last lap time.
    - time_of_day: Get the formatted time of day.

    Methods
    - as_dict: Get the state of the object in a dictionary format.
    """

    def __post_init__(self):
        self.time = datetime.now()

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
    def rotation(self) -> Vector3D:
        """
        Get the rotation as a Vector3D.
        """
        return Vector3D(self.rotation_x, self.rotation_y, self.rotation_z)

    @property
    def angular_velocity(self) -> Vector3D:
        """
        Get the angular velocity as a Vector3D.
        """
        return Vector3D(self.ang_vel_x, self.ang_vel_y, self.ang_vel_z)

    @property
    def road_plane(self) -> Vector3D:
        """
        Get the road plane coordinates as a Vector3D.
        """
        return Vector3D(self.road_plane_x, self.road_plane_y, self.road_plane_z)

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
        return bool(1 & self.flags)

    @property
    def is_paused(self) -> bool:
        """
        Check if the simulation is paused.
        """
        return bool(2 & self.flags)

    @property
    def is_loading(self) -> bool:
        """
        Check if the simulation is loading.
        """
        return bool(3 & self.flags)

    @property
    def in_gear(self) -> bool:
        """
        Check if the vehicle is in gear.
        """
        return bool(4 & self.flags)

    @property
    def has_turbo(self) -> bool:
        """
        Check if the vehicle has a turbo.
        """
        return bool(5 & self.flags)

    @property
    def rev_limit(self) -> bool:
        """
        Check if the vehicle is at the rev limit.
        """
        return bool(6 & self.flags)

    @property
    def hand_brake_active(self) -> bool:
        """
        Check if the hand brake is active.
        """
        return bool(7 & self.flags)

    @property
    def lights_active(self) -> bool:
        """
        Check if the lights are active.
        """
        return bool(8 & self.flags)

    @property
    def high_beams(self) -> bool:
        """
        Check if the high beams are active.
        """
        return bool(9 & self.flags)

    @property
    def low_beams(self) -> bool:
        """
        Check if the low beams are active.
        """
        return bool(10 & self.flags)

    @property
    def asm_active(self) -> bool:
        """
        Check if the ASM (Active Stability Management) is active.
        """
        return bool(11 & self.flags)

    @property
    def tcs_active(self) -> bool:
        """
        Check if the TCS (Traction Control System) is active.
        """
        return bool(12 & self.flags)

    @property
    def unknown_bool_1(self) -> bool:
        """
        Get the value of an unknown boolean flag.
        """
        return bool(13 & self.flags)

    @property
    def clutch_out(self) -> bool:
        """
        Check if the clutch is out.
        """
        return bool(14 & self.flags)

    @property
    def unknown_bool_3(self) -> bool:
        """
        Get the value of another unknown boolean flag.
        """
        return bool(15 & self.flags)

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
            "rotation": self.rotation,
            "angular_velocity": self.angular_velocity,
            "road_plane": self.road_plane,
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
            "clutch_out": self.clutch_out,
            "unknown_bool_3": self.unknown_bool_3,
            "best_lap_time": self.best_lap_time,
            "last_lap_time": self.last_lap_time,
            "time_of_day": self.time_of_day,
        }

        result = dict(self.__dict__, **added)
        for remove_key in remove_keys:
            result.pop(remove_key, None)

        return result

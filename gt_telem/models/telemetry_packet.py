from dataclasses import dataclass
from datetime import datetime


@dataclass
class TelemetryPacket:
    position_x: float
    position_y: float
    position_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    rotation_w: float
    rotation_i: float
    rotation_j: float
    rotation_k: float
    ang_vel_x: float
    ang_vel_y: float
    ang_vel_z: float
    body_height: float
    engine_rpm: float
    iv: float
    fuel_level: float
    fuel_capacity: float
    speed_mps: float
    boost_pressure: float
    oil_pressure: float
    water_temp: float
    oil_temp: float
    tire_fl_temp: float
    tire_fr_temp: float
    tire_rl_temp: float
    tire_rr_temp: float
    packet_id: int
    current_lap: int
    total_laps: int
    best_lap_time_ms: int
    last_lap_time_ms: int
    time_of_day_ms: int
    race_start_pos: int
    total_cars: int
    min_alert_rpm: int
    max_alert_rpm: int
    calc_max_speed: int
    flags: int
    bits: int
    throttle: int
    brake: int
    empty: int
    road_plane_w: float
    road_plane_i: float
    road_plane_j: float
    road_plane_k: float
    wheel_fl_rps: float
    wheel_fr_rps: float
    wheel_rl_rps: float
    wheel_rr_rps: float
    tire_fl_radius: float
    tire_fr_radius: float
    tire_rl_radius: float
    tire_rr_radius: float
    tire_fl_sus_height: float
    tire_fr_sus_height: float
    tire_rl_sus_height: float
    tire_rr_sus_height: float
    unused1: int
    unused2: int
    unused3: int
    unused4: int
    unused5: int
    unused6: int
    unused7: int
    unused8: int
    clutch_pedal: float
    clutch_engagement: float
    trans_rpm: float
    trans_top_speed: float
    gear1: float
    gear2: float
    gear3: float
    gear4: float
    gear5: float
    gear6: float
    gear7: float
    gear8: float
    car_code: int

    def __post_init__(self):
        self.time = datetime.now()
        self.rotation_euler = None
        self.plane_euler = None

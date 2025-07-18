from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemetryPacket:
    position_x: float
    position_y: float
    position_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    orientation: float
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
    road_plane_x: float
    road_plane_y: float
    road_plane_z: float
    road_plane_dist: float
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
    
    # Additional fields for heartbeat type "B" (motion data)
    wheel_rotation_radians: Optional[float] = None
    filler_float_fb: Optional[float] = None  # Possibly lateral slip angle
    sway: Optional[float] = None
    heave: Optional[float] = None
    surge: Optional[float] = None
    
    # Additional fields for heartbeat type "~" (extended data)
    throttle_filtered: Optional[int] = None  # Filtered throttle value
    brake_filtered: Optional[int] = None     # Filtered brake value
    unk_tilde_1: Optional[int] = None       # Unknown field 1
    unk_tilde_2: Optional[int] = None       # Unknown field 2
    energy_recovery: Optional[float] = None  # Energy recovery value
    unk_tilde_3: Optional[float] = None     # Unknown field 3

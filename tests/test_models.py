import unittest
from datetime import datetime

from gt_telem.models import Telemetry, Vector3D


class TestTelemetry(unittest.TestCase):
    def setUp(self):
        self.telemetry = Telemetry(
            position_x=1.0,
            position_y=2.0,
            position_z=3.0,
            velocity_x=4.0,
            velocity_y=5.0,
            velocity_z=6.0,
            rotation_x=7.0,
            rotation_y=8.0,
            rotation_z=9.0,
            orientation=10.0,
            ang_vel_x=11.0,
            ang_vel_y=12.0,
            ang_vel_z=13.0,
            body_height=14.0,
            engine_rpm=15.0,
            iv=16.0,
            fuel_level=17.0,
            fuel_capacity=18.0,
            speed_mps=19.0,
            boost_pressure=20.0,
            oil_pressure=21.0,
            water_temp=22.0,
            oil_temp=23.0,
            tire_fl_temp=24.0,
            tire_fr_temp=25.0,
            tire_rl_temp=26.0,
            tire_rr_temp=27.0,
            packet_id=28,
            current_lap=29,
            total_laps=30,
            best_lap_time_ms=31,
            last_lap_time_ms=32,
            time_of_day_ms=33,
            race_start_pos=34,
            total_cars=35,
            min_alert_rpm=36,
            max_alert_rpm=37,
            calc_max_speed=38,
            flags=39,
            bits=40,
            throttle=41,
            brake=42,
            empty=43,
            road_plane_x=44.0,
            road_plane_y=45.0,
            road_plane_z=46.0,
            road_plane_dist=47.0,
            wheel_fl_rps=48.0,
            wheel_fr_rps=49.0,
            wheel_rl_rps=50.0,
            wheel_rr_rps=51.0,
            tire_fl_radius=52.0,
            tire_fr_radius=53.0,
            tire_rl_radius=54.0,
            tire_rr_radius=55.0,
            tire_fl_sus_height=56.0,
            tire_fr_sus_height=57.0,
            tire_rl_sus_height=58.0,
            tire_rr_sus_height=59.0,
            unused1=60,
            unused2=61,
            unused3=62,
            unused4=63,
            unused5=64,
            unused6=65,
            unused7=66,
            unused8=67,
            clutch_pedal=68.0,
            clutch_engagement=69.0,
            trans_rpm=70.0,
            trans_top_speed=71.0,
            gear1=72.0,
            gear2=73.0,
            gear3=74.0,
            gear4=75.0,
            gear5=76.0,
            gear6=77.0,
            gear7=78.0,
            gear8=79.0,
            car_code=80,
        )

    def test_position_property(self):
        self.assertEqual(self.telemetry.position, Vector3D(1.0, 2.0, 3.0))

    def test_velocity_property(self):
        self.assertEqual(self.telemetry.velocity, Vector3D(4.0, 5.0, 6.0))

    def test_time_formatting(self):
        pass

    def tearDown(self):
        # Clean up if needed
        pass


if __name__ == "__main__":
    unittest.main()

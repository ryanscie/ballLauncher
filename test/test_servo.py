#!/usr/bin/env python3
"""
Test: move a servo on a fixed BCM pin to 0° using gpiozero.Servo.

- Uses Futaba S3003 calibration from config.py (SERVO_MIN_DC/SERVO_MAX_DC @ SERVO_PWM_FREQ).
- Fixed BCM pin below; edit PIN if needed.
"""

import time
from gpiozero import Servo
import config

# Fixed BCM pin for this test
PIN = 12  # BCM pin. Change here if your servo signal is wired elsewhere.


def deg_to_value(deg: float) -> float:
    """
    Map degrees [0..180] to gpiozero.Servo.value [-1..+1]
    0° -> -1.0, 90° -> 0.0, 180° -> +1.0
    """
    d = max(0.0, min(180.0, float(deg)))
    return (d / 90.0) - 1.0


def main():
    frame_s = 1.0 / float(config.SERVO_PWM_FREQ)
    min_pw_s = (config.SERVO_MIN_DC / 100.0) * frame_s
    max_pw_s = (config.SERVO_MAX_DC / 100.0) * frame_s

    print(
        f"[test_servo] Using BCM pin {PIN}, frame={frame_s*1000:.2f}ms,"
        f" min={min_pw_s*1e6:.0f}us, max={max_pw_s*1e6:.0f}us"
    )

    servo = Servo(
        PIN,
        min_pulse_width=min_pw_s,
        max_pulse_width=max_pw_s,
        frame_width=frame_s,
    )

    try:
        target_deg = 0.0
        servo.value = deg_to_value(target_deg)
        print(f"[test_servo] Set servo to {target_deg:.1f}° (value={servo.value:.3f})")
        time.sleep(3.0)  # hold for observation
    finally:
        servo.close()
        print("[test_servo] Closed servo and exit.")


if __name__ == "__main__":
    main()

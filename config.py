# Global configuration for Raspberry Pi 5 turret project
# Adjust pin assignments to match your wiring.

from dataclasses import dataclass

# GPIO numbering mode: use BCM numbering
GPIO_MODE_BCM = True

# ===== Stepper (Yaw) =====
STEPPER_DIR_PIN = 20
STEPPER_STEP_PIN = 21
STEPPER_EN_PIN = 16  # optional, set to None if not used

# Mechanical parameters
STEPS_PER_REV = 200  # 1.8°/step motor
MICROSTEPPING = 8  # e.g. A4988/DRV8825 microstep setting
GEAR_RATIO = 1.0  # external gear ratio if any

# Motion limits and dynamics
YAW_MIN_DEG = -90.0
YAW_MAX_DEG = 90.0
YAW_MAX_SPEED_DPS = 180.0  # degrees per second

# ===== Tilt Servo (Pitch) =====
TILT_SERVO_PIN = 12
SERVO_PWM_FREQ = 50  # Hz

# Servo calibration (duty cycle at 50Hz). Typical: 0.5ms-2.5ms -> 2.5-12.5% duty
SERVO_MIN_DC = 5.6  # Futaba S3003 ≈1.12ms (1520±400us) at 50Hz
SERVO_MAX_DC = 9.6  # Futaba S3003 ≈1.92ms (1520±400us) at 50Hz
PITCH_MIN_DEG = -10.0
PITCH_MAX_DEG = 35.0
# ===== Reload Servo (Feeder) =====
RELOAD_SERVO_PIN = 13
RELOAD_IDLE_ANGLE = 0.0
RELOAD_LOAD_ANGLE = 60.0
RELOAD_HOLD_SEC = 0.25

# ===== Flywheel Motors (L298N) =====
# Motor A (left)
MOTOR_A_IN1 = 5
MOTOR_A_IN2 = 6
MOTOR_A_EN = 26  # PWM capable preferred

# Motor B (right)
MOTOR_B_IN3 = 19
MOTOR_B_IN4 = 13
MOTOR_B_EN = 18  # PWM capable preferred


# ===== Loop timing =====
MAIN_LOOP_HZ = 100.0  # 10ms tick

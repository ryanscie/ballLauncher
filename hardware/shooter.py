import time
from enum import Enum, auto

from subsystem_base import SubsystemBase
from gpiozero import AngularServo, Motor
import config


class ShooterState(Enum):
    IDLE = auto()
    SPINNING_UP = auto()
    PUSHING = auto()
    AT_POSITION = auto()
    RETRACTING = auto()


class Shooter(SubsystemBase):
    """
    Combined shooter system with flywheel motors and reload servo.

    A complete shoot cycle:
    1. Flywheels spin up to target speed
    2. Pusher moves forward to feed position
    3. Pusher holds at position briefly
    4. Pusher retracts to idle position
    5. Flywheels can be stopped or kept spinning

    Public:
      - shoot(speed): trigger a shoot cycle with flywheel speed
      - set_flywheel_power(p): directly control flywheel power
      - state: current shooter state
    """

    def __init__(self):
        super().__init__()
        self._hold_sec = config.RELOAD_HOLD_SEC
        self._move_to_load_est = 0.6
        self._move_to_idle_est = 0.6
        self._spinup_time = 1.0  # Time to spin up flywheels

    # ----- Public API -----
    def shoot(self, speed: float) -> bool:
        """Trigger a complete shoot cycle with given flywheel speed (0.0-1.0)"""
        if self.state == ShooterState.IDLE:
            self.target_flywheel_power = max(0.0, min(1.0, speed))
            self._to_state(ShooterState.SPINNING_UP)
            return True
        return False

    def set_flywheel_power(self, p: float):
        """Directly control flywheel power for manual operation"""
        self.target_flywheel_power = max(0.0, min(1.0, float(p)))

    # ----- Internals -----
    def _apply_flywheel_outputs(self):
        duty = max(0.0, min(1.0, self.target_flywheel_power))
        self._motor_a.value = duty
        self._motor_b.value = duty

    def _to_state(self, st: ShooterState):
        self.state = st
        self._state_ts = time.monotonic()
        match st:
            case ShooterState.IDLE:
                self._pusher.angle = config.RELOAD_IDLE_ANGLE
            case ShooterState.SPINNING_UP:
                # Keep pusher at idle, start flywheels
                self._pusher.angle = config.RELOAD_IDLE_ANGLE
                self._apply_flywheel_outputs()
            case ShooterState.PUSHING:
                self._pusher.angle = config.RELOAD_LOAD_ANGLE
            case ShooterState.AT_POSITION:
                # Hold at load position
                pass
            case ShooterState.RETRACTING:
                self._pusher.angle = config.RELOAD_IDLE_ANGLE
            case _:
                pass

    # ----- SubsystemBase -----
    def initialize(self):
        # Initialize flywheel motors
        self._motor_a = Motor(
            forward=config.MOTOR_A_IN1,
            backward=config.MOTOR_A_IN2,
            enable=config.MOTOR_A_EN,
            pwm=True,
        )
        self._motor_b = Motor(
            forward=config.MOTOR_B_IN3,
            backward=config.MOTOR_B_IN4,
            enable=config.MOTOR_B_EN,
            pwm=True,
        )

        # Initialize pusher servo
        self._pusher = AngularServo(
            config.RELOAD_SERVO_PIN,
            min_angle=min(config.RELOAD_IDLE_ANGLE, config.RELOAD_LOAD_ANGLE),
            max_angle=max(config.RELOAD_IDLE_ANGLE, config.RELOAD_LOAD_ANGLE),
            min_pulse_width=(config.SERVO_MIN_DC / 100.0) / config.SERVO_PWM_FREQ,
            max_pulse_width=(config.SERVO_MAX_DC / 100.0) / config.SERVO_PWM_FREQ,
            frame_width=1.0 / config.SERVO_PWM_FREQ,
            initial_angle=config.RELOAD_IDLE_ANGLE,
        )

        # Initialize state
        self.target_flywheel_power = 0.0
        self._to_state(ShooterState.IDLE)

    def periodic(self):
        # Always update flywheel outputs
        self._apply_flywheel_outputs()

        # Handle state machine
        now = time.monotonic()
        elapsed = now - self._state_ts

        match self.state:
            case ShooterState.SPINNING_UP:
                if elapsed >= self._spinup_time:
                    self._to_state(ShooterState.PUSHING)
            case ShooterState.PUSHING:
                if elapsed >= self._move_to_load_est:
                    self._to_state(ShooterState.AT_POSITION)
            case ShooterState.AT_POSITION:
                if elapsed >= self._hold_sec:
                    self._to_state(ShooterState.RETRACTING)
            case ShooterState.RETRACTING:
                if elapsed >= self._move_to_idle_est:
                    self._to_state(ShooterState.IDLE)
            case ShooterState.IDLE:
                pass
            case _:
                pass

    def shutdown(self):
        try:
            self.target_flywheel_power = 0.0
            self._apply_flywheel_outputs()
        finally:
            self._motor_a.close()
            self._motor_b.close()
            self._pusher.close()

from subsystem_base import SubsystemBase
from gpiozero import AngularServo
import config


class TiltServo(SubsystemBase):
    """
    Pitch (tilt) servo subsystem using gpiozero.Servo.

    Attributes:
        current_angle (deg): Estimated current pitch.
        target_angle (deg): Desired pitch setpoint.
    """

    def __init__(self):
        super().__init__()

    # ----- Public API -----
    def set_target_angle(self, deg: float):
        self.target_angle = max(config.PITCH_MIN_DEG, min(config.PITCH_MAX_DEG, deg))

    # ----- SubsystemBase -----
    def initialize(self):
        self._servo = AngularServo(
            config.TILT_SERVO_PIN,
            min_angle=config.PITCH_MIN_DEG,
            max_angle=config.PITCH_MAX_DEG,
            min_pulse_width=(config.SERVO_MIN_DC / 100.0) / config.SERVO_PWM_FREQ,
            max_pulse_width=(config.SERVO_MAX_DC / 100.0) / config.SERVO_PWM_FREQ,
            frame_width=1.0 / config.SERVO_PWM_FREQ,
            initial_angle=0.0,
        )
        self.current_angle = 0.0
        self.target_angle = 0.0

    def periodic(self):
        self._servo.angle = self.target_angle
        self.current_angle = self.target_angle

    def shutdown(self):
        self._servo.close()

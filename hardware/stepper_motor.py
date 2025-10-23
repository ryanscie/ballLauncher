from time import perf_counter as now
from subsystem_base import SubsystemBase
from gpiozero import DigitalOutputDevice
import config


class StepperYaw(SubsystemBase):
    """
    Stepper-based yaw subsystem using gpiozero OutputDevice pins.

    Attributes:
        current_angle (deg): Estimated current yaw.
        target_angle (deg): Desired yaw setpoint.
    """

    def __init__(self):
        super().__init__()
        self._en_active_low = True
        self._steps_per_rev = (
            config.STEPS_PER_REV * config.MICROSTEPPING * config.GEAR_RATIO
        )
        self._steps_per_deg = self._steps_per_rev / 360.0
        self._min_deg = config.YAW_MIN_DEG
        self._max_deg = config.YAW_MAX_DEG
        self._max_speed_dps = config.YAW_MAX_SPEED_DPS
        self._pulse_high_s = 0.0002
        self._pulse_low_s = 0.0002

    # ----- Public API -----
    def set_target_angle(self, deg: float):
        self.target_angle = max(self._min_deg, min(self._max_deg, deg))

    def _set_en_pin(self, enabled: bool):
        if self._en_active_low:
            self._en.off() if enabled else self._en.on()
        else:
            self._en.on() if enabled else self._en.off()

    # ----- SubsystemBase -----
    def initialize(self):
        self._dir = DigitalOutputDevice(
            config.STEPPER_DIR_PIN, active_high=True, initial_value=False
        )
        self._step = DigitalOutputDevice(
            config.STEPPER_STEP_PIN, active_high=True, initial_value=False
        )
        self._en = DigitalOutputDevice(
            config.STEPPER_EN_PIN, active_high=True, initial_value=True
        )
        self._set_en_pin(True)
        self.current_angle = max(self._min_deg, min(self._max_deg, 0.0))
        self.target_angle = self.current_angle
        self._step_residual = 0.0
        self._pending_steps = 0

    def periodic(self):
        dt = self._dt()
        error = self.target_angle - self.current_angle

        if abs(error) < 1e-4:
            self._set_en_pin(False)
            return

        self._set_en_pin(True)
        max_step_rate = self._max_speed_dps * self._steps_per_deg
        step_budget = max_step_rate * dt
        error_steps = abs(error) * self._steps_per_deg
        desired_steps = min(step_budget, error_steps) + self._step_residual
        steps_to_issue = int(desired_steps)
        self._step_residual = desired_steps - steps_to_issue

        if steps_to_issue <= 0:
            return

        direction_positive = error > 0.0
        if direction_positive:
            self._dir.on()
        else:
            self._dir.off()

        if steps_to_issue > 0 and self._pending_steps == 0:
            self._pending_steps = steps_to_issue
            pulse_period = self._pulse_high_s + self._pulse_low_s
            self._step.blink(
                on_time=self._pulse_high_s,
                off_time=self._pulse_low_s,
                n=steps_to_issue,
                background=True,
            )

        if not self._step.is_active and self._pending_steps > 0:
            delta_deg = (self._pending_steps / self._steps_per_deg) * (
                1.0 if direction_positive else -1.0
            )
            self.current_angle += delta_deg
            self.current_angle = max(
                self._min_deg, min(self._max_deg, self.current_angle)
            )
            self._pending_steps = 0

    def shutdown(self):
        try:
            self._set_en_pin(False)
        finally:
            self._dir.close()
            self._step.close()
            self._en.close()

import config
from control.subsystem_base import SubsystemBase
class StepperMotor(SubsystemBase):
    def __init__(self):
        super().__init__(); self._target_deg=0.0; self._cur_deg=0.0
    def initialize(self): self._initialized=True
    def shutdown(self): pass
    def set_target_angle(self, deg: float):
        deg=max(config.YAW_MIN_DEG,min(config.YAW_MAX_DEG,float(deg))); self._target_deg=deg
    def get_angle(self)->float: return float(self._cur_deg)
    def periodic(self):
        if not self._initialized: return
        dt=self._dt(); err=self._target_deg-self._cur_deg; m=config.YAW_MAX_SPEED_DPS*dt
        self._cur_deg += min(err,m) if err>0 else max(err,-m)

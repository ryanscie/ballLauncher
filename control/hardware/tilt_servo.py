import config
from control.subsystem_base import SubsystemBase
class TiltServo(SubsystemBase):
    def __init__(self):
        super().__init__(); self._target=0.0; self._cur=0.0; self._rate=60.0
    def initialize(self): self._initialized=True
    def shutdown(self): pass
    def set_target_angle(self, deg: float):
        deg=max(config.PITCH_MIN_DEG,min(config.PITCH_MAX_DEG,float(deg))); self._target=deg
    def get_angle(self)->float: return float(self._cur)
    def periodic(self):
        if not self._initialized: return
        dt=self._dt(); err=self._target-self._cur; m=self._rate*dt
        self._cur += min(err,m) if err>0 else max(err,-m)

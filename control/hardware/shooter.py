import config
from control.subsystem_base import SubsystemBase
class Shooter(SubsystemBase):
    IDLE=0; SPINNING=1; PUSHING=2; HOLDING=3; RETRACT=4
    def __init__(self):
        super().__init__(); self._power=0.0; self._state=Shooter.IDLE; self._timer=0.0
    @property
    def state(self): return self._state
    def initialize(self): self._initialized=True
    def shutdown(self): self._power=0.0; self._state=Shooter.IDLE
    def set_flywheel_power(self, p: float): self._power=max(0.0,min(1.0,float(p)))
    def shoot(self, p: float):
        p=max(0.0,min(1.0,float(p))); self._power=p
        if self._state in (Shooter.IDLE, Shooter.RETRACT): self._state=Shooter.SPINNING; self._timer=0.0
    def periodic(self):
        if not self._initialized: return
        dt=self._dt()
        if self._state==Shooter.SPINNING:
            self._timer+=dt
            if self._timer>=0.35: self._state=Shooter.PUSHING; self._timer=0.0
        elif self._state==Shooter.PUSHING:
            self._timer+=dt
            if self._timer>=config.RELOAD_HOLD_SEC: self._state=Shooter.RETRACT; self._timer=0.0
        elif self._state==Shooter.RETRACT:
            self._timer+=dt
            if self._timer>=0.15: self._state=Shooter.IDLE

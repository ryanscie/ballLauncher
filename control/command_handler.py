import json, time
import config
def _ts(): return time.strftime('%H:%M:%S')
class CommandHandler:
    def __init__(self, stepper_motor, tilt_servo, shooter):
        self.stepper=stepper_motor; self.tilt=tilt_servo; self.shooter=shooter
    def handle_command(self, command: str):
        command=command.strip()
        try:
            if command.startswith('{'):
                obj=json.loads(command); cmd=(obj.get('cmd','') or '').lower(); val=obj.get('value', None)
                print(f"[{_ts()}] [CMD] raw={obj}")
                resp=self._dispatch(cmd, val); print(f"[{_ts()}] [CMD] resp={resp}"); return resp
            parts=command.split(); 
            if not parts: return "ERR: empty"
            cmd=parts[0].lower(); val=float(parts[1]) if len(parts)>1 else None
            print(f"[{_ts()}] [CMD] raw={{'cmd': '{cmd}', 'value': {val}}}")
            resp=self._dispatch(cmd, val); print(f"[{_ts()}] [CMD] resp={resp}"); return resp
        except Exception as e:
            err=f"ERR: {e}"; print(f"[{_ts()}] [CMD] error={err}"); return err
    def _dispatch(self, cmd, val):
        if cmd=='yaw':
            if val is None: return 'ERR: yaw needs value'
            v=max(config.YAW_MIN_DEG,min(config.YAW_MAX_DEG,float(val))); self.stepper.set_target_angle(v); return f'OK: yaw={v:.2f}'
        if cmd=='tilt':
            if val is None: return 'ERR: tilt needs value'
            v=max(config.PITCH_MIN_DEG,min(config.PITCH_MAX_DEG,float(val))); self.tilt.set_target_angle(v); return f'OK: tilt={v:.2f}'
        if cmd=='shoot':
            if val is None: return 'ERR: shoot needs power 0..1'
            p=max(0.0,min(1.0,float(val))); self.shooter.shoot(p); return f'OK: shoot power={p:.2f}'
        if cmd=='flywheel':
            if val is None: return 'ERR: flywheel needs power 0..1'
            p=max(0.0,min(1.0,float(val))); self.shooter.set_flywheel_power(p); return f'OK: flywheel power={p:.2f}'
        if cmd=='reload':
            p=max(0.2, getattr(self.shooter, '_power', 0.0)); self.shooter.shoot(p); return 'OK: reload'
        if cmd=='status':
            payload={'ok': True,'yaw': self.stepper.get_angle(),'tilt': self.tilt.get_angle(),'flywheel': getattr(self.shooter, '_power', 0.0),'state': self.shooter.state}
            print(f"[{_ts()}] [CMD] status={payload}")
            return json.dumps(payload)
        return f"ERR: unknown cmd '{cmd}'"

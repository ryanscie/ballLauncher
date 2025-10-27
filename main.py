import threading, time, uvicorn, config
from control.hardware.stepper_motor import StepperMotor
from control.hardware.tilt_servo import TiltServo
from control.hardware.shooter import Shooter
from control.command_handler import CommandHandler
from web.app import app
def control_loop(stepper, tilt, shooter, stop_event):
    stepper.initialize(); tilt.initialize(); shooter.initialize()
    print('Control loop started (SIM, PC webcam).')
    try:
        while not stop_event.is_set():
            stepper.periodic(); tilt.periodic(); shooter.periodic(); time.sleep(1.0/config.MAIN_LOOP_HZ)
    finally:
        print('Shutting down subsystems...'); stepper.shutdown(); tilt.shutdown(); shooter.shutdown(); print('All subsystems shut down.')
if __name__=='__main__':
    stepper=StepperMotor(); tilt=TiltServo(); shooter=Shooter(); handler=CommandHandler(stepper, tilt, shooter)
    from web import app as webapp; webapp.handler=handler
    stop_event=threading.Event(); th=threading.Thread(target=control_loop, args=(stepper,tilt,shooter,stop_event), daemon=True); th.start()
    try: uvicorn.run('web.app:app', host='0.0.0.0', port=8000, reload=False)
    except KeyboardInterrupt: pass
    finally: stop_event.set(); th.join()

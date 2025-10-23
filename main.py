import os
from hardware.stepper_motor import StepperMotor
from hardware.tilt_servo import TiltServo
from hardware.shooter import Shooter


def main():
    stepper = StepperMotor()
    tilt_servo = TiltServo()
    shooter = Shooter()

    try:
        print("Initializing subsystems...")
        stepper.initialize()
        tilt_servo.initialize()
        shooter.initialize()

        print("Running subsystems... (press Ctrl+C to exit)")
        while True:
            stepper.periodic()
            tilt_servo.periodic()
            shooter.periodic()

    except KeyboardInterrupt:
        print("\nShutting down subsystems...")
    finally:
        stepper.shutdown()
        tilt_servo.shutdown()
        shooter.shutdown()
        print("All subsystems shut down.")


if __name__ == "__main__":
    main()

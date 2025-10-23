#!/usr/bin/env python3
"""
Interactive test for Shooter subsystem (Flywheel + Reload Servo).

- Runs the shooter subsystem periodic loop in a background thread (~100 Hz)
- Accepts user input to control shooting and individual components

Commands:
  shoot <speed>    : trigger complete shoot cycle with flywheel speed (0..1)
  power <0..1>     : set flywheel power (normalized 0..1)
  push             : manually move pusher to load position
  retract          : manually move pusher to idle position
  status           : print current state and flywheel power
  help             : print this help
  quit/exit/q      : stop and cleanup

Run:
  python test/test_shooter.py
"""

import sys
import time
import threading

from hardware.shooter import Shooter, ShooterState


def periodic_thread(subsys: Shooter, stop_evt: threading.Event, hz: float = 100.0):
    tick = 1.0 / max(1e-3, hz)
    next_ts = time.monotonic()
    while not stop_evt.is_set():
        try:
            subsys.periodic()
        except Exception as e:
            print(f"[periodic] error: {e}", file=sys.stderr)
        next_ts += tick
        sleep_left = next_ts - time.monotonic()
        if sleep_left > 0:
            time.sleep(sleep_left)
        else:
            next_ts = time.monotonic()


def print_help():
    print(__doc__)


def main():
    shooter = Shooter()
    stop_evt = threading.Event()

    try:
        print("[init] Initializing Shooter...")
        shooter.initialize()
        thr = threading.Thread(
            target=periodic_thread, args=(shooter, stop_evt, 100.0), daemon=True
        )
        thr.start()
        print_help()

        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue

            toks = line.split()
            cmd = toks[0].lower()

            if cmd in ("quit", "exit", "q"):
                break
            elif cmd == "help":
                print_help()
            elif cmd == "shoot":
                if len(toks) < 2:
                    print("Usage: shoot <speed 0..1>")
                    continue
                try:
                    speed = float(toks[1])
                except ValueError:
                    print("Invalid speed number")
                    continue
                success = shooter.shoot(speed)
                if success:
                    print(f"[cmd] Started shoot cycle with speed {speed:.2f}")
                else:
                    print(f"[cmd] Cannot shoot - current state: {shooter.state.name}")
            elif cmd == "power":
                if len(toks) < 2:
                    print("Usage: power <0..1>")
                    continue
                try:
                    p = float(toks[1])
                except ValueError:
                    print("Invalid number")
                    continue
                shooter.set_flywheel_power(p)
                print(f"[cmd] flywheel power -> {shooter.target_flywheel_power:.2f}")
            elif cmd == "push":
                if shooter.state == ShooterState.IDLE:
                    shooter._to_state(ShooterState.PUSHING)
                    print("[cmd] Manually pushing to load position")
                else:
                    print(f"[cmd] Cannot push - current state: {shooter.state.name}")
            elif cmd == "retract":
                if shooter.state in [ShooterState.PUSHING, ShooterState.AT_POSITION]:
                    shooter._to_state(ShooterState.RETRACTING)
                    print("[cmd] Manually retracting to idle position")
                else:
                    print(f"[cmd] Cannot retract - current state: {shooter.state.name}")
            elif cmd == "status":
                print(
                    f"state={shooter.state.name}, flywheel_power={shooter.target_flywheel_power:.2f}"
                )
            else:
                print("Unknown command. Type 'help' for usage.")

    finally:
        print("[shutdown] Stopping...")
        stop_evt.set()
        time.sleep(0.05)
        try:
            shooter.shutdown()
        except Exception as e:
            print(f"[shutdown] Shooter error: {e}", file=sys.stderr)
        print("[done] Cleanup complete.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Interactive test for StepperYaw (hardware/stepper_motor.py).

- Runs the subsystem periodic loop in a background thread (~100 Hz)
- Accepts user input to set target angle, enable/disable driver, and query status

Commands:
  set <deg>        : set target yaw angle in degrees (clamped by config)
  angle <deg>      : same as set
  goto <deg>       : same as set
  enable on|off    : energize (on) / de-energize (off) stepper driver if EN pin is wired
  status           : print current/target angles
  help             : print this help
  quit/exit/q      : stop and cleanup

Run:
  python test/test_stepper.py
"""

import sys
import time
import threading

import config
from hardware.stepper_motor import StepperYaw


def periodic_thread(subsys: StepperYaw, stop_evt: threading.Event, hz: float = 100.0):
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
    yaw = StepperYaw()
    stop_evt = threading.Event()

    try:
        print("[init] Initializing StepperYaw...")
        yaw.initialize()
        thr = threading.Thread(
            target=periodic_thread, args=(yaw, stop_evt, 100.0), daemon=True
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
            elif cmd in ("set", "angle", "goto"):
                if len(toks) < 2:
                    print("Usage: set <deg>")
                    continue
                try:
                    deg = float(toks[1])
                except ValueError:
                    print("Invalid number")
                    continue
                yaw.set_target_angle(deg)
                print(f"[cmd] target_angle -> {yaw.target_angle:.2f} deg")
            elif cmd == "enable":
                if len(toks) < 2 or toks[1].lower() not in ("on", "off"):
                    print("Usage: enable on|off")
                    continue
                yaw.set_enabled(toks[1].lower() == "on")
                print(f"[cmd] enabled -> {toks[1].lower()}")
            elif cmd == "status":
                print(
                    f"current={yaw.current_angle:.2f} deg, target={yaw.target_angle:.2f} deg"
                )
            else:
                print("Unknown command. Type 'help' for usage.")

    finally:
        print("[shutdown] Stopping...")
        stop_evt.set()
        time.sleep(0.05)
        try:
            yaw.shutdown()
        except Exception as e:
            print(f"[shutdown] StepperYaw error: {e}", file=sys.stderr)
        print("[done] Cleanup complete.")


if __name__ == "__main__":
    main()

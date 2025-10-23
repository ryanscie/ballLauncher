#!/usr/bin/env python3
"""
Interactive test for TiltServo (hardware/tilt_servo.py, gpiozero-based).

- Runs the subsystem periodic loop in a background thread (~100 Hz)
- Accepts user input to set target pitch angle and enable/disable
- Uses Futaba S3003 calibration from config.py

Commands:
  set <deg>        : set target pitch angle in degrees (clamped by config)
  angle <deg>      : same as set
  goto <deg>       : same as set
  enable on|off    : enable/disable motion (holds last position when disabled)
  status           : print current/target angles
  help             : print this help
  quit/exit/q      : stop and cleanup

Run:
  python test/test_tilt_servo.py
"""

import sys
import time
import threading

from hardware.tilt_servo import TiltServo


def periodic_thread(subsys: TiltServo, stop_evt: threading.Event, hz: float = 100.0):
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
    tilt = TiltServo()
    stop_evt = threading.Event()

    try:
        print("[init] Initializing TiltServo...")
        tilt.initialize()
        thr = threading.Thread(
            target=periodic_thread, args=(tilt, stop_evt, 100.0), daemon=True
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
                tilt.set_target_angle(deg)
                print(f"[cmd] target_angle -> {tilt.target_angle:.2f} deg")
            elif cmd == "enable":
                if len(toks) < 2 or toks[1].lower() not in ("on", "off"):
                    print("Usage: enable on|off")
                    continue
                tilt.set_enabled(toks[1].lower() == "on")
                print(f"[cmd] enabled -> {toks[1].lower()}")
            elif cmd == "status":
                print(
                    f"current={tilt.current_angle:.2f} deg, target={tilt.target_angle:.2f} deg"
                )
            else:
                print("Unknown command. Type 'help' for usage.")

    finally:
        print("[shutdown] Stopping...")
        stop_evt.set()
        time.sleep(0.05)
        try:
            tilt.shutdown()
        except Exception as e:
            print(f"[shutdown] TiltServo error: {e}", file=sys.stderr)
        print("[done] Cleanup complete.")


if __name__ == "__main__":
    main()

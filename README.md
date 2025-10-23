# Raspberry Pi 5 UDP RC Turret

Modular subsystems:

- Stepper yaw (left/right)
- Tilt servo (up/down)
- Reload servo (feeder FSM)
- Dual DC flywheels via L298N
- UDP command receiver (JSON)
- UDP video streamer (JPEG fragments)

Each subsystem implements `SubsystemBase` and provides `initialize / periodic / shutdown`. The main loop ticks all subsystems at a fixed rate and applies targets from the command receiver.

## Wiring (BCM)

Update `config.py` if your wiring differs.

- Stepper (yaw): DIR=20, STEP=21, EN=16
- Tilt servo: PWM=12 (50Hz)
- Reload servo: PWM=13 (50Hz)
- L298N:
  - Motor A: IN1=5, IN2=6, ENA=26 (PWM)
  - Motor B: IN3=19, IN4=13, ENB=18 (PWM)
- Camera: OpenCV-compatible (V4L2 on Pi)
- Networking:
  - Commands: bind 0.0.0.0:5005
  - Video: send to VIDEO_UDP_TARGET_IP:5600

## Configure

Edit `config.py`:

- Set `VIDEO_UDP_TARGET_IP` to the ground-station IP.
- Check pins, limits, speeds, MTU, and loop rate.

## Dependencies

On ground station or dev host (for receiver/tools):

```bash
# Python 3.9+
pip install opencv-python numpy
```

On Raspberry Pi:

- GPIO/servos (gpiozero backend): sudo apt install python3-gpiozero
- OpenCV (optional for video): sudo apt install python3-opencv # or: pip install opencv-python

## Run on Raspberry Pi

```bash
python main.py
```

## Receive video on ground station

A minimal OpenCV receiver is provided (to be added in tools/recv_video.py):

```bash
python tools/recv_video.py --port 5600
```

## Send commands

A helper script is provided (to be added in tools/send_commands.py):

```bash
# Absolute targets
python tools/send_commands.py --host <pi-ip> --port 5005 --yaw 10 --pitch 5 --flywheel 0.8

# Trigger one reload cycle
python tools/send_commands.py --host <pi-ip> --port 5005 --reload
```

JSON protocol (UDP, one packet per message):

```json
{"yaw": 10.0, "pitch": 5.0, "flywheel": 0.8}
{"reload": true}
```

## Safety

- Verify mechanical end-stops and angle limits in `config.py`.
- Start with low flywheel power.
- Keep clear of muzzle and moving parts.

## Project structure

```text
.
├─ config.py
├─ main.py
├─ subsystem_base.py
├─ hardware/
│  ├─ stepper_motor.py
│  ├─ tilt_servo.py
│  ├─ reload_servo.py
│  └─ flywheel_motors.py
├─ rc/
│  ├─ command_receiver.py
│  └─ video_streamer.py
└─ tools/
   ├─ send_commands.py         # helper (to be added)
   └─ recv_video.py            # helper (to be added)
```

## Notes

- Video streamer sends JPEG frames fragmented into UDP chunks sized by `VIDEO_MTU`.
- Main loop rate is `MAIN_LOOP_HZ` (default 100Hz).

import socket
import argparse
import signal
import threading
from typing import Callable, Optional, Tuple


class CommandReceiver:
    def __init__(
        self,
        host: str,
        port: int,
        command_handler: Callable[[str], str],
    ):
        self._host = host
        self._port = port
        self._command_handler = command_handler
        self._server_socket: Optional[socket.socket] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self._host, self._port))
        self._server_socket.listen(1)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[CommandReceiver] Listening on {self._host}:{self._port}")

    def stop(self):
        self._stop_event.set()
        if self._server_socket:
            self._server_socket.close()
        if self._thread:
            self._thread.join()

    def _run(self):
        while not self._stop_event.is_set():
            try:
                client_socket, addr = self._server_socket.accept()
                print(f"[CommandReceiver] Connection from {addr}")
                with client_socket:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        command = data.decode().strip()
                        print(f"[CommandReceiver] Received command: {command}")
                        response = self._command_handler(command)
                        client_socket.sendall(response.encode() + b"\n")
            except OSError:
                break  # Socket closed, exit thread


class CommandHandler:
    def __init__(self, stepper_motor, tilt_servo, shooter):
        self.stepper_motor = stepper_motor
        self.tilt_servo = tilt_servo
        self.shooter = shooter

    def handle_command(self, command: str) -> str:
        pass

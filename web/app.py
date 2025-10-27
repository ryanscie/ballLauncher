\
import json, time, threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool

import cv2
import numpy as np

from control.command_handler import CommandHandler

def _ts(): return time.strftime('%H:%M:%S')

app = FastAPI()
app.mount('/static', StaticFiles(directory='web/static'), name='static')

handler = None  # injected in main.py

_cam = None
_cam_lock = threading.Lock()
_cam_index = 0   # change if your webcam isn't index 0
_cam_width = 640
_cam_height = 480
_cam_fps = 30

@app.on_event("startup")
def _start_camera():
    global _cam
    with _cam_lock:
        cap = cv2.VideoCapture(_cam_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, _cam_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _cam_height)
        cap.set(cv2.CAP_PROP_FPS, _cam_fps)
        if not cap.isOpened():
            print(f"[{_ts()}] [CAM] Failed to open webcam index={_cam_index}")
        else:
            print(f"[{_ts()}] [CAM] Webcam opened index={_cam_index} size={_cam_width}x{_cam_height} fps~{_cam_fps}")
        _cam = cap

@app.on_event("shutdown")
def _stop_camera():
    global _cam
    with _cam_lock:
        if _cam is not None:
            try:
                _cam.release()
                print(f"[{_ts()}] [CAM] Webcam released")
            except Exception:
                pass
            _cam = None

@app.get('/')
async def index():
    with open('web/static/index.html','r',encoding='utf-8') as f:
        return HTMLResponse(f.read())

@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    client=f"{ws.client.host}:{ws.client.port}" if ws.client else 'unknown'
    print(f"[{_ts()}] [WS] open from {client}")
    try:
        while True:
            msg = await ws.receive_text()
            print(f"[{_ts()}] [WS] recv {msg}")
            if handler is None:
                out=json.dumps({'ok':False,'error':'handler not ready'})
                await ws.send_text(out); print(f"[{_ts()}] [WS] sent {out}")
                continue
            resp = await run_in_threadpool(handler.handle_command, msg)
            try:
                if isinstance(resp,str) and resp.startswith('{'):
                    await ws.send_text(resp); print(f"[{_ts()}] [WS] sent JSON {resp}")
                else:
                    out=json.dumps({'ok':True,'msg':resp})
                    await ws.send_text(out); print(f"[{_ts()}] [WS] sent {out}")
            except Exception as e:
                err=json.dumps({'ok':False,'error':str(e)})
                await ws.send_text(err); print(f"[{_ts()}] [WS] sent ERROR {err}")
    except WebSocketDisconnect:
        print(f"[{_ts()}] [WS] closed {client}")
    except Exception as e:
        print(f"[{_ts()}] [WS] error {client}: {e}")

def mjpeg_generator():
    global _cam
    while True:
        with _cam_lock:
            cap = _cam
        if cap is None or not cap.isOpened():
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            ok, frame = cap.read()
            if not ok or frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ret, jpg = cv2.imencode('.jpg', frame)
        chunk = jpg.tobytes() if ret else b''
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + chunk + b'\r\n')
        time.sleep(0.001)

@app.get('/video')
async def video():
    return StreamingResponse(mjpeg_generator(),
                             media_type='multipart/x-mixed-replace; boundary=frame')

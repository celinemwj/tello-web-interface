import threading
import time

import cv2
from djitellopy import Tello


class TelloCameraStream:
    def __init__(self):
        self.tello = None
        self.frame_reader = None
        self.is_streaming = False
        self.last_error = None
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.is_streaming:
                return

            self.last_error = None

            try:
                self.tello = Tello()
                self.tello.connect()
                self.tello.streamon()

                time.sleep(2)

                self.frame_reader = self.tello.get_frame_read()
                self.is_streaming = True

            except Exception as error:
                self.last_error = str(error)
                self.is_streaming = False

                try:
                    if self.tello is not None:
                        self.tello.end()
                except Exception:
                    pass

                self.tello = None
                self.frame_reader = None

                raise error

    def stop(self):
        with self.lock:
            if self.tello is not None:
                try:
                    self.tello.streamoff()
                except Exception:
                    pass

                try:
                    self.tello.end()
                except Exception:
                    pass

            self.tello = None
            self.frame_reader = None
            self.is_streaming = False

    def status(self):
        return {
            "is_streaming": self.is_streaming,
            "last_error": self.last_error,
        }

    def generate_frames(self):
        self.start()

        while self.is_streaming:
            if self.frame_reader is None:
                time.sleep(0.05)
                continue

            frame = self.frame_reader.frame

            if frame is None:
                time.sleep(0.05)
                continue

            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                success, buffer = cv2.imencode(".jpg", frame)

                if not success:
                    continue

                frame_bytes = buffer.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )

            except Exception as error:
                self.last_error = str(error)
                time.sleep(0.1)


camera_stream = TelloCameraStream()
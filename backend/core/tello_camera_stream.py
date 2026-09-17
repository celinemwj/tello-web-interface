import threading
import time

import cv2
from djitellopy import Tello
from backend.utils.tello_manager import get_tello_manager


class TelloCameraStream:
    def __init__(self):
        self.manager = None
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
                # Use singleton manager to prevent port conflicts
                self.manager = get_tello_manager()
                
                if not self.manager.connect():
                    raise Exception("Failed to connect to Tello using singleton manager")
                
                self.tello = self.manager.get_tello()
                self.tello.streamon()

                time.sleep(2)

                self.frame_reader = self.tello.get_frame_read()
                self.is_streaming = True

            except Exception as error:
                self.last_error = str(error)
                self.is_streaming = False

                # Don't call end() here since we're using singleton
                self.manager = None
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

            # On ne deconnecte volontairement PAS le drone ici.
            # self.manager est le singleton TelloManager, partage avec
            # l'execution des commandes : appeler disconnect() ferait
            # tello.end() et couperait aussi le pilotage.
            # Arreter la video ne doit arreter que la video.
            self.manager = None
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
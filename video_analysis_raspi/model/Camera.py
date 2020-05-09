import logging
import time

from picamera import PiCamera


class Camera:
    piCamera: PiCamera
    resolution_width: int = 640
    resolution_height: int = 480
    framerate: int = 60
    iso = 0
    shutter_speed = 0
    exposure_speed: int = 0
    mutex: bool = True

    def __init__(self):
        self.piCamera = PiCamera()
        time.sleep(0.5)
        self.piCamera.framerate = self.framerate
        self.piCamera.resolution = (self.resolution_width, self.resolution_height)
        time.sleep(0.5)
        logging.info("Camera started and ready.")
        self.mutex = False

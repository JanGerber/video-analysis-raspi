import time

from picamera import PiCamera


class Camera:
    camera: PiCamera
    resolution_width: int = 640
    resolution_height: int = 480
    framerate: int = 60
    iso = 0
    shutter_speed = 0
    exposure_speed: int = 0

    def __init__(self):
        self.camera = PiCamera()
        self.camera.framerate(self.framerate)
        self.camera.resolution(self.resolution_width, self.resolution_height)
        time.sleep(2)

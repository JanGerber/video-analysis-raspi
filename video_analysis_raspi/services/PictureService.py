import logging
import os
import sched
import shutil
import time

from video_analysis_raspi.model.Camera import Camera
from video_analysis_raspi.model.PictureStartRequest import PictureStartRequest
from video_analysis_raspi.services.SettingsService import SettingsService


class PictureService:
    scheduler: sched
    camera: Camera

    def __init__(self, camera: Camera, settings: SettingsService):
        self.camera = camera
        self.settings = settings
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def take_pictures(self, request: PictureStartRequest):
        if self.camera.mutex:
            return "Camera already busy"
        self.camera.mutex = True
        request.start_time += 1
        os.mkdir(request.groupId)
        for x in range(request.num_images):
            self.scheduler.enterabs(request.start_time + (request.interval * x),
                                    1 + x,
                                    self.picture,
                                    argument=(request, x,))
        self.scheduler.run()
        # TODO upload pictures
        shutil.rmtree(os.getcwd() + "/" + request.groupId)
        return "All pictures taken"

    def picture(self, request: PictureStartRequest, number: int):
        self.camera.piCamera.capture("{}/picture_{}.jpeg".format(request.groupId, number), format='jpeg',
                                     use_video_port=False, resize=None, splitter_port=1, bayer=False)
        logging.debug("Picture number {} taken at: {}".format(number, time.time()))

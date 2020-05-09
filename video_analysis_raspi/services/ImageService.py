import json
import logging
import os
import sched
import shutil
import time

import requests
from requests_toolbelt import MultipartEncoder

from video_analysis_raspi.exceptions.ImageTakingError import ImageTakingError
from video_analysis_raspi.model.Camera import Camera
from video_analysis_raspi.model.ImageStartRequest import ImageStartRequest
from video_analysis_raspi.services.SettingsService import SettingsService


class ImageService:
    scheduler: sched
    camera: Camera
    settings_service: SettingsService

    def __init__(self, camera: Camera, settings: SettingsService):
        self.camera = camera
        self.settings_service = settings
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def take_pictures(self, request: ImageStartRequest):
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
        for x in range(request.num_images):
            self.upload_file(request, x)
        shutil.rmtree(os.getcwd() + "/" + request.groupId)
        return "All pictures taken"

    def picture(self, request: ImageStartRequest, number: int):
        self.camera.piCamera.capture("{}/{}{}.{}".format(request.groupId,
                                                         self.settings_service.settings.image_name_pre,
                                                         number,
                                                         self.settings_service.settings.image_format),
                                     format=self.settings_service.settings.image_format,
                                     splitter_port=1)
        logging.debug("Picture number {} taken at: {}".format(number, time.time()))

    def upload_file(self, request: ImageStartRequest, number: int):
        metadata = {
            'idRaspi': self.settings_service.settings.raspi_uuid,
            'groupId': request.groupId,
            'number': number,
            'time': request.start_time + request.interval * number,
            'imageFormat': self.settings_service.settings.image_format
        }
        m = MultipartEncoder(
            fields={'file':
                        ("{}{}.{}".format(self.settings_service.settings.image_name_pre,
                                          number,
                                          self.settings_service.settings.image_format),
                         open("{}/{}{}.{}".format(request.groupId,
                                                  self.settings_service.settings.image_name_pre,
                                                  number,
                                                  self.settings_service.settings.image_format), 'rb'),
                         'image/{}'.format(self.settings_service.settings.image_format)),
                    'metadata': ('metadata', json.dumps(metadata), 'application/json')}
        )

        url = self.settings_service.settings.server_url_base + self.settings_service.settings.server_url_image_file_upload
        headers = self.settings_service.settings.server_auth_header
        headers.update({'Content-Type': m.content_type})
        r = requests.post(url,
                          data=m,
                          headers=headers)
        if r.status_code != 200:
            raise ImageTakingError(msg="Something went wrong during upload")

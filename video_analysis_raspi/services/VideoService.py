import json
import logging
import sched
import time
from io import BytesIO

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from video_analysis_raspi.exceptions.VideoRecordingError import VideoRecordingError
from video_analysis_raspi.model import Camera
from video_analysis_raspi.model.VideoStartRequest import VideoStartRequest
from video_analysis_raspi.services.SettingsService import SettingsService


class VideoService:
    camera: Camera
    stream_output: BytesIO = BytesIO()
    settings_service: SettingsService
    request: VideoStartRequest
    scheduler: sched

    def __init__(self, camera, settings_service: SettingsService):
        self.camera = camera
        self.settings_service = settings_service
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.camera.piCamera.start_recording(self.stream_output,
                                             format='mjpeg',
                                             splitter_port=2)

    def start_recording(self, request: VideoStartRequest):
        if self.camera.mutex:
            return "Video already stared"
        self.camera.mutex = True
        logging.info("Schedule started:     {}".format(time.time_ns()))
        new_start_time = request.start_time + 1
        logging.info("Recording start Time: {}".format(new_start_time))
        self.scheduler.enterabs(new_start_time, 1, self.recording, argument=(request,))
        self.scheduler.run()
        return "Video recording started"

    def recording(self, request: VideoStartRequest):
        self.camera.piCamera.start_recording(self.settings_service.settings.video_filename,
                                             format=self.settings_service.settings.video_format,
                                             splitter_port=1)
        logging.info("Recording started:    {}".format(time.time_ns()))
        if request.duration != 0:
            self.camera.piCamera.wait_recording(request.duration)
            self.camera.piCamera.stop_recording(splitter_port=1)
            if request.store:
                self.upload_file(request)
            self.camera.mutex = False
        else:
            self.request = request

    def upload_file(self, request):
        metadata = {
            'groupId': request.groupId,
            'duration': request.duration,
            'startTime': request.start_time,
            'videoFormat': self.settings_service.settings.video_format
        }
        m = MultipartEncoder(
            fields={'file':
                        (self.settings_service.settings.video_filename,
                         open(self.settings_service.settings.video_filename, 'rb'),
                         'video/h264'),
                    'metadata': ('metadata', json.dumps(metadata), 'application/json')}
        )

        url = self.settings_service.settings.server_url_base + self.settings_service.settings.server_url_file_upload
        headers = self.settings_service.settings.server_auth_header
        headers.update({'Content-Type': m.content_type})
        r = requests.post(url,
                          data=m,
                          headers=headers)
        if r.status_code != 200:
            raise VideoRecordingError(msg="Something went wrong during upload")

    def stop_recording(self):
        if not self.camera.mutex:
            return "Currently no recording"
        self.camera.piCamera.stop_recording(splitter_port=1)
        if self.request.store:
            self.upload_file(self.request)
        self.camera.mutex = False
        return "Video stopped!"

    def gen(self):
        """Video streaming generator function."""
        while True:
            if self.stream_output is not None and self.stream_output.closed:
                break
            if self.stream_output is not None:
                self.stream_output.seek(0)
                frame = self.stream_output.read()
                if frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                self.stream_output.seek(0)
                self.stream_output.truncate()

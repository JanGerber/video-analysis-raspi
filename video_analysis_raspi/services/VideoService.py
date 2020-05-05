import json
from io import BytesIO

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from video_analysis_raspi.exceptions.VideoRecordingError import VideoRecordingError
from video_analysis_raspi.model import Camera
from video_analysis_raspi.model.VideoStartRequest import VideoStartRequest
from video_analysis_raspi.services.SettingsService import SettingsService


class VideoService:
    mutex: bool = False
    camera: Camera
    stream_output: BytesIO = BytesIO()
    settings_service: SettingsService
    request: VideoStartRequest

    def __init__(self, camera, settings_service: SettingsService):
        self.camera = camera
        self.settings_service = settings_service
        self.camera.start_recording(self.stream_output,
                                    format='mjpeg',
                                    splitter_port=2)

    def start_recording(self, request: VideoStartRequest):
        if self.mutex:
            return "Video already stared"
        self.mutex = True
        self.camera.start_recording(self.settings_service.settings.video_filename,
                                    format=self.settings_service.settings.video_format,
                                    splitter_port=1)
        if request.duration != 0:
            self.camera.wait_recording(request.duration)
            self.camera.stop_recording(splitter_port=1)
            if request.store:
                self.upload_file(request)
            self.mutex = False
            return "Video started and stoped"
        else:
            self.request = request
        return "Video started!"

    def upload_file(self, request):
        print("start upload")
        metadata = {
            'groupId': request.groupId,
            'duration': request.duration,
            'startTime': request.start_time
        }
        m = MultipartEncoder(
            fields={'file': ('video.h264', open(self.settings_service.settings.video_filename, 'rb'), 'video/h264'),
                    'metadata': ('metadata', json.dumps(metadata), 'application/json')}
        )

        url = self.settings_service.settings.server_url_base + self.settings_service.settings.server_url_file_upload
        headers = self.settings_service.settings.server_auth_header
        headers.update({'Content-Type': m.content_type})
        print("Headers", headers)
        r = requests.post(url,
                          data=m,
                          headers=headers)
        print(r.request.headers)
        print(r.status_code, r.text)
        if r.status_code != 200:
            raise VideoRecordingError(msg="Something went wrong during upload")

    def stop_recording(self):
        if not self.mutex:
            return "Currently no recording"
        self.camera.camera.stop_recording()
        if self.store_file:
            self.upload_file()
        self.mutex = False
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

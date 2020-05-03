from io import BytesIO

from video_analysis_raspi.model import Camera
from video_analysis_raspi.model.VideoStartRequest import VideoStartRequest
from video_analysis_raspi.services.SettingsService import SettingsService


class VideoService:
    mutex: bool = False
    camera: Camera
    stream_output: BytesIO = BytesIO()
    settings_service: SettingsService
    store_file: bool = True

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
        self.store_file = request.store
        self.camera.start_recording(self.settings_service.settings.video_filename,
                                    format=self.settings_service.settings.video_format,
                                    splitter_port=1)
        if request.duration != 0:
            self.camera.wait_recording(request.duration)
            self.camera.stop_recording(splitter_port=1)
            if request.store:
                self.upload_file()
            self.mutex = False
            return "Video started and stoped"

        return "Video started!"

    def upload_file(self):
        pass

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

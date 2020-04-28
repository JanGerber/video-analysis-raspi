from flask import Flask
from picamera import PiCamera

from video_analysis_raspi.services.PictureService import PictureService
from video_analysis_raspi.services.SettingsService import SettingsService
from video_analysis_raspi.services.VideoService import VideoService

app = Flask(__name__)

camera = PiCamera()
settings_service = SettingsService()

video_service = VideoService(camera, settings_service)
picture_service = PictureService(camera, settings_service)


@app.route('/api/v1/video/start', methods=['POST'])
def post_start_video():
    video_service.start_recording()
    return 'Video started'


@app.route('/api/v1/video/stop', methods=['POST'])
def post_stop_video():
    video_service.stop_recording()
    return 'Video stopped'


@app.route('/api/v1/picture', methods=['POST'])
def post_picture_start():
    picture_service.take_pictures()
    return 'Hello World!'


@app.route('/api/v1/setting', methods=['GET'])
def get_settings():
    return settings_service.get_settings()


@app.route('/api/v1/setting/<string:setting_name>', methods=['GET'])
def get_setting_item(setting_name):
    return settings_service.get_setting(setting_name)


@app.route('/api/v1/setting/<string:setting_name>', methods=['PUT'])
def put_setting_item(setting_name):
    return settings_service.change_setting(setting_name)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8090)

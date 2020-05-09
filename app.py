import logging
import sys

from flask import Flask, request, render_template, Response

from video_analysis_raspi.exceptions.VideoRecordingError import VideoRecordingError
from video_analysis_raspi.model.Camera import Camera
from video_analysis_raspi.model.PictureStartRequest import PictureStartRequest
from video_analysis_raspi.model.VideoStartRequest import VideoStartRequest
from video_analysis_raspi.services.PictureService import PictureService
from video_analysis_raspi.services.SettingsService import SettingsService
from video_analysis_raspi.services.VideoService import VideoService

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)

camera = Camera()
settings_service = SettingsService(sys.argv[1:])

video_service = VideoService(camera, settings_service)
picture_service = PictureService(camera, settings_service)



@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(video_service.gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/v1/video/start', methods=['POST'])
def post_start_video():
    data = VideoStartRequest(request.data)
    try:
        result = video_service.start_recording(data)
        return result, 202
    except VideoRecordingError as e:
        return repr(e), 500


@app.route('/api/v1/video/stop', methods=['POST'])
def post_stop_video():
    video_service.stop_recording()
    return 'Video stopped'


@app.route('/api/v1/picture', methods=['POST'])
def post_picture_start():
    data = PictureStartRequest(request.data)
    try:
        result = picture_service.take_pictures(data)
        return result, 202
    except VideoRecordingError as e:
        return repr(e), 500


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

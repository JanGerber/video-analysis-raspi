class Settings:
    camera_led: bool = True
    camera_width: int = 640
    camera_height: int = 480

    video_filename: str = "video.h264"
    video_format: str = "h264"

    server_url_info: str = ""
    server_url_file_upload = ""

    def __init__(self):
        pass

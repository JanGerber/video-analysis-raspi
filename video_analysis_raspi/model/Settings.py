class Settings:
    raspi_uuid: str = ""
    camera_led: bool = True
    camera_width: int = 640
    camera_height: int = 480

    video_filename: str = "video.h264"
    video_format: str = "h264"

    image_name_pre: str = "picture_"
    image_format: str = "jpeg"

    server_url_base: str = ""
    server_url_video_file_upload = "/api/v1/upload/video"
    server_url_image_file_upload = "/api/v1/upload/image"
    server_url_login: str = "/api/v1/login"
    server_jwt: str
    server_auth_header = {}
    server_user: str
    server_pwd: str

    def __init__(self):
        pass

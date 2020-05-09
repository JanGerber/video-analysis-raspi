class VideoRecordingError(Exception):
    def __init__(self, msg='Something went wrong during the video recording', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

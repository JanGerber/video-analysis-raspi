class ImageTakingError(Exception):
    def __init__(self, msg='Something went wrong during the picture taking', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

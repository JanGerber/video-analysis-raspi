import datetime
import json


class ImageStartRequest:
    store: bool = False
    num_images: int = 1
    start_time: datetime
    groupId: str = ""
    interval: int = 1

    def __init__(self, j):
        self.__dict__ = json.loads(j)

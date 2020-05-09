import datetime
import json


class VideoStartRequest:
    store: bool = False
    stream: bool = False
    duration: int = 20
    start_time: datetime
    groupId: str = ""

    def __init__(self, j):
        self.__dict__ = json.loads(j)

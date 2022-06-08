from pymongo.cursor import Cursor
from .enemy import Enemy


class Location:
    _id: int

    def __init__(self, id: int, data: Cursor):
        self._id = id



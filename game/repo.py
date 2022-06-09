from typing import List

from pymongo.collection import Collection
from pymongo.cursor import Cursor

from . import Player
from .character import Character
from .player import Player
from .enemy import Enemy


class Repo:
    _source: Collection

    def __init__(self, table: Collection):
        self._source = table

    def insert(self, c: Character):
        self._source.insert_one(c.export())

    def delete(self, c: Character):
        self._source.delete_one({'_id': c.get_id()})

    def update(self, c: Character):
        self._source.update_one({'_id': c.get_id()}, {'$set': c.export()})

    def get_by_id(self, id: str) -> dict | None:
        return self._source.find_one({'_id': id})

    def select(self) -> Cursor | None:
        return self._source.find({})


class PlayerRepo(Repo):
    def __init__(self, table: Collection):
        super().__init__(table)

    def select(self) -> list[Player]:
        p = []
        pls = self._source.find({})
        for pl in pls:
            p.append(Player(pl))
        return p

    def get_by_id(self, id: str) -> Player | None:
        p = self._source.find_one({'_id': id})
        return None if p is None else Player(p)

    def get_by_player_id(self, id: int) -> Player | None:
        p = self._source.find_one({'player_id': id})
        return None if p is None else Player(p)


class MobRepo(Repo):
    def __init__(self, table: Collection):
        super().__init__(table)

    def select(self, channel: int | None = None) -> list[Enemy]:
        e = []
        if channel is None:
            enms = self._source.find({})
        else:
            enms = self._source.find({'channel': channel})
        for enemy in enms:
            e.append(Enemy(enemy))
        return e

    def select_by_type(self, type: str, channel: int | None = None):
        e = []
        if channel is None:
            enms = self._source.find({'type': type})
        else:
            enms = self._source.find({'type': type, 'channel': channel})
        for enemy in enms:
            e.append(Enemy(enemy))
        return e

    def select_by_name(self, name: str, channel: int | None = None):
        e = []
        if channel is None:
            enms = self._source.find({'name': name})
        else:
            enms = self._source.find({'name': name, 'channel': channel})
        for enemy in enms:
            e.append(Enemy(enemy))
        return e

    def select_names_by_type(self, type: str, channel: int | None = None) -> list[str]:
        names = []
        self._source.find()

    def get_by_id(self, id: str) -> Enemy | None:
        p = self._source.find_one({'_id': id})
        return None if p is None else Enemy(p)

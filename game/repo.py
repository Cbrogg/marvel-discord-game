from pymongo.collection import Collection
from pymongo.cursor import Cursor

from .character import Character, Avatar
from .player import Player
from .enemy import Enemy


class Repo:
    _source: Collection

    def __init__(self, table: Collection):
        self._source = table

    # Добавить игрока или моба
    def insert(self, c: Character):
        self._source.insert_one(c.export())

    # Удалить игрока или моба
    def delete(self, c: Character):
        self._source.delete_one({'_id': c.get_id()})

    # Обновить игрока или моба
    def update(self, c: Character):
        self._source.update_one({'_id': c.get_id()}, {'$set': c.export()})

    # Выбор игрока или моба по внутреннему ID
    def get_by_id(self, id: str) -> dict | None:
        return self._source.find_one({'_id': id})

    # Выбор всех объектов
    def select(self) -> Cursor | None:
        return self._source.find({})


class PlayerAvatarRepo(Repo):
    def __init__(self, table: Collection):
        super().__init__(table)

    # Выбрать аватар по внутреннему ID
    def get_by_id(self, id: str) -> Avatar | None:
        p = self._source.find_one({'_id': id})
        return None if p is None else Avatar(p)

    # Выбрать активный аватар по дискордному ID
    def get_active_by_player_id(self, id: int) -> Avatar | None:
        p: dict = self._source.find_one({'player_id': id, 'active': True})
        if p is None:
            p = self._source.find_one({'player_id': id, 'archived': False})
            if p is not None:
                p['active'] = True
        return None if p is None else Avatar(p)

    # Выбрать аватар по дискордному ID
    def select_by_player_id(self, id: int) -> list[Avatar] | None:
        p = []
        pls = self._source.find({'player_id': id})
        for pl in pls:
            p.append(Avatar(pl))
        return p


class MobAvatarRepo(Repo):
    def __init__(self, table: Collection):
        super().__init__(table)

    # Выбрать аватар моба по ID
    def get_by_id(self, id: str) -> Avatar | None:
        if id == "":
            return None
        p = self._source.find_one({'_id': id})
        return None if p is None else Avatar(p)

    # Выбрать аватар моба по названию
    def get_by_name(self, name: str) -> Avatar | None:
        m = self._source.find_one({'name': name})
        return None if m is None else Avatar(m)

    # Выбор всех аватаров мобов
    def select(self) -> list[Avatar]:
        m = []
        mobs = self._source.find({})
        for mob in mobs:
            m.append(Avatar(mob))
        return m


class PlayerRepo(Repo):
    _avatar_repo: PlayerAvatarRepo

    def __init__(self, table: Collection, avatars: PlayerAvatarRepo):
        super().__init__(table)
        self._avatar_repo = avatars

    # Выбор всех игроков
    def select(self) -> list[Player]:
        p = []
        pls = self._source.find({})
        for pl in pls:
            p.append(Player(pl))
        return p

    # Выбор игрока по внутреннему ID
    def get_by_id(self, id: str) -> Player | None:
        p = self._source.find_one({'_id': id})
        return None if p is None else Player(p)

    # Выбор игрока по дискордному ID
    def get_by_player_id(self, id: int) -> Player | None:
        if id == 0:
            return None
        p: dict = self._source.find_one({'player_id': id})
        if p is None:
            return None
        player = Player(p)
        player.set_avatar(self._avatar_repo.get_active_by_player_id(id))
        return player


class MobRepo(Repo):
    _avatar_repo: MobAvatarRepo

    def __init__(self, table: Collection, avatars: MobAvatarRepo):
        super().__init__(table)
        self._avatar_repo = avatars

    # Выбор врага по ID
    def get_by_id(self, id: str) -> Enemy | None:
        if id == "":
            return None
        p: dict = self._source.find_one({'_id': id})
        if p is None:
            return None
        avatar = self._avatar_repo.get_by_id(p.get('avatar_id', ""))
        mob = Enemy(p)
        mob.set_avatar(avatar)
        return mob

    # Выбор врагов. Возможен выбор врагов в определённом канале
    def select(self, channel: int | None = None) -> list[Enemy] | None:
        if channel == 0:
            return None
        e = []
        if channel is None:
            enms = self._source.find({})
        else:
            enms = self._source.find({'channel': channel})
        for enemy in enms:
            en = Enemy(enemy)
            en.set_avatar(self._avatar_repo.get_by_name(en.get_name()))
            e.append(en)
        return e

    # Выбор врагов по типу. Возможен выбор врагов по типу в определённом канале
    def select_by_type(self, type: str, channel: int | None = None):
        e = []
        if channel is None:
            enms = self._source.find({'type': type})
        else:
            enms = self._source.find({'type': type, 'channel': channel})
        for enemy in enms:
            e.append(Enemy(enemy))
        return e

    # Выбор врагов по названию. Возможен выбор врагов по названию в определённом канале
    def select_by_name(self, name: str, channel: int | None = None):
        e = []
        if channel is None:
            enms = self._source.find({'name': name})
        else:
            enms = self._source.find({'name': name, 'channel': channel})
        for enemy in enms:
            e.append(Enemy(enemy))
        return e

    # Выбор названий по типу врагов. Возможен выбор врагов в определённом канале
    def select_names_by_type(self, type: str, channel: int | None = None) -> list[str]:
        names = []
        enms = self.select_by_type(type, channel)
        for enemy in enms:
            try:
                names.index(enemy.get_name())
            except ValueError:
                names.append(enemy.get_name())
        return names

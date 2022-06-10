import uuid

from .enums import HealthStatus
from .special import Special


class Avatar:
    _id: str
    _name: str
    avatar_class: str
    player_id: int = 0
    special: Special
    skills: dict
    active: bool

    def __init__(self, data: dict):
        self._id = data.get('_id', str(uuid.uuid4()))
        self._name = data.get('name', 'empty')
        self.avatar_class = data.get('class', 'empty')
        self.player_id = data.get('player_id', 0)
        self.special = Special(data.get('special', {}))
        self.skills = data.get('skills', {})
        self.active = data.get('active', True)

    def __str__(self) -> str:
        return f"{self._name} (S:{self.special.s}/P:{self.special.p}/E:{self.special.e}/C:{self.special.c}/I:{self.special.i}/A:{self.special.a}/L:{self.special.l})"

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def export(self) -> dict:
        return {
            '_id': self._id,
            'name': self._name,
            'class': self.avatar_class,
            'player_id': self.player_id,
            'special': self.special.export(),
            'skills': self.skills,
            'active': self.active
        }


class Character:
    _id: str
    _name: str
    _type: str
    _hp: int
    _stamina: int
    _avatar_id: str
    _avatar: Avatar
    _effects: dict

    def __init__(self, data: dict):
        self._id = data.get('_id', str(uuid.uuid4()))
        self._name = data.get('name', 'empty')
        self._type = data.get('type', 'character')
        self._avatar_id = data.get('avatar_id', "")
        self._hp = data.get('hp', 0)
        self._stamina = data.get('stamina', 0)
        self._effects = data.get('effects', {})

    def __str__(self) -> str:
        return f"{self._name}({self._hp}/{self.max_hp()})"

    def set_avatar(self, avatar: Avatar):
        self._avatar = avatar

    def max_hp(self) -> int:
        return int(pow(100, (1 + (self._avatar.special.e / 30))) / 2 + self._avatar.special.s)

    def max_mille_damage(self) -> int:
        return int(self._avatar.special.s * 2 + self._avatar.special.a)

    def max_range_damage(self) -> int:
        return int(self._avatar.special.p * 2 + self._avatar.special.a)

    def max_magic_damage(self) -> int:
        return int(self._avatar.special.p * 2 + self._avatar.special.i * 2)

    def export(self) -> dict:
        return {
            '_id': self._id,
            'name': self._name,
            'type': self._type,
            'hp': self._hp,
            'stamina': self._stamina,
            'avatar_id': self._avatar.get_id(),
            'effects': self._effects
        }

    def status(self) -> str:
        if self._hp >= self.max_hp():
            return str(HealthStatus.HEALTH)
        elif int(self.max_hp() * 4 / 5) <= self._hp:
            return str(HealthStatus.DAM10)
        elif int(self.max_hp() * 2 / 5) <= self._hp < int(self.max_hp() * 4 / 5):
            return str(HealthStatus.DAM20)
        elif 20 <= self._hp < int(self.max_hp() * 2 / 5):
            return str(HealthStatus.DAM60)
        elif 0 < self._hp < 20:
            return str(HealthStatus.DAM80)
        else:
            return str(HealthStatus.DEAD)

    def heal(self, heal: int):
        if self._hp < int(self.max_hp() * 4 / 5):
            if self._hp + heal > int(self.max_hp() * 4 / 5):
                self._hp = int(self.max_hp() * 4 / 5)
            else:
                self._hp += heal

    def is_healable(self) -> bool:
        return self._hp < int(self.max_hp() * 4 / 5)

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_type(self) -> str:
        return self._type

import uuid

from .enums import HealthStatus
from .special import Special

_msg_fall = "{name} без сознания.\n"
_msg_self_get_damage = '{name} получил(а) {damage} урона.'


class Avatar:
    _id: str
    _name: str
    type: dict = {}
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
        self.type = data.get('type', {'one': 'монстр', 'many': 'монстры', 'no': 'монстров'})
        self.special = Special(data.get('special', {}))
        self.skills = data.get('skills', {})
        self.active = data.get('active', True)

    def __str__(self) -> str:
        return f"{self._name} (S:{self.special.s}/P:{self.special.p}" + \
               f"/E:{self.special.e}/C:{self.special.c}/I:{self.special.i}/A:{self.special.a}/L:{self.special.l})"

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
    id: str
    name: str
    hp: int
    stamina: int
    type: str
    avatar_id: str
    avatar: Avatar
    effects: dict

    def __init__(self, data: dict, avatar: Avatar | None = None):
        self.id = data.get('_id', str(uuid.uuid4()))
        self.name = data.get('name', 'empty')
        self.type = data.get('type', 'character')
        self.avatar_id = data.get('avatar_id', "")
        self.hp = data.get('hp', 0)
        self.stamina = data.get('stamina', 0)
        self.effects = data.get('effects', {})
        self.avatar = avatar

    def __str__(self) -> str:
        return f"{self.name}({self.hp}/{self.max_hp()})"

    def set_avatar(self, avatar: Avatar):
        self.avatar = avatar

    def max_hp(self) -> int:
        return int(pow(100, (1 + (self.avatar.special.e / 30))) / 2 + self.avatar.special.s)

    def max_mille_damage(self) -> int:
        return int(self.avatar.special.s * 2 + self.avatar.special.a)

    def max_range_damage(self) -> int:
        return int(self.avatar.special.p * 2 + self.avatar.special.a)

    def max_magic_damage(self) -> int:
        return int(self.avatar.special.p * 2 + self.avatar.special.i * 2)

    def export(self) -> dict:
        return {
            '_id': self.id,
            'name': self.name,
            'type': self.type,
            'hp': self.hp,
            'stamina': self.stamina,
            'avatar_id': self.avatar.get_id(),
            'effects': self.effects
        }

    def status(self) -> str:
        if self.hp >= self.max_hp():
            return str(HealthStatus.HEALTH)
        elif int(self.max_hp() * 4 / 5) <= self.hp:
            return str(HealthStatus.DAM10)
        elif int(self.max_hp() * 2 / 5) <= self.hp < int(self.max_hp() * 4 / 5):
            return str(HealthStatus.DAM20)
        elif 20 <= self.hp < int(self.max_hp() * 2 / 5):
            return str(HealthStatus.DAM60)
        elif 0 < self.hp < 20:
            return str(HealthStatus.DAM80)
        else:
            return str(HealthStatus.DEAD)

    def heal(self, heal: int):
        if self.hp < int(self.max_hp() * 4 / 5):
            if self.hp + heal > int(self.max_hp() * 4 / 5):
                self.hp = int(self.max_hp() * 4 / 5)
            else:
                self.hp += heal

    # Получение урона игроком
    def take_damage(self, damage: int) -> str:  # TODO
        d = damage - self.avatar.special.e if damage > self.avatar.special.e else 0
        msg = _msg_self_get_damage.format(name=self.get_name(), damage=d)
        self.hp -= d
        if self.hp <= 0:
            msg += _msg_fall.format(name=self.get_name())
            self.hp = 0
        else:
            msg += '\n'

        return msg

    def is_healable(self) -> bool:
        return self.hp < int(self.max_hp() * 4 / 5)

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> dict:
        return self.avatar.type

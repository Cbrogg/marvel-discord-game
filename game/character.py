import uuid
from .special import Special


class Character:
    _id: str
    _name: str
    _type: str
    _hp: int
    _stamina: int
    _special: Special
    _effects: dict

    def __init__(self, data: dict = {}):
        self._id = data.get('_id', str(uuid.uuid4()))
        self._name = data.get('name', 'empty')
        self._type = data.get('type', 'character')
        self._hp = data.get('hp', 0)
        self._stamina = data.get('stamina', 0)
        self._special = Special(data.get('special', {}))
        self._effects = data.get('effects', {})

    def __str__(self) -> str:
        return f"{self._name}({self._hp}/{self.max_hp()})"

    def export(self) -> dict:
        return {
            '_id': self._id,
            'name': self._name,
            'type': self._type,
            'hp': self._hp,
            'stamina': self._stamina,
            'special': self._special.to_dict(),
            'effects': self._effects
        }

    def get_id(self) -> str:
        return self._id


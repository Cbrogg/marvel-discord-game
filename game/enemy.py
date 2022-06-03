from typing import Any
from .character import Character
from .enums import Gender, EnemyCombatStatus, EnemyHealthStatus


class Enemy(Character):
    _gender: str
    _c_status: str
    _h_status: str
    _channel: int
    _targets: dict

    def __init__(self, data: dict, ch_id=None):
        super().__init__(data)
        self._channel = data.get('channel', ch_id)
        self._status = data.get('status', EnemyCombatStatus.IDLE)
        self._targets = data.get('targets', {})

    def get_max_priority(self) -> int:
        if len(self._targets) == 0:
            return 0
        else:
            p = 0
            for key in self._targets.keys():
                if self._targets[key] > p:
                    p = self._targets[key]
        return p

    def get_priority_target_id(self) -> Any:
        p = self.get_max_priority()
        id = None
        for key in self._targets.keys():
            if self._targets[key] == p:
                id = key
        return id

    def in_combat(self):
        self._c_status = EnemyCombatStatus.COMBAT

    def in_chase(self):
        self._c_status = EnemyCombatStatus.CHASE

    def add_target(self, id):
        self._targets[id] = 0
        # if len(self._targets) > 0 and self.status == 'ждет':
        #     self.status = 'в погоне'

    def del_target(self, id):
        self._targets.pop(str(id))
        if len(self._targets) <= 0:
            self.status = EnemyCombatStatus.IDLE

    def export(self) -> dict:
        return {
            'hp': self.hp,
            'name': self.name,
            'channel': self.channel,
            'special': self.special,
            'targets': self._targets,
            'status': self.status,
        }

    def max_hp(self) -> int:
        return int(5 + (self._special.s + self._special.e * 3))

    def take_damage(self, damage: int) -> str:
        msg = ""
        d = damage - self._special.e if damage > self._special.e else 0
        msg += f"{self._name} получил {d} урона." if self._gender == Gender.MALE else f"{self._name} получила {d} урона."
        self.hp -= d
        if self._hp <= 0:
            msg += f" {self._name} мертв.\n" if self._gender == Gender.MALE else f" {self._name} мертва.\n"
            self._hp = 0
            self._h_status = EnemyHealthStatus.DEAD
        else:
            msg += '\n'

        return msg

    def is_dead(self) -> bool:
        return True if self._hp <= 0 else False

    def heal(self, heal):
        self._hp += heal
        if self._hp > self.max_hp():
            self._hp = self.max_hp()

    def get_status(self) -> str:
        return self.status

    def inc_priority(self, id):
        p = self.get_max_priority()
        self._targets[id] = p + 1

    def dec_priority(self, id):
        self._targets[id] = self._targets.get(id, 1) - 1

import random

from .character import Character
from .enums import Gender, EnemyCombatStatus, EnemyHealthStatus
from priority import Priority


class Enemy(Character):
    _gender: Gender
    _c_status: EnemyCombatStatus
    _h_status: EnemyHealthStatus
    _level: int
    _channel: int
    _targets: [Priority]

    def __init__(self, data: dict, ch_id=None):
        super().__init__(data)
        self._gender = data.get('gender', Gender.MALE)
        self._level = data.get('level', 1)
        self._channel = data.get('channel', ch_id)
        self._status = data.get('status', EnemyCombatStatus.IDLE)
        self.targets_from_dict(data.get('targets', {}))

    def max_mille_damage(self) -> int:
        return int(self._special.s * 2 + self._special.a)

    def max_range_damage(self) -> int:
        return int(self._special.p * 2 + self._special.a)

    def max_magic_damage(self) -> int:
        return int(self._special.p * 2 + self._special.i * 2)

    def get_max_priority(self) -> Priority:
        return max(self._targets)

    def get_priority_by_id(self, id: int) -> Priority | None:
        for pr in self._targets:
            if pr.id == id:
                return pr
        return None

    def priority_to_dict(self) -> dict:
        d = {}
        for pr in self._targets:
            d[str(pr.id)] = pr.value
        return d

    def targets_from_dict(self, d: dict):
        for key in d.keys():
            self._targets.append(Priority(int(key), d[key]))

    def inc_priority(self, id=0) -> Priority:
        self._targets.remove(self.get_priority_by_id(id))
        pr = max(self._targets)
        new_pr = Priority(id, pr.value + 1)
        self._targets.append(new_pr)
        return new_pr

    def dec_priority(self, id):
        pr = self.get_priority_by_id(id)
        self._targets.remove(pr)
        pr -= 1
        self._targets.append(pr)

    def add_target(self, id: int):
        self._targets.append(Priority(id))

    def del_target(self, id: int):
        self._targets.remove(self.get_priority_by_id(id))

    def in_combat(self):
        self._c_status = EnemyCombatStatus.COMBAT

    def in_chase(self):
        self._c_status = EnemyCombatStatus.CHASE

    def idle(self):
        self._c_status = EnemyCombatStatus.IDLE

    def export(self) -> dict:
        return {
            '_id': self._id,
            'name': self._name,
            'type': self._type,
            'hp': self._hp,
            'stamina': self._stamina,
            'special': self._special.to_dict(),
            'effects': self._effects,
            'channel': self._channel,
            'targets': self.priority_to_dict(),
            'h_status': self.get_health_status(),
            'c_status': self.get_combat_status()
        }

    def max_hp(self) -> int:
        return int(5 + (self._special.s + self._special.e * 3))

    def take_damage(self, damage: int) -> str:
        d = damage - self._special.e if damage > self._special.e else 0
        msg = f"{self._name} получил {d} урона." if self._gender == Gender.MALE else f"{self._name} получила {d} урона."
        self._hp -= d
        if self._hp <= 0:
            msg += f" {self._name} мертв.\n" if self._gender == Gender.MALE else f" {self._name} мертва.\n"
            self._hp = 0
            self._h_status = EnemyHealthStatus.DEAD
        else:
            msg += '\n'

        return msg

    def deal_damage(self) -> int:
        match self._c_status:
            case EnemyCombatStatus.MILLE:
                max_damage = self.max_mille_damage()
            case EnemyCombatStatus.RANGE:
                max_damage = self.max_range_damage()
            case EnemyCombatStatus.MAGIC:
                max_damage = self.max_magic_damage()
            case _:
                max_damage = self.max_mille_damage()

        dice = random.randint(1, 20)
        damage = 0 if dice < 10 else max_damage * dice / 20

        return damage

    def is_dead(self) -> bool:
        return True if self._hp <= 0 else False

    def heal(self, heal):
        self._hp += heal
        if self._hp > self.max_hp():
            self._hp = self.max_hp()

    def get_combat_status(self) -> str:
        return str(self._c_status)

    def get_health_status(self) -> str:
        return str(self._h_status)


class EnemyGroup:
    _leader: Enemy
    _vanguard: [Enemy]
    _core: [Enemy]
    _rearguard: [Enemy]

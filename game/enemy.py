import random

from .character import Character
# from .player import Player
from .enums import Gender, EnemyCombatStatus, EnemyHealthStatus
from .priority import Priority

_msg_take_damage_male = "{} получил {} урона."
_msg_take_damage_female = "{} получила {} урона."

_msg_dead_male = " {} мертв.\n"
_msg_dead_female = " {} мертва.\n"


class Enemy(Character):
    _gender: Gender
    _c_status: EnemyCombatStatus
    _h_status: EnemyHealthStatus
    _level: int
    _channel: int
    _targets: list[Priority] = []
    # _priority_target: Player | None = None



    def __init__(self, data: dict, ch_id=None):
        super().__init__(data)
        self._gender = data.get('gender', Gender.MALE)
        self._level = data.get('level', 1)
        self._channel = data.get('channel', ch_id)
        self._c_status = data.get('status', EnemyCombatStatus.IDLE)
        self.targets_from_dict(data.get('targets', {}))

    # def get_priority_target(self) -> Player:
    #     return self._priority_target
    #
    # def set_priority_target(self, target: Player):
    #     self._priority_target = target

    def get_reaction(self) -> int:
        return self._avatar.special.reaction()

    def get_max_priority(self) -> Priority:
        return max(self._targets)

    def get_priority_by_id(self, id: int) -> Priority | None:
        pr = None
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
        pr = max(self._targets)
        self._targets.remove(self.get_priority_by_id(id))
        new_pr = Priority(id, pr.value + 1)
        self._targets.append(new_pr)
        return new_pr

    def dec_priority(self, id):
        pr = self.get_priority_by_id(id)
        self._targets.remove(pr)
        pr -= 1
        self._targets.append(pr)

    def add_target(self, id: int):
        if self.get_priority_by_id(id) is None:
            self._targets.append(Priority(id))

    def del_target(self, id: int):
        p = self.get_priority_by_id(id)
        self._targets.remove(p)

    def in_combat(self):
        self._c_status = EnemyCombatStatus.COMBAT

    def in_chase(self):
        self._c_status = EnemyCombatStatus.CHASE

    def idle(self):
        self._c_status = EnemyCombatStatus.IDLE

    def export(self) -> dict:
        s = super().export()
        s['gender'] = self._gender
        s['level'] = self._level
        s['channel'] = self._channel
        s['targets'] = self.priority_to_dict()
        s['status'] = self.get_combat_status()

        return s

    def max_hp(self) -> int:
        return int(5 + (self._avatar.special.s + self._avatar.special.e * 3))

    def take_damage(self, damage: int) -> str:
        d = damage - self._avatar.special.e if damage > self._avatar.special.e else 0
        msg = _msg_take_damage_male.format(self._name, d) if self._gender == Gender.MALE else _msg_take_damage_female.format(self._name, d)
        self._hp -= d
        if self._hp <= 0:
            msg += _msg_dead_male.format(self._name) if self._gender == Gender.MALE else _msg_dead_female.format(self._name)
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

    # def deal_damage_to_priority_target(self) -> str:
    #     msg = self._priority_target.take_damage(int(self.deal_damage()/3))
    #     msg = msg[:-1] + "вместо {name}. \n"
    #     return msg

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

    def is_healthy(self) -> bool:
        return self._hp >= self.max_hp()

    def max_hp(self) -> int:
        return int(5 + (self.special['s'] + self.special['e']) * 3)

    def is_idle(self) -> bool:
        return self._c_status == EnemyCombatStatus.IDLE


class EnemyGroup:
    _leader: Enemy
    _vanguard: list[Enemy]
    _core: list[Enemy]
    _rearguard: list[Enemy]

import random

from .character import Character, Avatar
from .enums import Gender, EnemyCombatStatus
from .priority import Priority

msg_take_damage_male = "{} получил {} урона."
msg_take_damage_female = "{} получила {} урона."

msg_dead_male = " {} мертв.\n"
msg_dead_female = " {} мертва.\n"


class Enemy(Character):
    gender: Gender
    c_status: str
    level: int
    channel: int | None
    _targets: list[Priority]
    priority_target: Character | None = None

    def __init__(self, data: dict, ch_id: int | None = None, avatar: Avatar | None = None):
        super().__init__(data, avatar)
        self.c_status = data.get('status', 'ждет')
        self.gender = data.get('gender', Gender.MALE)
        self.level = data.get('level', 1)
        self.channel = data.get('channel', ch_id)
        self.targets_from_dict(data.get('targets', {}))
        return

    def get_channel(self) -> int:
        return self.channel

    def is_in_chase(self) -> bool:
        return self.c_status == 'в погоне'

    def is_in_combat(self) -> bool:
        return self.c_status == 'в бою'

    def is_idle(self) -> bool:
        return self.c_status == 'ждет'

    def get_priority_target(self) -> Character:
        return self.priority_target

    def set_priority_target(self, target: Character):
        self.priority_target = target

    def get_max_priority(self) -> Priority:
        return max(self._targets)

    def get_priority_by_id(self, p_id: int) -> Priority | None:
        for pr in self._targets:
            if pr.p_id == p_id:
                return pr
        return None

    def get_priority_target_id(self) -> int:
        if len(self._targets) == 0:
            return -1
        p = self.get_max_priority()
        return int(p.p_id)

    def priority_to_dict(self) -> dict:
        d = {}
        for pr in self._targets:
            d[str(pr.p_id)] = pr.value
        return d

    def targets_from_dict(self, d: dict):
        self._targets = []
        for key in d.keys():
            if self.get_priority_by_id(int(key)) is None:
                self._targets.append(Priority(int(key), d[key]))
        return

    def inc_priority(self, p_id=0) -> Priority:
        pr = max(self._targets)
        self._targets.remove(self.get_priority_by_id(p_id))
        new_pr = Priority(p_id, pr.value + 1)
        self._targets.append(new_pr)
        return new_pr

    def dec_priority(self, p_id):
        pr = self.get_priority_by_id(p_id)
        self._targets.remove(pr)
        pr -= 1
        self._targets.append(pr)

    def add_target(self, p_id: int):
        if len(self._targets) == 0:
            if self.get_priority_by_id(p_id) is None:
                self._targets.append(Priority(p_id, 1))
        else:
            if self.get_priority_by_id(p_id) is None:
                self._targets.append(Priority(p_id))

    def del_target(self, p_id: int):
        p = self.get_priority_by_id(p_id)
        if p is not None:
            self._targets.remove(p)
        if len(self._targets) == 0:
            self.c_status = 'ждет'

    def in_combat(self):
        self.c_status = 'в бою'

    def in_chase(self):
        self.c_status = 'в погоне'

    def idle(self):
        self.c_status = 'ждет'

    def export(self) -> dict:
        s = super().export()
        s['gender'] = self.gender
        s['level'] = self.level
        s['channel'] = self.channel
        s['targets'] = self.priority_to_dict()
        s['status'] = self.c_status

        return s

    def max_hp(self) -> int:
        return int(5 + (self.avatar.special.s + self.avatar.special.e * 3))

    def is_dead(self) -> bool:
        return True if self.hp <= 0 else False

    def heal(self, heal):
        self.hp += heal
        if self.hp > self.max_hp():
            self.hp = self.max_hp()

    def get_combat_status(self) -> str:
        return str(self.c_status)

    def is_healthy(self) -> bool:
        return self.hp >= self.max_hp()

    def detection(self) -> int:
        return self.avatar.special.detection()

    def dead(self):
        self.c_status = 'мертв'

    def fiction(self) -> int:
        """
        Возвращает фиктивный урон для проверки процесса боя.
        :return:
        """
        return random.randint(1, self.max_hp())

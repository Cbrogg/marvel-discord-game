import random

from .enemy import Enemy

_msg_clean_location = "Вокруг нет ни следа противника.\n"
_msg_count_enemy = "Осмотревшись, вы насчитали {count} {type}.\n"
_msg_hear_enemy = "В округе слышны {type}.\n"


class Location:
    _id: int = 0
    _mobs: dict = {}

    def __init__(self, id: int = 0, mob_list: list[Enemy] | None = None):
        self._id = id
        if mob_list is None:
            pass
        for mob in mob_list:
            mobs = self._mobs.get(mob.get_name(), [])
            if len(mobs) == 0:
                self._mobs[mob.get_name()] = [mob]
            else:
                self._mobs[mob.get_name()].append(mob)

    def get_max_detection(self) -> int:
        if len(self._mobs) == 0:
            return 0
        d = [int]
        for name in self._mobs.keys():
            d.append(self._mobs[name][0].special.detection())

        return max(d)

    def is_clean(self) -> bool:
        return len(self._mobs) == 0

    def get_any_mob(self) -> Enemy | None:
        if self.is_clean():
            return None

        mob = None

        name = self._mobs.keys()[random.randint(0, len(self._mobs))]

        for i in range(len(self._mobs[name])):
            m: Enemy = self._mobs[name][i]
            if m.is_healthy() and m.is_idle():
                mob = m

        if mob is None:
            for i in range(len(self._mobs[name])):
                m: Enemy = self._mobs[name][i]
                if m.is_idle():
                    mob = m

        if mob is None:
            mob = self._mobs[name][0]

        return mob

    def look_around(self) -> str:
        if self.is_clean():
            return _msg_clean_location

        else:
            r = random.randint(1, 20)
            count = 0
            for name in self._mobs.keys():
                count += len(self._mobs[name])

            if r == 20:
                return _msg_count_enemy.format(count=count, type=self.get_any_mob().get_type())
            elif 10 <= r < 20:
                c = 'не больше десятка' if count < 10 else 'не меньше десятка'
                return _msg_count_enemy.format(count=c, type=self.get_any_mob().get_type())
            elif r < 10:
                return _msg_hear_enemy.format(type=self.get_any_mob().get_type())

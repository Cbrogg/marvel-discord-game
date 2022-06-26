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
        d = []
        for name in self._mobs.keys():
            m: Enemy = self._mobs[name][0]
            d.append(m.detection())

        return max(d)

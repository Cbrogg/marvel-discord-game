import random

from .enemy import Enemy


class Location:
    _id: int
    _mobs: dict

    def __init__(self, id: int, mob_list: list[Enemy]):
        self._id = id
        for mob in mob_list:
            mobs = self._mobs.get(mob.get_name(), [])
            if len(mobs) == 0:
                self._mobs[mob.get_name()] = [mob]
            else:
                self._mobs[mob.get_name()].append(mob)

    def get_max_detection(self) -> int:
        d = [int]
        for name in self._mobs.keys():
            d.append(self._mobs[name][0].special.detection())

        return max(d)

    def is_clean(self) -> bool:
        return len(self._mobs) == 0

    def get_any_mob(self) -> Enemy | None:
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
# channel = Location(channel_id, self.mob_table.find({'channel': channel_id}))


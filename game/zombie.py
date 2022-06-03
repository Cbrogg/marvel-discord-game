from typing import Any


class Zombie:
    def __init__(self, z: dict, ch_id=None):
        self.special: dict = z['special']
        self.id = z['_id']
        self.name = z['name']
        self.hp = z.get('hp', int(5 + (self.special['s'] + self.special['e']) * 3))
        self.channel = z.get('channel', ch_id)
        self.status = z.get('status', 'ждет')
        self.targets = z.get('targets', {})

    def get_max_priority(self) -> int:
        if len(self.targets) == 0:
            return 0
        else:
            p = 0
            for key in self.targets.keys():
                if self.targets[key] > p:
                    p = self.targets[key]
        return p

    def get_priority_target_id(self) -> Any:
        p = self.get_max_priority()
        id = None
        for key in self.targets.keys():
            if self.targets[key] == p:
                id = key
        return id

    def in_combat(self):
        self.status = 'в бою'

    def in_chase(self):
        self.status = 'в погоне'

    def add_target(self, id):
        self.targets[id] = 0
        if len(self.targets) > 0 and self.status == 'ждет':
            self.status = 'в погоне'

    def del_target(self, id):
        self.targets.pop(str(id))
        if len(self.targets) <= 0:
            self.status = 'ждет'

    def export(self) -> dict:
        return {'hp': self.hp,
                'name': self.name,
                'channel': self.channel,
                'special': self.special,
                'targets': self.targets,
                'status': self.status,
                }

    def max_stamina(self) -> int:
        return int(self.special['e'] * 20)

    def max_mille_damage(self) -> int:
        return int(self.special['s'] * 2 + self.special['a'])

    def max_range_damage(self) -> int:
        return int(self.special['p'] * 2 + self.special['a'])

    def max_damage(self) -> int:
        return int((self.special['s'] + self.special['a']) * 2)

    def max_weight(self) -> int:
        return 30 + int(pow(30, ((self.special['s'] - 1) / 5)))

    def max_action_points(self) -> int:
        return int(self.special['a'] / 3)

    def max_hp(self) -> int:
        return int(5 + (self.special['s'] + self.special['e']) * 3)

    def reaction(self) -> int:
        return int(2 * self.special['p'] + 2 * self.special['a'])

    def heal_points(self) -> int:
        return int(self.special['e'] / 3)

    def take_damage(self, damage: int) -> int:
        d = damage - self.special['e'] if damage > self.special['e'] else 0
        if self.hp - d < 0:
            self.hp = 0
            self.status = 'мертв'
        else:
            self.hp -= d
        return d

    def is_dead(self) -> bool:
        return True if self.status == 'мертв' else False

    def heal(self):
        self.hp = self.max_hp()

    def get_status(self) -> str:
        return self.status

    def stealth(self) -> int:
        return int(20 + self.special['a'] + int(self.special['l'] / 3))

    def detection(self) -> int:
        return int(35 + self.special['p'] + int(self.special['l'] / 2))

    def inc_priority(self, id):
        p = self.get_max_priority()
        self.targets[id] = p + 1

    def dec_priority(self, id):
        self.targets[id] = self.targets.get(id, 1) - 1
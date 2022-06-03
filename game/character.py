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
        # self.player_id = c['player_id']
        # self.kills = data['kills']
        # self.zombie_id = data['zombie']
        # self.zombie = None
        # self.z_status = data['z_status']
        # self.p_class = c.get('class', 'физ')

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

    def stealth(self) -> int:
        return int(25 + self._special.a + int(self._special.l / 3))

    def detection(self) -> int:
        return int(30 + self._special.p + int(self._special.l / 2))

    def reaction(self) -> int:
        return int(2 * self._special.p + 2 * self._special.a)

    def max_mille_damage(self) -> int:
        return int(self._special.s * 2 + self._special.a)

    def max_range_damage(self) -> int:
        return int(self._special.p * 2 + self._special.a)
        # return int(self._special.p * 3 + self._special.a * 2) if self.p_class == 'физ' else int(
        #     self._special.p * 2 + self._special.a)  # TODO

    def max_magic_damage(self) -> int:
        return int(self._special.p * 2 + self._special.i * 2)
        # return 0 if self.p_class != 'маг' else int(self._special.p * 2 + self._special.i * 2)

    def max_weight(self) -> int:
        return 30 + int(pow(30, ((self._special.s - 1) / 5)))

    def max_action_points(self) -> int:
        return int(self._special.a / 3)

    def max_hp(self) -> int:
        return int(pow(100, (1 + (self._special.e / 30))) / 2 + self._special.s)

    def heal_points(self) -> int:
        return int(self._special.e / 3)

    def max_stamina(self) -> int:
        return int(self._special.e * 20)

    def stamina_points(self) -> int:
        return int(self._special.e * 2)

    # def take_damage(self, damage: int) -> int:
    #     d = damage - self._special.e if damage > self._special.e else 0
    #     if self.hp - d < 0:
    #         self.hp = 0
    #     else:
    #         self.hp -= d
    #     return d
    #
    # def is_dead(self) -> bool:
    #     return True if self.hp <= 0 else False
    #
    # def status(self) -> str:
    #     if self.hp >= self.max_hp():
    #         return 'здоров'
    #     elif int(self.max_hp() * 4 / 5) <= self.hp:
    #         return 'легкое ранение'
    #     elif int(self.max_hp() * 2 / 5) <= self.hp < int(self.max_hp() * 4 / 5):
    #         return 'среднее ранение'
    #     elif 20 <= self.hp < int(self.max_hp() * 2 / 5):
    #         return 'тяжелое ранение'
    #     elif 0 < self.hp < 20:
    #         return 'критическое состояние'
    #     else:
    #         return 'без сознания'
    #
    # def has_enemy(self) -> bool:
    #     if self.zombie is None:
    #         return False
    #     else:
    #         return True
    #
    # def heal(self, heal: int):
    #     if self.hp < int(self.max_hp() * 4 / 5):
    #         if self.hp + heal > int(self.max_hp() * 4 / 5):
    #             self.hp = int(self.max_hp() * 4 / 5)
    #         else:
    #             self.hp += heal
    #
    # def rest(self):
    #     if self.hp < self.max_hp():
    #         self.hp += self.heal_points()
    #
    # def kill_enemy(self):
    #     if self.zombie is not None:
    #         self.zombie = None
    #         self.zombie_id = ""
    #         self.kills += 1
    #         self.z_status = 'не замечен' if random.randint(0, 100) > 50 else 'замечен'
    #
    # def drop_enemy(self):
    #     if self.zombie is not None:
    #         self.zombie = None
    #         self.zombie_id = ""
    #
    # def set_enemy(self, z: Zombie):
    #     self.z_status = 'замечен'
    #     self.zombie = z

    # def get_chase_escape_chance(self) -> int:
    #     if not self.has_enemy():
    #         return 100
    #     else:
    #         return int(50 * (self.reaction() / self.zombie.reaction()))

    # def is_priority_target(self) -> bool:
    #     if self.zombie is not None:
    #         return str(self.player_id) == self.zombie.get_priority_target_id()
    #     else:
    #         return False

    # def detect_chance(self, enemy_stealth: int = 0) -> int:
    #     if enemy_stealth == 0:
    #         return 0
    #     else:
    #         return int(30 * (self.detection() / enemy_stealth))
    #
    # def stealth_chance(self, enemy_detection: int = 0) -> int:
    #     if enemy_detection == 0:
    #         return 100
    #     else:
    #         return int(30 * (enemy_detection / self.stealth()))

    # def get_enemy_status(self) -> str:
    #     if self.zombie is not None:
    #         return self.zombie.get_status()
    #     else:
    #         return "нет"

import random

from .character import Character
from .enemy import Enemy


class Player(Character):
    def __init__(self, data: dict = {}, enemy: Enemy | None = None):
        super().__init__(data)
        self._player_id = data.get('player_id', 0)
        self._kills = data.get('kills', 0)
        self._enemy_id = data.get('enemy_id', "")
        self._enemy = enemy
        self._e_status = data.get('e_status', "")  # TODO PlayerEnemyStatus("Замечен, Не замечен, и т.д.")
        # self._h_status = data.get('h_status', "")  # TODO PlayerHealthStatus("Здоров, ранен и т.д.")
        self._player_class = data.get('class', 'физ')

    def max_mille_damage(self) -> int:
        return int(self._special.s * 2 + self._special.a)

    def max_range_damage(self) -> int:
        return int(self._special.p * 3 + self._special.a * 2) if self._player_class == 'физ' else int(
            self._special.p * 2 + self._special.a)

    def max_magic_damage(self) -> int:
        return 0 if self._player_class != 'маг' else int(self._special.p * 2 + self._special.i * 2)

    def take_damage(self, damage: int) -> int:
        d = damage - self._special.e if damage > self._special.e else 0
        if self.hp - d < 0:
            self.hp = 0
        else:
            self.hp -= d
        return d

    def is_dead(self) -> bool:
        return True if self._hp <= 0 else False

    def status(self) -> str:
        if self.hp >= self._special.max_hp():
            return 'здоров'
        elif int(self._special.max_hp() * 4 / 5) <= self.hp:
            return 'легкое ранение'
        elif int(self._special.max_hp() * 2 / 5) <= self.hp < int(self._special.max_hp() * 4 / 5):
            return 'среднее ранение'
        elif 20 <= self.hp < int(self._special.max_hp() * 2 / 5):
            return 'тяжелое ранение'
        elif 0 < self.hp < 20:
            return 'критическое состояние'
        else:
            return 'без сознания'

    def has_enemy(self) -> bool:
        if self._enemy is None:
            return False
        else:
            return True

    def heal(self, heal: int):
        if self.hp < int(self._special.max_hp() * 4 / 5):
            if self.hp + heal > int(self._special.max_hp() * 4 / 5):
                self.hp = int(self._special.max_hp() * 4 / 5)
            else:
                self.hp += heal

    def rest(self):
        if self.hp < self._special.max_hp():
            self.hp += self._special.heal_points()

    def kill_enemy(self):
        if self.zombie is not None:
            self.zombie = None
            self.zombie_id = ""
            self._kills += 1
            self.z_status = 'не замечен' if random.randint(0, 100) > 50 else 'замечен'

    def drop_enemy(self):
        if self.zombie is not None:
            self.zombie = None
            self.zombie_id = ""

    def set_enemy(self, z: Enemy):
        self.z_status = 'замечен'
        self.zombie = z

    def get_chase_escape_chance(self) -> int:
        if not self.has_enemy():
            return 100
        else:
            return int(50 * (self._special.reaction() / self._enemy._special.reaction()))

    def is_priority_target(self) -> bool:
        if self.zombie is not None:
            return str(self._player_id) == self.zombie.get_priority_target_id()
        else:
            return False

    def detect_chance(self, enemy_stealth: int = 0) -> int:
        if enemy_stealth == 0:
            return 0
        else:
            return int(30 * (self._special.detection() / enemy_stealth))

    def stealth_chance(self, enemy_detection: int = 0) -> int:
        if enemy_detection == 0:
            return 100
        else:
            return int(30 * (enemy_detection / self._special.stealth()))

    def get_enemy_status(self) -> str:
        if self.zombie is not None:
            return self.zombie.get_status()
        else:
            return "нет"

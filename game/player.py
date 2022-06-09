import random

from .character import Character
from .enemy import Enemy


class Player(Character):
    # Проверки
    _msg_dead_player = "{mention}, вы без сознания и не можете реагировать на происходящее пока вас не вылечили"
    _msg_more_actions = "{mention}, вы не можете использовать более одного атакующего действия за пост."
    _msg_more_defs = "{mention}, вы не можете использовать более одного оборонительно действия за пост."
    _msg_helped = "Вам помогли избавиться от {type_r}.\n"
    _msg_dont_look = "Вам некогда осматриваться по сторонам.\n"
    _msg_need_rest = "Персонаж {name} максимально вылечен. Теперь ему нужен отдых.\n"
    _msg_self_need_rest = "Вы максимально вылечены. Теперь вам необходим отдых. \n"
    _msg_defend_not_needed = "Ваша защита не требуется.\n"
    _msg_cant_help = "Нет возможности помочь, вас атакуют.\n"
    _msg_help_not_needed = "Ваша помощь не требуется.\n"
    _msg_cleared_location = "Локация зачищена.\n"
    _msg_next_mob = "К вам движется следующий {name}.\n"
    _msg_caught = "Вас догнал {name}!\n"
    _msg_attacked = "Вас атакует {name}!\n"
    _msg_followed = "К вам движется {name}.\n"
    _msg_no_target = "Нет цели для атаки.\n"

    # Подсчёт
    _msg_clean_location = "Вокруг нет ни следа {type}.\n"
    _msg_count_zombie = "Осмотревшись, вы насчитали {count} {type}.\n"
    _msg_hear_zombie = "В округе слышны {type}.\n"

    # Лечение
    _msg_max_healed = "Вы максимально вылечили {name}.\n"
    _msg_healed = "Вы вылечили {name} на {heal} единиц.\n"
    _msg_self_max_healed = "Вы максимально вылечили себя.\n"
    _msg_self_healed = "Вы вылечили себя на {heal} единиц.\n"

    # Атаки
    _msg_get_damage = "{name} получил {count} урона.\n"
    _msg_shoot = "{name} ранен выстрелом.\n"
    _msg_mage = "{name} ранен магией.\n"
    _msg_death_shoot = "{name} убит точным попаданием.\n"
    _msg_kill = "{name} убит.\n"
    _msg_attack = "Вы атаковали {name_r}.\n"

    # Защита, помощь и внимание
    _msg_defend_player = "{defender_name} защищает {name}.\n"
    _msg_change_target = "{enemy_name} переключил внимание на {name}.\n"
    _msg_help = "{helper_name} помогает {name}.\n"

    # Получение урона и текущий статус
    _msg_stat = "Текущий статус персонажа {name}: {status}.\n"
    _msg_fall = "{name} без сознания.\n"
    _msg_self_get_damage = 'Вы получили {damage} урона.\n'
    _msg_def_get_damage = '{defender_name} получил {damage} урона вместо {name}.\n'

    # Побег из боя или уклонение
    _msg_run_away = "Вы убежали от {name}.\n"
    _msg_get_invis = "{type} потеряли вас из виду.\n"
    _msg_not_run = "Убежать не вышло.\n"
    _msg_not_dodge = "Вы не смогли уклониться и получили {} урона.\n"
    _msg_dodge = "Вы смогли уклониться и получили 0 урона.\n"

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

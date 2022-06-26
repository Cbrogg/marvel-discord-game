import random

from .character import Character, Avatar
from .enemy import Enemy
from .location import Location


class Player(Character):
    enemy: Enemy | None = None
    player_id: int
    kills: int
    enemy_id: str
    e_status: str
    player_class: str

    def __init__(self, data: dict, avatar: Avatar | None = None, enemy: Enemy | None = None):
        super().__init__(data, avatar)
        self.player_id = data.get('player_id', 0)
        self.kills = data.get('kills', 0)
        self.enemy_id = data.get('enemy_id', "")
        if self.enemy_id == "":
            self.enemy_id = data.get('zombie', "")
        self.enemy = enemy
        self.e_status = data.get('e_status', "")  # TODO PlayerEnemyStatus("Замечен, Не замечен, и т.д.")
        # self._h_status = data.get('h_status', "")  # TODO PlayerHealthStatus("Здоров, ранен и т.д.")
        self.player_class = data.get('class', 'физ')

    def export(self) -> dict:
        d = super().export()
        d['enemy_id'] = self.enemy_id if self.enemy_id != "" else self.enemy.get_id() if self.has_enemy() else ""
        d['player_id'] = self.player_id
        d['kills'] = self.kills
        d['status'] = self.status()
        d['e_status'] = self.e_status
        return d

    # Получить дискордовый ID игрока
    def get_player_id(self) -> int:
        return self.player_id

    # Получить ID врага
    def get_enemy_id(self) -> str:
        return self.enemy_id

    # Уставить эффект
    def set_effect(self, key: str):
        self.effects[key] = True

    # Удалить эффект
    def remove_effect(self, key):
        self.effects.pop(key)

    def is_escaped(self) -> bool:
        return self.effects.get('escaped', False)

    # Максимальный урон дальней атаки
    def max_range_damage(self) -> int:
        return int(self.avatar.special.p * 3 + self.avatar.special.a * 2) if self.player_class == 'физ' else int(
            self.avatar.special.p * 2 + self.avatar.special.a)

    # Максимальный урон магической атаки
    def max_magic_damage(self) -> int:
        return 0 if self.player_class != 'маг' else int(self.avatar.special.p * 2 + self.avatar.special.i * 2)

    # Проверка игрока на жизнедеятельность
    def is_dead(self) -> bool:
        return True if self.hp <= 0 else False

    def is_detected(self) -> bool:
        return self.e_status == 'замечен'

    # Проверка, если ли враг у игрока
    def has_enemy(self) -> bool:
        if self.enemy is None:
            return False
        else:
            return True

    # Пассивный отхил игрока
    def rest(self):
        if self.hp < self.max_hp():
            self.hp += self.avatar.special.heal_points()

    # Убийство моба игроком
    def kill_enemy(self):
        if self.enemy is not None:
            self.enemy = None
            self.enemy_id = ""
            self.kills += 1
            self.e_status = 'не замечен'

    # Удаление моба из врагов игрока. Сброс противника
    def drop_enemy(self):
        if self.enemy is not None:
            self.enemy.del_target(self.player_id)
            self.enemy = None
        if self.enemy_id != "":
            self.enemy_id = ""

    # Привязка моба к игроку
    def set_enemy(self, e: Enemy | None):
        if e is None:
            return
        self.e_status = 'замечен'
        self.enemy = e
        self.enemy.add_target(self.player_id)

    # Расчёт шансов на побег
    def get_chase_escape_chance(self) -> int:
        if not self.has_enemy():
            return 100
        else:
            return int(50 * (self.avatar.special.reaction() / self.enemy.avatar.special.reaction()))

    # Проверка, является ли игрок приоритетной целью
    def is_priority_target(self) -> bool:
        if self.enemy is not None:
            t_id = self.enemy.get_priority_target_id()
            return self.player_id == t_id
        else:
            return False

    # Расчёт шансов игрока обнаружить моба
    def detect_chance(self, enemy_stealth: int = 0) -> int:
        if enemy_stealth == 0:
            return 0
        else:
            return int(30 * (self.avatar.special.detection() / enemy_stealth))

    # Расчёт шансов игрока быть незамеченным мобом
    def stealth_chance(self, enemy_detection: int = 0) -> int:
        if enemy_detection == 0:
            return 100
        else:
            return int(30 * (enemy_detection / self.avatar.special.stealth()))

    # Узнать статус врага
    def get_enemy_status(self) -> str:
        if self.enemy is not None:
            return self.enemy.get_combat_status()
        else:
            return "нет"
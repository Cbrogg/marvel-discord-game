import random

from .character import Character
from .enemy import Enemy
from .location import Location


class Player(Character):
    enemy: Enemy | None = None
    player_id: int
    kills: int
    enemy_id: str
    e_status: str
    player_class: str

    def __init__(self, data: dict, enemy: Enemy | None = None):
        super().__init__(data)
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

    # def on_message(self, message: discord.Message):
    #     if not player.has_enemy():
    #         if self.is_channel_clean(message.channel.id):
    #             return
    #         else:
    #             if player.z_status == 'не замечен':
    #                 notion = random.randint(1, 100)
    #                 embed.add_field(name="уведомление", value=f"result = {notion}/50")
    #                 if notion <= 50:
    #                     async with message.channel.typing():
    #                         msg += f"В округе слышны зомби.\n"
    #                 # TODO логгер
    #
    #                 detection = random.randint(1, 100)
    #                 max_d = self.get_max_detection(message.channel.id)
    #                 dc = player.stealth_chance(max_d)
    #                 detected = dc <= detection
    #                 if detected:
    #                     msg += f"Вас заметили!\n"
    #                     z = self.get_any_zombie(message.channel.id)
    #                     z.add_target(str(player.player_id))
    #                     player.set_enemy(z)
    #                     player.z_status = 'замечен'  # TODO
    #                     z.in_chase()
    #                     self.save_player(player)
    #                     self.save_zombie(z)
    #
    #     if player.z_status == 'замечен':
    #         if player.get_enemy_status() == 'в погоне':
    #             if actions['!стреляет'] or actions['!колдует']:
    #                 hit = random.randint(1, 20)
    #                 max_damage = player.max_range_damage() if actions['!стреляет'] else player.max_magic_damage() if actions['!колдует'] else 0
    #                 damage = max_damage * 2 if hit == 20 else int(hit / 20 * max_damage) if hit >= 10 else 0
    #                 embed.add_field(name="!стреляет", value=f"result = {damage}/15")
    #                 z: Zombie = player.zombie
    #                 msg += f"{z.name} ранен выстрелом и получил {z.take_damage(damage*2)} урона.\n"
    #                 if z.is_dead():
    #                     player.kill_enemy()
    #                     self.kill_zombie(z)
    #                     msg += f"{z.name} убит точным попаданием.\n"
    #                     self.save_player(player)
    #                     if player.z_status == 'не замечен':
    #                         if not self.is_channel_clean(message.channel.id):
    #                             msg += "Зомби потеряли вас из виду.\n"
    #                         else:
    #                             msg += f"Локация зачищена.\n"
    #                     else:
    #                         if not self.is_channel_clean(message.channel.id):
    #                             z: Zombie = self.get_any_zombie(message.channel.id)
    #                             player.set_enemy(z)
    #                             z.add_target(str(player.player_id))
    #                             msg += f"К вам движется следующий {player.zombie.name}.\n"
    #                             self.save_zombie(z)
    #                             self.save_player(player)
    #                         else:
    #                             msg += f"Локация зачищена.\n"
    #                 else:
    #                     embed.add_field(name="zombie", value=f"id = {z.id}")
    #                     self.save_zombie(z)
    #                     self.save_player(player)
    #
    #             if actions['!атакует']:
    #                 msg += f"Вы атаковали зомби.\n"
    #                 player.zombie.inc_priority(str(player.player_id))
    #                 player.zombie.in_combat()
    #
    #             if player.has_enemy() and player.zombie.status == 'в погоне':
    #                 async with message.channel.typing():
    #                     chase = random.randint(1, 100)
    #                     chased = chase <= player.get_chase_escape_chance()
    #                     embed.add_field(name="погоня", value=f"result = {chase}/80")
    #                     if not chased:
    #                         embed.add_field(name="zombie", value=f"id = {player.zombie.id}")
    #                         player.zombie.inc_priority(str(player.player_id))
    #                         player.zombie.in_combat()
    #                         self.save_player(player)
    #                         self.save_zombie(player.zombie)
    #                         msg += f"{player.zombie.name} вас догнал!\n"
    #                     else:
    #                         msg += f"К вам движется {player.zombie.name}.\n"
    #                         if not actions['!атакует']:
    #                             embed.set_footer(
    #                                 text=f"{player.name}: {player.status()}({player.hp}/{player.max_hp()}), {player.z_status}")
    #                             await self.log.send(embed=embed)
    #                             msg += f"Текущий статус персонажа {player.name}: {player.status()}."
    #                             await message.channel.send(msg, reference=message)
    #                             return
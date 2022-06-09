import random

from .character import Character
from .enemy import Enemy
from .enums import HealthStatus
from .location import Location

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

# Лечение
_msg_max_healed = "Вы максимально вылечили {name}. Теперь ему нужен отдых.\n"
_msg_healed = "Вы вылечили {name} на {heal} единиц.\n"
_msg_self_max_healed = "Вы максимально вылечили себя. Теперь вам нужен отдых.\n"
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
_msg_self_get_krit_damage = 'Разозлённый противник нанёс вам {damage} урона.\n'
_msg_def_get_damage = '{defender_name} получил {damage} урона вместо {name}.\n'

# Побег из боя или уклонение
_msg_run_away = "Вы убежали от {name}.\n"
_msg_get_invis = "{type} потеряли вас из виду.\n"
_msg_not_run = "Убежать не вышло.\n"
_msg_not_dodge = "Вы не смогли уклониться и получили {} урона.\n"
_msg_dodge = "Вы смогли уклониться и получили 0 урона.\n"


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

    def max_range_damage(self) -> int:
        return int(self._avatar.special.p * 3 + self._avatar.special.a * 2) if self._player_class == 'физ' else int(
            self._avatar.special.p * 2 + self._avatar.special.a)

    def max_magic_damage(self) -> int:
        return 0 if self._player_class != 'маг' else int(self._avatar.special.p * 2 + self._avatar.special.i * 2)

    def take_damage(self, damage: int) -> int:
        d = damage - self._avatar.special.e if damage > self._avatar.special.e else 0
        if self.hp - d < 0:
            self.hp = 0
        else:
            self.hp -= d
        return d

    def is_dead(self) -> bool:
        return True if self._hp <= 0 else False

# ======================================================================================================================

    def has_enemy(self) -> bool:
        if self._enemy is None:
            return False
        else:
            return True

    def rest(self):
        if self.hp < self.max_hp():
            self.hp += self._avatar.special.heal_points()

    def kill_enemy(self):
        if self._enemy is not None:
            self._enemy = None
            self._enemy_id = ""
            self._kills += 1
            self._e_status = 'не замечен' if random.randint(0, 100) > 50 else 'замечен'

    def drop_enemy(self):
        if self._enemy is not None:
            self._enemy = None
            self._enemy_id = ""

    def set_enemy(self, e: Enemy):
        self._e_status = 'замечен'
        self._enemy = e

    def get_chase_escape_chance(self) -> int:
        if not self.has_enemy():
            return 100
        else:
            return int(50 * (self._avatar.special.reaction() / self._enemy._avatar.special.reaction()))

    def is_priority_target(self) -> bool:
        if self._enemy is not None:
            return str(self._player_id) == self._enemy_id.get_priority_target_id()
        else:
            return False

    def detect_chance(self, enemy_stealth: int = 0) -> int:
        if enemy_stealth == 0:
            return 0
        else:
            return int(30 * (self._avatar.special.detection() / enemy_stealth))

    def stealth_chance(self, enemy_detection: int = 0) -> int:
        if enemy_detection == 0:
            return 100
        else:
            return int(30 * (enemy_detection / self._avatar.special.stealth()))

    def get_enemy_status(self) -> str:
        if self._enemy is not None:
            return self._enemy.get_combat_status()
        else:
            return "нет"

    def is_alive(self) -> str:
        if self._hp <= 0:
            return _msg_dead_player.format(mention=f"<@{self._player_id}>")
        else:
            return ""

    def look_around_action(self, location: Location) -> str:
        if self.has_enemy():
            return _msg_dont_look

        msg = location.look_around()
        msg += _msg_stat.format(name=self._name, status=self.status())

        return msg

    def heal_action(self, player2: Character | None = None):
        msg = ""
        if player2 is not None:
            if not player2.is_healable():
                msg += _msg_need_rest.format(name=player2.get_name())
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    player2.heal(player2.max_hp())
                    msg += _msg_max_healed.format(name=player2.get_name())
                else:
                    player2.heal(healing)
                    msg += _msg_healed[:-1].format(name=player2.get_name()) + _msg_stat.format(name=player2.get_name(),status=player2.status())
        else:
            if not self.is_healable():
                msg += _msg_self_need_rest
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    self.heal(self.max_hp())
                    msg += _msg_self_max_healed
                else:
                    healing = int(healing / 2)
                    self.heal(healing)
                    msg += _msg_self_healed[:-1].format(heal=healing) + _msg_stat.format(name=self.get_name(),status=self.status())

    def defend_action(self, player2: Character | None = None, enemy: Enemy | None = None) -> str:
        self._effects['defending'] = True

        if player2 is None or enemy is None:
            return _msg_defend_not_needed

        if enemy is not None and self.has_enemy():
            if self._enemy.get_id() != enemy.get_id():  # если есть враг и это не враг защищаемого персонажа
                self._enemy.del_target(self._player_id)
                self.set_enemy(enemy)
                enemy.inc_priority(self._player_id)
                return _msg_defend_player[:-1].format(defender_name=self.get_name(),name=player2.get_name()) + _msg_change_target.format(enemy_name=enemy.get_name(),name=self.get_name())
            else:
                self._enemy.inc_priority(self._player_id)
                return _msg_defend_player[:-1].format(defender_name=self.get_name(),name=player2.get_name()) + _msg_change_target.format(enemy_name=enemy.get_name(),name=self.get_name())

        elif enemy is not None:
            self.set_enemy(enemy)
            enemy.add_target(self._player_id)
            enemy.inc_priority(self._player_id)
            return _msg_defend_player[:-1].format(defender_name=self.get_name(),name=player2.get_name()) + _msg_change_target.format(enemy_name=enemy.get_name(),name=self.get_name())

        else:
            return _msg_defend_not_needed

    # def on_message(self, message: discord.Message):
    #
    #     if actions['!убегает']:
    #         if player.has_enemy():
    #             async with message.channel.typing():
    #                 escape = random.randint(0, 100)
    #                 embed.add_field(name="!убегает", value=f"result = {escape}")
    #                 if escape <= 80:
    #                     # player.zombie.heal()
    #
    #                     self.save_zombie(player.zombie)
    #                     player.drop_enemy()
    #                     msg += f"Вы убежали от зомби.\n"
    #                     if random.randint(0, 100) <= 75:
    #                         msg += "Зомби потеряли вас из виду.\n"
    #                         player.z_status = 'не замечен'
    #                     self.save_player(player)
    #                 else:
    #                     damage = random.randint(1, 20)
    #                     player.take_damage(damage)
    #                     self.save_player(player)
    #
    #                     msg += f"Убежать не вышло. {player.zombie.name} нанес удар на {damage} единиц\n"
    #         else:
    #             if player.z_status == 'замечен':
    #                 escape = random.randint(0, 100)
    #                 embed.add_field(name="!убегает", value=f"result = {escape}")
    #                 if escape <= 75:
    #                     msg += "Зомби потеряли вас из виду.\n"
    #                     player.z_status = 'не замечен'
    #                     self.save_player(player)
    #
    #     if actions['!помогает']:
    #         if player.has_enemy():
    #             msg += f"Нет возможности помочь, вас атакуют.\n"
    #         else:
    #             player2: Character = self.get_character_by_player_id(utils.get_user_from_message(message).id)
    #             player2.zombie = self.get_zombie(player2.zombie_id)
    #             if player2 is None or not player2.has_enemy():
    #                 msg += f"Ваша помощь не требуется.\n"
    #             else:
    #                 player.set_enemy(player2.zombie)
    #                 player2.zombie.add_target(str(player.player_id))
    #                 player.z_status = 'замечен'
    #                 if player.p_class == 'маг':
    #                     actions['!колдует'] = True
    #                 else:
    #                     actions['!стреляет'] = True
    #                 self.save_player(player)
    #                 self.save_zombie(player.zombie)
    #                 msg += f"Вы помогаете персонажу {player2.name}.\n"
    #
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
    #
    #     if actions['!атакует'] or actions['!стреляет'] or actions['!колдует']:
    #         async with message.channel.typing():
    #             if not player.has_enemy():
    #                 if self.is_channel_clean(message.channel.id):
    #                     msg += "Нет цели для атаки.\n"
    #                 else:
    #                     z = self.get_any_zombie(message.channel.id)
    #                     player.set_enemy(z)
    #                     z.add_target(str(player.player_id))
    #                     embed.add_field(name="zombie", value=f"id = {z.id}")
    #                     player.z_status = 'замечен'
    #                     player.zombie.in_combat()
    #                     self.save_player(player)
    #                     self.save_zombie(z)
    #
    #             crit_m = 2
    #
    #             if actions['!атакует']:
    #                 if not player.is_priority_target():
    #                     player.zombie.inc_priority(str(player.player_id))
    #                     msg += f"{player.zombie.name} сосредоточил внимание на {player.name}.\n"
    #                 max_damage = player.max_mille_damage()
    #
    #             if actions['!стреляет']:
    #                 max_damage = player.max_range_damage()
    #
    #             if actions['!колдует']:
    #                 max_damage = player.max_magic_damage()
    #
    #             if actions['!уклон']:
    #                 max_damage = int(max_damage / 2)
    #                 crit_m = 4
    #
    #             hit = random.randint(1, 20)
    #             z_hit = random.randint(1, 20)
    #             damage_player = max_damage * crit_m if hit == 20 else int(max_damage * (hit / 20)) if hit > 1 else 0
    #
    #             damage = player.zombie.max_damage() * 2 if hit == 1 else int(player.zombie.max_damage() * z_hit / 20)
    #
    #             if player.is_priority_target():
    #                 if actions['!защищает']:
    #                     damage = int(damage / 2)
    #                     msg += f'Вы получили {player.take_damage(damage)} урона.\n'
    #                     if player.is_dead():
    #                         msg += f"{player.name} без сознания.\n"
    #                     else:
    #                         msg += f'{player.zombie.name} получил {player.zombie.take_damage(damage_player)} урона.\n'
    #                         if player.zombie.is_dead():
    #                             msg += f'{player.zombie.name} убит.\n'
    #                             self.kill_zombie(player.zombie)
    #                             player.kill_enemy()
    #                 else:
    #                     if player.reaction() > player.zombie.reaction():
    #                         msg += f'{player.zombie.name} получил {player.zombie.take_damage(damage_player)} урона.\n'
    #                         if player.zombie.is_dead():
    #                             msg += f'{player.zombie.name} убит.\n'
    #                             self.kill_zombie(player.zombie)
    #                             player.kill_enemy()
    #                         else:
    #                             if actions['!уклон']:
    #                                 msg += 'Вы '
    #                                 dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
    #                                 if not dodged:
    #                                     msg += f'не смогли уклониться и получили {player.take_damage(damage)} урона.\n'
    #                                     if player.is_dead():
    #                                         msg += f"{player.name} без сознания.\n"
    #                                 else:
    #                                     msg += f'смогли уклониться и получили 0 урона.\n'
    #                             else:
    #                                 msg += f'Вы получили {player.take_damage(damage)} урона.\n'
    #                                 if player.is_dead():
    #                                     msg += f"{player.name} без сознания.\n"
    #                     else:
    #                         if actions['!уклон']:
    #                             msg += 'Вы '
    #                             dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
    #                             if not dodged:
    #                                 msg += f'не смогли уклониться и получили {player.take_damage(damage)} урона.\n'
    #                                 if player.is_dead():
    #                                     msg += f"{player.name} без сознания.\n"
    #                                 else:
    #                                     msg += f'{player.zombie.name} получил {player.zombie.take_damage(damage_player)} урона.\n'
    #                                     if player.zombie.is_dead():
    #                                         msg += f'{player.zombie.name} убит.\n'
    #                                         self.kill_zombie(player.zombie)
    #                                         player.kill_enemy()
    #
    #                             else:
    #                                 msg += f'смогли уклониться и получили 0 урона.\n'
    #                                 msg += f'{player.zombie.name} получил {player.zombie.take_damage(damage_player)} урона.\n'
    #                                 if player.zombie.is_dead():
    #                                     msg += f'{player.zombie.name} убит.\n'
    #                                     self.kill_zombie(player.zombie)
    #                                     player.kill_enemy()
    #                         else:
    #                             msg += f'Вы получили {player.take_damage(damage)} урона.\n'
    #                             if player.is_dead():
    #                                 msg += f"{player.name} без сознания.\n"
    #                             else:
    #                                 msg += f'{player.zombie.name} получил {player.zombie.take_damage(damage_player)} урона.\n'
    #                                 if player.zombie.is_dead():
    #                                     msg += f'{player.zombie.name} убит.\n'
    #                                     self.kill_zombie(player.zombie)
    #                                     player.kill_enemy()
    #                 if player.is_dead():
    #                     player.z_status = 'не замечен'
    #                     msg += "Зомби потеряли к вам интерес.\n"
    #                 else:
    #                     if player.z_status == 'не замечен':
    #                         if not self.is_channel_clean(message.channel.id):
    #                             msg += "Зомби потеряли вас из виду.\n"
    #                         else:
    #                             msg += f"Локация зачищена.\n"
    #                     else:
    #                         if not self.is_channel_clean(message.channel.id):
    #                             if not player.has_enemy():
    #                                 msg += f"К вам движется {player.zombie.name}.\n"
    #                         else:
    #                             msg += f"Локация зачищена.\n"
    #                 self.save_player(player)
    #                 if player.has_enemy():
    #                     self.save_zombie(player.zombie)
    #             else:
    #                 player2_id = player.zombie.get_priority_target_id()
    #                 player2 = self.get_character_by_player_id(int(player2_id))
    #                 player.zombie.take_damage(damage_player)
    #                 msg += f'{player.zombie.name} получил {player.zombie.take_damage(damage_player)} урона.\n'
    #                 if player.zombie.is_dead():
    #                     msg += f'{player.zombie.name} убит.\n'
    #                     self.kill_zombie(player.zombie)
    #                     player.kill_enemy()
    #                 else:
    #                     msg += f'{player2.name} получил вместо {player.name} {player2.take_damage(int(damage / 3))} урона.\n'
    #                     if player2.is_dead():
    #                         msg += f"{player2.name} без сознания.\n"
    #                         player2.drop_enemy()
    #                         player2.z_status = 'не замечен'
    #                         player.zombie.del_target(player2.id)
    #
    #                 self.save_player(player)
    #                 self.save_player(player2)
    #                 if player.has_enemy():
    #                     self.save_zombie(player.zombie)
    #     else:
    #         if player.has_enemy():
    #             if player.zombie.status == 'в бою':
    #                 async with message.channel.typing():
    #                     if player.is_priority_target():
    #                         z_hit = random.randint(1, 20)
    #                         damage = player.zombie.max_damage() * 2 if z_hit == 20 else int(
    #                             player.zombie.max_damage() * z_hit / 20)
    #
    #                         if actions['!защищает']:
    #                             damage = int(damage / 2)
    #                             msg += f'Вы получили {player.take_damage(damage)} урона.\n'
    #                             if player.is_dead():
    #                                 msg += f"{player.name} без сознания.\n"
    #
    #                         if actions['!уклон']:
    #                             msg += 'Вы '
    #                             dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
    #                             if not dodged:
    #                                 player.take_damage(damage)
    #                                 msg += f'не смогли уклониться и получили {damage} урона.\n'
    #                                 if player.is_dead():
    #                                     msg += f"{player.name} без сознания.\n"
    #                             else:
    #                                 msg += f'смогли уклониться и получили 0 урона.\n'
    #
    #                             self.save_player(player)
    #                             self.save_zombie(player.zombie)
    #                             embed.add_field(name="не !атакует", value=f"damage = {0 if dodged else damage}")
    #
    #     embed.set_footer(text=f"{player.name}: {player.status()}({player.hp}/{player.max_hp()}), {player.z_status}")
    #     await self.log.send(embed=embed)
    #
    #     if msg == "":
    #         return
    #     async with message.channel.typing():
    #         msg += f"Текущий статус персонажа {player.name}: {player.status()}."
    #         await message.channel.send(msg, reference=message)
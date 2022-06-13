import random

from .character import Character
from .enemy import Enemy
from .enums import HealthStatus
from .location import Location

# Проверки
_msg_dead_player = "{mention}, вы без сознания и не можете реагировать на происходящее пока вас не вылечили"
_msg_helped = "Вам помогли избавиться от противника.\n"
_msg_dont_look = "Вам некогда осматриваться по сторонам.\n"
_msg_need_rest = "Персонаж {name} максимально вылечен. Теперь {name} нужен отдых.\n"
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
_msg_lost_interest = "{name} потеряли к вам интерес.\n"

# Лечение
_msg_max_healed = "Вы максимально вылечили {name}. Теперь {name} нужен отдых.\n"
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
_msg_take_target = "{enemy_name} сосредоточил внимание на {name}.\n"
_msg_help = "{helper_name} помогает {name}.\n"
_msg_self_defending = "Вы защищаетесь.\n"

# Получение урона и текущий статус
_msg_stat = "Текущий статус персонажа {name}: {status}.\n"
_msg_fall = "{name} без сознания.\n"
_msg_self_get_damage = 'Вы получили {damage} урона.'
_msg_self_get_krit_damage = 'Разозлённый противник нанёс вам {damage} урона.\n'
_msg_def_get_damage = '{defender_name} получил {damage} урона вместо {name}.\n'

# Побег из боя или уклонение
_msg_run_away = "Вы убежали от {name}.\n"
_msg_get_invis = "Вас потеряли из виду.\n"
_msg_not_run = "Убежать не вышло.\n"
_msg_not_dodge = "Вы не смогли уклониться и получили {} урона.\n"
_msg_dodge = "Вы смогли уклониться и получили 0 урона.\n"


class Player(Character):
    _enemy: Enemy | None = None

    def __init__(self, data: dict, enemy: Enemy | None = None):
        super().__init__(data)
        self._player_id = data.get('player_id', 0)
        self._kills = data.get('kills', 0)
        self._enemy_id = data.get('enemy_id', "")
        if self._enemy_id == "":
            self._enemy_id = data.get('zombie', "")
        self._enemy = enemy
        self._e_status = data.get('e_status', "")  # TODO PlayerEnemyStatus("Замечен, Не замечен, и т.д.")
        # self._h_status = data.get('h_status', "")  # TODO PlayerHealthStatus("Здоров, ранен и т.д.")
        self._player_class = data.get('class', 'физ')

    def export(self) -> dict:
        d = super().export()
        d['enemy_id'] = self._enemy_id if self._enemy_id != "" else self._enemy.get_id() if self.has_enemy() else ""
        d['player_id'] = self._player_id
        d['kills'] = self._kills
        d['status'] = self.status()
        d['e_status'] = self._e_status
        return d

    # Получить дискордовый ID игрока
    def get_player_id(self) -> int:
        return self._player_id

    # Получить ID врага
    def get_enemy_id(self) -> str:
        return self._enemy_id

    # Уставить эффект
    def set_effect(self, key: str):
        self._effects[key] = True

    # Удалить эффект
    def remove_effect(self, key):
        self._effects.pop(key)

    def is_escaped(self) -> bool:
        return self._effects.get('escaped', False)

    # Максимальный урон дальней атаки
    def max_range_damage(self) -> int:
        return int(self._avatar.special.p * 3 + self._avatar.special.a * 2) if self._player_class == 'физ' else int(
            self._avatar.special.p * 2 + self._avatar.special.a)

    # Максимальный урон магической атаки
    def max_magic_damage(self) -> int:
        return 0 if self._player_class != 'маг' else int(self._avatar.special.p * 2 + self._avatar.special.i * 2)

    # # Получение урона игроком
    # def take_damage(self, damage: int) -> str:  # TODO
    #     d = damage - self._avatar.special.e if damage > self._avatar.special.e else 0
    #     msg = _msg_self_get_damage.format(damage=d)
    #     self._hp -= d
    #     if self._hp <= 0:
    #         msg += _msg_fall.format(name='Вы')
    #         self._hp = 0
    #     else:
    #         msg += '\n'
    #
    #     return msg

    # Проверка игрока на жизнедеятельность
    def is_dead(self) -> bool:
        return True if self._hp <= 0 else False

    def is_detected(self) -> bool:
        return self._e_status == 'замечен'

    # Проверка, если ли враг у игрока
    def has_enemy(self) -> bool:
        if self._enemy is None:
            return False
        else:
            return True

    # Пассивный отхил игрока
    def rest(self):
        if self._hp < self.max_hp():
            self._hp += self._avatar.special.heal_points()

    # Убийство моба игроком
    def kill_enemy(self):
        if self._enemy is not None:
            self._enemy = None
            self._enemy_id = ""
            self._kills += 1
            self._e_status = 'не замечен' if random.randint(0, 100) > 50 else 'замечен'

    # Удаление моба из врагов игрока. Сброс противника
    def drop_enemy(self):
        if self._enemy is not None:
            self._enemy.del_target(self._player_id)
            self._enemy = None
            self._enemy_id = ""
        if self._enemy_id != "":
            self._enemy_id = ""

    # Привязка моба к игроку
    def set_enemy(self, e: Enemy | None):
        if e is None:
            return
        self._e_status = 'замечен'
        self._enemy = e
        self._enemy.add_target(self._player_id)

    # Расчёт шансов на побег
    def get_chase_escape_chance(self) -> int:
        if not self.has_enemy():
            return 100
        else:
            return int(50 * (self._avatar.special.reaction() / self._enemy._avatar.special.reaction()))

    # Проверка, является ли игрок приоритетной целью
    def is_priority_target(self) -> bool:
        if self._enemy is not None:
            t_id = self._enemy.get_priority_target_id()
            return self._player_id == t_id
        else:
            return False

    # Расчёт шансов игрока обнаружить моба
    def detect_chance(self, enemy_stealth: int = 0) -> int:
        if enemy_stealth == 0:
            return 0
        else:
            return int(30 * (self._avatar.special.detection() / enemy_stealth))

    # Расчёт шансов игрока быть незамеченным мобом
    def stealth_chance(self, enemy_detection: int = 0) -> int:
        if enemy_detection == 0:
            return 100
        else:
            return int(30 * (enemy_detection / self._avatar.special.stealth()))

    # Узнать статус врага
    def get_enemy_status(self) -> str:
        if self._enemy is not None:
            return self._enemy.get_combat_status()
        else:
            return "нет"

    # Жив ли игрок
    def is_alive(self) -> str:
        if self._hp <= 0:
            return _msg_dead_player.format(mention=f"<@{self._player_id}>")
        else:
            return ""

    # Осмотр
    def look_around_action(self, location: Location) -> str:
        if self.has_enemy():
            return _msg_dont_look

        msg = location.look_around()
        msg += _msg_stat.format(name=self._name, status=self.status())

        return msg

    # Лечение
    def heal_action(self, player2: Character | None = None) -> str:
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
                    msg += _msg_healed[:-1].format(name=player2.get_name(), heal=healing) + _msg_stat.format(name=player2.get_name(), status=player2.status())
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
                    msg += _msg_self_healed[:-1].format(heal=healing) + _msg_stat.format(name=self.get_name(), status=self.status())
        return msg

    # Защита
    def defend_action(self, player2: Character | None = None, enemy: Enemy | None = None) -> str:
        self._effects['defending'] = True

        if player2 is None and enemy is None:
            return _msg_self_defending

        if player2 is None or enemy is None:
            return _msg_defend_not_needed

        if enemy is not None and self.has_enemy():
            if self._enemy.get_id() != enemy.get_id():  # если есть враг и это не враг защищаемого персонажа
                self._enemy.del_target(self._player_id)
                self.set_enemy(enemy)
                enemy.inc_priority(self._player_id)
                return _msg_defend_player[:-1].format(defender_name=self.get_name(), name=player2.get_name()) + " " + _msg_take_target.format(enemy_name=enemy.get_name(), name=self.get_name())
            else:
                self._enemy.inc_priority(self._player_id)
                return _msg_defend_player[:-1].format(defender_name=self.get_name(), name=player2.get_name()) + " " + _msg_take_target.format(enemy_name=enemy.get_name(), name=self.get_name())

        elif enemy is not None:
            self.set_enemy(enemy)
            enemy.inc_priority(self._player_id)
            return _msg_defend_player[:-1].format(defender_name=self.get_name(), name=player2.get_name()) + " " +_msg_take_target.format(enemy_name=enemy.get_name(), name=self.get_name())

        else:
            return _msg_defend_not_needed

    # Побег
    def run_away_action(self) -> str:
        if self.has_enemy():
            e = self._enemy.get_type().get('no', 'Монстра')
            escape = random.randint(0, 100)
            if escape <= 80:
                self._effects['escaped'] = True
                self._enemy.del_target(self._player_id)
                self.drop_enemy()
                msg = _msg_run_away.format(name=e)
                if random.randint(0, 100) <= 75:
                    msg += _msg_get_invis
                    self._e_status = 'не замечен'
                    return msg
            else:
                self._effects['not_escaped'] = True
                damage = self._enemy.deal_damage()
                return _msg_not_run + _msg_self_get_damage.format(damage=damage)
        else:
            if self._e_status == 'замечен':
                escape = random.randint(0, 100)
                if escape <= 75:
                    self._e_status = 'не замечен'
                    return _msg_get_invis
                else:
                    return _msg_yet_followed

    # Помощь
    def help_action(self, player2: Character | None = None, enemy: Enemy | None = None) -> str:
        if self.has_enemy():
            return _msg_cant_help
        else:
            if player2 is None or enemy is None:
                return _msg_help_not_needed
            else:
                enemy.add_target(self._player_id)
                self.set_enemy(enemy)
                self._e_status = 'замечен'
                if self._avatar.avatar_class == 'маг':
                    self._effects['magic_attack'] = True
                else:
                    self._effects['range_attack'] = True
                return _msg_help.format(helper_name=self.get_name(), name=player2.get_name())

    # Атака
    def attack_action(self) -> str:
        msg = ""
        if self._effects.get('mille_attack', False):
            self._effects.pop('mille_attack')
            if not self.is_priority_target():
                self._enemy.inc_priority(self._player_id)
                msg += _msg_take_target.format(enemy_name=self._enemy.get_name(), name=self._name)
            max_damage = self.max_mille_damage()

        elif self._effects.get('magic_attack', False):
            self._effects.pop('magic_attack')
            max_damage = self.max_magic_damage()

        elif self._effects.get('range_attack', False):
            self._effects.pop('range_attack')
            max_damage = self.max_range_damage()

        else:
            return ""

        crit_m = 2

        if self._effects.get('dodged', False):
            self._effects.pop('dodged')
            max_damage = int(max_damage / 2)
            crit_m = 4

        hit = random.randint(1, 20)
        damage_player = max_damage * crit_m if hit == 20 else int(max_damage * (hit / 20)) if hit > 1 else 0

        damage = self._enemy.deal_damage()

        if self.is_priority_target():
            if self._effects.get('defending', False):
                self._effects.pop('defending')
                damage = int(damage / 2)
                msg += self.take_damage(damage)
                if not self.is_dead():
                    msg += self._enemy.take_damage(damage_player)
                    if self._enemy.is_dead():
                        self.kill_enemy()
            else:
                if self._avatar.special.reaction() > self._enemy.get_reaction():
                    msg += self._enemy.take_damage(damage_player)
                    if self._enemy.is_dead():
                        self.kill_enemy()
                    else:
                        if self._effects.get('dodged', False):
                            self._effects.pop('dodged')
                            dodged = random.randint(1, 100) <= self.get_chase_escape_chance()
                            if not dodged:
                                msg += _msg_not_dodge
                                msg += self.take_damage(damage)
                            else:
                                msg += _msg_dodge
                        else:
                            msg += self.take_damage(damage)
                else:
                    if self._effects.get('dodged', False):
                        self._effects.pop('dodged')
                        dodged = random.randint(1, 100) <= self.get_chase_escape_chance()
                        if not dodged:
                            msg += self.take_damage(damage)
                            if self.is_dead():
                                msg += _msg_fall.format(name=self._name)
                            else:
                                msg += self._enemy.take_damage(damage_player)
                                if self._enemy.is_dead():
                                    msg += _msg_kill.format(name=self._enemy.get_name())
                                    self.kill_enemy()
                        else:
                            msg += _msg_dodge
                            msg += self._enemy.take_damage(damage_player)
                            if self._enemy.is_dead():
                                self.kill_enemy()
                    else:
                        msg += self.take_damage(damage)
                        if self.is_dead():
                            msg += _msg_fall.format(name='Вы')
                        else:
                            msg += self._enemy.take_damage(damage_player)
                            if self._enemy.is_dead():
                                self.kill_enemy()
            if self.is_dead():
                self._e_status = 'не замечен'
                msg += _msg_lost_interest.format(name=self._enemy.get_type())
        else:  # TODO
            msg += self._enemy.deal_damage_to_priority_target().format(name=self._name)
            msg += self._enemy.take_damage(damage_player)
            if self._enemy.is_dead():
                self.kill_enemy()

        return msg

    # Отсутствие активных действий игрока
    def idle_action(self) -> str:
        msg = ""
        if self.get_enemy_status() != 'в бою':
            return ""
        if self.has_enemy() and self.is_priority_target():
            damage = self._enemy.deal_damage()
            if self._effects.get('defending', False):
                damage = int(damage / 2)
                msg += self.take_damage(damage)

            elif self._effects.get('dodged', False):
                dodged = random.randint(1, 100) <= self.get_chase_escape_chance()
                if not dodged:
                    msg += _msg_not_dodge
                    msg += self.take_damage(damage)
                else:
                    msg += _msg_dodge
            else:
                msg += self.take_damage(damage)
        return msg

    # def on_message(self, message: discord.Message):
    #
    #
    #
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
import random

from pymongo.database import Database
from .repo import *
from .location import Location

# Ошибки сообщения игрока
msg_more_actions = "{mention}, вы не можете использовать более одного атакующего действия за пост."
msg_more_defs = "{mention}, вы не можете использовать более одного оборонительно действия за пост."

# Ошибки обработки сообщения
msg_no_id = "В событии нет ID персонажа"
msg_no_action = "В событии нет ни одного действия"

# Ошибки управления игрой
msg_player_not_find = "Персонажа нет в игре"
msg_player_in_game = "Персонаж уже в игре"

# Осмотр
msg_clean_location = "Вокруг нет ни следа противника.\n"
msg_count_enemy = "Осмотревшись, вы насчитали {count} {type}.\n"
msg_hear_enemy = "В округе слышны {type}.\n"
msg_detected = "Вас заметили. \n"
msg_change_loc = "Вы сменили локацию. Противник не последовал за вами. Можно отдышаться\n"

# Проверки
msg_dead_player = "{mention}, вы без сознания и не можете реагировать на происходящее пока вас не вылечили"
msg_helped = "Ваш предыдущий противник мёртв.\n"
msg_dont_look = "Вам некогда осматриваться по сторонам.\n"
msg_need_rest = "Персонаж {name} максимально вылечен. Теперь {name} нужен отдых.\n"
msg_self_need_rest = "Вы максимально вылечены. Теперь вам необходим отдых. \n"
msg_defend_not_needed = "Ваша защита не требуется.\n"
msg_cant_help = "Нет возможности помочь, вас атакуют.\n"
msg_help_not_needed = "Ваша помощь не требуется.\n"
msg_cleared_location = "Локация зачищена.\n"
msg_next_mob = "К вам движется следующий {name}.\n"
msg_caught = "Вас догнал {name}!\n"
msg_attacked = "Вас атакует {name}!\n"
msg_followed = "К вам движется {name}.\n"
msg_no_target = "Нет цели для атаки.\n"
msg_lost_interest = "{name} потеряли к вам интерес.\n"
msg_yet_followed = "Вас всё ещё преследуют.\n"

# Лечение
msg_max_healed = "Вы максимально вылечили {name}. Теперь {name} нужен отдых.\n"
msg_healed = "Вы вылечили {name} на {heal} единиц.\n"
msg_self_max_healed = "Вы максимально вылечили себя. Теперь вам нужен отдых.\n"
msg_self_healed = "Вы вылечили себя на {heal} единиц.\n"

# Атаки
msg_get_damage = "{name} получил {count} урона.\n"
msg_shoot = "{name} ранен выстрелом.\n"
msg_mage = "{name} ранен магией.\n"
msg_death_shoot = "{name} убит точным попаданием.\n"
msg_kill = "{name} убит.\n"
msg_attack = "Вы атаковали {name_r}.\n"

# Защита, помощь и внимание
msg_defend_player = "{defender_name} защищает {name}.\n"
msg_take_target = "{enemy_name} сосредоточил внимание на {name}.\n"
msg_help = "{helper_name} помогает {name}.\n"
msg_self_defending = "Вы защищаетесь.\n"

# Получение урона и текущий статус
msg_stat = "Текущий статус персонажа {name}: {status}.\n"
msg_fall = "{name} без сознания.\n"
msg_self_get_damage = 'Вы получили {damage} урона.'
msg_self_get_krit_damage = 'Разозлённый противник нанёс вам {damage} урона.\n'
msg_def_get_damage = '{defender_name} получил {damage} урона вместо {name}.\n'

# Побег из боя или уклонение
msg_run_away = "Вы убежали от {name}.\n"
msg_get_invis = "Вас потеряли из виду.\n"
msg_not_run = "Убежать не вышло.\n"
msg_not_dodge = "Вы не смогли уклониться. "
msg_dodge = "Вы смогли уклониться и получили 0 урона.\n"


class Game:
    player_repo: PlayerRepo
    mob_repo: MobRepo
    player_avatar_repo: PlayerAvatarRepo
    mob_avatar_repo: MobAvatarRepo

    def __init__(self, db: Database):
        self.player_avatar_repo = PlayerAvatarRepo(db['characters'])
        self.mob_avatar_repo = MobAvatarRepo(db['mobs'])
        self.player_repo = PlayerRepo(db['z_players'], self.player_avatar_repo)
        self.mob_repo = MobRepo(db['zombies'], self.mob_avatar_repo)

    # Обработка входящего сообщения
    def exec_event(self, event: dict) -> str:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy = self.mob_repo.get_by_id(player.get_enemy_id())
        msg = ""

        loc = Location(event.get('channel_id', 0), self.mob_repo.select(event.get('channel_id', 0)))

        if enemy is not None:
            enemy.set_priority_target(self.player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_enemy(enemy)
            if event.get('channel_id', 0) != enemy.get_channel():
                msg += msg_change_loc
                player.drop_enemy()
                self.player_repo.update(player)
                self.mob_repo.update(enemy)
                return msg

        if enemy is None and player.get_enemy_id() != "":
            msg += msg_helped
            player.drop_enemy()

        if player is None:
            return msg_no_id

        actions = event.get('actions', None)

        if actions is None:
            return msg_no_action

        player.rest()

        if actions.get('!защищает', False):
            player2 = self.player_repo.get_by_player_id(event.get('player2_id', 0))
            if player2 is not None:
                enemy2 = self.mob_repo.get_by_id(player2.get_enemy_id())
            else:
                enemy2 = None
            msg += self.defend_action(player2, enemy2)
            if player2 is not None:
                self.player_repo.update(player2)
            if enemy2 is not None:
                self.mob_repo.update(enemy2)

        if actions.get('!уклон', False):
            player.set_effect('dodged')

        if not (actions.get('!атакует', False) or
                actions.get('!стреляет', False) or
                actions.get('!колдует', False)) and player.has_enemy():
            msg += self.idle_action(player)

        if actions.get('!осмотр', False):
            if player.has_enemy():
                msg += msg_dont_look
            else:
                msg += loc.look_around()

        if actions.get('!лечит', False):
            player2 = self.player_repo.get_by_player_id(event.get('player2_id', 0))
            msg += self.heal_action(player, player2)
            if player2 is not None:
                self.player_repo.update(player2)

        if actions.get('!помогает', False):
            player2 = self.player_repo.get_by_player_id(event.get('player2_id', 0))
            enemy2 = self.mob_repo.get_by_id(player2.get_enemy_id())
            if enemy2 is not None:
                enemy2.set_priority_target(self.player_repo.get_by_player_id(enemy2.get_priority_target_id()))
            msg += self.help_action(player2, enemy2)
            msg += self.attack_action(player)
            if player2 is not None:
                self.player_repo.update(player2)
            if enemy2 is not None:
                self.mob_repo.update(enemy2)

        if actions.get('!убегает', False):
            msg += self.run_away_action(player)

        msg += self.passive_event(player, enemy, event.get('channel_id', 0))

        if actions.get('!атакует', False):
            if not player.has_enemy():
                enemy = loc.get_any_mob()
                if enemy is not None:
                    player.set_enemy(enemy)
                    enemy.set_priority_target(self.player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_effect('mille_attack')
            msg += self.attack_action(player)

        if actions.get('!стреляет', False):
            if not player.has_enemy():
                enemy = loc.get_any_mob()
                if enemy is not None:
                    player.set_enemy(enemy)
                    enemy.set_priority_target(self.player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_effect('range_attack')
            msg += self.attack_action(player)

        if actions.get('!колдует', False):
            if not player.has_enemy():
                enemy = loc.get_any_mob()
                if enemy is not None:
                    player.set_enemy(enemy)
                    enemy.set_priority_target(self.player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_effect('magic_attack')
            msg += self.attack_action(player)

        self.player_repo.update(player)
        if enemy is not None:
            self.mob_repo.update(enemy)
            if enemy.get_priority_target() is not None:
                self.player_repo.update(enemy.get_priority_target())

        self.mob_repo.delete_by_status()

        return msg

    def passive_event(self, player: Player | None = None, enemy: Enemy | None = None, location: int = 0) -> str:
        msg = ""
        if player.is_escaped():
            player.remove_effect('escaped')
            self.player_repo.update(player)
            return msg
        loc = Location(location, self.mob_repo.select(location))
        if not player.has_enemy():
            notion = random.randint(1, 100)
            if notion <= 50:
                m = loc.get_any_mob()
                msg += msg_hear_enemy.format(type=m.get_type().get('many', 'Монстры'))

            detection = random.randint(1, 100)

            max_d = loc.get_max_detection()
            dc = player.stealth_chance(max_d)
            detected = dc <= detection
            if detected:
                msg += msg_detected
                z = loc.get_any_mob()
                player.set_enemy(z)
                z.in_chase()
                msg += msg_followed.format(name=z.get_name())
                self.mob_repo.update(z)
        else:
            if player.get_enemy_status() == 'в погоне':
                chase = random.randint(1, 100)
                if chase < player.get_chase_escape_chance():
                    enemy.in_combat()
                    msg += msg_caught.format(name=enemy.get_name())
                    msg += player.take_damage(enemy.deal_damage())
                else:
                    msg += msg_yet_followed
            self.mob_repo.update(enemy)
        self.player_repo.update(player)
        return msg

    # Лечение
    def heal_action(self, player: Player, player2: Player | None = None) -> str:
        msg = ""
        if player2 is not None:
            if not player2.is_healable():
                msg += msg_need_rest.format(name=player2.get_name())
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    player2.heal(player2.max_hp())
                    msg += msg_max_healed.format(name=player2.get_name())
                else:
                    player2.heal(healing)
                    msg += msg_healed[:-1].format(name=player2.get_name(), heal=healing) + msg_stat.format(
                        name=player2.get_name(), status=player2.status())
        else:
            if not player.is_healable():
                msg += msg_self_need_rest
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    player.heal(player.max_hp())
                    msg += msg_self_max_healed
                else:
                    healing = int(healing / 2)
                    player.heal(healing)
                    msg += msg_self_healed[:-1].format(heal=healing) + msg_stat.format(name=player.get_name(),
                                                                                       status=player.status())
        return msg

    # Защита
    def defend_action(self, player: Player, player2: Player | None = None, enemy: Enemy | None = None) -> str:
        player.effects['defending'] = True

        if player2 is None and enemy is None:
            return msg_self_defending

        if player2 is None or enemy is None:
            return msg_defend_not_needed

        if enemy is not None and player.has_enemy():
            if player.enemy.get_id() != enemy.get_id():  # если есть враг и это не враг защищаемого персонажа
                player.enemy.del_target(player.player_id)
                player.set_enemy(enemy)
                enemy.inc_priority(player.player_id)
                return msg_defend_player[:-1].format(defender_name=player.get_name(),
                                                     name=player2.get_name()) + " " + msg_take_target.format(
                    enemy_name=enemy.get_name(), name=player.get_name())
            else:
                player.enemy.inc_priority(player.player_id)
                return msg_defend_player[:-1].format(defender_name=player.get_name(),
                                                     name=player2.get_name()) + " " + msg_take_target.format(
                    enemy_name=enemy.get_name(), name=player.get_name())

        elif enemy is not None:
            player.set_enemy(enemy)
            enemy.inc_priority(player.player_id)
            return msg_defend_player[:-1].format(defender_name=player.get_name(),
                                                 name=player2.get_name()) + " " + msg_take_target.format(
                enemy_name=enemy.get_name(), name=player.get_name())

        else:
            return msg_defend_not_needed

    # Побег
    def run_away_action(self, player: Player) -> str:
        if player.has_enemy():
            e = player.enemy.get_type().get('no', 'Монстра')
            escape = random.randint(0, 100)
            if escape <= 80:
                player.effects['escaped'] = True
                player.enemy.del_target(player.player_id)
                player.drop_enemy()
                msg = msg_run_away.format(name=e)
                # if random.randint(0, 100) <= 75:
                msg += msg_get_invis
                player.e_status = 'не замечен'
                return msg
            else:
                damage = player.enemy.deal_damage()
                return msg_not_run + msg_self_get_damage.format(damage=damage)
        else:
            if player.e_status == 'замечен':
                escape = random.randint(0, 100)
                if escape <= 75:
                    player.e_status = 'не замечен'
                    return msg_get_invis
                else:
                    return msg_yet_followed

    # Помощь
    def help_action(self, player: Player, player2: Character | None = None, enemy: Enemy | None = None) -> str:
        if player.has_enemy():
            return msg_cant_help
        else:
            if player2 is None or enemy is None:
                return msg_help_not_needed
            else:
                enemy.add_target(player.player_id)
                player.set_enemy(enemy)
                player.e_status = 'замечен'
                if player.avatar.avatar_class == 'маг':
                    player.effects['magic_attack'] = True
                else:
                    player.effects['range_attack'] = True
                return msg_help.format(helper_name=player.get_name(), name=player2.get_name())

    # Атака
    def attack_action(self, player: Player) -> str:
        msg = ""
        if player.enemy.get_combat_status() != 'в бою':
            player.enemy.in_combat()
        if player.effects.get('mille_attack', False):
            player.effects.pop('mille_attack')
            if not player.is_priority_target():
                player.enemy.inc_priority(player.player_id)
                msg += msg_take_target.format(enemy_name=player.enemy.get_name(), name=player.name)
            max_damage = player.max_mille_damage()

        elif player.effects.get('magic_attack', False):
            player.effects.pop('magic_attack')
            max_damage = player.max_magic_damage()

        elif player.effects.get('range_attack', False):
            player.effects.pop('range_attack')
            max_damage = player.max_range_damage()

        else:
            return ""

        crit_m = 2

        if player.effects.get('dodged', False):
            max_damage = int(max_damage / 2)
            crit_m = 4

        hit = random.randint(1, 20)
        damage_player = max_damage * crit_m if hit == 20 else int(max_damage * (hit / 20)) if hit > 1 else 0

        damage = player.enemy.deal_damage()

        if player.is_priority_target():
            if player.effects.get('defending', False):
                player.effects.pop('defending')
                damage = int(damage / 2)
                msg += player.take_damage(damage)
                if not player.is_dead():
                    msg += player.enemy.take_damage(damage_player)
                    if player.enemy.is_dead():
                        player.kill_enemy()
            else:
                if player.avatar.special.reaction() > player.enemy.get_reaction():
                    msg += player.enemy.take_damage(damage_player)
                    if player.enemy.is_dead():
                        player.kill_enemy()
                    else:
                        if player.effects.get('dodged', False):
                            player.effects.pop('dodged')
                            dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
                            if not dodged:
                                msg += msg_not_dodge
                                msg += player.take_damage(damage)
                            else:
                                msg += msg_dodge
                        else:
                            msg += player.take_damage(damage)
                else:
                    if player.effects.get('dodged', False):
                        player.effects.pop('dodged')
                        dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
                        if not dodged:
                            msg += msg_not_dodge
                            msg += player.take_damage(damage)
                            if player.is_dead():
                                msg += msg_fall.format(name=player.name)
                            else:
                                msg += player.enemy.take_damage(damage_player)
                                if player.enemy.is_dead():
                                    msg += msg_kill.format(name=player.enemy.get_name())
                                    player.kill_enemy()
                        else:
                            msg += msg_dodge
                            msg += player.enemy.take_damage(damage_player)
                            if player.enemy.is_dead():
                                player.kill_enemy()
                    else:
                        msg += player.take_damage(damage)
                        if player.is_dead():
                            msg += msg_fall.format(name='Вы')
                        else:
                            msg += player.enemy.take_damage(damage_player)
                            if player.enemy.is_dead():
                                player.kill_enemy()
            if player.is_dead():
                player.e_status = 'не замечен'
                msg += msg_lost_interest.format(name=player.enemy.get_type())
        else:  # TODO
            msg += player.enemy.deal_damage_to_priority_target().format(name=player.name)
            msg += player.enemy.take_damage(damage_player)
            if player.enemy.is_dead():
                player.kill_enemy()

        msg += msg_stat.format(name=player.name, status=player.status())
        return msg

    # Отсутствие активных действий игрока
    def idle_action(self, player: Player) -> str:
        msg = ""
        if player.get_enemy_status() != 'в бою':
            return ""
        if player.has_enemy() and player.is_priority_target():
            damage = player.enemy.deal_damage()
            if player.effects.get('defending', False):
                player.effects.pop('defending')
                damage = int(damage / 2)
                msg += player.take_damage(damage)

            elif player.effects.get('dodged', False):
                player.effects.pop('dodged')
                dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
                if not dodged:
                    msg += msg_not_dodge
                    msg += player.take_damage(damage)
                else:
                    msg += msg_dodge
            else:
                msg += player.take_damage(damage)

        msg += msg_stat.format(name=player.name, status=player.status())
        return msg

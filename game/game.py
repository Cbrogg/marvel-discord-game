import random

from pymongo.database import Database
from .repo import *
from .location import Location


class Messages:
    # Ошибки сообщения игрока
    msg_more_actions = "{mention}, вы не можете использовать более одного атакующего действия за пост."
    msg_more_defs = "{mention}, вы не можете использовать более одного оборонительно действия за пост."

    # Ошибки обработки сообщения
    msg_no_id = "В событии нет ID персонажа"
    msg_no_action = "В событии нет ни одного действия"
    msg_no_player = "Игрок неизвестен"
    msg_no_loc = "Локация неизвестна"

    # Ошибки управления игрой
    msg_player_not_find = "Персонажа нет в игре"
    msg_player_in_game = "Персонаж уже в игре"

    # Осмотр
    msg_clean_location = "Вокруг нет противников.\n"
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
    msg_escape_not_needed = "Вам не от кого бежать.\n"
    msg_self_defend_not_needed = "Вам не требуется защита.\n"
    msg_cant_help = "Нет возможности помочь, вас атакуют.\n"
    msg_help_not_needed = "Ваша помощь не требуется.\n"
    msg_cleared_location = "Локация зачищена.\n"
    msg_next_mob = "К вам движется следующий {name}.\n"
    msg_caught = "Вас догнал {name}!\n"
    msg_attacked = "Вас атакует {name}!\n"
    msg_followed = "К вам движется {name}.\n"
    msg_no_target = "Нет цели для атаки.\n"
    msg_lost_interest = "{enemy_name} потеряли интерес к {name}.\n"
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
    msg_defend_player = "Вы защищаете {name}.\n"
    msg_take_target = "{enemy_name} сосредоточил внимание на {name}.\n"
    msg_help = "Вы помогаете {name}.\n"
    msg_self_defending = "Вы защищаетесь.\n"

    # Получение урона и текущий статус
    msg_stat = "Текущий статус персонажа {name}: {status}.\n"
    msg_fall = "{name} без сознания.\n"
    msg_self_get_damage = 'Вы получили {damage} урона.'
    msg_self_get_krit_damage = 'Разозлённый противник нанёс вам {damage} урона.\n'
    msg_def_get_damage = '{defender_name} получил {damage} урона вместо {name}.\n'

    # Побег из боя или уклонение
    msg_run_away = "Вы субежали от противника.\n"
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
    def exec_event(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy = self.mob_repo.get_by_id(player.get_enemy_id())
        result = {}

        if player is None:
            return {"no_player_error": -1}
        else:
            result["player_name"] = player.name

        if enemy is None and player.get_enemy_id() != "":
            result['dropped'] = 1
            player.drop_enemy()

        actions = event.get('actions', None)

        if actions is None:
            return {"no_actions_error": -1}

        player.rest()

        if enemy is not None and enemy.get_reaction() > player.get_reaction():
            result.update(self.enemy_action(event))
            enemy_action_finished = True
        else:
            enemy_action_finished = False

        if actions.get('!защищает', False):
            result.update(self.defend_action(event))

        if actions.get('!уклон', False):
            player.set_effect('dodged')
            self.player_repo.update(player)

        if actions.get('!осмотр', False):
            if enemy is not None:
                result.update((("search", -1),))
            else:
                loc = Location(event.get('channel_id', 0), self.mob_repo.select(event.get('channel_id', 0)))
                result.update(loc.look_around())

        if actions.get('!лечит', False):
            result.update(self.heal_action(event))

        if actions.get('!помогает', False):
            result.update(self.assist_action(event))

        if actions.get('!убегает', False):
            result.update(self.run_away_action(event))

        result.update(self.passive_event(event))

        if actions.get('!атакует', False):
            player.set_effect('mille_attack')
            self.player_repo.update(player)
            result.update(self.attack_action(event))

        if actions.get('!стреляет', False):
            player.set_effect('range_attack')
            self.player_repo.update(player)
            result.update(self.attack_action(event))

        if actions.get('!колдует', False):
            player.set_effect('magic_attack')
            self.player_repo.update(player)
            result.update(self.attack_action(event))

        if enemy is not None and not enemy_action_finished:
            result.update(self.enemy_action(event))

        self.mob_repo.delete_by_status()

        return result

    def passive_event(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
        result = {}

        if player.is_escaped():
            player.remove_effect('escaped')
            self.player_repo.update(player)
            return result

        if enemy is None:
            loc = Location(event.get('channel_id', 0), self.mob_repo.select(event.get('channel_id', 0)))
            if loc is None:
                return {"no_loc_err": -1}

            detection = random.randint(1, 100)
            max_d = loc.get_max_detection()
            dc = player.stealth_chance(max_d)
            detected = dc <= detection
            result["detected"] = int(detected)

            if detected:
                m = loc.get_any_mob()
                result["enemy_name"] = m.name
                player.set_enemy(m)
                m.in_chase()
                self.mob_repo.update(m)
                self.player_repo.update(player)

        return result

    # Лечение
    def heal_action(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        player2: Player = self.player_repo.get_by_player_id(event.get('player2_id', 0))
        result = {}

        if player2 is not None:
            result["player2_name"] = player2.name
            if not player2.is_healable():
                result["heal_other"] = -1
                return result
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    player2.heal(player2.max_hp())
                else:
                    player2.heal(healing)
                self.player_repo.update(player2)
                result["heal_other"] = healing
                return result
        else:
            if not player.is_healable():
                result["heal_self"] = -1
                return result
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    player.heal(player.max_hp())
                else:
                    healing = int(healing / 2)
                    player.heal(healing)

                self.player_repo.update(player)
                result["heal_self"] = healing
                return result

    # Защита
    def defend_action(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        player2: Player | None = self.player_repo.get_by_player_id(event.get('player2_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        result = {}

        if player2 is None:
            if enemy is None:
                result["defend_self"] = 0
                return result
            else:
                result["enemy_name"] = enemy.name
                player.effects['defending'] = True
                self.player_repo.update(player)
                result["defend_self"] = 1
                return result
        else:
            result["player2_name"] = player2.name
            enemy2: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
            if enemy2 is None:
                result["defend_other"] = 0
                return result
            else:
                result["enemy2_name"] = enemy2.name
                player.effects['defending'] = True
                if enemy is not None:
                    if enemy.id != enemy2.id:
                        enemy.del_target(player.player_id)
                        player.set_enemy(enemy2)
                        self.mob_repo.update(enemy)
                player.set_enemy(enemy2)
                enemy2.inc_priority(player.player_id)

                self.player_repo.update(player)
                self.mob_repo.update(enemy2)

                result["defend_other"] = 1
                result["new_priority"] = 1
                return result

    # Побег
    def run_away_action(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
        result = {}

        if player is None:
            return {"no_player_error": -1}

        if enemy is not None:
            player.set_enemy(enemy)
            result["enemy_name"] = enemy.name
        else:
            result["escape"] = -1
            return result

        escape = random.randint(0, 100)
        e = escape > 20
        result["escape"] = int(e)
        if e:
            player.effects['escaped'] = True
            player.drop_enemy()
            player.e_status = 'не замечен'
            self.player_repo.update(player)
            self.mob_repo.update(enemy)

        return result

    # Помощь
    def assist_action(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
        result = {}

        if enemy is not None:
            result["enemy_name"] = enemy.name
            result["assist"] = -1
            return result

        player2: Player | None = self.player_repo.get_by_player_id(event.get('player2_id', 0))

        if player2 is None:
            result["assist"] = 0
            return result
        else:
            result["player2_name"] = player2.name
            enemy2: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
            if enemy2 is None:
                result["assist"] = 0
                return result
            else:
                result["enemy2_name"] = enemy2.name
                player.set_enemy(enemy2)
                player.e_status = 'замечен'
                if player.avatar.avatar_class == 'маг':
                    player.effects['magic_attack'] = True
                else:
                    player.effects['range_attack'] = True

                self.player_repo.update(player)
                self.mob_repo.update(enemy2)

                result["assist"] = 0
                return result

    # Атака
    def attack_action(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        if enemy is None:
            loc = Location(event.get('channel_id', 0), self.mob_repo.select(event.get('channel_id', 0)))
            if loc is None:
                return {"no_loc_error": -1}
            else:
                enemy = loc.get_any_mob()
                if enemy is not None:
                    enemy.set_priority_target(self.player_repo.get_by_player_id(enemy.get_priority_target_id()))
                    player.set_enemy(enemy)
                else:
                    return {"player_attack": -1}

        result = {}

        if player.effects.get('mille_attack', False):
            enemy.inc_priority(player.player_id)
            enemy.set_priority_target(player)
            result["new_priority"] = 1

        player_damage, player_dice = player.deal_damage()

        if enemy.is_in_chase():
            player_damage *= 2
            result["in_chase_damage"] = 1

        enemy.in_combat()

        damage = enemy.take_damage(player_damage)
        if enemy.is_dead():
            player.kill_enemy()

        result["player_attack"] = damage
        result["enemy_dead"] = int(enemy.is_dead())

        self.mob_repo.update(enemy)
        self.player_repo.update(player)

        result["player_status"] = player.status()

        return result

    def enemy_action(self, event: dict) -> dict:
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
        result = {}

        if enemy is None:
            return {}
        else:
            result["enemy_name"] = enemy.name

        if enemy.is_in_chase():
            chase = random.randint(0, 100)
            chased = chase > 30
            result["chased"] = int(chased)
            if not chased:
                enemy.in_combat()
            else:
                return result

        enemy_damage, enemy_dice = enemy.deal_damage()

        if player.player_id == enemy.get_priority_target_id():
            if player.effects.get('dodged', False):
                player.effects.pop('dodged')
                dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
                if dodged:
                    result["enemy_attack"] = 0
                    result["dodged"] = 1
                    return result
            self.player_repo.update(player)

            damage = player.take_damage(enemy_damage)

            result["enemy_attack"] = damage

            result["player_dead"] = int(player.is_dead())
            if player.is_dead():
                enemy.del_target(player.player_id)
                self.mob_repo.update(enemy)

            return result
        else:
            player2: Player | None = self.player_repo.get_by_player_id(enemy.get_priority_target_id())
            if player2 is None:
                return {"player2_error": -1}

            damage = player2.take_damage(int(enemy_damage/3))
            result["enemy_attack"] = damage
            result["priority_target"] = player2.name

            self.player_repo.update(player2)

            result["player_dead"] = int(player2.is_dead())
            if player2.is_dead():
                enemy.del_target(player2.player_id)
                self.mob_repo.update(enemy)
                result["player2_dead"] = int(player2.is_dead())

            result["player2_status"] = player2.status()

            return result

    def result_parser(self, result: dict) -> str:
        msg = ""

        # =========================
        for flag in result:
            match flag:
                case "no_player_error":
                    return Messages.msg_no_player

                case "no_loc_error":
                    return Messages.msg_no_loc

                case "detected":
                    match result["detected"]:
                        case 1:
                            msg += Messages.msg_followed.format(name=result.get("enemy_name"))

                case "heal_other":
                    match result["heal_other"]:
                        case -1:
                            msg += Messages.msg_need_rest.format(name=result["player2_name"])
                        case 20:
                            msg += Messages.msg_max_healed.format(name=result["player2_name"])
                        case _:
                            msg += Messages.msg_healed.format(name=result["player2_name"],heal=result["heal_other"])

                case "heal_self":
                    match result["heal_self"]:
                        case -1:
                            msg += Messages.msg_self_need_rest.format(name=result["player_name"])
                        case 20:
                            msg += Messages.msg_self_max_healed.format(name=result["player_name"])
                        case _:
                            msg += Messages.msg_self_healed.format(name=result["player_name"], heal=result["heal_self"])

                case "defend_self":
                    match result["defend_self"]:
                        case 0:
                            msg += Messages.msg_self_defend_not_needed
                        case 1:
                            msg += Messages.msg_self_defending

                case "defend_other":
                    match result["defend_other"]:
                        case 0:
                            msg += Messages.msg_defend_not_needed
                        case 1:
                            msg += Messages.msg_defend_player.format(name=result["player2_name"])

                case "escape":
                    match result["escape"]:
                        case -1:
                            msg += Messages.msg_escape_not_needed
                        case 0:
                            msg += Messages.msg_not_run
                        case 1:
                            return Messages.msg_run_away

                case "assist":
                    match result["assist"]:
                        case -1:
                            msg += Messages.msg_cant_help
                        case 0:
                            msg += Messages.msg_help_not_needed
                        case 1:
                            msg += Messages.msg_help.format(name=result["player2_name"])

                case "player_attack":
                    match result["player_attack"]:
                        case -1:
                            return Messages.msg_clean_location
                        case _:
                            msg += Messages.msg_get_damage.format(name=result["enemy_name"],count=result["player_attack"])
                            if result["enemy_dead"]:
                                msg += Messages.msg_kill.format(name=result["enemy_name"])

                case "enemy_attack":
                    match result["enemy_attack"]:
                        case _:
                            if result["priority_target"] is not None:
                                msg += Messages.msg_def_get_damage.format(defender_name=result["priority_target"], damage=result["enemy_attack"])
                                if result["player_dead"]:
                                    msg += Messages.msg_fall.format(name=result["priority_target"])
                                    msg += Messages.msg_lost_interest.format(enemy_name=result["enemy_name"], name=result["priority_target"])
                                else:
                                    msg += Messages.msg_stat.format(name=result["priority_target"], status=result["player2_status"])
                            else:
                                msg += Messages.msg_get_damage.format(name=result["enemy_name"], count=result["enemy_attack"])
                                if result["player_dead"]:
                                    msg += Messages.msg_fall.format(name="Вы")
                                    msg += Messages.msg_lost_interest.format(enemy_name=result["enemy_name"], name="вам")
                                else:
                                    msg += Messages.msg_stat.format(name=result["player_name"], status=result["player_status"])

                case "new_priority":
                    msg += Messages.msg_take_target.format(enemy_name=result["enemy_name"],name=result["priority_target"])

                case "chased":
                    match result["chased"]:
                        case 0:
                            return Messages.msg_caught.format(name=result["enemy_name"])
                        case 1:
                            msg += Messages.msg_followed.format(name=result["enemy_name"])

                case "search":
                    match result["search"]:
                        case -1:
                            msg += Messages.msg_dont_look
                        case 0:
                            msg += Messages.msg_clean_location
                        case 1:
                            msg += Messages.msg_hear_enemy.format(type=result["enemy_type"])
                        case 2:
                            if result["search_count"] > 10:
                                msg += Messages.msg_count_enemy.format(count="не меньше десятка ", type=result["enemy_type"])
                            else:
                                msg += Messages.msg_count_enemy.format(count="не больше десятка ", type=result["enemy_type"])
                        case 3:
                            msg += Messages.msg_count_enemy.format(count=result["search_count"], type=result["enemy_type"])

                case "player_name", "search_count", "enemy_type", "enemy_name":
                    msg += ""
                    break

                case _:
                    msg += f"unknown flag {flag}\n"

        # =========================

        return msg

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
    def exec_event(self, event: dict) -> dict:  # TODO
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy = self.mob_repo.get_by_id(player.get_enemy_id())

        if player is None:
            return {"player_error": -1}

        result = {}

        if enemy is None and player.get_enemy_id() != "":
            result['dropped'] = 1
            player.drop_enemy()

        actions = event.get('actions', None)

        if actions is None:
            return Messages.msg_no_action

        player.rest()

        if actions.get('!защищает', False):
            result.update((self.defend_action(event),))

        if actions.get('!уклон', False):
            player.set_effect('dodged')

        if actions.get('!осмотр', False):
            if player.has_enemy():
                result.update((("search", -1),))
            else:
                loc = Location(event.get('channel_id', 0), self.mob_repo.select(event.get('channel_id', 0)))
                result.update((loc.look_around(),))

        if actions.get('!лечит', False):
            result.update((self.heal_action(event),))

        if actions.get('!помогает', False):
            result.update((self.assist_action(event),))

        if actions.get('!убегает', False):
            result.update((self.run_away_action(event),))

        result.update((self.passive_event(event),))

        if actions.get('!атакует', False):
            player.set_effect('mille_attack')
            result.update((self.attack_action(event),))

        if actions.get('!стреляет', False):
            player.set_effect('range_attack')
            result.update((self.attack_action(event),))

        if actions.get('!колдует', False):
            player.set_effect('magic_attack')
            result.update((self.attack_action(event),))

        result.update((self.enemy_attack(event),))

        self.mob_repo.delete_by_status()

        return result

    def passive_event(self, event: dict) -> (str, int):
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        if player is None:
            return "no_player_error", -1

        if player.is_escaped():
            player.remove_effect('escaped')
            self.player_repo.update(player)
            return "passive", 0

        if enemy is None:
            loc = Location(event.get('channel_id', 0), self.mob_repo.select(event.get('channel_id', 0)))
            if loc is None:
                return "no_loc_err", -1

            detection = random.randint(1, 100)
            max_d = loc.get_max_detection()
            dc = player.stealth_chance(max_d)
            detected = dc <= detection

            if not detected:
                return "passive", 1
            else:
                m = loc.get_any_mob()
                player.set_enemy(m)
                m.in_chase()
                self.mob_repo.update(m)
                self.player_repo.update(player)
                return "passive", 2

    # Лечение
    def heal_action(self, event: dict) -> (str, int):
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        player2: Player = self.player_repo.get_by_player_id(event.get('player2_id', 0))

        if player is None:
            return "no_player_error", -1

        if player2 is not None:
            if not player2.is_healable():
                return "not_healable_other", -1
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    player2.heal(player2.max_hp())
                else:
                    player2.heal(healing)
                self.player_repo.update(player2)
                return "heal_other", healing
        else:
            if not player.is_healable():
                return "not_healable_self", -1
            else:
                healing = random.randint(1, 20)
                if healing == 20:
                    player.heal(player.max_hp())
                else:
                    healing = int(healing / 2)
                    player.heal(healing)

                self.player_repo.update(player)
                return "heal_self", healing

    # Защита
    def defend_action(self, event: dict) -> (str, int):
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        player2: Player | None = self.player_repo.get_by_player_id(event.get('player2_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        if player is None:
            return "no_player_error", -1

        if player2 is None:
            if enemy is None:
                return "defend_self", 0
            else:
                player.effects['defending'] = True
                self.player_repo.update(player)
                return "defend_self", 1
        else:
            enemy2: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
            if enemy2 is None:
                return "defend_other", 0
            else:
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

                return "defend_other", 1

    # Побег
    def run_away_action(self, event: dict) -> (str, int):
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        if player is None:
            return "no_player_error", -1

        if enemy is not None:
            player.set_enemy(enemy)

        if not player.has_enemy():
            return "escape", -1
        else:
            escape = random.randint(0, 100)
            if escape > 20:
                player.effects['escaped'] = True
                player.drop_enemy()
                player.e_status = 'не замечен'
                self.player_repo.update(player)
                self.mob_repo.update(enemy)

            return 'escape', escape

    # Помощь
    def assist_action(self, event: dict) -> (str, int):
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        if player is None:
            return "no_player_error", -1

        if enemy is not None:
            return "assist", -1

        player2: Player | None = self.player_repo.get_by_player_id(event.get('player2_id', 0))

        if player2 is None:
            return "assist", 0
        else:
            enemy2: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())
            if enemy2 is None:
                return "assist", 0
            else:
                player.set_enemy(enemy2)
                player.e_status = 'замечен'
                if player.avatar.avatar_class == 'маг':
                    player.effects['magic_attack'] = True
                else:
                    player.effects['range_attack'] = True

                self.player_repo.update(player)
                self.mob_repo.update(enemy2)

                return "assist", 1

    # Атака
    def attack_action(self, event: dict) -> (str, int):
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        if player is None:
            return "no_player_error", -1

        if enemy is None:
            loc = Location(event.get('channel_id', 0), self.mob_repo.select(event.get('channel_id', 0)))
            if loc is None:
                return "no_loc_error", -1
            else:
                enemy = loc.get_any_mob()
                if enemy is not None:
                    enemy.set_priority_target(self.player_repo.get_by_player_id(enemy.get_priority_target_id()))
                    player.set_enemy(enemy)
                else:
                    return "attack", -1

        if player.enemy.get_combat_status() != 'в бою':
            player.enemy.in_combat()

        if player.effects.get('mille_attack', False):
            enemy.inc_priority(player.player_id)
            enemy.set_priority_target(player)

        player_damage, player_dice = player.deal_damage()

        damage = enemy.take_damage(player_damage)
        if enemy.is_dead():
            player.kill_enemy()

        self.mob_repo.update(enemy)
        self.player_repo.update(player)
        return "attack", damage

    def enemy_attack(self, event: dict) -> (str, int):
        player: Player = self.player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy | None = self.mob_repo.get_by_id(player.get_enemy_id())

        if player is None:
            return "no_player_error", -1

        if enemy is None:
            return "no_enemy", 0

        enemy_damage, enemy_dice = enemy.deal_damage()

        if player.is_priority_target():
            if player.effects.get('dodged', False):
                player.effects.pop('dodged')
                dodged = random.randint(1, 100) <= player.get_chase_escape_chance()
                if dodged:
                    return "dodged", 1
            self.player_repo.update(player)

            if player.is_dead():
                enemy.del_target(player.player_id)
                self.mob_repo.update(enemy)

            return "player_damage", player.take_damage(enemy_damage)
        else:
            player2: Player | None = self.player_repo.get_by_player_id(enemy.get_priority_target_id())
            if player2 is None:
                return "player2_error", -1

            damage = player2.take_damage(int(enemy_damage/3))
            self.player_repo.update(player2)

            if player2.is_dead():
                enemy.del_target(player2.player_id)
                self.mob_repo.update(enemy)

            return "priority_damage", damage

    def enemy_chase(self, event: dict) -> (str, int):
        pass  # TODO

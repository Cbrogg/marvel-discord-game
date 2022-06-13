import random

from pymongo.database import Database
from .repo import *
from .location import Location

# Ошибки сообщения игрока
_msg_dead_player = "{mention}, вы без сознания и не можете реагировать на происходящее пока вас не вылечили"
_msg_more_actions = "{mention}, вы не можете использовать более одного атакующего действия за пост."
_msg_more_defs = "{mention}, вы не можете использовать более одного оборонительно действия за пост."

# Ошибки обработки сообщения
_msg_no_id = "В событии нет ID персонажа"
_msg_no_action = "В событии нет ни одного действия"

# Ошибки управления игрой
_msg_player_not_find = "Персонажа нет в игре"
_msg_player_in_game = "Персонаж уже в игре"

# Осмотр
_msg_clean_location = "Вокруг нет ни следа противника.\n"
_msg_count_enemy = "Осмотревшись, вы насчитали {count} {type}.\n"
_msg_hear_enemy = "В округе слышны {type}.\n"
_msg_detected = "Вас заметили. \n"
_msg_followed = "К вам движется {name}.\n"
_msg_yet_followed = "Вас всё ещё преследуют.\n"
_msg_caught = "Вас догнал {name}!\n"
_msg_helped = "Вам помогли избавиться от противника.\n"


class Game:
    _player_repo: PlayerRepo
    _mob_repo: MobRepo
    _player_avatar_repo: PlayerAvatarRepo
    _mob_avatar_repo: MobAvatarRepo

    def __init__(self, db: Database):
        self._player_avatar_repo = PlayerAvatarRepo(db['characters'])
        self._mob_avatar_repo = MobAvatarRepo(db['mobs'])
        self._player_repo = PlayerRepo(db['z_players'], self._player_avatar_repo)
        self._mob_repo = MobRepo(db['zombies'], self._mob_avatar_repo)

    # Обработка входящего сообщения
    def exec_event(self, event: dict) -> str:
        player: Player = self._player_repo.get_by_player_id(event.get('player_id', 0))
        enemy: Enemy = self._mob_repo.get_by_id(player.get_enemy_id())
        l = Location(event.get('channel_id', 0), self._mob_repo.select(event.get('channel_id', 0)))

        msg = ""

        if enemy is not None:
            enemy.set_priority_target(self._player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_enemy(enemy)
        if enemy is None and player.get_enemy_id() != "":
            msg += _msg_helped
            player.drop_enemy()
        if player is None:
            return _msg_no_id
        actions = event.get('actions', None)
        if actions is None:
            return _msg_no_action

        if actions.get('!защищает', False):
            player2 = self._player_repo.get_by_player_id(event.get('player2_id', 0))
            if player2 is not None:
                enemy2 = self._mob_repo.get_by_id(player2.get_enemy_id())
            else:
                enemy2 = None
            msg += player.defend_action(player2, enemy2)
            if player2 is not None:
                self._player_repo.update(player2)
            if enemy2 is not None:
                self._mob_repo.update(enemy2)

        if actions.get('!уклон', False):
            player.set_effect('dodged')

        if not (actions.get('!атакует', False) or actions.get('!стреляет', False) or actions.get('!колдует', False)) and player.has_enemy():
            msg += player.idle_action()

        if actions.get('!осмотр', False):
            msg += player.look_around_action(Location(event.get('channel_id', 0), self._mob_repo.select(event.get('channel_id', 0))))

        if actions.get('!лечит', False):
            player2 = self._player_repo.get_by_player_id(event.get('player2_id', 0))
            msg += player.heal_action(player2)
            if player2 is not None:
                self._player_repo.update(player2)

        if actions.get('!помогает', False):
            player2 = self._player_repo.get_by_player_id(event.get('player2_id', 0))
            enemy2 = self._mob_repo.get_by_id(player2.get_enemy_id())
            if enemy2 is not None:
                enemy2.set_priority_target(self._player_repo.get_by_player_id(enemy2.get_priority_target_id()))
            msg += player.help_action(player2, enemy2)
            msg += player.attack_action()
            if player2 is not None:
                self._player_repo.update(player2)
            if enemy2 is not None:
                self._mob_repo.update(enemy2)

        if actions.get('!убегает', False):
            msg += player.run_away_action()

        msg += self.passive_event(player, enemy, event.get('channel_id', 0))

        if actions.get('!атакует', False):
            if not player.has_enemy():
                enemy = l.get_any_mob()
                if enemy is not None:
                    player.set_enemy(enemy)
                    enemy.set_priority_target(self._player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_effect('mille_attack')
            msg += player.attack_action()

        if actions.get('!стреляет', False):
            if not player.has_enemy():
                enemy = l.get_any_mob()
                if enemy is not None:
                    player.set_enemy(enemy)
                    enemy.set_priority_target(self._player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_effect('range_attack')
            msg += player.attack_action()

        if actions.get('!колдует', False):
            if not player.has_enemy():
                enemy = l.get_any_mob()
                if enemy is not None:
                    player.set_enemy(enemy)
                    enemy.set_priority_target(self._player_repo.get_by_player_id(enemy.get_priority_target_id()))
            player.set_effect('magic_attack')
            msg += player.attack_action()

        self._player_repo.update(player)
        if enemy is not None:
            self._mob_repo.update(enemy)
            if enemy.get_priority_target() is not None:
                self._player_repo.update(enemy.get_priority_target())

        self._mob_repo.delete_by_status()

        return msg

    def passive_event(self, player: Player | None = None, enemy: Enemy | None = None, location: int = 0) -> str:
        msg = ""
        if player.is_escaped():
            player.remove_effect('escaped')
            return msg
        l = Location(location, self._mob_repo.select(location))
        if not player.has_enemy():
            notion = random.randint(1, 100)
            if notion <= 50:
                m = l.get_any_mob()
                msg += _msg_hear_enemy.format(type=m.get_type().get('many', 'Монстры'))

            detection = random.randint(1, 100)

            max_d = l.get_max_detection()
            dc = player.stealth_chance(max_d)
            detected = dc <= detection
            if detected:
                msg += _msg_detected
                z = l.get_any_mob()
                player.set_enemy(z)
                z.in_chase()
                msg += _msg_followed.format(name=z.get_name())
                self._mob_repo.update(z)
        else:
            if player.get_enemy_status() == 'в погоне':
                chase = random.randint(1, 100)
                if chase < player.get_chase_escape_chance():
                    enemy.in_combat()
                    msg += _msg_caught.format(name=enemy.get_name())
                    msg += player.take_damage(enemy.deal_damage())
                else:
                    msg += _msg_yet_followed
            self._mob_repo.update(enemy)
        self._player_repo.update(player)
        return msg
# ======================================================================================================================

    # def on_message(self, message: discord.Message):
    #     if message.author.bot:
    #         return
    #     if message.channel.id != 936972542286110780:
    #         if utils.not_logable(message):
    #             return
    #     else:
    #         if self.bot.user.id == settings['id']:
    #             return
    #
    #     self.log: discord.TextChannel = self.bot.get_guild(settings['guild_id']).get_channel(980839132358131752)
    #
    #     embed = discord.Embed(title=f"log {message.id}", url=message.jump_url, colour=message.author.color)
    #     embed.set_author(name=utils.get_user_nick(message.author), icon_url=message.author.avatar.url)
    #     embed.description = message.content
    #
    #     actions = parse_message(message)
    #
    #     if (actions['!атакует'] and actions['!стреляет']) or \
    #             (actions['!атакует'] and actions['!колдует']) or \
    #             (actions['!колдует'] and actions['!стреляет']):
    #         await message.delete()
    #         await message.channel.send(
    #             f"{message.author.mention}, вы не можете использовать более одного атакующего действия за пост.",
    #             delete_after=30)
    #         return
    #
    #     if actions['!уклон'] and actions['!защищает']:
    #         await message.delete()
    #         await message.channel.send(
    #             f"{message.author.mention}, вы не можете использовать более одного оборонительно действия за пост.",
    #             delete_after=30)
    #         return
    #
    #     player: Character = self.get_character_by_player_id(message.author.id)
    #
    #     if player is None:
    #         return
    #
    #     msg = ""
    #
    #     if player.zombie_id != "":
    #         player.zombie = self.get_zombie(player.zombie_id)
    #         if not player.has_enemy():
    #             player.zombie_id = ""
    #             player.z_status = "не замечен"
    #             actions['!осмотр'] = True
    #             msg += f"Вам помогли избавиться от зомби.\n"
    #
    #     if player.hp <= 0:
    #         await message.delete()
    #         await message.channel.send(
    #             f"{message.author.mention}, вы без сознания и не можете реагировать на происходящее пока вас не вылечили",
    #             delete_after=30)
    #         return
    #
    #     player.rest()
    #     self.save_player(player)
    #
    #     if actions['!осмотр']:
    #         async with message.channel.typing():
    #             if not player.has_enemy():
    #                 if self.is_channel_clean(message.channel.id):
    #                     msg += "Вокруг нет ни следа зомби.\n"
    #                     msg += f"Текущий статус персонажа {player.name}: {player.status()}."
    #                     await message.channel.send(msg, reference=message)
    #                 else:
    #                     r = random.randint(1, 20)
    #                     embed.add_field(name="!осмотр", value=f"result = {r}")
    #                     if r == 20:
    #                         msg += f"Осмотревшись, вы насчитали {self.zombies.count_documents({'channel': message.channel.id})} зомби.\n"
    #                     elif 10 <= r < 20:
    #                         c = 'меньше' if self.zombies.count_documents(
    #                             {'channel': message.channel.id}) < 10 else 'больше'
    #                         msg += f"Осмотревшись, вы насчитали {c} десятка зомби.\n"
    #                     elif 1 < r < 10:
    #                         msg += "Осмотревшись, вы не увидели зомби, но они где-то рядом.\n"
    #                     else:
    #                         msg += "Вокруг нет ни следа зомби.\n"
    #             else:
    #                 msg += "Вам некогда осматриваться по сторонам.\n"
    #
    #     if actions['!лечит']:
    #         async with message.channel.typing():
    #             if len(message.mentions) > 0:
    #                 player2 = self.get_character_by_player_id(utils.get_user_from_message(message).id)
    #                 if player2.hp >= int(player2.max_hp() * 4 / 5):
    #                     msg += f"Персонаж {player2.name} максимально вылечен. Теперь ему нужен отдых. \n"
    #                 else:
    #                     healing = random.randint(1, 20)
    #                     embed.add_field(name="!лечит", value=f"result = {healing}")
    #                     if healing == 20:
    #                         player2.heal(player2.max_hp())
    #                         msg += f"Вы максимально вылечили {utils.get_user_nick(message.mentions[0])}.\n Текущий статус персонажа {player2.name}: {player2.status()}.\n"
    #
    #                     else:
    #                         player2.heal(healing)
    #                         msg += f"Вы вылечили {utils.get_user_nick(message.mentions[0])} на {healing} единиц. Текущий статус персонажа {player2.name}: {player2.status()}.\n"
    #
    #                     self.save_player(player2)
    #             else:
    #                 if player.hp >= int(player.max_hp() * 4 / 5):
    #                     msg += f"Вы максимально вылечены. Теперь вам необходим отдых. \n"
    #                 else:
    #                     healing = random.randint(1, 20)
    #                     embed.add_field(name="!лечит", value=f"result = {healing}")
    #                     if healing == 20:
    #                         player.heal(player.max_hp())
    #                         msg += f"Вы максимально вылечили себя.\n"
    #                     else:
    #                         healing = int(healing / 2)
    #                         player.heal(healing)
    #                         msg += f"Вы вылечили себя на {healing} единиц.\n"
    #
    #                     self.save_player(player)
    #
    #             if self.is_channel_clean(message.channel.id):
    #                 embed.set_footer(
    #                     text=f"{player.name}: {player.status()}({player.hp}/{player.max_hp()}), {player.z_status}")
    #                 await self.log.send(embed=embed)
    #                 msg += f"Текущий статус персонажа {player.name}: {player.status()}."
    #                 await message.channel.send(msg, reference=message)
    #                 return
    #
    #     if self.is_channel_clean(message.channel.id):
    #         return
    #
    #     if actions['!защищает']:
    #         if len(message.mentions) > 0:
    #             player2 = self.get_character_by_player_id(utils.get_user_from_message(message).id)
    #             player2.zombie = self.get_zombie(player2.zombie_id)
    #             if player2 is None or not player2.has_enemy():
    #                 msg += f"Ваша защита не требуется.\n"
    #             else:
    #                 if player.has_enemy():
    #                     if player.zombie.id != player2.zombie.id:  # если есть враг и это не враг защищаемого персонажа
    #                         player.zombie.del_target(str(player.player_id))
    #                         self.save_zombie(player.zombie)
    #                         player.zombie = player2.zombie
    #                         player.zombie.inc_priority(str(player.player_id))
    #                         msg += f"{player.name} защищает {player2.name}. {player.zombie.name} переключил внимание на {player.name}.\n"
    #                         self.save_player(player)
    #                         self.save_zombie(player.zombie)
    #                     else:
    #                         player.zombie.inc_priority(str(player.player_id))
    #                         msg += f"{player.name} защищает {player2.name}. {player.zombie.name} переключил внимание на {player.name}.\n"
    #                         self.save_player(player)
    #                         self.save_zombie(player.zombie)
    #                 else:
    #                     player.zombie = player2.zombie
    #                     player.zombie.add_target(str(player.player_id))
    #                     player.zombie.inc_priority(str(player.player_id))
    #                     msg += f"{player.name} защищает {player2.name}. {player.zombie.name} переключил внимание на {player.name}.\n"
    #                     self.save_player(player)
    #                     self.save_zombie(player.zombie)
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
    #
    # @app_commands.command(name="добавить", description="Добавить в игру")
    # @app_commands.rename(member="игрок", role="роль")
    # async def invite_to_game(self, interaction: discord.Interaction,
    #                          member: Optional[discord.Member] = None,
    #                          role: Optional[discord.Role] = None):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #     if member is None and role is None:
    #         await interaction.followup.send("Ошибка. Необходимо указать игрока или роль.",
    #                                         ephemeral=debug_flag)
    #         return
    #
    #     if member is not None:
    #         pl = self.characters.find_one({'player_id': member.id, 'archived': False})
    #         if pl is None:
    #             await interaction.followup.send("Ошибка. Указанный игрок не имеет активного персонажа.",
    #                                             ephemeral=debug_flag)
    #             return
    #
    #         self.players.insert_one({'character_id': pl['_id'],
    #                                  'name': utils.get_user_nick(member),
    #                                  'hp': int(pow(100, (1 + (pl['special']['e'] / 30))) / 2 + pl['special']['s']),
    #                                  'status': 'здоров',
    #                                  'kills': 0,
    #                                  'zombie': "",
    #                                  'z_status': 'не замечен'})
    #
    #     if role is not None:
    #         for player in role.members:
    #             pl = self.characters.find_one({'player_id': player.id, 'archived': False})
    #             if pl is None:
    #                 continue
    #             self.players.insert_one({'character_id': pl['_id'],
    #                                      'name': utils.get_user_nick(player),
    #                                      'hp': int(pow(100, (1 + (pl['special']['e'] / 30))) / 2 + pl['special']['s']),
    #                                      'status': 'здоров',
    #                                      'kills': 0,
    #                                      'zombie': "",
    #                                      'z_status': 'не замечен'})
    #
    #     await interaction.followup.send("Готово", ephemeral=debug_flag)
    #     return
    #
    # @app_commands.command(name="создать", description="Создать игрока")
    # @app_commands.rename(member="игрок", s='сила', p='восприятие', e='выносливость', c='харизма', i='интеллект',
    #                      a='ловкость', l='удача', )
    # async def create_character(self, interaction: discord.Interaction,
    #                            member: discord.Member, s: str, p: str, e: str, c: str, i: str, a: str, l: str,
    #                            p_class: Optional[Literal['физ', 'маг']] = 'физ'):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     self.characters.update_one({'player_id': member.id, 'archived': False}, {'$set': {'archived': True}})
    #
    #     self.characters.insert_one({'player_id': member.id,
    #                                 'archived': False,
    #                                 'name': utils.get_user_nick(member),
    #                                 'special': {
    #                                     's': int(s),
    #                                     'p': int(p),
    #                                     'e': int(e),
    #                                     'c': int(c),
    #                                     'i': int(i),
    #                                     'a': int(a),
    #                                     'l': int(l)
    #                                 },
    #                                 'class': p_class,
    #                                 'Навыки': {
    #                                     'Легкое оружие': {
    #                                         'base': 35 + int(a) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Тяжёлое оружие': {
    #                                         'base': 10 + int(a) + int(int(l) / 4),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Энергетическое оружие': {
    #                                         'base': 10 + int(a) + int(int(l) / 3),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Без оружия': {
    #                                         'base': 40 + int((int(s) + int(a)) / 2) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Холодное оружие': {
    #                                         'base': 30 + int((int(s) + int(a)) / 2) + int(int(l) / 3),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Метание': {
    #                                         'base': 30 + int(a) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Красноречие': {
    #                                         'base': 25 + int(c) * 2 + int(int(l) / 3),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Бартер': {
    #                                         'base': 20 + int(c) * 2 + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Азартные игры': {
    #                                         'base': 20 + int(c) * 2 + int(l) * 3,
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Натуралист': {
    #                                         'base': 10 + int((int(e) + int(i)) / 2) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Скрытность': {
    #                                         'base': 25 + int(a) + int(int(l) / 3),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Внимание': {
    #                                         'base': 30 + int(p) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Взлом': {
    #                                         'base': 20 + int((int(i) + int(a)) / 2) + int(int(l) / 3),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Кража': {
    #                                         'base': 20 + int(a) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Ловушки': {
    #                                         'base': 20 + int((int(i) + int(a)) / 2) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Первая помощь': {
    #                                         'base': 30 + int((int(e) + int(i)) / 2) + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Доктор': {
    #                                         'base': 15 + int((int(p) + int(i)) / 2) + int(int(l) / 4),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Наука': {
    #                                         'base': 25 + int(i) * 2 + int(int(l) / 4),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Ремонт': {
    #                                         'base': 20 + int(i) + int(int(l) / 4),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Пилот': {
    #                                         'base': 15 + (int(p) + int(a)) * 2 + int(int(l) / 3),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     },
    #                                     'Магия': {
    #                                         'base': 10 + (int(p) + int(i)) * 2 + int(int(l) / 2),
    #                                         'exp': 0,
    #                                         'mod': 0
    #                                     }
    #                                 }
    #                                 }
    #                                )
    #     await interaction.followup.send("Готово.", ephemeral=debug_flag)
    #
    # @app_commands.command(name="перегрузить", description="Перегрузить игру для отдельного игрока")
    # @app_commands.rename(member="игрок")
    # async def reboot_player(self, interaction: discord.Interaction,
    #                         member: discord.Member):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     pl = self.players.find_one({'_id': member.id})
    #     if pl is None:
    #         await interaction.followup.send("Ошибка. Указанный игрок не в игре.", ephemeral=debug_flag)
    #         return
    #
    #     z: Zombie = self.get_zombie(pl['zombie'])
    #     if z is not None:
    #         z.heal()
    #         self.save_zombie(z)
    #     pl['zombie'] = ""
    #     pl['z_status'] = "не замечен"
    #     self.players.find_one_and_delete({'_id': member.id})
    #     self.players.insert_one(pl)
    #     await interaction.followup.send("Готово", ephemeral=debug_flag)
    #     return
    #
    # @app_commands.command(name="исключить", description="Завершить игру для отдельного игрока")
    # @app_commands.rename(member="игрок")
    # async def kick_player(self, interaction: discord.Interaction,
    #                       member: discord.Member):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     pl = self.players.find_one({'_id': member.id})
    #     if pl is None:
    #         await interaction.followup.send("Ошибка. Указанный игрок не в игре.", ephemeral=debug_flag)
    #         return
    #
    #     pl = self.players.find_one_and_delete({'_id': member.id})
    #
    #     await interaction.followup.send("Готово", ephemeral=debug_flag)
    #     return
    #
    # @app_commands.command(name="статус", description="Проверить статус всех игроков")
    # async def status(self, interaction: discord.Interaction):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     count = self.players.count_documents({})
    #     if count == 0:
    #         await interaction.followup.send("Ошибка. Нет игроков в игре.", ephemeral=debug_flag)
    #         return
    #
    #     pl = self.players.find({})
    #     msg = ""
    #     for player in pl:
    #         msg += f"{player['name']}: Статус-{player['status']}({player['hp']}), убийств-{player['kills']}\n"
    #
    #     await interaction.followup.send(msg, ephemeral=debug_flag)
    #     return
    #
    # @zombie_group.command(name="спавн", description="Спавн противников на локации")
    # @app_commands.rename(channel="канал", count="сколько", mob_type="тип")
    # async def spawn(self, interaction: discord.Interaction,
    #                 channel: Optional[discord.TextChannel] = None,
    #                 count: Optional[int] = 0,
    #                 mob_type: Optional[Literal['Ходок', 'Бегун', 'Толстяк', 'Отродье', 'Некромант', 'Все']] = 'Все'):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     if channel is None:
    #         channel = interaction.channel
    #
    #     if count == 0:
    #         count = random.randint(10, 100)
    #
    #     z = []
    #
    #     if mob_type == 'Все':
    #         m = {}
    #         types = self.mobs.find({})
    #         for mob in types:
    #             m[mob['name']] = mob
    #
    #         for i in range(count):
    #             rand = random.randint(1, 100)
    #             if rand <= int(m['Отродье']['rate']):
    #                 z.append(Zombie(m['Отродье'], channel.id).export())
    #             elif rand <= int(m['Толстяк']['rate']):
    #                 z.append(Zombie(m['Толстяк'], channel.id).export())
    #             elif rand <= int(m['Бегун']['rate']):
    #                 z.append(Zombie(m['Бегун'], channel.id).export())
    #             else:
    #                 z.append(Zombie(m['Ходок'], channel.id).export())
    #     else:
    #         types = self.mobs.find_one({'name': mob_type})
    #         for i in range(count):
    #             z.append(Zombie(types, channel.id).export())
    #
    #     self.zombies.insert_many(z)
    #
    #     await interaction.followup.send(f'В локации "{channel.name}" появились {count} зомби.',
    #                                     ephemeral=debug_flag)
    #     return
    #
    # @app_commands.command(name="ситуация", description="Проверить статус локаций")
    # @app_commands.rename(channel="канал", details="подробно")
    # async def status_location(self, interaction: discord.Interaction,
    #                           channel: Optional[discord.TextChannel] = None,
    #                           details: Optional[Literal['да', 'нет']] = 'нет'):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     if self.zombies.count_documents({}) == 0:
    #         await interaction.followup.send("Противников не обнаружено.", ephemeral=debug_flag)
    #         return
    #
    #     msg = ""
    #     if channel is None:
    #         for channel in interaction.guild.text_channels:
    #             total = self.zombies.count_documents({'channel': channel.id})
    #             if total > 0:
    #                 msg += f"{channel.name}: {total} зомби"
    #                 if details == 'нет':
    #                     msg += '\n'
    #                 else:
    #                     h_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Ходок'})
    #                     b_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Бегун'})
    #                     t_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Толстяк'})
    #                     o_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Отродье'})
    #                     n_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Некромант'})
    #                     msg += f" (Х:{h_ch_count}/Б:{b_ch_count}/Т:{t_ch_count}/О:{o_ch_count}/Н:{n_ch_count}).\n"
    #
    #         await interaction.followup.send(msg, ephemeral=debug_flag)
    #         return
    #
    #     else:
    #         count = self.zombies.count_documents({'channel': channel.id})
    #         if count > 0:
    #             msg += f'В локации "{channel.name}" находятся {count} зомби.'
    #             if details == 'нет':
    #                 msg += '\n'
    #             else:
    #                 h_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Ходок'})
    #                 b_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Бегун'})
    #                 t_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Толстяк'})
    #                 o_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Отродье'})
    #                 n_ch_count = self.zombies.count_documents({'channel': channel.id, 'name': 'Некромант'})
    #                 msg += f" (Х:{h_ch_count}/Б:{b_ch_count}/Т:{t_ch_count}/О:{o_ch_count}/Н:{n_ch_count}).\n"
    #         else:
    #             await interaction.followup.send("Противников не обнаружено.", ephemeral=debug_flag)
    #             return
    #
    #         await interaction.followup.send(msg, ephemeral=debug_flag)
    #         return
    #
    # @app_commands.command(name="вылечить", description="Вылечить всех зомби")
    # @app_commands.rename(channel="канал")
    # async def heal_zombie(self, interaction: discord.Interaction,
    #                           channel: Optional[discord.TextChannel] = None):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     if self.zombies.count_documents({}) == 0:
    #         await interaction.followup.send("Противников не обнаружено.", ephemeral=debug_flag)
    #         return
    #
    #     msg = ""
    #     if channel is None:
    #         for channel in interaction.guild.text_channels:
    #             total = self.zombies.count_documents({'channel': channel.id})
    #             if total > 0:
    #                 zombies = self.zombies.find({'channel': channel.id})
    #                 for z in zombies:
    #                     z.heal()
    #                     self.save_zombie(z)
    #                 msg += f"{channel.name}: {total} зомби вылечено"
    #
    #         await interaction.followup.send(msg, ephemeral=debug_flag)
    #         return
    #
    #     else:
    #         count = self.zombies.count_documents({'channel': channel.id})
    #         if count > 0:
    #             zombies = self.zombies.find({'channel': channel.id})
    #             for z in zombies:
    #                 z.heal()
    #                 self.save_zombie(z)
    #             msg += f"{channel.name}: {count} зомби вылечено"
    #
    #         await interaction.followup.send(msg, ephemeral=debug_flag)
    #         return
    #
    # @zombie_group.command(name="удалить", description="Удалить противников на локации")
    # @app_commands.rename(channel="канал")
    # async def clean(self, interaction: discord.Interaction,
    #                 channel: Optional[discord.TextChannel] = None):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     if channel is None:
    #         channel = interaction.channel
    #
    #     count = self.zombies.count_documents({'channel': channel.id})
    #
    #     self.zombies.delete_many({'channel': channel.id})
    #
    #     await interaction.followup.send(f'В локации "{channel.name}" удалило {count} зомби.', ephemeral=debug_flag)
    #     return
    #
    # @zombie_group.command(name="создать", description="Создать новый вид зомби")
    # @app_commands.rename(name="название", s='сила', p='восприятие', e='выносливость', c='харизма', i='интеллект',
    #                      a='ловкость', l='удача', rate='вероятность')
    # async def create_zombie(self, interaction: discord.Interaction,
    #                         name: str, s: str, p: str, e: str, c: str, i: str, a: str, l: str, rate: str):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     self.mobs.insert_one({'name': name,
    #                           'rate': float(rate),
    #                           'special': {
    #                               's': int(s),
    #                               'p': int(p),
    #                               'e': int(e),
    #                               'c': int(c),
    #                               'i': int(i),
    #                               'a': int(a),
    #                               'l': int(l)
    #                           }
    #                           }
    #                          )
    #     await interaction.followup.send("Готово.", ephemeral=debug_flag)
    #
    # @app_commands.command(name="задать", description="Задать параметры игрока")
    # @app_commands.rename(member="игрок", hp="здоровье", status="статус", kills="убийств")
    # async def set(self, interaction: discord.Interaction,
    #               member: discord.Member,
    #               hp: Optional[str] = None,
    #               status: Optional[str] = None,
    #               kills: Optional[str] = None):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #
    #     c = self.characters.find_one({'player_id': member.id, 'archived': False})
    #     if c is None:
    #         await interaction.followup.send("Ошибка. Игрок не имеет активного персонажа.")
    #         return
    #
    #     m = self.players.find_one({'character_id': c['_id']})
    #     if m is None:
    #         await interaction.followup.send("Ошибка. Персонаж не в игре.")
    #         return
    #
    #     m['hp'] = int(hp) if hp is not None else m['hp']
    #     m['status'] = status if status is not None else m['status']
    #     m['kills'] = int(kills) if kills is not None else m['kills']
    #     self.players.update_one({'_id': member.id}, {'$set': m})
    #     await interaction.followup.send("Готово.", ephemeral=debug_flag)
    #     return
    #
    # @app_commands.command(name="обновить", description="Обновить параметры игрока")
    # async def update(self, interaction: discord.Interaction):
    #     await interaction.response.defer(ephemeral=debug_flag)
    #     pl = self.players.find({})
    #     for player in pl:
    #         user = discord.utils.get(interaction.guild.members, name=player['name'])
    #         if user is None:
    #             user = discord.utils.get(interaction.guild.members, nick=player['name'])
    #             if user is None:
    #                 continue
    #         self.players.update_one({'_id': player['_id']}, {'$set': {'player_id': user.id}})
    #     await interaction.followup.send("Готово.", ephemeral=debug_flag)
    #     return
    #
    # @app_commands.command(name="топ", description="Вывести топ по килам")
    # @app_commands.rename(title="название")
    # async def top_list(self, interaction: discord.Interaction, title: Optional[str] = "Топ достижений сезона!"):
    #     await interaction.response.defer()
    #     count = self.players.count_documents({})
    #     if count == 0:
    #         await interaction.followup.send("Ошибка. Нет игроков в игре.")
    #         return
    #
    #     pl = self.players.find({})
    #     msg = ""
    #
    #     kills_dict = {}
    #
    #     for player in pl:
    #         if player['kills'] > 0:
    #             kills_dict[player['name']] = -player['kills']
    #
    #     if len(kills_dict) == 0:
    #         await interaction.followup.send("Нет статистики для топа...")
    #         return
    #
    #     sorted_keys = sorted(kills_dict, key=kills_dict.get)
    #     msg = "`" + 30*"-" + "`\n"
    #     for w in sorted_keys:
    #         kl = f"{-kills_dict[w]}"
    #         string = f"`{w} . {kl}`\n"
    #         while len(string) < 33:
    #             string = string.replace(".", "..", 1)
    #         msg += string
    #     msg += "`" + 30*'-' + "`"
    #
    #     embed = discord.Embed(title=title, colour=interaction.user.colour, description=msg)
    #
    #     await interaction.followup.send(embed=embed)
    #     return
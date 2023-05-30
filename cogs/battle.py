import discord
from discord.ext import commands
import sqlite3
from collections import defaultdict
import random

class BattleCog(commands.Cog, name="2. Battle"):
    def __init__(self, bot):
        self.bot = bot
        self.TEAM_LIMIT = 5
        self.weakness = {"inferno :boom:": "aqua :cyclone:",
                         "cosmic :fleur_de_lis:": "inferno :boom:",
                         "spectral :performing_arts:": "cosmic :fleur_de_lis:",
                         "crystal :trident:": "spectral :performing_arts:",
                         "aqua :cyclone:": "crystal :trident:",
                         "void :eight_pointed_black_star:": ""}
        self.typeEmoji = {"inferno :boom:": ":boom:",
                         "cosmic :fleur_de_lis:": ":fleur_de_lis:",
                         "spectral :performing_arts:": ":performing_arts:",
                         "crystal :trident:": ":trident:",
                         "aqua :cyclone:": ":cyclone:",
                         "void :eight_pointed_black_star:": ":eight_pointed_black_star:"}
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        cursor.execute(f"SELECT card_name FROM kebot_cards")
        result = cursor.fetchall()
        self.CARDS = [' '.join(x[0].split("_")) for x in result]

        cursor.close()
        db.close()

    @commands.command(name='b', brief="Commands for battling. Type **~help b** for more info.",
                      description="~b info                      Displays info on the battle system.\n" +
                                  "~b select card_#             Select the # of the card you wish to use.\n" +
                                  "~b unselect                  Unselect the card you wish to use.\n" +
                                  "~b view                      View the current state of battle.\n" +
                                  "~b cards                     Have Kebot resend the card-number pairing to you.\n" +
                                  "~b forfeit                   Forfeit the current battle.")
    async def b(self, ctx, *args):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM kebot_battle WHERE user_id = '{ctx.message.author.id}'")
        result = cursor.fetchone()
        if len(args) == 1 and args[0] == "info":
            embed = discord.Embed(
                title=f"General Battle Information",
                description=f"General Rules:\n"
                            f"Earn primosticks for winning!\n"
                            f"Each battle is best 2 out of 3, or until both players have exhausted their cards.\n"
                            f"Each card can only be used once per battle, though duplicate cards may be put on a team.\n"
                            f"A card beats another card if:\n"
                            f"  - The card's type is strong against the other card\n"
                            f"  - If card types are neutral, higher top energy wins",
                color=discord.Color.gold()
            )
            card_types = ["inferno :boom:", "cosmic :fleur_de_lis:", "spectral :performing_arts:",
                          "crystal :trident:", "aqua :cyclone:"]
            msg = ""
            for card_type in card_types:
                msg += f"{self.weakness[card_type]} beats {card_type}\n"
            msg += "void :eight_pointed_black_star: is neutral to all types"
            embed.add_field(name="Type Advantages:",
                            value=msg,
                            inline=False)
            embed.add_field(name="Misc Battle Help:",
                            value=":warning: When the battle begins, Shish Kebot will randomize your team order and dm it to you.\n"
                                  "The initial set up of the battle is NOT your team order! :warning:\n"
                                  "When you select your card, use the number that card is linked to, not the card itself.\n"
                                  "Make sure to select your card in the server, not the dm, otherwise Kebot will not register it.\n"
                                  "This process helps ensure anonymity when choosing the card you'll play that round.\n"
                                  "Good luck!",
                            inline=False)
            await ctx.send(embed=embed)
        elif not result:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You're not in a battle right now! Type **~battle @player** to battle someone.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif len(args) == 1:
            user_id, battle_id, battle_team, selected_card, grave, score = result
            nickname = ctx.message.guild.get_member(int(user_id)).display_name
            cursor.execute(f"SELECT user_id,score FROM kebot_battle WHERE battle_id = '{battle_id}' AND user_id IS NOT '{user_id}'")
            p2_id, p2_score = cursor.fetchone()
            nickname2 = ctx.message.guild.get_member(int(p2_id)).display_name
            if args[0] == "unselect":
                cursor.execute(f'''
UPDATE kebot_battle
SET selected_card = '-1'
WHERE user_id = '{user_id}'
''')
                db.commit()
                embed = discord.Embed(
                    title=f"Card has been unselected!",
                    color=discord.Color.gold()
                )
                await ctx.send(embed=embed)
            elif args[0] == "view":
                embed = discord.Embed(
                    title=f"Current Battle Information",
                    description=f"{nickname}: {score} | {nickname2}: {p2_score}",
                    color=discord.Color.gold()
                )
                cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = {user_id}")
                p1_team = cursor.fetchone()[0].split(",")
                p1_team.pop()
                team1 = ""
                for card in p1_team:
                    cursor.execute(f"SELECT top_energy,card_type FROM kebot_cards WHERE card_name = '{card}'")
                    top_energy, card_type = cursor.fetchone()
                    team1 += f"{card} | {card_type} | {top_energy}\n"
                cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = {p2_id}")
                p2_team = cursor.fetchone()[0].split(",")
                p2_team.pop()
                team2 = ""
                for card in p2_team:
                    cursor.execute(f"SELECT top_energy,card_type FROM kebot_cards WHERE card_name = '{card}'")
                    top_energy, card_type = cursor.fetchone()
                    team2 += f"{card} | {card_type} | {top_energy}\n"
                embed.add_field(name=f"{nickname}'s team", value=team1)
                embed.add_field(name=f"{nickname2}'s team", value=team2)
                await ctx.send(embed=embed)
            elif args[0] == "cards":
                cursor.execute(f"SELECT battle_team,grave FROM kebot_battle WHERE user_id = {user_id}")
                user_battle_team, user_grave = cursor.fetchone()
                user_battle_team = user_battle_team.split(",")
                user_grave = user_grave.split(",")

                user_message = "Type **~b select #** on the server to choose your card!\n"
                increment = 1
                for card in user_battle_team:
                    if str(increment - 1) in user_grave:
                        user_message += f"~~{increment}: {card}~~\n"
                    else:
                        user_message += f"{increment}: {card}\n"
                    increment += 1
                await ctx.message.guild.get_member(int(user_id)).send(user_message)
            elif args[0] == "forfeit":
                await self.end_battle(ctx, battle_id, f"{nickname} has forfeited the battle! "
                                                      f"{nickname2} wins and earns {int(p2_score) * 10} primosticks!\n"
                                                      f"Final score: {score}-{p2_score}",
                                      p2_id, int(p2_score))
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"Wrong syntax. Try **~help b** for more details.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        elif len(args) == 2 and args[0] == "select" and args[1].isdigit():
            user_id, battle_id, battle_team, selected_card, grave, score = result
            number = int(args[1]) - 1
            grave = grave.split(",")
            if 0 <= number <= 4 and str(number) not in grave:
                cursor.execute(f'''
UPDATE kebot_battle
SET selected_card = '{number}'
WHERE user_id = '{user_id}'
''')
                db.commit()
                embed = discord.Embed(
                    title=f"Card {args[1]} has been selected!",
                    color=discord.Color.gold()
                )
                await ctx.send(embed=embed)

                if battle_id.find(user_id) == 0:
                    user_id2 = battle_id[len(user_id):]
                else:
                    user_id2 = battle_id[:len(battle_id) - len(user_id)]
                cursor.execute(f"SELECT * FROM kebot_battle WHERE user_id = '{user_id2}'")
                result = cursor.fetchone()
                user_id2, battle_id2, battle_team2, selected_card2, grave2, score2 = result
                if selected_card2 == -1:
                    return

                await self.battle_between(ctx, user_id, user_id2)

            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"Either the number is invalid or you already used this card!",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)


        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"Wrong syntax. Type **~help b** for more details.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        cursor.close()
        db.close()

    async def battle_between(self, ctx, p1_id, p2_id):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        result = ""
        nickname1 = ctx.message.guild.get_member(int(p1_id)).display_name
        nickname2 = ctx.message.guild.get_member(int(p2_id)).display_name
        cursor.execute(f"SELECT battle_team,selected_card,grave,score FROM kebot_battle WHERE user_id = '{p1_id}'")
        p1_battle_team, p1_selected, p1_grave, p1_score = cursor.fetchone()
        cursor.execute(f"SELECT battle_team,selected_card,grave,score FROM kebot_battle WHERE user_id = '{p2_id}'")
        p2_battle_team, p2_selected, p2_grave, p2_score = cursor.fetchone()
        p1_grave = p1_grave.split(",")
        p2_grave = p2_grave.split(",")
        p1_battle_team = p1_battle_team.split(",")
        p2_battle_team = p2_battle_team.split(",")
        p1_card = p1_battle_team[p1_selected]
        p2_card = p2_battle_team[p2_selected]

        cursor.execute(f"SELECT top_energy,card_type FROM kebot_cards WHERE card_name = '{p1_card}'")
        p1_energy, p1_type = cursor.fetchone()
        cursor.execute(f"SELECT top_energy,card_type FROM kebot_cards WHERE card_name = '{p2_card}'")
        p2_energy, p2_type = cursor.fetchone()

        if self.weakness[p1_type] == p2_type:
            result = "p2"
        elif self.weakness[p2_type] == p1_type:
            result = "p1"
        elif int(p1_energy) > int(p2_energy):
            result = "p1"
        elif int(p2_energy) > int(p1_energy):
            result = "p2"

        if result == "":
            embed = discord.Embed(
                title=f"TIE",
                description=f'''{nickname1}'s {p1_card} {self.typeEmoji[p1_type]}({p1_energy})
-   ties with   -
{nickname2}'s {p2_card} {self.typeEmoji[p2_type]}({p2_energy})''',
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)
        elif result == "p1":
            p1_score = str(int(p1_score)+1)
            cursor.execute(f'''
UPDATE kebot_battle
SET score = '{p1_score}'
WHERE user_id = '{p1_id}'
''')
            db.commit()

            embed = discord.Embed(
                title=f"{nickname1} wins this round!",
                description=f'''{nickname1}'s {p1_card} {self.typeEmoji[p1_type]}({p1_energy})
-   topped   -
{nickname2}'s {p2_card} {self.typeEmoji[p2_type]}({p2_energy})''',
                color=discord.Color.gold()
            )
            image = "_".join(p1_card.split(" ")) + ".png"
            file = discord.File("card_images/" + image, filename=image)
            embed.set_image(url=f"attachment://{image}")
            await ctx.send(file=file, embed=embed)
        else:
            p2_score = str(int(p2_score)+1)
            cursor.execute(f'''
UPDATE kebot_battle
SET score = '{p2_score}'
WHERE user_id = '{p2_id}'
''')
            db.commit()
            embed = discord.Embed(
                title=f"{nickname2} wins this round!",
                description=f'''{nickname2}'s {p2_card} {self.typeEmoji[p2_type]}({p2_energy})
-   topped   -
{nickname1}'s {p1_card} {self.typeEmoji[p1_type]}({p1_energy})''',
                color=discord.Color.gold()
            )
            image = "_".join(p2_card.split(" ")) + ".png"
            file = discord.File("card_images/" + image, filename=image)
            embed.set_image(url=f"attachment://{image}")
            embed.add_field(name="Current Score:", value=f"{nickname1}: {p1_score} | {nickname2}: {p2_score}")
            await ctx.send(file=file, embed=embed)

        cursor.execute(f'''
UPDATE kebot_battle
SET selected_card = '-1'
WHERE user_id = '{p1_id}'
''')
        db.commit()
        cursor.execute(f'''
UPDATE kebot_battle
SET selected_card = '-1'
WHERE user_id = '{p2_id}'
''')
        db.commit()

        p1_grave.append(str(p1_selected))
        cursor.execute(f'''
UPDATE kebot_battle
SET grave = '{",".join(p1_grave)}'
WHERE user_id = '{p1_id}'
''')
        db.commit()
        p2_grave.append(str(p2_selected))
        cursor.execute(f'''
UPDATE kebot_battle
SET grave = '{",".join(p2_grave)}'
WHERE user_id = '{p2_id}'
''')
        db.commit()

        await self.check_end(ctx, p1_id, p2_id)
        cursor.close()
        db.close()

    async def check_end(self, ctx, p1_id, p2_id):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        win_msg = ""
        winner_id = ""
        winner_score = 0
        cursor.execute(f"SELECT battle_id,grave,score FROM kebot_battle WHERE user_id = '{p1_id}'")
        battle_id, p1_grave, p1_score = cursor.fetchone()
        cursor.execute(f"SELECT grave,score FROM kebot_battle WHERE user_id = '{p2_id}'")
        p2_grave, p2_score = cursor.fetchone()
        p1_grave = p1_grave.split(",")
        p1_score = int(p1_score)
        p2_score = int(p2_score)
        nickname1 = ctx.message.guild.get_member(int(p1_id)).display_name
        nickname2 = ctx.message.guild.get_member(int(p2_id)).display_name
        if p1_score == 2:
            win_msg = f"{nickname1} won the battle! They earn 20 primosticks!\nFinal score: {p1_score}-{p2_score}"
            winner_id = p1_id
            winner_score = p1_score
        elif p2_score == 2:
            win_msg = f"{nickname2} won the battle! They earn 20 primosticks!\nFinal score: {p2_score}-{p1_score}"
            winner_id = p2_id
            winner_score = p2_score
        elif len(p1_grave) == 5:
            win_msg = f"{nickname1} and {nickname2} are out of cards. The battle ends in a draw!"

        if win_msg != "":
            await self.end_battle(ctx, battle_id, win_msg, winner_id, winner_score)

        cursor.close()
        db.close()

    async def end_battle(self, ctx, battle_id, end_msg, winner_id, winner_score):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        cursor.execute(f'''
DELETE FROM kebot_battle
WHERE battle_id = '{battle_id}'
''')
        db.commit()
        if winner_id != "":
            cursor.execute(f'''
UPDATE kebot_users
SET primosticks = primosticks + {winner_score * 10}
WHERE user_id = '{winner_id}'
''')
            db.commit()
            cursor.execute(f'''
UPDATE kebot_users
SET level = level + 1
WHERE user_id = '{winner_id}'
''')
            db.commit()

        embed = discord.Embed(
            title=f"BATTLE END",
            description=end_msg,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.command(name='battle', brief="Battle a player (not implemented yet)",
                      description="~battle @player")
    async def battle(self, ctx):
        if not await self.is_player(ctx):
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        args = ctx.message.content[len(self.bot.command_prefix + "battle"):].strip().split(' ')
        p1 = ctx.message.author.id
        p2 = args[0]
        p2 = p2[3:len(p2)-1]

        # Check that p2 is a registered player
        cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = '{p2}'")
        result = cursor.fetchone()
        if result is not None:
            tmp = result[0]
            p2_team = [' '.join(x.split("_")) for x in tmp[:len(tmp) - 1].split(",")]
            cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = {p1}")
            tmp = cursor.fetchone()[0]
            p1_team = [' '.join(x.split("_")) for x in tmp[:len(tmp) - 1].split(",")]
            if len(p1_team) == 5 and len(p2_team) == 5:
                if await self.not_in_battle(p1, p2):
                    nickname1 = ctx.message.guild.get_member(int(p1)).display_name
                    nickname2 = ctx.message.guild.get_member(int(p2)).display_name

                    await self.start_battle(ctx, p1, p2)
                    embed = discord.Embed(
                        title=f"The battle between {nickname1} and {nickname2} has begun!",
                        description=f"Type **~help b** for battle commands!",
                        color=discord.Color.gold()
                    )
                    team1 = ""
                    for card in p1_team:
                        cursor.execute(f"SELECT top_energy,card_type FROM kebot_cards WHERE card_name = '{card}'")
                        top_energy, card_type = cursor.fetchone()
                        team1 += f"{card} | {card_type} | {top_energy}\n"

                    team2 = ""
                    for card in p2_team:
                        cursor.execute(f"SELECT top_energy,card_type FROM kebot_cards WHERE card_name = '{card}'")
                        top_energy, card_type = cursor.fetchone()
                        team2 += f"{card} | {card_type} | {top_energy}\n"
                    embed.add_field(name=f"{nickname1}'s team", value=team1)
                    embed.add_field(name=f"{nickname2}'s team", value=team2)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"One or more players are already in battle!\n"
                                    f"Type **~b forfeit** to end current battle.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"Both players need a full team.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"That player isn't registered!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        cursor.close()
        db.close()

    async def start_battle(self, ctx, p1_id, p2_id):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        battle_id = f"{p1_id}{p2_id}"

        cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = '{p1_id}'")
        battle_team1 = cursor.fetchone()[0].split(",")
        battle_team1.pop()
        random.shuffle(battle_team1)
        cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = '{p2_id}'")
        battle_team2 = cursor.fetchone()[0].split(",")
        battle_team2.pop()
        random.shuffle(battle_team2)

        p1_battle_team = ",".join(battle_team1)
        p2_battle_team = ",".join(battle_team2)
        selected_card = -1
        grave = ""
        score = "0"
        sql = (f'''
INSERT INTO kebot_battle
VALUES (?,?,?,?,?,?)
''')
        val = (str(p1_id), battle_id, p1_battle_team, selected_card, grave, score)
        cursor.execute(sql, val)
        db.commit()
        sql = (f'''
INSERT INTO kebot_battle
VALUES (?,?,?,?,?,?)
''')
        val = (str(p2_id), battle_id, p2_battle_team, selected_card, grave, score)
        cursor.execute(sql, val)
        db.commit()

        p1_message = "Type **~b select #** on the server to choose your card!\n"
        increment = 1
        for card in battle_team1:
            p1_message += f"{increment}: {card}\n"
            increment += 1
        await ctx.message.guild.get_member(int(p1_id)).send(p1_message)

        p2_message = "Type **~b select #** on the server to choose your card!\n"
        increment = 1
        for card in battle_team2:
            p2_message += f"{increment}: {card}\n"
            increment += 1
        await ctx.message.guild.get_member(int(p2_id)).send(p2_message)
        cursor.close()
        db.close()

    @commands.command(name='team', brief="Edit your battle team",
                      description="For card name, replace spaces in name with _ (e.g. crab_knife)\n"
                                  "~team add card_name                        - Add a card to your team\n"
                                  "~team remove card_name                     - Remove a card from your team\n"
                                  "~team clear                                - Removes all cards from your team\n")
    async def team(self, ctx, *args):
        if not await self.is_player(ctx):
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        if args:
            command = args[0]
        else:
            command = ""
        valid = True

        cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = '{ctx.message.author.id}'")
        raw_current_team = cursor.fetchone()[0]
        current_team = [' '.join(x.split("_")) for x in raw_current_team[:len(raw_current_team)-1].split(",")]
        current_team_dict = defaultdict(int)
        for card in current_team:
            current_team_dict[card] += 1
        cursor.execute(f"SELECT card_name,card_quantity FROM kebot_user_inv "
                       f"WHERE user_id = '{ctx.message.author.id}' AND card_quantity > 0")
        current_inv = {}
        for (card_name, card_quantity) in cursor.fetchall():
            current_inv[card_name] = card_quantity

        if command == "add":
            if len(args) == 2:
                card_name = ' '.join(args[1].split("_"))
                if len(current_team) < self.TEAM_LIMIT:
                    current_team_dict[card_name] += 1
                    if card_name in self.CARDS and \
                       card_name in current_inv and \
                       current_team_dict[card_name] <= current_inv[card_name]:
                        new_current_team = raw_current_team + card_name + ','
                        cursor.execute(f'''
UPDATE kebot_users
SET battle_team = '{new_current_team}'
WHERE user_id = '{ctx.message.author.id}'
''')
                        db.commit()
                        await ctx.send(f"'{card_name}' has been added to your team!")
                    else:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"You either do not own the card '{card_name}' or do not "
                                        f"own enough copies of the card to add it to your team!",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Your team is full!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                valid = False
        elif command == "remove":
            if len(args) == 2:
                card_name = ' '.join(args[1].split("_"))
                if len(current_team) > 0:
                    if card_name in self.CARDS and \
                       card_name in current_team:
                        new_current_team = raw_current_team[:raw_current_team.find(card_name)] + \
                                            raw_current_team[raw_current_team.find(card_name)+len(card_name)+1:]
                        cursor.execute(f'''
UPDATE kebot_users
SET battle_team = '{new_current_team}'
WHERE user_id = '{ctx.message.author.id}'
''')
                        db.commit()
                        await ctx.send(f"'{card_name}' has been removed from your team!")
                    else:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"'{card_name}' is not in your team!",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Your team is already empty!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                valid = False
        elif command == "clear":
            if len(args) == 1:
                cursor.execute(f'''
UPDATE kebot_users
SET battle_team = ""
WHERE user_id = '{ctx.message.author.id}'
''')
                db.commit()
                await ctx.send("Team successfully cleared!")
            else:
                valid = False
        else:
            valid = False

        if not valid:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"Wrong syntax. Type **~help team** for more details.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        cursor.close()
        db.close()

    async def not_in_battle(self, p1, p2):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        notInBattle = True
        cursor.execute(f"SELECT * FROM kebot_battle WHERE user_id = '{p1}'")
        result = cursor.fetchone()
        cursor.execute(f"SELECT * FROM kebot_battle WHERE user_id = '{p2}'")
        result2 = cursor.fetchone()
        if result or result2:
            notInBattle = False

        cursor.close()
        db.close()
        return notInBattle

    async def is_player(self, ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        valid = True
        cursor.execute(f"SELECT * FROM kebot_users WHERE user_id = {ctx.message.author.id}")
        result = cursor.fetchone()
        if result is None:
            valid = False
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You're not registered! Type **~start** to begin your journey.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        cursor.close()
        db.close()
        return valid

async def setup(bot):
    await bot.add_cog(BattleCog(bot))
    print("Battle is loaded.")
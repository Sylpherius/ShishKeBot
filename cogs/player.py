import discord
from discord.ext import commands, tasks
import sqlite3
import random
from numpy import random
from collections import defaultdict

class PlayerCog(commands.Cog, name="1. Player"):
    def __init__(self, bot):
        self.claimEnabled = True
        self.bot = bot
        self.april_fools = False
        self.CARD_SPAWN_RATE = 0.05
        self.AFK_SPAWN_RATE = 0.004
        self.UNCOMMON_RATE = 0.4
        self.RARE_RATE = 0.1
        self.EPIC_RATE = 0.02
        self.LEGENDARY_RATE = 0.005
        self.LIMITED_RATE = 0.95
        self.limited = False
        self.TEAM_LIMIT = 5
        self.afk_spawn.start()
        self.inv_offset = 10
        self.claimDict = {}
        self.doOnce = True
        self.id = {"fufu": 228652644284104704}
        self.convertToPrimosticks = {"common": 10,
                                     "uncommon": 20,
                                     "rare": 50,
                                     "epic": 200,
                                     "legendary": 1000,
                                     "???": -1}
        self.responseDict = {"well i guess": "i gotta end it",
                             "i am": "going to die",
                             "i": ":eye:"}

    @commands.command(name='daily', brief="Get a free card every day!")
    async def daily(self, ctx):
        if not await self.is_player(ctx):
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        cursor.execute(f"SELECT daily FROM kebot_users WHERE user_id = {ctx.message.author.id}")
        daily = cursor.fetchone()[0]
        if daily == 1 or ctx.message.author.id == self.id["fufu"]:
            sql = (f'''
UPDATE kebot_users
SET daily = 0
WHERE user_id = '{ctx.message.author.id}'
''')
            cursor.execute(sql)
            db.commit()
            rarity = random.rand()
            prank = False
            if self.april_fools and rarity < 0.5:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'legendary'"
                msg = "The divine top light has shined down upon you! :point_left:"
                prank = True
            elif rarity < self.LEGENDARY_RATE / 4:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'legendary'"
                msg = "The divine top light has shined down upon you! :point_left:"
            elif rarity < self.EPIC_RATE / 3:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'epic'"
                msg = "WOW!"
            elif rarity < self.RARE_RATE / 2:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'rare'"
                msg = "Lucky!"
            elif rarity < self.UNCOMMON_RATE:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'uncommon'"
                msg = "Nice!"
            else:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'common'"
                msg = "Cool."
            cursor.execute(sql)
            result = cursor.fetchall()
            chosen_card = int(random.rand() * len(result))
            card = result[chosen_card][0]

            cursor.execute(f"SELECT image FROM kebot_cards WHERE card_name = '{card}'")
            image = cursor.fetchone()[0]
            cursor.execute(f"SELECT card_quantity FROM kebot_user_inv WHERE user_id = '{ctx.message.author.id}' "
                           f"AND card_name = '{card}'")
            result = cursor.fetchone()
            nickname = ctx.message.author.nick if ctx.message.author.nick else ctx.message.author

            if not prank:
                if result is None:
                    sql = (f'''
INSERT INTO kebot_user_inv
VALUES ({ctx.message.author.id}, '{card}', 1)
''')
                else:
                    sql = (f'''
UPDATE kebot_user_inv
SET card_quantity = '{int(result[0]) + 1}'
WHERE user_id = '{ctx.message.author.id}'
AND card_name = '{card}'
''')
                cursor.execute(sql)
                db.commit()
                cursor.execute(f'''
UPDATE kebot_users
SET total_cards = total_cards + 1
WHERE user_id = '{ctx.message.author.id}'
''')
                db.commit()

                embed = discord.Embed(
                    title=f"{msg}\n '{card}' has been added to {nickname}'s collection!",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title=f"{msg}\n '{card}' has been added to {nickname}'s collection!.. jk you got nothing today.",
                    color=discord.Color.green()
                )

            file = discord.File("card_images/" + image, filename=image)
            embed.set_thumbnail(url=f"attachment://{image}")
            await ctx.send(file=file, embed=embed)
        else:
            embed = discord.Embed(
                title=f"You've already used your daily today!",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.command(name='start', brief="Start your journey.")
    async def start(self, ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM kebot_users WHERE user_id = {ctx.message.author.id}")
        result = cursor.fetchone()
        nickname = ctx.message.author.nick if ctx.message.author.nick else ctx.message.author
        if result is None:
            sql = (f'''
INSERT INTO kebot_users
VALUES (?,?,?,"",0,1)
''')
            val = (ctx.message.author.id, 1, 0)
            cursor.execute(sql, val)
            db.commit()
            await ctx.send(f"Good luck out there {nickname}, don't be an uber bottom!!")
        else:
            await ctx.send(f"You already have an account, {nickname}!")
        cursor.close()
        db.close()

    @commands.command(name='prof', brief="Check your profile")
    async def profile(self, ctx):
        if not await self.is_player(ctx):
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        cursor.execute(f"SELECT * FROM kebot_users WHERE user_id = {ctx.message.author.id}")
        result = cursor.fetchone()
        nickname = ctx.message.author.nick if ctx.message.author.nick else ctx.message.author
        embed = discord.Embed(
            title=f"*{nickname}*",
            color=discord.Color.green()
        )
        author = ctx.message.author
        pfp = ctx.message.author.avatar.url
        level = result[1]
        total_cards = result[2]
        battle_team = [x for x in result[3][:len(result[3])-1].split(",")] if result[3] != "" else None
        primosticks = result[4]
        embed.set_author(name=str(author)[:len(str(author)) - 5], icon_url=pfp)
        embed.add_field(name="Victories", value=str(int(level)-1), inline=False)
        embed.add_field(name="Primosticks", value=primosticks, inline=False)
        embed.add_field(name="Total Cards", value=total_cards, inline=False)
        team = ""
        file = None
        if battle_team:
            empty = self.TEAM_LIMIT - len(battle_team)
            for card_name in battle_team:
                cursor.execute(f"SELECT top_energy,card_type FROM kebot_cards WHERE card_name = '{card_name}'")
                (top_energy, card_type) = cursor.fetchone()
                card_type_symbol = card_type[card_type.find(":"):]
                team += f"{card_name} | {str(top_energy)} {card_type_symbol}\n"
            for x in range(empty):
                team += "-\n"

            cursor.execute(f"SELECT image FROM kebot_cards WHERE card_name = '{battle_team[0]}'")
            image = cursor.fetchone()[0]
            file = discord.File("card_images/" + image, filename=image)
            embed.set_image(url=f"attachment://{image}")
        else:
            team = "Not set yet! Type **~help team** for more info on creating your team!"\

        embed.add_field(name="Battle Team", value=team, inline=False)
        await ctx.send(file=file, embed=embed)
        cursor.close()
        db.close()

    @commands.command(name='claim', brief="Claim a card")
    async def claim(self, ctx):
        if self.doOnce:
            self.doOnce = False
            await self.load_kebot()
            await self.update_guilds()
        if not await self.is_player(ctx):
            return
        if not self.claimEnabled:
            await ctx.send("Claim is currently disabled :3")
        if self.claimDict[ctx.message.guild.id][0] and self.claimEnabled:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "claim"):].strip().split(' ')
            if len(args) > 0:
                user_card = ' '.join(args).lower()
                if user_card == self.claimDict[ctx.message.guild.id][1]:
                    self.claimDict[ctx.message.guild.id][0] = False
                    cursor.execute(f"SELECT card_quantity FROM kebot_user_inv WHERE user_id = '{ctx.message.author.id}' AND card_name = '{self.claimDict[ctx.message.guild.id][1]}'")
                    result = cursor.fetchone()
                    if result is None:
                        sql = (f'''
INSERT INTO kebot_user_inv
VALUES ({ctx.message.author.id}, '{self.claimDict[ctx.message.guild.id][1]}', 1)
''')
                    else:
                        sql = (f'''
UPDATE kebot_user_inv
SET card_quantity = '{int(result[0]) + 1}'
WHERE user_id = '{ctx.message.author.id}'
AND card_name = '{self.claimDict[ctx.message.guild.id][1]}'
''')
                    cursor.execute(sql)
                    db.commit()
                    cursor.execute(f'''
UPDATE kebot_users
SET total_cards = total_cards + 1
WHERE user_id = '{ctx.message.author.id}'
''')
                    db.commit()
                    nickname = ctx.message.author.nick if ctx.message.author.nick else ctx.message.author
                    await ctx.send(f"Congrats! '{self.claimDict[ctx.message.guild.id][1]}' has been added to {nickname}'s collection!")

            cursor.close()
            db.close()

    @commands.command(name='kill', brief="Kill a card and get primosticks",
                      description="For card name, replace spaces in name with _ (e.g. crab_knife)\n"
                                  "~kill card_name     - removes one specified card from inventory\n"
                                  "~kill card_name #   - removes # of specified card from inventory\n")
    async def kill(self, ctx):
        if not await self.is_player(ctx):
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        args = ctx.message.content[len(self.bot.command_prefix + "kill"):].strip().split(' ')

        cursor.execute(f"SELECT battle_team FROM kebot_users WHERE user_id = '{ctx.message.author.id}'")
        raw_current_team = cursor.fetchone()[0]
        current_team = [' '.join(x.split("_")) for x in raw_current_team[:len(raw_current_team) - 1].split(",")]
        current_team_dict = defaultdict(int)
        for card in current_team:
            current_team_dict[card] += 1

        if len(args) >= 1:
            try:
                card_name = ' '.join(args[0].split('_'))
                cursor.execute(f"SELECT card_quantity FROM kebot_user_inv "
                               f"WHERE user_id = '{ctx.message.author.id}' AND card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is not None:
                    current_quantity = result[0]
                    remove_quantity = 1

                    # check they don't remove a negative number
                    if len(args) == 2:
                        remove_quantity = int(args[1])
                        if remove_quantity <= 0:
                            embed = discord.Embed(
                                title=f":knife: ERROR :knife:",
                                description=f"Wrong syntax. Try **~help kill** for more details.",
                                color=discord.Color.red()
                            )
                            await ctx.send(embed=embed)
                            cursor.close()
                            db.close()
                            return

                    # check they don't remove a card that's on their team
                    if card_name in current_team_dict and \
                        current_team_dict[card_name] > current_quantity - remove_quantity:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"Removing {remove_quantity} '{card_name}' "
                                        f"makes your team invalid.\n"
                                        f"Please change the quantity or remove the card from your team.",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        cursor.close()
                        db.close()
                        return

                    if remove_quantity <= current_quantity:
                        cursor.execute(f'''
UPDATE kebot_user_inv
SET card_quantity = card_quantity - {remove_quantity}
WHERE user_id = '{ctx.message.author.id}'
AND card_name = '{card_name}'
''')
                        db.commit()
                        cursor.execute(f'''
UPDATE kebot_users
SET total_cards = total_cards - {remove_quantity}
WHERE user_id = '{ctx.message.author.id}'
''')

                        # get primosticks
                        cursor.execute(f"SELECT card_rarity FROM kebot_cards WHERE card_name = '{card_name}'")
                        rarity = cursor.fetchone()[0]
                        coins_gained = self.convertToPrimosticks[rarity] * remove_quantity
                        cursor.execute(f'''
UPDATE kebot_users
SET primosticks = primosticks + {coins_gained}
WHERE user_id = '{ctx.message.author.id}'
''')
                        db.commit()
                        await ctx.send(f"You've successfully murdered {remove_quantity} '{card_name}'(s) and received "
                                       f"{coins_gained} primosticks!")

                    else:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"You attempted to remove {remove_quantity} '{card_name}' "
                                        f"but you only have {current_quantity}!",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"You don't own any copies of this card to kill!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"Wrong syntax. Type **~help kill** for more details.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.command(name='inv', brief="Show player's inventory",
                      description="~inv     - Takes you to first page of inventory\n"
                                  "~inv #   - Takes you to page # of inventory")
    async def inv(self, ctx):
        if not await self.is_player(ctx):
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        args = ctx.message.content[len(self.bot.command_prefix + "inv"):].strip().split(' ')
        page = 0
        if args[0] != "":
            try:
                page = int(args[0]) - 1
                if page < 0:
                    raise Exception

            except Exception as e:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"Wrong syntax. Type **~help inv** for more details.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                cursor.close()
                db.close()
                return

        cursor.execute(f"SELECT card_name,card_quantity FROM kebot_user_inv "
                       f"WHERE user_id = '{ctx.message.author.id}' "
                       f"AND card_quantity > 0 "
                       f"LIMIT {self.inv_offset} OFFSET {page * self.inv_offset}")
        result = cursor.fetchall()
        inventory = ""
        for (card_name, card_quantity) in result:
            (card_rarity, top_energy, card_type) = cursor.execute(f"SELECT card_rarity,top_energy,card_type "
                                                                  f"FROM kebot_cards "
                                                                  f"WHERE card_name = '{card_name}'").fetchone()
            inventory += f"\n\n**{card_name}** {card_type[card_type.find(':'):]}\n" \
                         f"{card_rarity} | {top_energy} | owned: {card_quantity}"

        nickname = ctx.message.author.nick if ctx.message.author.nick else ctx.message.author
        embed = discord.Embed(
            title=f"*{nickname}'s inventory - page {page + 1}*",
            description=inventory,
            color=discord.Color.green()
        )
        author = ctx.message.author
        pfp = ctx.message.author.avatar.url
        embed.set_author(name=str(author)[:len(str(author)) - 5], icon_url=pfp)
        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    # V.v.V SPAWN CARD
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.doOnce:
            self.doOnce = False
            await self.load_kebot()
            await self.update_guilds()

        if message.author == self.bot.user:
            return

        if message.content.lower() in self.responseDict:
            await message.channel.send(self.responseDict[message.content.lower()])
        elif "bless" in message.content.lower():
            await message.channel.send("blessings are for the weak")
        elif "top" in message.content.lower():
            await message.channel.send(":point_left:")
        elif ("how was your day" in message.content.lower() or "how are you" in message.content.lower() or
              "how r u" in message.content.lower() or "how are u" in message.content.lower()) and \
             ("mr bot" in message.content.lower() or "kebot" in message.content.lower() or "mr kebot" in message.content.lower()):
            responses = ["I'm good", "Doing alright", "Fine", "Good", "It's great now that you're here :)",
                         "It's been good", "Could be worse", "It's been good", "Doing well", "I'm doing well"]
            response = responses[random.randint(1, len(responses)) - 1]
            await message.channel.send(response)
        elif "cwosan" in message.content.lower():
            await message.channel.send(":croissant:")

        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM kebot WHERE guild_id = '{message.guild.id}'")
        result = cursor.fetchone()
        current_channel = ""
        if result is None:
            await self.update_guilds()
        else:
            current_channel = result[0]

        channel = message.channel.id if current_channel == "" else current_channel

        if len(message.embeds) == 0 and message.content and message.content[0] != self.bot.command_prefix:
            await self.spawn_card(message.guild, channel, self.CARD_SPAWN_RATE)

        cursor.close()
        db.close()

    @tasks.loop(seconds=60)
    async def afk_spawn(self):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        for guild in self.bot.guilds:
            if self.doOnce:
                self.doOnce = False
                await self.load_kebot()
                await self.update_guilds()

            cursor.execute(f"SELECT channel_id FROM kebot WHERE guild_id = '{guild.id}'")
            result = cursor.fetchone()
            if result is not None:
                channel = result[0]
                await self.spawn_card(guild, channel, self.AFK_SPAWN_RATE)

        cursor.close()
        db.close()

    async def spawn_card(self, guild, channel, rate):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        spawn = random.rand()
        card = ""
        if spawn < rate:
            rarity = random.rand()
            if rarity > (1 - self.LEGENDARY_RATE):
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = '???'"
            elif rarity < self.LEGENDARY_RATE:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'legendary'"
            elif rarity < self.EPIC_RATE:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'epic'"
            elif rarity < self.RARE_RATE:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'rare'"
            elif rarity < self.UNCOMMON_RATE:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'uncommon'"
            else:
                sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'common'"
            cursor.execute(sql)
            result = cursor.fetchall()
            chosen_card = int(random.rand() * len(result))
            card = result[chosen_card][0]

        if card != "":
            cursor.execute(f"SELECT image FROM kebot_cards WHERE card_name = '{card}'")
            image = cursor.fetchone()[0]
            self.claimDict[guild.id][0] = True
            self.claimDict[guild.id][1] = card
            embed = discord.Embed(
                title=f"A wild {card} appeared!",
                description=f"Type **~claim {card}** to get the card!",
                color=discord.Color.blue()
            )
            file = discord.File("card_images/" + image, filename=image)
            embed.set_image(url=f"attachment://{image}")
            await self.bot.get_channel(int(channel)).send(file=file, embed=embed)

        cursor.close()
        db.close()

    # V.v.V GUILD
    async def update_guilds(self):
        print("guilds have been updated")
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        for guild in self.bot.guilds:
            if guild.id not in self.claimDict:
                self.claimDict[guild.id] = [False, ""]
            cursor.execute(f"SELECT guild_id FROM kebot WHERE guild_id = '{guild.id}'")
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f'''
INSERT INTO kebot
VALUES ('{guild.id}', "")
''')
                db.commit()
        cursor.close()
        db.close()

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

    async def load_kebot(self):
        kebot_names = ["kebot", "mr bot", "mr kebot", "mr shish", "bot", "shish kebot"]
        for hi in ["hey", "hi", "hello", "hewo", "herro", "heyo", "sup", "yo", "wassup", "greetings"]:
            for name in kebot_names:
                self.responseDict[f"{hi} {name}"] = hi
        for thanks in ["thanks", "thank u", "thank you"]:
            for name in kebot_names:
                self.responseDict[f"{thanks} {name}"] = "np"
        for night in ["good night", "g'night", "night", "goodnight", "gnight"]:
            for name in kebot_names:
                self.responseDict[f"{night} {name}"] = "goodnight"
        for morning in ["good morning", "g'morning", "morning", "gmorning", "goodmorning"]:
            for name in kebot_names:
                self.responseDict[f"{morning} {name}"] = "good morning"
        for afternoon in ["good afternoon", "afternoon", "g'afternoon"]:
            for name in kebot_names:
                self.responseDict[f"{afternoon} {name}"] = "good afternoon"
        for name in kebot_names:
            self.responseDict[f"{name} love me"] = "you _are_ loved... just not by the cards :)"
        for love in ["i love you", "love you", "i love u", "love u", "ily"]:
            for name in kebot_names:
                self.responseDict[f"{love} {name}"] = ":heart:"
                self.responseDict[f"{name} {love}"] = ":heart:"
        #for name in kebot_names:
        #    for punctuation in ["!", "", " !", " :heart:"]:
        #        self.responseDict[f"happy valentines day {name}{punctuation}"] = "happy valentines day! :heart:"
        for hate in ["i hate you", "hate you", "i hate u", "hate u"]:
            for name in kebot_names:
                self.responseDict[f"{hate} {name}"] = ":broken_heart:"
                self.responseDict[f"{name} {hate}"] = ":broken_heart:"

async def setup(bot):
    await bot.add_cog(PlayerCog(bot))
    print("Player is loaded.")

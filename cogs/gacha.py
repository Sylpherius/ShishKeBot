import discord
from discord.ext import commands
import sqlite3
from numpy import random

class GachaCog(commands.Cog, name="3. Gacha"):
    def __init__(self, bot):
        self.bot = bot
        self.UNCOMMON_RATE = 0.4
        self.RARE_RATE = 0.1
        self.EPIC_RATE = 0.02
        self.LEGENDARY_RATE = 0.005
        self.type = {"aqua": "aqua :cyclone:",
                     "inferno": "inferno :boom:",
                     "cosmic": "cosmic :fleur_de_lis:",
                     "spectral": "spectral :performing_arts:",
                     "crystal": "crystal :trident:",
                     "void": "void :eight_pointed_black_star:"}
        self.dailyCost = {"": 100,
                          "Spectral": 110,
                          "Aqua": 110,
                          "Inferno": 110,
                          "Cosmic": 110,
                          "Crystal": 110,
                          "Golden": 125}
        self.dailySpecials = ["Spectral", "Aqua", "Inferno", "Cosmic", "Crystal", "Golden"]
        self.daily = self.dailySpecials[random.randint(len(self.dailySpecials))]
        self.dailyDescription = {"Spectral": "Spectral card rate up by 50%! (+10% cost)",
                                 "Aqua": "Aqua card rate up by 50%! (+10% cost)",
                                 "Inferno": "Inferno card rate up by 50%! (+10% cost)",
                                 "Cosmic": "Cosmic card rate up by 50%! (+10% cost)",
                                 "Crystal": "Crystal card rate up by 50%! (+10% cost)",
                                 "Golden": "Legendary card rate quadrupled! (+25% cost)"}

    @commands.command(name='store', brief="Open the gachapan store.")
    async def store(self, ctx):
        if await self.is_player(ctx):
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            cursor.execute(f"SELECT primosticks FROM kebot_users WHERE user_id = '{ctx.message.author.id}'")
            primosticks = cursor.fetchone()[0]

            embed = discord.Embed(
                title=f"**Gacha Store**",
                description=f"Care to test your luck?\n"
                            f"To add the daily bonus, add 'daily' after the purchase command (e.g. ~pull ten daily)\n"
                            f"You currently own **{primosticks} primosticks**.",
                color=discord.Color.green()
            )
            embed.add_field(name="One Skewer", value="100 primosticks", inline=False)
            embed.add_field(name="Ten Skewers", value="1000 primosticks (_at least one epic guaranteed_)", inline=False)
            embed.add_field(name=self.daily + " Daily Special", value=self.dailyDescription[self.daily], inline=False)
            await ctx.send(embed=embed)

            cursor.close()
            db.close()

    @commands.command(name='pull', brief="Buy cards from the store.",
                      description="To pull with the daily deal, add 'daily' after the command.\n"
                                  "~pull one                         - pull one card\n"
                                  "~pull ten                         - pull ten cards\n"
                                  "~pull one daily                   - pull one card with daily deal\n"
                                  "~pull ten daily                   - pull ten cards with daily deal\n")
    async def pull(self, ctx, *args):
        if await self.is_player(ctx):
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cards = []
            cursor.execute(f"SELECT primosticks FROM kebot_users WHERE user_id = '{ctx.message.author.id}'")
            primosticks = cursor.fetchone()[0]

            if len(args) == 1 and (args[0] == "one" or args[0] == "ten"):
                if args[0] == "one":
                    if primosticks < 100:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"Not enough primosticks! You need 100. You have {primosticks}.",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        return

                    card, rarity = await self.pullOne(ctx)
                    cards.append(card)
                else:
                    if primosticks < 1000:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"Not enough primosticks! You need 1000. you have {primosticks}.",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        return

                    hasEpic = False
                    for i in range(10):
                        card, rarity = await self.pullOne(ctx)
                        cards.append(card)
                        if rarity == "epic" or rarity == "legendary":
                            hasEpic = True
                    if not hasEpic:
                        cards[9] = await self.pullEpic()
            elif len(args) == 2 and (args[0] == "one" or args[0] == "ten") and args[1] == "daily":
                if args[0] == "one":
                    if primosticks < self.dailyCost[self.daily]:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"Not enough primosticks! You need {self.dailyCost[self.daily]}. You have {primosticks}.",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        return

                    card, rarity = await self.pullOne(ctx, self.daily)
                    cards.append(card)
                else:
                    if primosticks < self.dailyCost[self.daily]*10:
                        embed = discord.Embed(
                            title=f":knife: ERROR :knife:",
                            description=f"Not enough primosticks! You need {self.dailyCost[self.daily]*10}. You have {primosticks}.",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        return

                    hasEpic = False
                    for i in range(10):
                        card, rarity = await self.pullOne(ctx, self.daily)
                        cards.append(card)
                        if rarity == "epic" or rarity == "legendary":
                            hasEpic = True
                    if not hasEpic:
                        cards[9] = await self.pullEpic(self.daily)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"Wrong syntax. Type **~help pull** for more details.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            if len(cards) == 1:
                card = cards[0]
                embed = discord.Embed(
                    title=f"Congratulations! You pulled the following card:",
                    color=discord.Color.green()
                )
                cursor.execute(f"SELECT image,card_rarity,top_energy,card_type FROM kebot_cards WHERE card_name = '{card}'")
                image, card_rarity, top_energy, card_type = cursor.fetchone()
                embed.add_field(name=f"{card}", value=f"{card_rarity} | {top_energy} | {card_type}", inline=False)
                file = discord.File("card_images/" + image, filename=image)
                embed.set_image(url=f"attachment://{image}")
                await ctx.send(file=file, embed=embed)
            if len(cards) == 10:
                embed = discord.Embed(
                    title=f"Congratulations! You pulled the following cards:",
                    color=discord.Color.green()
                )
                for card in cards:
                    cursor.execute(f"SELECT card_rarity,top_energy,card_type FROM kebot_cards WHERE card_name = '{card}'")
                    card_rarity, top_energy, card_type = cursor.fetchone()
                    embed.add_field(name=f"{card}", value=f"{card_rarity} | {top_energy} | {card_type}", inline=False)
                await ctx.send(embed=embed)

            for card in cards:
                cursor.execute(
                    f"SELECT card_quantity FROM kebot_user_inv WHERE user_id = '{ctx.message.author.id}' AND card_name = '{card}'")
                result = cursor.fetchone()
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

            cursor.close()
            db.close()

    async def pullOne(self, ctx, daily=""):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        tempDaily = daily.lower()
        legendary_rate = self.LEGENDARY_RATE
        epic_rate = self.EPIC_RATE
        if tempDaily == "golden":
            legendary_rate += 0.015
            epic_rate += 0.02

        rarity = random.rand()
        if rarity < legendary_rate:
            sql = "SELECT card_name,card_rarity FROM kebot_cards WHERE card_rarity = 'legendary'"
        elif rarity < epic_rate:
            sql = "SELECT card_name,card_rarity FROM kebot_cards WHERE card_rarity = 'epic'"
        elif rarity < self.RARE_RATE:
            sql = "SELECT card_name,card_rarity FROM kebot_cards WHERE card_rarity = 'rare'"
        elif rarity < self.UNCOMMON_RATE:
            sql = "SELECT card_name,card_rarity FROM kebot_cards WHERE card_rarity = 'uncommon'"
        else:
            sql = "SELECT card_name,card_rarity FROM kebot_cards WHERE card_rarity = 'common'"

        if tempDaily and tempDaily != "golden":
            doBonus = random.rand()
            if doBonus < 0.5:
                sql += f" AND card_type = '{self.type[tempDaily]}'"

        cursor.execute(sql)
        result = cursor.fetchall()
        chosen_card = int(random.rand() * len(result))
        (card, rarity) = result[chosen_card]

        cursor.execute(f'''
UPDATE kebot_users
SET primosticks = primosticks - {self.dailyCost[daily]}
WHERE user_id = '{ctx.message.author.id}'
''')
        db.commit()

        cursor.close()
        db.close()
        return card, rarity

    async def pullEpic(self, daily=""):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        sql = "SELECT card_name FROM kebot_cards WHERE card_rarity = 'epic'"
        if daily and daily != "Golden":
            doBonus = random.rand()
            if doBonus < 0.5:
                sql += f" AND card_type = '{self.type[daily]}'"

        cursor.execute(sql)
        result = cursor.fetchall()
        chosen_card = int(random.rand() * len(result))
        card = result[chosen_card][0]

        cursor.close()
        db.close()
        return card

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
    await bot.add_cog(GachaCog(bot))
    print("Gacha is loaded.")
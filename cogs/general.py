import discord
from discord.ext import commands
import random
from numpy import random
import sqlite3

class GeneralCog(commands.Cog, name="4. General"):
    def __init__(self, bot):
        self.bot = bot
        self.responses = ["Yes", "No", "Only in your dreams", "Absolutely.", "Definitely not.", "What a useless question",
                        "Probably", "Probably not", "Hmmm... ask me later", "Of course", "Most assuredly not", "Maybe...",
                        "I'm not sure you want to hear the answer", "Heck yea", "Not really", "Try again",
                        "Only if you realllly want it", "Yes! Wait no. I meant no.", "100% yes!", "Mmm... no.",
                        "Maybe if you ask nicely", "y e s", "n o", "If you were expecting a yes, you'll be disappointed",
                        "Yes. Wait no. Wait. Yes. Final answer."]

    @commands.command(name='info', brief="Check a card's information.")
    async def info(self, ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        args = ctx.message.content[len(self.bot.command_prefix + "info"):].strip().split(' ')
        card_name = ' '.join(args)
        cursor.execute(f"SELECT * FROM kebot_cards WHERE card_name = '{card_name}'")
        result = cursor.fetchone()
        if result is None:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"The card '{card_name}' doesn't exist.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            (card_name, image, card_rarity, top_energy, card_type, card_series, description) = result
            embed = discord.Embed(
                title=f"{card_name}",
                description=description,
                color=discord.Color.green()
            )
            embed.add_field(name="Top Energy", value=top_energy, inline=True)
            embed.add_field(name="Rarity", value=card_rarity, inline=True)
            embed.add_field(name="Type", value=card_type, inline=True)
            embed.add_field(name="Series", value=card_series, inline=True)
            file = discord.File("card_images/" + image, filename=image)
            embed.set_image(url=f"attachment://{image}")
            await ctx.send(file=file, embed=embed)

        cursor.close()
        db.close()

    @commands.command(name='ball', brief="Magic 8 ball")
    async def ball(self, ctx, *args):
        if len(args) >= 1:
            response = self.responses[random.randint(1, len(self.responses)) - 1]
            await ctx.send(response)
        else:
            await ctx.send("Ask a yes/no question! (e.g. ~ball <question>)")

    @commands.command(name='redirect', help="Redirects all spawns from Shish KeBot to this channel.")
    async def redirect(self, ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        await self.update_guilds()
        cursor.execute(f'''
UPDATE kebot
SET channel_id = '{ctx.message.channel.id}'
WHERE guild_id = '{ctx.message.guild.id}';
''')
        db.commit()
        await ctx.send("All spawns will now appear on this channel!")
        cursor.close()
        db.close()

    @commands.command(name='un-redirect', help="Allows spawns to appear in any channel.")
    async def unredirect(self, ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'''
UPDATE kebot
SET channel_id = ''
WHERE guild_id = '{ctx.message.guild.id}';
    ''')
        db.commit()
        await ctx.send("Spawns can now appear on any channel!")
        cursor.close()
        db.close()

    async def update_guilds(self):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        for guild in self.bot.guilds:
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

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
    print("General is loaded.")
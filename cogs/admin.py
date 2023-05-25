import discord
from discord.ext import commands
import sqlite3

class AdminCog(commands.Cog, name="Admin"):
    def __init__(self, bot):
        self.bot = bot
        self.rarity = ["common", "uncommon", "rare", "epic", "legendary", "???"]
        self.type = {"aqua": "aqua :cyclone:",
                     "inferno": "inferno :boom:",
                     "cosmic": "cosmic :fleur_de_lis:",
                     "spectral": "spectral :performing_arts:",
                     "crystal": "crystal :trident:",
                     "void": "void :eight_pointed_black_star:"}
        self.id = {"fufu": 228652644284104704}

    # V.v.V CARD
    @commands.command(name='add-card', brief="Add a card", description="~add-card card rarity top_energy type series description")
    async def add_card(self, ctx):
        num_args = 5
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "add-card"):].strip().split(' ')
            if len(args) == num_args:
                card_name = ' '.join(args[0].split('_'))
                image = args[0] + ".png"
                card_rarity = args[1]
                top_energy = int(args[2])
                card_type = args[3]
                card_series = args[4]
                if card_rarity not in self.rarity or card_type not in self.type:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Rarity or Type invalid.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return
                cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is None:
                    sql = (f'''
INSERT INTO kebot_cards (card_name, image, card_rarity, top_energy, card_type, card_series)
VALUES (?,?,?,?,?,?)
''')
                    val = (card_name, image, card_rarity, top_energy, self.type[card_type], card_series)
                    cursor.execute(sql, val)
                    db.commit()
                    await ctx.send(f"Card '{card_name}' has been added successfully!")
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"{args[0]} already exists in the database",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"features expected: " + str(num_args) +
                                "\nfeatures received: " + str(len(args)),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to add cards",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='remove-card', brief="Remove a card", description="~remove-card card")
    async def remove_card(self, ctx):
        num_args = 1
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "remove-card"):].strip().split(' ')
            if len(args) == num_args:
                card_name = ' '.join(args[0].split('_'))
                cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute(f'''
DELETE FROM kebot_cards
WHERE card_name = '{card_name}';
''')
                    db.commit()
                    await ctx.send(f"Card '{card_name}' has been removed!")
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Card '{card_name}' does not exist!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"features expected: " + str(num_args) +
                               "\nfeatures received: " + str(len(args)),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to edit cards.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='edit-name', brief="Edit card", description="~edit-name name new_name")
    async def edit_card_name(self, ctx):
        num_args = 2
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "edit-name"):].strip().split(' ')
            if len(args) == num_args:
                card_name = ' '.join(args[0].split('_'))
                new_name = ' '.join(args[1].split('_'))
                new_image = args[1] + ".png"
                cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute(f'''
UPDATE kebot_cards
SET card_name = '{new_name}', image = '{new_image}'
WHERE card_name = '{card_name}';
''')
                    db.commit()
                    await ctx.send(f"Card '{card_name}' has been changed to '{new_name}'!")
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Card '{card_name}' does not exist!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"features expected: " + str(num_args) +
                                "\nfeatures received: " + str(len(args)),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to edit cards.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='edit-rarity', brief="Edit card", description="~edit-rarity name rarity")
    async def edit_card_rarity(self, ctx):
        num_args = 2
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "edit-rarity"):].strip().split(' ')
            if len(args) == num_args:
                card_name = ' '.join(args[0].split('_'))
                new_rarity = args[1]
                if new_rarity not in self.rarity:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"'{new_rarity}' is not a valid rarity.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return
                cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute(f'''
UPDATE kebot_cards
SET card_rarity = '{new_rarity}'
WHERE card_name = '{card_name}';
''')
                    db.commit()
                    await ctx.send(f"Card '{card_name}' rarity has been changed to '{new_rarity}'!")
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Card '{card_name}' does not exist!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"features expected: " + str(num_args) +
                               "\nfeatures received: " + str(len(args)),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to edit cards.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='edit-energy', brief="Edit card", description="~edit-energy name energy")
    async def edit_top_energy(self, ctx):
        num_args = 2
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "edit-energy"):].strip().split(' ')
            if len(args) == num_args:
                card_name = ' '.join(args[0].split('_'))
                new_energy = int(args[1])
                cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute(f'''
UPDATE kebot_cards
SET top_energy = '{new_energy}'
WHERE card_name = '{card_name}';
''')
                    db.commit()
                    await ctx.send(f"Card '{card_name}' top energy has been changed to '{new_energy}'!")
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Card '{card_name}' does not exist!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"features expected: " + str(num_args) +
                                "\nfeatures received: " + str(len(args)),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to edit cards.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='edit-type', brief="Edit card", description="~edit-type name type")
    async def edit_card_type(self, ctx):
        num_args = 2
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "edit-type"):].strip().split(' ')
            if len(args) == num_args:
                card_name = ' '.join(args[0].split('_'))
                new_type = args[1]
                if new_type not in self.type:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"'{new_type}' is not a valid rarity.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
                    return
                new_type = self.type[new_type]
                cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute(f'''
UPDATE kebot_cards
SET card_type = '{new_type}'
WHERE card_name = '{card_name}';
''')
                    db.commit()
                    await ctx.send(f"Card '{card_name}' type has been changed to '{new_type}'!")
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Card '{card_name}' does not exist!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"features expected: " + str(num_args) +
                               "\nfeatures received: " + str(len(args)),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to edit cards.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='edit-series', brief="Edit card", description="~edit-series name series")
    async def edit_card_series(self, ctx):
        num_args = 2
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "edit-series"):].strip().split(' ')
            if len(args) == num_args:
                card_name = ' '.join(args[0].split('_'))
                new_series = args[1]
                cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute(f'''
UPDATE kebot_cards
SET card_series = '{new_series}'
WHERE card_name = '{card_name}';
''')
                    db.commit()
                    await ctx.send(f"Card '{card_name}' series has been changed to '{new_series}'!")
                else:
                    embed = discord.Embed(
                        title=f":knife: ERROR :knife:",
                        description=f"Card '{card_name}' does not exist!",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"features expected: " + str(num_args) +
                                "\nfeatures received: " + str(len(args)),
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to edit cards.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='edit-description', brief="Edit card", description="~edit-description name description")
    async def edit_card_description(self, ctx):
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            args = ctx.message.content[len(self.bot.command_prefix + "edit-description"):].strip().split(' ')
            card_name = ' '.join(args[0].split('_'))
            new_description = ' '.join(args[1:])
            cursor.execute(f"SELECT card_name FROM kebot_cards WHERE card_name = '{card_name}'")
            result = cursor.fetchone()
            if result is not None:
                cursor.execute(f'''
UPDATE kebot_cards
SET description = '{new_description}'
WHERE card_name = '{card_name}';
''')
                db.commit()
                await ctx.send(f"Card '{card_name}' description has been changed to '{new_description}'!")
            else:
                embed = discord.Embed(
                    title=f":knife: ERROR :knife:",
                    description=f"Card '{card_name}' does not exist!",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

            cursor.close()
            db.close()
        else:
            embed = discord.Embed(
                title=f":knife: ERROR :knife:",
                description=f"You don't have the authority to edit cards.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # V.v.V TEST
    @commands.command(name='test', help="A test command. Does nothing.")
    async def test(self, ctx, *args):
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            image = "confidence_booster_allen.png"
            embed = discord.Embed(
                title=f"Testing image",
                color=discord.Color.green()
            )
            file = discord.File("card_images/" + image, filename=image)
            embed.set_thumbnail(url=f"attachment://{image}")
            await ctx.send(file=file, embed=embed)

            cursor.close()
            db.close()

    @commands.command(name='compensate', brief="For bug fixes",
                      description="~compensate @user #")
    async def compensate(self, ctx, *args):
        if ctx.message.author.id == self.id["fufu"]:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            player = args[0]
            player = player[3:len(player) - 1]
            primosticks = args[1]
            cursor.execute(f'''
UPDATE kebot_users
SET primosticks = primosticks + {primosticks}
WHERE user_id = '{player}'
''')
            db.commit()
            await ctx.send(f"The player has received {primosticks} primosticks!")

            cursor.close()
            db.close()

    @commands.command(name='say', brief="For fun",
                      description="~say message")
    async def say(self, ctx, *args):
        if ctx.message.author.id == self.id["fufu"]:
            await ctx.message.delete()
            await ctx.send(' '.join(args))

def setup(bot):
    bot.add_cog(AdminCog(bot))
    print("Admin is loaded.")

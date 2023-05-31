# Shish KeBot
import os
import sqlite3
from dotenv import load_dotenv
from discord.ext import commands
import sys
import discord

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
intents.members = True
bot = commands.Bot(command_prefix='~', intents=intents)

'''
TABLE SCHEMAS

kebot
---------------
guild_id TEXT,
channel_id TEXT
========================================================================
kebot_users
---------------
user_id TEXT,
level INT,
total_cards INT,
battle_team TEXT,
primosticks INT,
daily INT
========================================================================
kebot_user_inv
---------------
user_id TEXT,
card_name TEXT,
card_quantity INT
========================================================================
kebot_cards
---------------
card_name TEXT,
image TEXT,
card_rarity TEXT,
top_energy INT,
card_type TEXT,
card_series TEXT,
description TEXT
========================================================================
kebot_battle
---------------
user_id TEXT,
battle_id TEXT,
battle_team TEXT,
selected_card INT,
grave TEXT,
score TEXT
'''

CARD_SPAWN_RATE = 1
UNCOMMON_RATE = 0.4
RARE_RATE = 0.1
EPIC_RATE = 0.02
LEGENDARY_RATE = 0.005
claimable = False
claimable_card = ""

initial_extensions = ["cogs.admin", "cogs.player", "cogs.general", "cogs.battle", "cogs.gacha"]

@bot.event
async def on_ready():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}", file=sys.stderr)
    create_database(False)
    check_database(False)
    edit_database(False)
    check_new_cards(False)
    reset_daily(True)
    print(f'{bot.user.name} has connected to Discord!')

def reset_daily(val: bool) -> None:
    if val:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        cursor.execute("SELECT user_id,daily FROM kebot_users")
        result = cursor.fetchall()
        for (user_id, daily) in result:
            sql = (f'''
UPDATE kebot_users
SET daily = 1
WHERE user_id = '{user_id}'
''')
            cursor.execute(sql)
            db.commit()

        cursor.close()
        db.close()


# V.v.V DATABASE
def create_database(val: bool) -> None:
    if val:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()

        cursor.execute('''
CREATE TABLE IF NOT EXISTS kebot_battle(
user_id TEXT,
battle_id TEXT,
battle_team TEXT,
selected_card INT,
grave TEXT,
score TEXT
)    
''')

        cursor.close()
        db.close()


def check_database(val: bool) -> None:
    if val:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT user_id,battle_team FROM kebot_users")
        result = cursor.fetchall()
        for (user_id, battle_team) in result:
            print(f"{user_id}")
        cursor.close()
        db.close()


def edit_database(val: bool) -> None:
    if val:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute('''
ALTER TABLE kebot_users
ADD april_fools_card TEXT DEFAULT ""
''')
        db.commit()
        cursor.close()
        db.close()


def check_new_cards(val: bool) -> None:
    if val:
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT card_name,image FROM kebot_cards")
        result = cursor.fetchall()
        all_good = True
        for (card_name, image) in result:
            if not os.path.isfile("card_images/" + image):
                if all_good:
                    print("Missing image for:")
                all_good = False
                print(card_name)
        if all_good:
            print("All cards look good!")
        cursor.close()
        db.close()


bot.run(TOKEN)

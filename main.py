import discord
from discord import app_commands
import mysql.connector
import random
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

base_dir = os.path.dirname(os.path.abspath(__file__))

def ensure_database():
    create_script = os.path.join(base_dir, "bot_db.sql")
    if not os.path.exists(create_script):
        raise FileNotFoundError(f"Database script not found: {create_script}")

    tmp_db = mysql.connector.connect(
        host="localhost",
        user="root",  
        password="admin123"  # WAIT I FORGOT MY PASSWORDD
    )
    tmp_cur = tmp_db.cursor()

    with open(create_script, "r", encoding="utf-8") as f:
        sql = f.read()

    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            tmp_cur.execute(stmt)
        except mysql.connector.Error as e:
            if e.errno in (1007, 1050, 1049):
                continue
            raise

    tmp_db.commit()
    tmp_cur.close()
    tmp_db.close()

ensure_database()

db = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="admin123",  # PASSWORDDDDDDDDD
    database="typing_bot"
)
cursor = db.cursor()

current_word = None
claimed = False
channel_id = 1288124712948  #enter YOUR dAMN CHANNel ID

words_file = os.path.join(base_dir, 'words.txt')
if not os.path.exists(words_file):
    raise FileNotFoundError(f"Words file not found: {words_file}")
with open(words_file, 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip()]

def generate_word():
    return random.choice(words)

def get_user(discord_id):
    cursor.execute("SELECT * FROM users WHERE discord_id = %s", (discord_id,))
    return cursor.fetchone()

def create_user(discord_id, username):
    cursor.execute("INSERT INTO users (discord_id, username, xp, level) VALUES (%s, %s, 0, 1)", (discord_id, username))
    db.commit()

def update_xp(discord_id, xp_gain):
    user = get_user(discord_id)
    if not user:
        return
    new_xp = user[3] + xp_gain
    new_level = (new_xp // 100) + 1
    cursor.execute("UPDATE users SET xp = %s, level = %s WHERE discord_id = %s", (new_xp, new_level, discord_id))
    db.commit()
    return new_level, user[4] != new_level

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await tree.sync()
    bot.loop.create_task(send_word_task())

async def send_word_task():
    await bot.wait_until_ready()
    channel = bot.get_channel(channel_id)
    while True:
        global current_word, claimed
        current_word = generate_word()
        claimed = False
        await channel.send(f"Type the word: **{current_word}**")
        await asyncio.sleep(random.randint(250, 350))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    global current_word, claimed
    if message.content.lower() == current_word and not claimed:
        claimed = True
        xp_gain = 10
        user = get_user(message.author.id)
        if not user:
            create_user(message.author.id, str(message.author))
        level, leveled_up = update_xp(message.author.id, xp_gain)
        response = f"{message.author.mention} typed it first! +{xp_gain} XP!"
        if leveled_up:
            response += f" You leveled up to level {level}!"
        await message.channel.send(response)
        current_word = None

@tree.command(name="leaderboard", description="Show the XP leaderboard")
async def leaderboard(interaction):
    cursor.execute("SELECT username, xp, level FROM users ORDER BY xp DESC LIMIT 10")
    results = cursor.fetchall()
    embed = discord.Embed(title="Leaderboard", color=0x00ff00)
    for i, (username, xp, level) in enumerate(results, 1):
        embed.add_field(name=f"{i}. {username}", value=f"Level {level} - {xp} XP", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run('BOT TOKEN')  #bot token GOES IN HERE NIGGER

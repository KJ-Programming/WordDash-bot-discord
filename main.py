import discord
from discord import app_commands
import psycopg2
import random
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

base_dir = os.path.dirname(os.path.abspath(__file__))

def ensure_database():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Create tables if they don't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            discord_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(255) NOT NULL,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id SERIAL PRIMARY KEY,
            word VARCHAR(50) NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()

# Remove ensure_database() call here

# db connection will be established in on_ready

current_word = None
claimed = False
channel_id = int(os.getenv('CHANNEL_ID', '1288124712948'))  # Default if not set

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
    
    # Initialize database after bot is ready
    global db, cursor
    ensure_database()
    db = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = db.cursor()
    
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
    
TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)  #bot token GOES IN HERE NIGGER

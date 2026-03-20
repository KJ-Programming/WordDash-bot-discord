A Discord bot that sends random 10-letter words every 25-30 minutes. The first person to type the word gets XP and levels up.


1. Install dependencies: `pip install -r ../requirements.txt`

2. Set up the database: Run `bot_db.sql` in MySQL to create the database and tables.

3. Create a Discord bot at https://discord.com/developers/applications and get the token.

4. Replace `YOUR_BOT_TOKEN` in `main.py` with your bot token.

5. Replace `channel_id` with the ID of the channel where the bot should send messages.

6. Run the bot: `python main.py`

- Sends a random word every 25-30 minutes.
- Awards 10 XP to the first person who types the word.
- Leveling system: Level = XP // 100 + 1
- /leaderboard command to view top players.
- Uses MySQL database `typing_bot`.
- Tables: `users` (discord_id, username, xp, level), `words` (for future use).

## THANKS TO KJ FOR HELPING OUT
import discord
from discord.ext import commands
from discord.ext.commands import Context
from config import your_guild_id
from datetime import datetime
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('database/message_data.db')
cursor = conn.cursor()


# Create a table to store user message counts if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS message_counts (
                    user_id INTEGER PRIMARY KEY,
                    message_count INTEGER
                )''')


class levelling(commands.Cog, name="levelling"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.leveldata = {}
    @commands.Cog.listener()
    async def on_message(self, message):
        # Update message count in the database for the user
        cursor.execute('INSERT OR IGNORE INTO message_counts (user_id, message_count) VALUES (?, 0)', (message.author.id,))
        cursor.execute('UPDATE message_counts SET message_count = message_count + 1 WHERE user_id = ?', (message.author.id,))
        conn.commit()
    @commands.hybrid_command(
        name="rank",
        description="Check your rank on the server",
    )
    async def rank(self, context: Context) -> None:
        cursor.execute('SELECT message_count FROM message_counts WHERE user_id = ?', (context.author.id,))
        result = cursor.fetchone()

        if result:
            xp = result[0]
            lvl = 0
            while True:
                if xp < ((50 * (lvl**2)) + (50 * lvl)):
                    break
                lvl += 1
            xp_for_level = 200 * (1/2) * lvl
            xp_remaining = xp - (50 * ((lvl - 1)**2) + 50 * (lvl - 1))
            boxes = int((xp_remaining / xp_for_level) * 10)

            filled_emoji = "<:levelbarmiddlefilled:1211344248025382992>"
            unfilled_emoji = "<:levelbarmiddlenofull:1211344243201933412>"
            start_emoji = "<:levelbarfullstart:1211344244862619658>"
            end_emoji = "<:levelbarendnotfull:1211344504234188841>"
            middle_emoji = "<:levelbarmiddle:1211344246443872287>"

            progress_bar = start_emoji + (boxes-1)*filled_emoji + middle_emoji + unfilled_emoji*(10-boxes) + end_emoji

            embed = discord.Embed(title="", description=f"# {context.author.name}", color=discord.Colour(int("2B2D31", 16)))
            embed.add_field(name=f"<:greydot:1211378596434944010> XP: {xp}/{int(xp_for_level)}", value="", inline=False)
            embed.add_field(name=f"<:greydot:1211378596434944010> Level: {lvl}", value="", inline=False)
            
            # Calculate rank based on XP
            sorted_users = sorted(self.leveldata.items(), key=lambda x: x[1], reverse=True)
            user_ids = [user[0] for user in sorted_users]
            
            try:
                rank = user_ids.index(context.author.id) + 1
                embed.add_field(name="Rank", value=f"{rank}/{len(sorted_users)}", inline=True)
            except ValueError:
                pass

            embed.add_field(name="", value=progress_bar, inline=False)
            embed.set_thumbnail(url=context.author.display_avatar)

            await context.send(embed=embed)
        else:
            await context.send("You don't have a rank currently. Keep chatting to earn XP!")
    @commands.Cog.listener()
    async def on_disconnect():
        conn.close()


async def setup(bot) -> None:
    await bot.add_cog(levelling(bot))

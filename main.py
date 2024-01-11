from settings import *
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.bot(command_prefix = ",", intents = intents)

bot.event()
async def on_ready():
  print(bot.user, bot.user.id)
  print("__________")

bot.run(DISCORD_API_SECRET)

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv
from utils.database import get_prefix

load_dotenv(find_dotenv())
token = os.getenv('token')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=get_prefix, case_insensitive="true", intents=intents)
bot.remove_command("help")

@commands.has_permissions(ban_members=True)
@bot.command()
async def load(ctx, extension):
  bot.load_extension(f"cogs.{extension}")

@commands.has_permissions(ban_members=True)
@bot.command()
async def unload(ctx, extension):
  bot.unload_extension(f"cogs.{extension}")

@commands.has_permissions(ban_members=True)
@bot.command()
async def reload(ctx):
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      bot.unload_extension(f"cogs.{filename[:-3]}")
      bot.load_extension(f"cogs.{filename[:-3]}")

for i in os.listdir('./cogs'):
  if str(i) in ['__pycache__']:
    pass
  else:
    print('loaded ', i)
    bot.load_extension(f'cogs.{i[:-3]}')

bot.run(token)
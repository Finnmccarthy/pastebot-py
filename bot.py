import discord
from discord import client
from discord import message
from discord.ext import commands
from discord_slash import SlashCommand
import logging
import json
from pathlib import Path
from datetime import datetime
import asyncio

description = 'A Discord PasteBin Bot'

# Date & Time Variable
timestamp = datetime.now()
gettime = timestamp.strftime(r"%d/%m/%Y %I:%M%p")

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")

bot = discord.Client()
config_file = json.load(open(cwd+'/bot_config/config.json'))
bot.config_prefix = config_file['prefix']
intents = discord.Intents.all()
bot = commands.Bot(bot.config_prefix, intents=intents, description=description, case_insensitive=True)
slash = SlashCommand(bot)

# Token
token_file = json.load(open(cwd+'/bot_config/token.json'))
bot.token_file = token_file['token']
logging.basicConfig(level=logging.INFO)

# Bot ready log
@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nCurrent prefix = {config_file['prefix']} & /\n-----\nDate & Time: {gettime}\n-----\nBot is ready\n-----")

# Commands

# Ping
@slash.slash(name='ping', description='Bot Latency Test')
async def ping(message):
    await message.channel.send(f"Pong! {round(bot.latency * 1000)}ms")


@bot.command(name='create', description='Creates a private text channel to use as a PasteBin')
async def create(ctx):
    author = ctx.author.name
    channel = discord.utils.get(bot.get_all_channels(), name=ctx.author.name.lower())
    if (channel is None):
        guild = ctx.message.guild
        category = discord.utils.get(ctx.guild.categories, name="userbins")
        await guild.create_text_channel(f"{author}", category=category)

    else:
        await ctx.channel.send(f"You've already created a channel, check under the UserBins category")
        return

@bot.command(name='author')
async def author(ctx):
    author = ctx.author
    await ctx.channel.send(f"{author}")







# Auto Role on Join
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=config_file['autorole'])
    joined = (f"{gettime}: {member} joined the server and was given {role} role.\n")
    await member.add_roles(role)
    with open('cache/logs.txt', 'a') as f:
        f.write(joined)
    print(joined)

# Bot Login
bot.run(bot.token_file)
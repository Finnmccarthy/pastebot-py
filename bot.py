import asyncio
import discord
from discord import client
from discord import message
from discord.abc import GuildChannel
from discord.ext import commands
from discord.utils import get
from discord_slash import SlashCommand
import logging
import json
from pathlib import Path
from datetime import datetime
from threading import Timer
import time

description = 'A Discord PasteBin Bot'

# Date & Time Variable
timestamp = datetime.now()
gettime = timestamp.strftime(r"%d/%m/%Y %I:%M%p")

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")

intents = discord.Intents.all()

bot = discord.Client()
config_file = json.load(open(cwd+'/bot_config/config.json'))
bot.config_prefix = config_file['prefix']
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

# Create a new paste bin channel
@bot.command(name='create', description='Creates a private text channel to use as a PasteBin')
async def create(ctx):
    # Caches author & channel
    author = ctx.author.name.lower()
    author_id = ctx.author.id
    channel = discord.utils.get(ctx.guild.channels, name=author)
    if (channel is None):

        # Deletes user message
        await ctx.message.delete()
        
        guild = ctx.message.guild
        category = discord.utils.get(ctx.guild.categories, name="userbins")

        # Overwrides channel permission & adds author to channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True)
        }
        
        # Creates channel
        await guild.create_text_channel(f"{author}", category=category, overwrites=overwrites)
        

        channel_existing = discord.utils.get(ctx.guild.channels, name=author)
        channel_id = channel_existing.id
        author_channel = bot.get_channel(channel_id)
        emb = discord.Embed(description="This channel will be automaticlly deleted after 10 Minutes. If you wish to delete it sooner, react to this message :recycle:", color=0x4287f5)
        msg = await author_channel.send(embed=emb)
        emoji = '♻️'
        await msg.add_reaction(emoji)

        with open("bindb.json", 'a+') as f:

            new_bin_channel = {
                "author": author_id,
                "channel_id": channel_id,
                "message_id": msg.id
            }

            json.dump(new_bin_channel, f, indents=4)


        # Posts confirmation of channel creation
        embededvar0 = discord.Embed(title="PasteBin Created", description=f"{ctx.author.mention}", color=0x2bd642)
        await ctx.send(embed=embededvar0)

        # Deletes channel after 10 Minutes        
        await asyncio.sleep(10) 
        await channel_existing.delete()
        

    else:
        # Error message
        embededvar1 = discord.Embed(title="Error", description="You already have a channel created, check under the UserBins category", color=0xFF0000)
        await ctx.channel.send(embed=embededvar1, delete_after=15)
       
        await ctx.message.delete()
        return


@bot.event
async def on_raw_reaction_delete(payload):
    if payload.member.bot:
        pass

    else:
        emoji = '♻️'
        if [emoji] == payload.emoji.name:
            channel = bot.get_channel(payload.channel_id)
            await channel.delete()




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
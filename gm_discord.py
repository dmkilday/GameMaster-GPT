# Refer to https://github.com/kkrypt0nn/Python-Discord-Bot-Template/blob/main/bot.py for complex example
#
# Other resources:
# https://discordpy.readthedocs.io/en/stable/quickstart.html
# https://discordpy.readthedocs.io/en/stable/api.html
# https://superfastpython.com/asyncio-return-value/
#
# Right now requires message_content intents on the bot creation page at https://discord.com/developers/applications.

import asyncio
import platform
import os
import random
import sys

from dotenv import load_dotenv
import openai
import discord

from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

import chat
import messages
import utils

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = Bot(
    command_prefix=commands.when_mentioned_or("$"),
    intents=intents,
    help_command=None,
)


@bot.event
async def on_ready() -> None:
    print(f'We have logged in as {bot.user.name}')
    print(f'discord.py API version: {discord.__version__}')
    print(f'Python version: {platform.python_version()}')
    print(f'Running on: {platform.system()} {platform.release()} ({os.name})')
    
@bot.event
async def on_message(message:discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
        return
    response = await openai_pass_along(message)
    
    await message.channel.send(response)
    
@bot.event
async def on_command_completion(context: Context) -> None:
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        print(f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")
    else:
        print(f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs")

async def openai_pass_along(message) -> None:
    if message.content == "$exit":
        exit() # Ugly exit with no exception handling.
        
    ooc_dialog = [
        {"role":"system",
            "content":message.content
        }
    ]
        
    completion = chat.safe_chat_completion(
        model="gpt-3.5-turbo",
        messages = ooc_dialog
    )
    if completion == -1:
        return
        
    # Capture the AI's response
    assistant_msg = chat.get_content(completion)

    # Append the user input to the ongoing ooc_dialog
    ooc_dialog.append({"role": "assistant", "content": assistant_msg})
    return assistant_msg
    
    
bot.run(DISCORD_TOKEN)
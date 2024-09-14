# main.py
import os
import discord
from discord.ext import commands


TOKEN = os.getenv("DISCORD_TOKEN")

bot = discord.Client()


class DiscordBot(discord.Client):
    async def on_ready(self):
        #todo logging

    async def on_message(message):
        #todo send message to specified channel, maybe respond to initial message after some time?


if __name__ = "__main__":
    bot.run(TOKEN)

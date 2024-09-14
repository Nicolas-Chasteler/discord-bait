# main.py
import os
import discord
import logging
import utils
from discord.ext import commands

logger = PostgresLogger.initialize_logger()

TOKEN = os.getenv("DISCORD_TOKEN")


class DiscordBot(discord.Client):
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}. ID: {self.user.id}")

    async def on_message(message):
        #todo send message to specified channel, maybe respond to initial message after some time?


def main():
    bot = DiscordBot()
    bot.run(TOKEN)

if __name__ = "__main__":
    main()


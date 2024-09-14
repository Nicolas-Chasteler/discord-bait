# main.py
import os
import discord
import logging
from utils.postgreslogger import PostgresLogger
from discord.ext import commands

logger = PostgresLogger.initialize_logger()

TOKEN = os.getenv("DISCORD_TOKEN")


class DiscordBot(discord.Client):
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}. ID: {self.user.id}")

    async def on_message(self, message):
        logger.debug(f"Received message: {message}")
        author = message.author.id
        await self.send_message(message.channel, f"<@{author}> Hello!")
        #todo send message to specified channel, maybe respond to initial message after some time?


def main():
    bot = DiscordBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()


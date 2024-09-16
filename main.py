# main.py
import os
import discord
from utils.pglogger import logger
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

class DiscordBot(discord.Client):
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}. ID: {self.user.id}")

    async def on_message(self, message):
        logger.debug(f"Received message: {message.content}, {message}")
        if message.author == self.user:
            return

        # Regular message types
        if message.type in {discord.MessageType.default, discord.MessageType.reply}:
            logger.debug(f"User message: {message.type}, {message}")
            author = message.author.id
            await message.channel.send(f"<@{author}> Hello!")

        # System message types
        else:
            logger.debug(f"System message: {message.type}, {message}")


        #todo send message to specified channel, maybe respond to initial message after some time?


def main():
    bot = DiscordBot()
    print("test to see if ci/cd is working")
    bot.run(TOKEN)

if __name__ == "__main__":
    main()


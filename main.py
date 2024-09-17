# main.py
import os
import discord
from utils.pglogger import logger
from utils.discord_message_handler import save_message
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
HOST_CHANNEL = os.getenv("HOST_CHANNEL")

class DiscordBot(discord.Client):
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}. ID: {self.user.id}")

    async def on_message(self, message):
        logger.debug(f"Message {message.author.name}: {message.content}")
        save_message(message)

        # Received a DM
        if isinstance(message.channel, discord.DMChannel):
            host = self.get_channel(HOST_CHANNEL)

            if host is None:
                logger.warning(f"Host channel not found: {HOST_CHANNEL}")
                return

            attachments = []
            if message.attachments:
                for attachment in message.attachments:
                    file_buffer = BytesIO()
                    await attachment.save(file_buffer)
                    attachments.append(file_buffer)

            await host.send(content=f"<@{message.author.id}>: {message.content}", files=attachments)


def main():
    bot = DiscordBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()


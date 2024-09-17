# main.py
import os
from io import BytesIO
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
        await save_message(message)

        # Stop processing messages from bots
        if message.author.bot:
            return

        # Received a DM
        if isinstance(message.channel, discord.DMChannel):
            host = self.get_channel(int(HOST_CHANNEL))

            # Validate host channel exists
            if host is None:
                logger.warning(f"Host channel not found: {HOST_CHANNEL}")
                return

            # Validate host channel is a text channel
            if not isinstance(host, discord.TextChannel):
                logger.warning(f"Host channel is not a text channel {host}")
                return

            # Check for existance of message thread, if none exist create one

            # Create new thread
            msg = await host.send(content=f"<@{message.author.id}> started a DM")
            thread = await msg.create_thread(name=f"{message.author.name}")





            # Save and process attachments
            attachments = []
            if message.attachments:
                for attachment in message.attachments:
                    attachment_bytes = await attachment.read()
                    byte_io = BytesIO(attachment_bytes)
                    discord_file = discord.File(byte_io, filename=attachment.filename)
                    attachments.append(discord_file)

            await host.send(content=f"<@{message.author.id}>: {message.content}", files=attachments)


def main():
    bot = DiscordBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()


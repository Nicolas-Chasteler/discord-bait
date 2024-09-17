# main.py
import os
from io import BytesIO
import discord
from utils.pglogger import logger
from utils.discord_message_handler import save_message, save_thread, find_thread_id
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

        # Received thread message


        # Received a DM
        if isinstance(message.channel, discord.DMChannel):
            host = await self.pull_channel(int(HOST_CHANNEL))

            # Validate host channel is a text channel
            if not isinstance(host, discord.TextChannel):
                logger.warning(f"Host channel is not a text channel {host}")
                return

            # Check for existance of message thread, if none exist create one
            thread_id = find_thread_id(message)
            if thread_id:
                logger.debug(f"Found thread in DB {thread_id}")
                thread_id = await self.pull_channel(thread_id)

            # Create new thread if no thread exists or if unable to fetch thread
            if not thread_id:
                logger.debug(f"Unable to pull any thread {thread_id}")
                msg = await host.send(content=f"<@{message.author.id}> started a DM")
                thread = await msg.create_thread(name=f"{message.author.name}")
                save_thread(thread, message)
                logger.debug(f"Created thread {thread.channel.id}")
            else:
                thread = thread_id
                logger.debug(f"Found existing thread {thread.channel.id}")

            # Save and process attachments
            attachments = []
            if message.attachments:
                for attachment in message.attachments:
                    attachment_bytes = await attachment.read()
                    byte_io = BytesIO(attachment_bytes)
                    discord_file = discord.File(byte_io, filename=attachment.filename)
                    attachments.append(discord_file)

            await thread.send(content=f"<@{message.author.id}>: {message.content}", files=attachments)

    async def pull_channel(self, id):
        host = self.get_channel(id)

        # Validate host channel exists
        if host is None:
            # Try to fetch channel from discord API directly
            try:
                host = await self.fetch_channel(id)
            except discord.NotFound:
                logger.warning(f"Host channel not found: {id}")
                return None
            except discord.Forbidden:
                logger.warning(f"Bot does not have permission for channel: {id}")
                return None
            except discord.HTTPException as e:
                logger.warning(f"HTTP Exception: {e}")
                return None
        return host




def main():
    bot = DiscordBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()


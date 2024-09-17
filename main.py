# main.py
import os
from io import BytesIO
import discord
import asyncio
from utils.pglogger import logger
from utils.discord_message_handler import save_message, save_thread, find_thread_id_from_channel, find_channel_id_from_thread
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
HOST_CHANNEL = os.getenv("HOST_CHANNEL")

class DiscordBot(discord.Client):
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}. ID: {self.user.id}")

    async def on_message(self, message):
        logger.debug(f"Message {message.author.name}: {message.content}")
        await save_message(message)
        channel = message.channel

        # Stop processing messages from bots
        if message.author.bot:
            return

        # Received thread message
        if isinstance(channel, discord.Thread):

            # Stop processing if message is from bot
            if message.author == self.user:
                return

            # Return if thread is not owned by bot
            if channel.owner_id != self.user.id:
                return

            # Find user chat and send them the message contents
            channel_id = find_channel_id_from_thread(channel)
            dm_channel = await self.pull_channel(channel_id)
            if not dm_channel:
                logger.error(f"No thread info found")
            await dm_channel.send(message.content)

            # Attempt to delete persons message
            return # Disabled cause no perms
            try:
                await message.delete()
            except discord.Forbidden:
                logger.warning(f"Bot doesn't have permission to delete message")
            except discord.NotFound:
                logger.warning(f"Message was not found or has been deleted")
            except discord.HTTPException as e:
                logger.warning(f"Failed to delete due to error: {e}")

        # Received a DM
        if isinstance(channel, discord.DMChannel):
            host = await self.pull_channel(int(HOST_CHANNEL))

            # Validate host channel is a text channel
            if not isinstance(host, discord.TextChannel):
                logger.warning(f"Host channel is not a text channel {host}")
                return

            # Check for existance of message thread, if none exist create one
            thread_id = find_thread_id_from_channel(channel)
            if thread_id:
                logger.debug(f"Found thread in DB {thread_id}")
                thread_id = await self.pull_channel(thread_id)

            # Create new thread if no thread exists or if unable to fetch thread
            if not thread_id:
                logger.debug(f"Unable to pull any thread {thread_id}")
                msg = await host.send(content=f"<@{channel.recipient.id}> started a DM")
                thread = await msg.create_thread(name=f"{channel.recipient.name}")
                save_thread(thread, channel)
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

    @tasks.loop(seconds=60)
    async def poll_friend_requests(self):
        logger.debug(f"Polling for new friend requests")
        for relationship in self.user.relationships:
            if relationship.type == discord.RelationshipType.incoming_request:
                try:
                    await asyncio.sleep(15)
                    await relationship.accept()
                    logger.debug(f"Accepted friend request from {relationship.user.name}")
                    await relationship.user.send(f"Howdy!")
                except Exception as e:
                    logger.warning(f"Failed to accept friend request: {e}")

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


# utils/discord_message_handler.py
import discord
from io import BytesIO
from utils.pglogger import logger
from pygres import PostgresHandler

async def save_message(message):
    conn = PostgresHandler().get_cursor().connection
    cursor = conn.cursor()

    # Parse and save messages
    message_values = (
        message.id,
        message.content,
        message.author.id,
        message.author.name,
        message.channel.id,
        str(message.channel),
        message.guild.id if message.guild else None,
        message.guild.name if message.guild else None,
        message.created_at,
        message.edited_at,
        bool(message.attachments)
    )
    insert_message = """
        INSERT INTO discord_messages (message_id, content, author_id, author_name, channel_id, channel_name, guild_id, guild_name, created_at, edited_at, has_attachments)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_message, message_values)
    conn.commit()

    # Parse and save attachments for DMS only
    if isinstance(message.channel, discord.DMChannel) and message.attachments:
        for attachment in message.attachments:
            file_buffer = BytesIO()
            await attachment.save(file_buffer)

            message_values = (
                attachment.filename,
                file_buffer.getvalue(),
                attachment.content_type,
                message.id
            )
            insert_message = """
                INSERT INTO discord_attachments (filename, file_data, content_type, message_id)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_message, message_values)
            conn.commit()

def find_thread_id_from_channel(channel):
    conn = PostgresHandler().get_cursor().connection
    cursor = conn.cursor()

    select_message = """
        SELECT thread_id
        FROM discord_threads
        WHERE channel_id = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """
    cursor.execute(select_message, (channel.id,))
    thread_id = cursor.fetchone()

    if thread_id:
        return thread_id[0]
    else:
        return None

def find_channel_id_from_thread(thread):
    conn = PostgresHandler().get_cursor().connection
    cursor = conn.cursor()

    select_message = """
        SELECT channel_id
        FROM discord_threads
        WHERE thread_id = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """
    cursor.execute(select_message, (thread.id,))
    thread_id = cursor.fetchone()

    if thread_id:
        return thread_id[0]
    else:
        return None

def save_thread(thread, channel):
    conn = PostgresHandler().get_cursor().connection
    cursor = conn.cursor()
    message_values = (
        thread.id,
        channel.recipient.id,
        channel.recipient.name,
        channel.id,
        str(channel),
        thread.created_at
    )
    insert_message = """
        INSERT INTO discord_threads (thread_id, user_id, user_name, channel_id, channel_name, created_at)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_message, message_values)
    conn.commit()




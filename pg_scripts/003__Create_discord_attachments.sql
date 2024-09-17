CREATE TABLE discord_attachments (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    file_data BYTEA,
    content_type TEXT,
    message_id BIGINT
);
CREATE TABLE discord_threads (
    thread_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    user_name VARCHAR(255),
    channel_id BIGINT,
    channel_name VARCHAR(255),
    created_at TIMESTAMP
);
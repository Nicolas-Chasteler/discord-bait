ALTER TABLE discord_attachments
ADD CONSTRAINT fk_message_id
FOREIGN KEY (message_id)
REFERENCES discord_messages(message_id)
ON DELETE CASCADE;
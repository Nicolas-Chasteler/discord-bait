CREATE TABLE discord_messages (
    message_id BIGINT PRIMARY KEY,      
    content TEXT,               
    author_id BIGINT,           
    author_name VARCHAR(255),   
    channel_id BIGINT,          
    channel_name VARCHAR(255),  
    guild_id BIGINT,            
    guild_name VARCHAR(255),    
    created_at TIMESTAMP,       
    edited_at TIMESTAMP,        
    has_attachments BOOLEAN     
);
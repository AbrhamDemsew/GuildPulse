"""Database schema definitions and migrations."""

SCHEMA_VERSION = 2

CREATE_TABLES_V1 = """
CREATE TABLE IF NOT EXISTS channels (
    channel_id INTEGER PRIMARY KEY,
    messages TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_channels_channel_id ON channels(channel_id);
"""

CREATE_TABLES_V2 = """
CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id INTEGER PRIMARY KEY,
    system_prompt TEXT NOT NULL,
    model_name TEXT NOT NULL,
    max_history INTEGER NOT NULL DEFAULT 100,
    max_tokens INTEGER NOT NULL DEFAULT 500,
    temperature REAL NOT NULL DEFAULT 0.7,
    moderation_enabled INTEGER NOT NULL DEFAULT 1,
    knowledge_enabled INTEGER NOT NULL DEFAULT 1,
    daily_message_quota INTEGER NOT NULL DEFAULT 500,
    daily_token_quota INTEGER NOT NULL DEFAULT 100000,
    allowed_channel_ids TEXT NOT NULL DEFAULT '[]',
    admin_role_ids TEXT NOT NULL DEFAULT '[]',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS moderation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    content_preview TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_moderation_guild ON moderation_log(guild_id);
CREATE INDEX IF NOT EXISTS idx_moderation_user ON moderation_log(user_id);

CREATE TABLE IF NOT EXISTS usage_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    message_count INTEGER NOT NULL DEFAULT 1,
    recorded_on DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_usage_guild_day ON usage_records(guild_id, recorded_on);
CREATE INDEX IF NOT EXISTS idx_usage_user_day ON usage_records(user_id, recorded_on);

CREATE TABLE IF NOT EXISTS user_rate_limits (
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    window_start TIMESTAMP NOT NULL,
    message_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, guild_id)
);

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'manual',
    content TEXT NOT NULL,
    created_by INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_guild ON knowledge_documents(guild_id);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_estimate INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_guild ON knowledge_chunks(guild_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON knowledge_chunks(document_id);
"""

MIGRATIONS = [
    (1, CREATE_TABLES_V1),
    (2, CREATE_TABLES_V2),
]

-- Drop all database objects in reverse order of creation
-- to avoid foreign key constraint violations

-- First drop views
DROP VIEW IF EXISTS Recent_Chat_Messages;

-- Drop triggers
DROP TRIGGER IF EXISTS trg_update_balance;

-- Drop functions
DROP FUNCTION IF EXISTS get_total_points_sent;

-- Drop indexes
DROP INDEX IF EXISTS idx_user_email ON User;
DROP INDEX IF EXISTS idx_user_discord_id ON User;
DROP INDEX IF EXISTS idx_virtual_character_name ON Virtual_Character;
DROP INDEX IF EXISTS idx_transaction_sender ON Transaction;
DROP INDEX IF EXISTS idx_transaction_receiver ON Transaction;
DROP INDEX IF EXISTS idx_message_from_user ON Message;
DROP INDEX IF EXISTS idx_interaction_time ON Interaction;
DROP INDEX IF EXISTS idx_affinity_value ON Affinity;

-- Drop tables with foreign key constraints first
DROP TABLE IF EXISTS Affinity;
DROP TABLE IF EXISTS Customization;
DROP TABLE IF EXISTS Memory;
DROP TABLE IF EXISTS Interaction;
DROP TABLE IF EXISTS Chat_Session;
DROP TABLE IF EXISTS Message;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Virtual_Character;
DROP TABLE IF EXISTS User;
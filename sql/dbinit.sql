DROP DATABASE IF EXISTS chatgame;
CREATE DATABASE chatgame;
USE chatgame;

-- create tables
CREATE TABLE User
(
    user_id           CHAR(36) PRIMARY KEY,
    discord_id        VARCHAR(100) UNIQUE NOT NULL,
    username          VARCHAR(100)        NOT NULL,
    points_balance    INT     DEFAULT 0,
    current_character CHAR(36),
    is_admin          BOOLEAN DEFAULT FALSE
);

CREATE TABLE Virtual_Character
(
    character_id  CHAR(36) PRIMARY KEY,
    name          VARCHAR(100) UNIQUE NOT NULL,
    description   TEXT                NOT NULL,
    settings      TEXT                NOT NULL,
    creator_id    CHAR(36)            NOT NULL,
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES User (user_id)
);

CREATE TABLE Transaction
(
    transaction_id CHAR(36) PRIMARY KEY,
    sender_id      CHAR(36)       NOT NULL,
    receiver_id    CHAR(36)       NOT NULL,
    amount         DECIMAL(10, 2) NOT NULL,
    time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES User (user_id),
    FOREIGN KEY (receiver_id) REFERENCES User (user_id)
);

-- Moving Chat_Session before Message to fix circular reference
CREATE TABLE Chat_Session
(
    session_id   CHAR(36) PRIMARY KEY,
    user_id      CHAR(36) NOT NULL,
    character_id CHAR(36) NOT NULL,
    is_active    BOOLEAN   DEFAULT TRUE,
    start_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (user_id),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character (character_id)
);

CREATE TABLE Message
(
    session_id CHAR(36) NOT NULL,
    message_id CHAR(36),
    from_user  CHAR(36),
    content    TEXT     NOT NULL,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, message_id),
    FOREIGN KEY (from_user) REFERENCES User (user_id),
    FOREIGN KEY (session_id) REFERENCES Chat_Session (session_id)
);

CREATE TABLE Interaction
(
    user_id      CHAR(36)     NOT NULL,
    character_id CHAR(36)     NOT NULL,
    timestamp    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action       VARCHAR(100) NOT NULL,
    context      TEXT,
    PRIMARY KEY (user_id, character_id, timestamp),
    FOREIGN KEY (user_id) REFERENCES User (user_id),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character (character_id)
);

CREATE TABLE Memory
(
    user_id      CHAR(36) NOT NULL,
    character_id CHAR(36) NOT NULL,
    summary_text TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, character_id),
    FOREIGN KEY (user_id) REFERENCES User (user_id),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character (character_id)
);

CREATE TABLE Customization
(
    user_id      CHAR(36)     NOT NULL,
    character_id CHAR(36)     NOT NULL,
    attribute    VARCHAR(100) NOT NULL,
    value        VARCHAR(100),
    PRIMARY KEY (user_id, character_id, attribute),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character (character_id)
);

CREATE TABLE Affinity
(
    character_id CHAR(36) NOT NULL,
    user_id      CHAR(36) NOT NULL,
    value        INT CHECK (value BETWEEN 0 AND 100),
    PRIMARY KEY (user_id, character_id),
    FOREIGN KEY (user_id) REFERENCES User (user_id),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character (character_id)
);
-- create index
CREATE INDEX idx_user_discord_id ON User (discord_id);
CREATE INDEX idx_virtual_character_name ON Virtual_Character (name);
CREATE INDEX idx_transaction_sender ON Transaction (sender_id);
CREATE INDEX idx_transaction_receiver ON Transaction (receiver_id);
CREATE INDEX idx_message_from_user ON Message (from_user);
CREATE INDEX idx_interaction_time ON Interaction (timestamp);
CREATE INDEX idx_affinity_value ON Affinity (value);

-- view: messages in recent 24 hours
CREATE VIEW Recent_Chat_Messages AS
SELECT cs.session_id, m.content
FROM Chat_Session cs
         JOIN Message m ON m.timestamp > NOW() - INTERVAL 24 HOUR;

-- trigger 
-- auto update points after each balance
# DELIMITER $$
# CREATE TRIGGER trg_update_balance
# AFTER INSERT ON Transaction
# FOR EACH ROW
# BEGIN
#     UPDATE User
#     SET points_balance = points_balance - NEW.amount
#     WHERE user_id = NEW.sender_id;
#
#     UPDATE User
#     SET points_balance = points_balance + NEW.amount
#     WHERE user_id = NEW.receiver_id;
# END$$
#
# DELIMITER ;

-- function
DELIMITER $$

CREATE FUNCTION get_total_points_sent(uid INT)
    RETURNS DECIMAL(10, 2)
    DETERMINISTIC
    READS SQL DATA
BEGIN
    DECLARE total DECIMAL(10, 2);

    SELECT IFNULL(SUM(amount), 0)
    INTO total
    FROM Transaction
    WHERE sender_id = uid;

    RETURN total;
END$$

DELIMITER ;

-- insert the system user
INSERT INTO User (user_id, discord_id, username, points_balance, is_admin)
VALUES ('00000000-0000-0000-0000-000000000000', '', 'System', 0, TRUE);

-- insert the default character
INSERT INTO Virtual_Character (character_id, name, description, settings, creator_id)
VALUES ('00000000-0000-0000-0000-000000000000', 'Default Character', 'This is a default character.',
        'You are a friendly and helpful personal assistant for the user, but you never reveal your identity as a bot.',
        '00000000-0000-0000-0000-000000000000');

INSERT INTO Virtual_Character (character_id, name, description, settings, creator_id)
VALUES ('00000000-0000-0000-0000-000000000001', 'King Husky', 'Northeastern.',
        'You are King Husky, mascot of Northeastern University. You are a husky dog who knows everything NEU.',
        '00000000-0000-0000-0000-000000000000');
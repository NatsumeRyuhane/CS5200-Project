-- create tables
CREATE TABLE User (
    user_id INT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    points_balance INT DEFAULT 0,
    discord_id VARCHAR(100) UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE Virtual_Character (
    character_id INT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE Transaction (
    transaction_id INT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES User(user_id),
    FOREIGN KEY (receiver_id) REFERENCES User(user_id)
);

CREATE TABLE Message (
    message_id INT PRIMARY KEY,
    from_user INT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_user) REFERENCES User(user_id)
);

CREATE TABLE Chat_Session (
    session_id INT PRIMARY KEY,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Interaction (
    user_id INT NOT NULL,
    character_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action VARCHAR(100) NOT NULL,
    context TEXT,
    PRIMARY KEY (user_id, character_id, timestamp),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character(character_id)
);

CREATE TABLE Memory (
    user_id INT NOT NULL,
    character_id INT NOT NULL,
    summary_text TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, character_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character(character_id)
);

CREATE TABLE Customization (
    character_id INT NOT NULL,
    attribute VARCHAR(100) NOT NULL,
    value VARCHAR(100),
    PRIMARY KEY (character_id, attribute),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character(character_id)
);

CREATE TABLE Affinity (
    user_id INT NOT NULL,
    character_id INT NOT NULL,
    value DECIMAL(3, 2),
    PRIMARY KEY (user_id, character_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (character_id) REFERENCES Virtual_Character(character_id)
);

-- create index
CREATE INDEX idx_user_email ON User(email);
CREATE INDEX idx_user_discord_id ON User(discord_id);
CREATE INDEX idx_virtual_character_name ON Virtual_Character(name);
CREATE INDEX idx_transaction_sender ON Transaction(sender_id);
CREATE INDEX idx_transaction_receiver ON Transaction(receiver_id);
CREATE INDEX idx_message_from_user ON Message(from_user);
CREATE INDEX idx_interaction_time ON Interaction(timestamp);
CREATE INDEX idx_affinity_value ON Affinity(value);

-- view: messages in recent 24 hours
CREATE VIEW Recent_Chat_Messages AS
SELECT cs.session_id, m.content
FROM Chat_Session cs
JOIN Message m ON m.timestamp > NOW() - INTERVAL 24 HOUR;

-- trigger 
-- auto update points after each balance
DELIMITER $$
CREATE TRIGGER trg_update_balance
AFTER INSERT ON Transaction
FOR EACH ROW
BEGIN
    UPDATE User 
    SET points_balance = points_balance - NEW.amount
    WHERE user_id = NEW.sender_id;

    UPDATE User 
    SET points_balance = points_balance + NEW.amount
    WHERE user_id = NEW.receiver_id;
END$$

DELIMITER ;

-- function
DELIMITER $$

CREATE FUNCTION get_total_points_sent(uid INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total DECIMAL(10,2);

    SELECT IFNULL(SUM(amount), 0) INTO total
    FROM Transaction
    WHERE sender_id = uid;

    RETURN total;
END$$

DELIMITER ;



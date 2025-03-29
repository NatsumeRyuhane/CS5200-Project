-- Insert sample data into User table
INSERT INTO User (user_id, username, email, points_balance, discord_id, is_admin) VALUES
(1, 'johndoe', 'john.doe@example.com', 1000, 'johndoe#1234', FALSE),
(2, 'janedoe', 'jane.doe@example.com', 1500, 'janedoe#5678', FALSE),
(3, 'admin_user', 'admin@example.com', 5000, 'admin#9999', TRUE),
(4, 'gamer123', 'gamer123@example.com', 800, 'gamer123#4321', FALSE),
(5, 'techguy', 'tech@example.com', 1200, 'techguy#8765', FALSE),
(6, 'cooluser', 'cool@example.com', 600, 'cooluser#2468', FALSE),
(7, 'newplayer', 'newbie@example.com', 100, 'newplayer#1357', FALSE),
(8, 'moderator', 'mod@example.com', 2500, 'moderator#3579', TRUE),
(9, 'gamemaster', 'gm@example.com', 3000, 'gamemaster#2468', TRUE),
(10, 'casual_player', 'casual@example.com', 350, 'casual#9753', FALSE);

-- Insert sample data into Virtual_Character table
INSERT INTO Virtual_Character (character_id, name, description) VALUES
(1, 'Elara', 'A wise elven mage with centuries of arcane knowledge'),
(2, 'Brutus', 'A battle-hardened warrior with a heart of gold'),
(3, 'Luna', 'A mysterious fortune teller who speaks in riddles'),
(4, 'Zephyr', 'An air elemental who loves to play tricks'),
(5, 'Orion', 'A stoic hunter who rarely speaks but sees everything'),
(6, 'Seraphina', 'A celestial being with a melodic voice'),
(7, 'Grimm', 'A grumpy old wizard who reluctantly helps others'),
(8, 'Nova', 'A cosmic entity fascinated by human emotions');

-- Insert sample data into Transaction table
INSERT INTO Transaction (transaction_id, sender_id, receiver_id, amount, time) VALUES
(1, 1, 2, 50.00, '2025-01-15 14:30:00'),
(2, 3, 5, 100.00, '2025-01-16 09:45:00'),
(3, 2, 4, 25.00, '2025-01-17 18:20:00'),
(4, 5, 1, 75.00, '2025-01-18 11:10:00'),
(5, 4, 6, 30.00, '2025-01-19 16:55:00'),
(6, 7, 8, 20.00, '2025-01-20 13:40:00'),
(7, 9, 10, 150.00, '2025-01-21 10:25:00'),
(8, 8, 3, 80.00, '2025-01-22 15:15:00');

-- Insert sample data into Message table
INSERT INTO Message (message_id, from_user, content, timestamp) VALUES
(1, 1, 'Hello everyone!', '2025-01-15 10:00:00'),
(2, 2, 'Hi there, how are you?', '2025-01-15 10:05:00'),
(3, 3, 'Welcome to the chat.', '2025-01-15 10:10:00'),
(4, 4, 'Is anyone online?', '2025-01-16 14:20:00'),
(5, 5, 'I need help with a quest.', '2025-01-16 14:25:00'),
(6, 6, 'Has anyone seen the new character?', '2025-01-17 09:30:00'),
(7, 7, 'Just joined today!', '2025-01-17 09:35:00'),
(8, 8, 'Please follow the community guidelines.', '2025-01-17 09:40:00'),
(9, 9, 'Announcing a new event tomorrow!', '2025-01-18 12:00:00'),
(10, 10, 'Looking for a team to play with.', '2025-01-18 12:05:00');

-- Insert sample data into Chat_Session table
INSERT INTO Chat_Session (session_id, start_time) VALUES
(1, '2025-01-15 10:00:00'),
(2, '2025-01-16 14:20:00'),
(3, '2025-01-17 09:30:00'),
(4, '2025-01-18 12:00:00'),
(5, '2025-01-19 16:00:00'),
(6, '2025-01-20 11:30:00'),
(7, '2025-01-21 15:45:00');

-- Insert sample data into Interaction table
INSERT INTO Interaction (user_id, character_id, timestamp, action, context) VALUES
(1, 3, '2025-01-15 11:00:00', 'greeted', 'First meeting'),
(2, 1, '2025-01-15 11:30:00', 'asked_question', 'About magic spells'),
(3, 5, '2025-01-16 10:15:00', 'gave_gift', 'Rare artifact'),
(4, 2, '2025-01-16 13:45:00', 'trained_with', 'Combat practice'),
(5, 4, '2025-01-17 09:20:00', 'played_game', 'Riddle challenge'),
(6, 6, '2025-01-17 14:10:00', 'listened_to', 'Celestial song'),
(7, 7, '2025-01-18 16:30:00', 'requested_help', 'Potion brewing'),
(8, 8, '2025-01-19 12:50:00', 'discussed', 'Philosophy of the cosmos'),
(9, 2, '2025-01-20 11:25:00', 'sparred_with', 'Testing new abilities'),
(10, 3, '2025-01-21 15:40:00', 'fortune_told', 'Future adventures');

-- Insert sample data into Memory table
INSERT INTO Memory (user_id, character_id, summary_text, last_updated) VALUES
(1, 3, 'User seems interested in their future. Asked about career prospects.', '2025-01-15 11:05:00'),
(2, 1, 'User is a novice mage seeking knowledge about elemental spells.', '2025-01-15 11:35:00'),
(3, 5, 'User enjoys hunting and has shown exceptional tracking skills.', '2025-01-16 10:20:00'),
(4, 2, 'User is training to become a warrior, focusing on defensive techniques.', '2025-01-16 13:50:00'),
(5, 4, 'User loves solving puzzles and is particularly good at word games.', '2025-01-17 09:25:00'),
(6, 6, 'User has perfect pitch and enjoys singing along to celestial melodies.', '2025-01-17 14:15:00'),
(7, 7, 'User is new to alchemy but shows natural talent for potion ingredients.', '2025-01-18 16:35:00'),
(8, 8, 'User has deep thoughts about existence and frequently discusses philosophy.', '2025-01-19 12:55:00');

-- Insert sample data into Customization table
INSERT INTO Customization (character_id, attribute, value) VALUES
(1, 'robe_color', 'midnight_blue'),
(1, 'staff_type', 'oak_with_crystal'),
(2, 'armor_style', 'heavy_plate'),
(2, 'weapon_choice', 'two_handed_sword'),
(3, 'tarot_deck', 'ancient_mystic'),
(4, 'aura_color', 'swirling_cyan'),
(5, 'bow_type', 'longbow'),
(6, 'halo_brightness', 'radiant'),
(7, 'beard_length', 'very_long'),
(8, 'star_constellation', 'cassiopeia');

-- Insert sample data into Affinity table
INSERT INTO Affinity (user_id, character_id, value) VALUES
(1, 3, 0.75),
(2, 1, 0.90),
(3, 5, 0.85),
(4, 2, 0.95),
(5, 4, 0.70),
(6, 6, 0.80),
(7, 7, 0.60),
(8, 8, 0.85),
(9, 2, 0.75),
(10, 3, 0.65);
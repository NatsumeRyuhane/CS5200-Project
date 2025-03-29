-- SQL queries for the Virtual Character Interaction System

/* 
Query 1: Join query involving more than 2 relations
Find all interactions between users and characters, along with user details and character names,
sorted by interaction timestamp.
*/
SELECT 
    u.username, 
    u.email, 
    vc.name AS character_name, 
    vc.description AS character_description,
    i.action, 
    i.context, 
    i.timestamp
FROM 
    User u
JOIN 
    Interaction i ON u.user_id = i.user_id
JOIN 
    Virtual_Character vc ON i.character_id = vc.character_id
ORDER BY 
    i.timestamp DESC;

/* Expected Output:
+---------------+------------------------+----------------+---------------------------------------+----------------+--------------------+---------------------+
| username      | email                  | character_name | character_description                 | action         | context            | timestamp           |
+---------------+------------------------+----------------+---------------------------------------+----------------+--------------------+---------------------+
| casual_player | casual@example.com     | Luna           | A mysterious fortune teller...        | fortune_told   | Future adventures  | 2025-01-21 15:40:00 |
| gamemaster    | gm@example.com         | Brutus         | A battle-hardened warrior...          | sparred_with   | Testing abilities  | 2025-01-20 11:25:00 |
| moderator     | mod@example.com        | Nova           | A cosmic entity fascinated...         | discussed      | Philosophy         | 2025-01-19 12:50:00 |
| ...           | ...                    | ...            | ...                                   | ...            | ...                | ...                 |
+---------------+------------------------+----------------+---------------------------------------+----------------+--------------------+---------------------+
*/

/* 
Query 2: Aggregate query with GROUP BY, HAVING, and ORDER BY
Find characters with high average affinity (> 0.75) among users, 
showing number of interactions and highest affinity value.
*/
SELECT 
    vc.character_id,
    vc.name,
    COUNT(i.user_id) AS interaction_count,
    AVG(a.value) AS average_affinity,
    MAX(a.value) AS highest_affinity
FROM 
    Virtual_Character vc
JOIN 
    Interaction i ON vc.character_id = i.character_id
JOIN 
    Affinity a ON vc.character_id = a.character_id AND i.user_id = a.user_id
GROUP BY 
    vc.character_id, vc.name
HAVING 
    AVG(a.value) > 0.75
ORDER BY 
    average_affinity DESC;

/* Expected Output:
+-------------+----------------+-------------------+------------------+------------------+
| character_id| name           | interaction_count | average_affinity | highest_affinity |
+-------------+----------------+-------------------+------------------+------------------+
| 2           | Brutus         | 2                 | 0.850000         | 0.95             |
| 1           | Elara          | 1                 | 0.900000         | 0.90             |
| 5           | Orion          | 1                 | 0.850000         | 0.85             |
| 8           | Nova           | 1                 | 0.850000         | 0.85             |
| 3           | Luna           | 2                 | 0.800000         | 0.75             |
+-------------+----------------+-------------------+------------------+------------------+
*/

/* 
Query 3: Join query with subquery
Find users who have interacted with characters they have high affinity with (>0.8)
but haven't sent messages in the last 7 days.
*/
SELECT 
    u.user_id,
    u.username,
    u.email,
    vc.name AS favorite_character,
    a.value AS affinity_value
FROM 
    User u
JOIN 
    Affinity a ON u.user_id = a.user_id
JOIN 
    Virtual_Character vc ON a.character_id = vc.character_id
WHERE 
    a.value > 0.8
    AND u.user_id NOT IN (
        SELECT DISTINCT from_user 
        FROM Message 
        WHERE timestamp > DATE_SUB(NOW(), INTERVAL 7 DAY)
    )
ORDER BY 
    a.value DESC;

/* Expected Output:
+---------+----------+--------------------+-------------------+---------------+
| user_id | username | email              | favorite_character| affinity_value|
+---------+----------+--------------------+-------------------+---------------+
| 4       | gamer123 | gamer123@example.com | Brutus          | 0.95          |
| 2       | janedoe  | jane.doe@example.com | Elara           | 0.90          |
| 3       | admin_user | admin@example.com  | Orion           | 0.85          |
+---------+----------+--------------------+-------------------+---------------+
*/

/* 
Query 4: Aggregate query with GROUP BY and HAVING
Find users who have made transactions above average value,
showing their total sent and received amounts.
*/
SELECT 
    u.user_id,
    u.username,
    (SELECT SUM(amount) FROM Transaction WHERE sender_id = u.user_id) AS total_sent,
    (SELECT SUM(amount) FROM Transaction WHERE receiver_id = u.user_id) AS total_received,
    COUNT(DISTINCT t1.transaction_id) + COUNT(DISTINCT t2.transaction_id) AS transaction_count
FROM 
    User u
LEFT JOIN 
    Transaction t1 ON u.user_id = t1.sender_id
LEFT JOIN 
    Transaction t2 ON u.user_id = t2.receiver_id
GROUP BY 
    u.user_id, u.username
HAVING 
    (COALESCE((SELECT SUM(amount) FROM Transaction WHERE sender_id = u.user_id), 0) / 
     NULLIF(COUNT(DISTINCT t1.transaction_id), 0)) > 
    (SELECT AVG(amount) FROM Transaction)
    OR
    (COALESCE((SELECT SUM(amount) FROM Transaction WHERE receiver_id = u.user_id), 0) / 
     NULLIF(COUNT(DISTINCT t2.transaction_id), 0)) > 
    (SELECT AVG(amount) FROM Transaction)
ORDER BY 
    (COALESCE(total_sent, 0) + COALESCE(total_received, 0)) DESC;

/* Expected Output:
+---------+---------------+------------+----------------+------------------+
| user_id | username      | total_sent | total_received | transaction_count|
+---------+---------------+------------+----------------+------------------+
| 3       | admin_user    | 100.00     | 80.00          | 2                |
| 9       | gamemaster    | 150.00     | 0.00           | 1                |
| 5       | techguy       | 75.00      | 100.00         | 2                |
| 8       | moderator     | 80.00      | 20.00          | 2                |
+---------+---------------+------------+----------------+------------------+
*/

/* 
Query 5: Complex join with WITH clause (Common Table Expression)
Find the top 3 characters with the most detailed memory records
and their customizations.
*/
WITH CharacterMemoryStats AS (
    SELECT 
        vc.character_id,
        vc.name,
        COUNT(m.user_id) AS memory_count,
        AVG(LENGTH(m.summary_text)) AS avg_memory_length
    FROM 
        Virtual_Character vc
    LEFT JOIN 
        Memory m ON vc.character_id = m.character_id
    GROUP BY 
        vc.character_id, vc.name
)

SELECT 
    cms.character_id,
    cms.name,
    cms.memory_count,
    cms.avg_memory_length,
    GROUP_CONCAT(DISTINCT c.attribute ORDER BY c.attribute SEPARATOR ', ') AS customizations,
    COUNT(DISTINCT i.user_id) AS unique_interacting_users
FROM 
    CharacterMemoryStats cms
JOIN 
    Virtual_Character vc ON cms.character_id = vc.character_id
LEFT JOIN 
    Customization c ON vc.character_id = c.character_id
LEFT JOIN 
    Interaction i ON vc.character_id = i.character_id
GROUP BY 
    cms.character_id, cms.name, cms.memory_count, cms.avg_memory_length
ORDER BY 
    cms.avg_memory_length DESC, cms.memory_count DESC
LIMIT 3;

/* Expected Output:
+-------------+----------+--------------+------------------+------------------------------------------+-------------------------+
| character_id | name     | memory_count | avg_memory_length | customizations                          | unique_interacting_users|
+-------------+----------+--------------+------------------+------------------------------------------+-------------------------+
| 8           | Nova     | 1            | 78.0             | star_constellation                       | 1                       |
| 2           | Brutus   | 1            | 70.0             | armor_style, weapon_choice               | 2                       |
| 7           | Grimm    | 1            | 68.0             | beard_length                             | 1                       |
+-------------+----------+--------------+------------------+------------------------------------------+-------------------------+
*/
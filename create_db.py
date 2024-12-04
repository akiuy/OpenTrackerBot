import sqlite3
    

def create_predictions_db():
    connection = sqlite3.connect('main.db')
    cursor = connection.cursor()

    cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY,
tid INTEGER,
predictions_count INTEGER,
predictions_correct INTEGER,
predictions_incorrect INTEGER,
predictions_score INTEGER,
UNIQUE ("tid") ON CONFLICT IGNORE
)
''')

    cursor.execute('''
CREATE TABLE IF NOT EXISTS tournaments (
trn_id INTEGER PRIMARY KEY,
trn_name TEXT NOT NULL,
trn_status TEXT NOT NULL,
UNIQUE ("trn_name") ON CONFLICT IGNORE
)
''')
    cursor.execute('INSERT INTO tournaments (trn_name, trn_status) VALUES (?, ?)', ('Perfect World Shanghai Major 2024', 'Upcoming'))


    cursor.execute('''
CREATE TABLE IF NOT EXISTS matches (
match_id INTEGER PRIMARY KEY,
trn_name TEXT NOT NULL,
team_a TEXT NOT NULL,
team_b TEXT NOT NULL,
match_time TEXT NOT NULL,
match_type TEXT NOT NULL,
match_status TEXT NOT NULL,
team_a_win INTEGER,
team_b_win INTEGER,
prediction_points INTEGER
)
''')
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', 'G2', 'The MongolZ', '6:00 (MSK)', 'BO1', 'Upcoming', 100))
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', 'Natus Vincere', 'Liquid', '6:00 (MSK)', 'BO1', 'Upcoming', 100))
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', 'Vitality', 'GamerLegion', '7:00 (MSK)', 'BO1', 'Upcoming', 100))
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', 'Spirit', 'FURIA', '7:00 (MSK)', 'BO1', 'Upcoming', 100))
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', 'MOUZ', 'paiN', '8:00 (MSK)', 'BO1', 'Upcoming', 100))
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', 'FaZe', 'Wildcard', '8:00 (MSK)', 'BO1', 'Upcoming', 100))
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', 'Heroic', 'BIG', '9:00 (MSK)', 'BO1', 'Upcoming', 100))
    cursor.execute('INSERT INTO matches (trn_name, team_a, team_b, match_time, match_type, match_status, prediction_points) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  ('Perfect World Shanghai Major 2024', '3DMAX', 'MIBR', '9:00 (MSK)', 'BO1', 'Upcoming', 100))

    cursor.execute('''
CREATE TABLE IF NOT EXISTS predicts (
tid INTEGER,
match_id INTEGER,
predict INTEGER
)
''')

    connection.commit()
    connection.close()
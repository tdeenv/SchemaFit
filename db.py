import sqlite3
from typing import List, Dict, Any

# Initialize the database and create tables (with simple migrations)
def init_db(db_path: str = 'workouts.db') -> None:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # Create tables if missing
        c.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE
            )
        ''')
        # Ensure required columns exist in workouts (migrate if needed)
        c.execute("PRAGMA table_info(workouts)")
        existing = {row[1] for row in c.fetchall()}
        columns = [
            ('workout_type', 'TEXT'),
            ('weight', 'REAL'),
            ('arm', 'REAL'),
            ('neck', 'REAL'),
            ('quad', 'REAL'),
            ('waist', 'REAL')
        ]
        for col, col_type in columns:
            if col not in existing:
                c.execute(f"ALTER TABLE workouts ADD COLUMN {col} {col_type}")
        
        # Create exercises and sets tables if missing
        c.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER,
                name TEXT,
                FOREIGN KEY (workout_id) REFERENCES workouts(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_id INTEGER,
                weight REAL,
                reps INTEGER,
                comment TEXT,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id)
            )
        ''')
        conn.commit()

# Save one workout with multiple exercises and sets
def save_workout(date: str,
                 workout_type: str,
                 weight: float,
                 arm: float,
                 neck: float,
                 quad: float,
                 waist: float,
                 exercises: list,
                 db_path: str = 'workouts.db') -> None:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # Insert or replace the workout for that date
        c.execute(
            '''
            INSERT OR REPLACE INTO workouts
                (date, workout_type, weight, arm, neck, quad, waist)
            VALUES
                (?, ?, ?, ?, ?, ?, ?)
            ''',
            (date, workout_type, weight, arm, neck, quad, waist)
        )
        # Get the workout_id
        c.execute('SELECT id FROM workouts WHERE date = ?', (date,))
        workout_id = c.fetchone()[0]

        # Clear existing exercises/sets for this workout (if re-saving)
        c.execute(
            '''
            DELETE FROM sets
            WHERE exercise_id IN (
                SELECT id FROM exercises WHERE workout_id = ?
            )
            ''',
            (workout_id,)
        )
        c.execute(
            'DELETE FROM exercises WHERE workout_id = ?',
            (workout_id,)
        )

        # Insert exercises and their sets
        for name, sets in exercises:
            c.execute(
                'INSERT INTO exercises (workout_id, name) VALUES (?, ?)',
                (workout_id, name)
            )
            exercise_id = c.lastrowid
            for w, r, comment in sets:
                c.execute(
                    '''
                    INSERT INTO sets (exercise_id, weight, reps, comment)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (exercise_id, w, r, comment)
                )
        conn.commit()

# Fetch all workouts with nested exercises and sets
def fetch_all_workouts(db_path: str = 'workouts.db') -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # Load workouts
        c.execute('SELECT id, date, workout_type, weight, arm, neck, quad, waist FROM workouts ORDER BY date DESC')
        workouts = []
        for w in c.fetchall():
            workout_id, date, wtype, weight, arm, neck, quad, waist = w
            # Load exercises for this workout
            c.execute('SELECT id, name FROM exercises WHERE workout_id = ?', (workout_id,))
            exercises = []
            for ex in c.fetchall():
                ex_id, name = ex
                # Load sets for this exercise
                c.execute('SELECT weight, reps, comment FROM sets WHERE exercise_id = ?', (ex_id,))
                sets = c.fetchall()
                exercises.append({
                    'name': name,
                    'sets': [{'weight': s[0], 'reps': s[1], 'comment': s[2]} for s in sets]
                })
            workouts.append({
                'date': date,
                'type': wtype,
                'measurements': {'weight': weight, 'arm': arm, 'neck': neck, 'quad': quad, 'waist': waist},
                'exercises': exercises
            })
        return workouts
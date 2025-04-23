import sqlite3
from typing import List, Tuple

def init_db(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            date TEXT,
            type TEXT,
            weight REAL,
            arm REAL,
            neck REAL,
            quad REAL,
            waist REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY,
            workout_id INTEGER,
            name TEXT,
            FOREIGN KEY (workout_id) REFERENCES workouts(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY,
            exercise_id INTEGER,
            weight REAL,
            reps INTEGER,
            comment TEXT,
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        )
    ''')

    conn.commit()

def save_workout(conn: sqlite3.Connection,
                 date: str, workout_type: str,
                 weight: float, arm: float, neck: float,
                 quad: float, waist: float,
                 exercises: List[Tuple[str, List[Tuple[float, int, str]]]]):
    
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO workouts (date, type, weight, arm, neck, quad, waist)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, workout_type, weight, arm, neck, quad, waist))

    workout_id = cursor.lastrowid

    for exercise_name, sets in exercises:
        cursor.execute('''
            INSERT INTO exercises (workout_id, name)
            VALUES (?, ?)
        ''', (workout_id, exercise_name))
        exercise_id = cursor.lastrowid

        for weight_used, reps, comment in sets:
            cursor.execute('''
                INSERT INTO sets (exercise_id, weight, reps, comment)
                VALUES (?, ?, ?, ?)
            ''', (exercise_id, weight_used, reps, comment))

    conn.commit()

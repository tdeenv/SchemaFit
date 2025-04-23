import sqlite3
from schema import init_db, save_workout

def get_float(prompt):
    return float(input(prompt))

def get_exercises():
    exercises = []
    while True:
        name = input("Exercise name (or leave empty to finish): ").strip()
        if not name:
            break

        sets = []
        while True:
            try:
                weight = float(input("  Set weight (or leave blank to end): "))
                reps = int(input("  Set reps: "))
                comment = input("  Comment: ")
                sets.append((weight, reps, comment))
            except ValueError:
                break

        exercises.append((name, sets))
    return exercises

def main():
    conn = sqlite3.connect("workouts.db")
    init_db(conn)

    date = input("Workout date (YYYY-MM-DD): ")
    workout_type = input("Workout type (e.g. Push A, Legs): ")
    weight = get_float("Body weight (kg): ")
    arm = get_float("Arm avg (cm): ")
    neck = get_float("Neck avg (cm): ")
    quad = get_float("Quad avg (cm): ")
    waist = get_float("Waist avg (cm): ")

    exercises = get_exercises()

    save_workout(conn, date, workout_type, weight, arm, neck, quad, waist, exercises)
    print("Workout saved!")

if __name__ == "__main__":
    main()

from flask import Flask, request, render_template, redirect, url_for
from db import init_db, save_workout, fetch_all_workouts

app = Flask(__name__)
init_db()  # ensure tables exist

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Basic fields
        date = request.form['date']
        workout_type = request.form['workout_type']
        weight = float(request.form['weight'])
        arm = float(request.form['arm'])
        neck = float(request.form['neck'])
        quad = float(request.form['quad'])
        waist = float(request.form['waist'])

        # Collect lists
        names = request.form.getlist('exercise_name[]')
        set_weights = request.form.getlist('set_weight[]')
        reps = request.form.getlist('reps[]')
        comments = request.form.getlist('comment[]')
        set_idxs = request.form.getlist('set_exercise_index[]')

        # Build nested structure
        exercises = []
        for i, name in enumerate(names):
            sets = []
            for w, r, c, idx in zip(set_weights, reps, comments, set_idxs):
                if int(idx) == i:
                    sets.append((float(w), int(r), c))
            exercises.append((name, sets))

        save_workout(date, workout_type, weight, arm, neck, quad, waist, exercises)
        return redirect(url_for('history'))

    return render_template('form.html')

@app.route('/history')
def history():
    workouts = fetch_all_workouts()
    return render_template('history.html', workouts=workouts)

if __name__ == '__main__':
    app.run(debug=True)
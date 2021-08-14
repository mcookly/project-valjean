import os
from flask import Flask, send_from_directory, render_template, request, redirect, session
from flask.helpers import url_for

# This line initiates the Flask app
app = Flask(__name__)

########### Index
@app.route('/')
def index():
    return render_template('index.html')

########### Rate page group
@app.route('/rate/') # Redirect for simpler navigation to the rating section.
def rate():
    return redirect(url_for('dininghall'))
@app.route('/rate/dh/') # Select the DH
def dininghall():
    return render_template('rate/dininghall.html')
@app.route('/rate/<dh>/meal/') # Select the meal
def meal(dh = None):
    meals = ['Brunch', 'Dinner'] # TODO: replace with SQL data
    return render_template('rate/meal.html', dh=dh, meals=meals)
@app.route('/rate/<dh>/<meal>/select/')
def select(dh, meal):
    food = {'Beans': ['apple', 'pear', 'salmon'], 'Juice': ['cider', 'banana', 'tuna']} # TODO: replace with SQL data
    return render_template('rate/select.html', dh=dh, meal=meal, food_items = food)
@app.route('/rate/rating/')
def rating():
    return render_template('rate/rating.html')

########### Selector for dining hall selection
@app.route('/session/dh/<dh>/')
def selector_dh(dh):
    return redirect(url_for('meal', dh=dh))

########### Selector for meal selection
@app.route('/session/<dh>/<meal>')
def selector_meal(dh, meal):
    return redirect(url_for('select', dh=dh, meal=meal))

########### Stores selected food items
@app.route('/session/<dh>/<meal>/food-items', methods=['POST'])
def record_food_items(dh, meal):
    req = request.form.to_dict()
    return redirect(url_for('rating', dh=dh, meal=meal))

########### Stats
@app.route('/stats/')
def stats():
    return render_template('stats.html')

########### About
@app.route('/about/')
def about():
    return render_template('about.html')

########### Load favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/img/favicon'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

########### Error handling for missing pages
@app.errorhandler(404)
def handle_404(error):
    return redirect(url_for('index'), 303)

# Since this is the main script of the app, have it run itself.
if __name__ == "__main__":
    app.run(debug=True)
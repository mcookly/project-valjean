import os
from flask import Flask, send_from_directory, render_template, request, redirect, json
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
def meal(dh):
    if dh not in ('South', 'North'):
        return redirect(url_for('missing_data', data=dh))
    else:
        meals = ['Breakfast', 'Lunch', 'Dinner'] # TODO: replace with SQL data
        return render_template('rate/meal.html', dh=dh, meals=meals)
@app.route('/rate/<dh>/<meal>/select/')
def select(dh, meal):
    food = {'Grill': ['Gluten Free Hamburger Buns', 'Char-Grilled Chicken Breast', 'Crispy Chicken Patty', 'Hot Dog Buns', 'Beef and Mushroom Burger'], 'Pizzeria': ['Sausage Pizza', 'Cheese Pizza', 'Pepperoni Pizza']} # TODO: replace with SQL data
    return render_template('rate/select.html', dh=dh, meal=meal, food_items = food)
@app.route('/rate/rating/<dh>/<meal>/<food>')
def rating(dh, meal, food):
    food_dict = json.loads(food)
    return render_template('rate/rating.html', dh=dh, meal=meal, food=food_dict)
@app.route('/rate/submitted/<dh>/<meal>')
def submitted(dh, meal):
    return render_template('rate/submitted.html', dh=dh, meal=meal)

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
    food = request.form.to_dict(flat=False) # Gives food items per category
    food_str = json.dumps(food)
    return redirect(url_for('rating', dh=dh, meal=meal, food=food_str))

########### Writes ratings to DB
@app.route('/session/<dh>/<meal>/submit', methods=['POST'])
def submit_ratings(dh, meal):
    # Code for writing to DB goes here.
    rating = request.form.to_dict(flat=False) # Gives # rating per category-food
    # TODO: split cat-food str and send to DB.
    return redirect(url_for('submitted', dh=dh, meal=meal))

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

########### Error page for missing fata
@app.route('/error/missing-<data>')
def missing_data(data):
    return render_template('error/missing-data.html', data=data)


########### Error handling for missing pages
@app.errorhandler(404)
def handle_404(error):
    return redirect(url_for('index'), 303)

# Since this is the main script of the app, have it run itself.
# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=5000)
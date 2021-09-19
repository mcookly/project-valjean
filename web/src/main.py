from datetime import date
from logging import error
import firebase_admin, os
from flask import Flask, send_from_directory, render_template, request, redirect, json
from flask.helpers import url_for
from firebase_admin import credentials, firestore

# This line initiates the Flask app
app = Flask(__name__)

# Get DB
def get_db():
    cred = credentials.ApplicationDefault()
    try:
        firebase_admin.initialize_app(cred)
    except:
        # Firebase will throw an error if app is already initialized
        app.logger.info('Firebase app already initialized')
    app.logger.info("Opened Firebase session successfully")

    client = firestore.client()
    return client

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
        # Initialize database
        client = get_db()
        try:
            meta_meals = client.collection('foods-' + dh).document('META-meals').get()
            meals = meta_meals.to_dict()['meals']
            app.logger.info(f"Found meal list for {dh}: {meals}")

            if len(meals) == 0:
                raise ImportError('Meal list returned empty')
        except:
            return redirect(url_for('missing_data'), meals)

        return render_template('rate/meal.html', dh=dh, meals=meals)

@app.route('/rate/<dh>/<meal>/select/')
def select(dh, meal):
    food = dict()
    client = get_db()
    food_cats = client.collection('foods-' + dh).where('meal', '==', meal).stream()
    for cat in food_cats:
        cat_dict = cat.to_dict()
        food[cat_dict['name']] = cat_dict['foods']
    app.logger.info(f'Found foods for {meal} at {dh}')
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
    app.logger.info(f'Current ratings: {rating}')

    # Send reviews to DB
    client = get_db()
    for (name, review) in rating.items():
        item = client.collection('reviews-' + dh).document(meal + '-' + name)
        review_num = review[0]
        if item.get().exists:  
            item_dict = item.get().to_dict()
            likes = item_dict['likes']
            dislikes = item_dict['dislikes']
            if int(review_num):
                dislikes += 1
            else:
                likes += 1
        else:
            if int(review_num):
                dislikes = 1
                likes = 0
            else:
                dislikes = 0
                likes = 1 

        item.set({
            'name': name,
            'date': date.today().strftime('%Y-%m-%d'),
            'meal': meal,
            'likes': likes,
            'dislikes': dislikes
        })

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
import os
from flask import Flask, send_from_directory, render_template, redirect
from flask.helpers import url_for

# This line initiates the Flask app
app = Flask(__name__)

########### Index
@app.route('/')
def index():
    return render_template('index.html')

########### Rate
@app.route('/rate/')
def rate():
    return render_template('rate.html')

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
    app.run(host='0.0.0.0')
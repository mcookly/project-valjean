import os
from flask import Flask, send_from_directory, render_template

# This line initiates the Flask app
app = Flask(__name__)

########### Index
@app.route('/')
def index():
    return render_template('index.html', cuurent_page='Home')

########### Rate
@app.route('/rate/')
def rate():
    return render_template('rate.html', cuurent_page='Rate')

########### Stats
@app.route('/stats/')
def stats():
    return render_template('stats.html', cuurent_page='Stats')

########### About
@app.route('/about/')
def about():
    return render_template('about.html', cuurent_page='About')

########### Load favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/img/favicon'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Since this is the main script of the app, have it run itself.
if __name__ == "__main__":
    app.run(host='0.0.0.0')
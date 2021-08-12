import os
from flask import Flask, send_from_directory, render_template, redirect, session
from flask.helpers import url_for
from werkzeug.exceptions import MethodNotAllowed

# This line initiates the Flask app
app = Flask(__name__)

# Session
app.secret_key = 'potato beans'

########### Index
@app.route('/')
def index():
    return render_template('index.html')

########### Rate
@app.route('/rate/dh/')
def dininghall():
    if 'sdh' in session or 'ndh' in session:
        return redirect(url_for('select'))
    return render_template('rate/dininghall.html')
@app.route('/rate/select/')
def select():
    return render_template('rate/select.html')
@app.route('/rate/rating/')
def rating():
    return render_template('rate/rating.html')

########### Session handler for dining hall selection
@app.route('/session/ndh/', methods = ['GET', 'POST'])
def session_ndh():
    session['dininghall'] = 'ndh'
    return redirect(url_for('select'))

@app.route('/session/sdh/', methods = ['GET', 'POST'])
def session_sdh():
    session['dininghall'] = 'sdh'
    return redirect(url_for('select'))

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
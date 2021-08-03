from flask import Flask

# This file initiates the Flask app

app = Flask(__name__)
@app.route('/')
def index():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
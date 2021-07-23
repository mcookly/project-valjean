from flask import Flask

# This file initiates the Flask app

main = Flask(__name__)
@main.route('/')
def index():
    return "Hello World!"

if __name__ == "__main__":
    main.run(host='0.0.0.0')
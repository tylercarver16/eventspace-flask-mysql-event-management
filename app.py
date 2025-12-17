from flask import Flask
from routes import init_app

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'

    init_app(app)

    return app
from flask import Flask
from app.routes import routes
import app.logging_config

def create_app():
    app = Flask(__name__, template_folder="../static/templates", static_folder="../static")
    from app.routes import routes
    app.register_blueprint(routes)
    return app

import os
from datetime import timedelta

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.batch import batch_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(batch_bp)

    return app

from flask import Flask
from pathlib import Path
from Info.models import init_db
from Info.auth import auth_bp
from Info.routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-this"

    base_dir = Path(__file__).resolve().parent
    upload_dir = base_dir/ "uploads"
    (upload_dir/"carrier").mkdir(parents=True, exist_ok = True)
    (upload_dir/"payload").mkdir(parents=True, exist_ok = True)
    (upload_dir/"output").mkdir(parents=True, exist_ok = True)

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

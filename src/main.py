import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sqlalchemy.pool import NullPool
from flask import Flask
from src.extensions import db, migrate
from src.routes.auth import auth_bp

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Secret key per sessioni e sicurezza
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_default_fallback_secret_key")
    

    # Configurazione del database da variabile d'ambiente
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{os.path.join(app.instance_path, 'app.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Inizializza le estensioni
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint di autenticazione
    app.register_blueprint(auth_bp)

    with app.app_context():
        from src.models import user  # Assicura che il modello venga registrato

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask        # <-- questa riga serve!
from src.extensions import db, migrate
from src.routes.auth import auth_bp
from src.routes.suppliers import suppliers_bp
from src.routes.orders import orders_bp
from src.extensions import mail

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Config app
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_default_fallback_secret_key")
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{os.path.join(app.instance_path, 'app.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Config email
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Inizializza estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Registra le blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(suppliers_bp, url_prefix="/suppliers")
    app.register_blueprint(orders_bp, url_prefix="/orders")

    with app.app_context():
        from src.models import user, supplier, product

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
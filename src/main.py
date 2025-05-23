import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from src.config import Config
from src.extensions import db, migrate, mail
from src.routes.auth import auth_bp, login_manager
from src.routes.suppliers import suppliers_bp
from src.routes.orders import orders_bp
from src.routes.inventory import inventory_bp
from src.routes.locations import locations_bp  # NUOVA ROUTE
from src.models import user, supplier, product, order, order_item, location, inventory  # NUOVO MODELLO

def create_app(*args, **kwargs):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Inizializza estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    # Registra blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(suppliers_bp, url_prefix="/suppliers")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(locations_bp, url_prefix="/locations")  # NUOVA ROUTE

    # Importa modelli per le migrazioni
    with app.app_context():
        from src.models import (
            user, supplier, product, order, order_item, 
            location, inventory  # NUOVO MODELLO
        )

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
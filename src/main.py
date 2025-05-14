import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import blueprints
from src.routes.auth import auth_bp

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__,template_folder=\'templates\',
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_default_fallback_secret_key") #Usa variabile d'ambiente per la secret key
    
    # Configurazione Database: Priorità alla variabile d'ambiente DATABASE_URL (per Render)ls -l migra
    # Altrimenti, fallback a SQLite per sviluppo locale se DATABASE_URL non è impostata.
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Sostituisci 'postgres://' con 'postgresql://' se Render fornisce l'URL in quel formato
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://\", \"postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Fallback a SQLite per sviluppo locale
        local_db_path = os.path.join(app.instance_path, "app.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{local_db_path}"
        # Crea la cartella instance se non esiste per SQLite locale
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
            
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inizializza le estensioni
    db.init_app(app)
    migrate.init_app(app, db)

    # Registra i blueprint
    app.register_blueprint(auth_bp)
    
    # Importa i modelli qui per assicurarti che siano registrati con SQLAlchemy
    # prima di creare le tabelle o eseguire le migrazioni.
    with app.app_context():
        from src.models import user 

    return app

app = create_app()

if __name__ == "__main__":
    # Per lo sviluppo locale, puoi specificare host e porta.
    # Per il deploy su Render, Render gestirà il binding a host/porta appropriati.
    port = int(os.environ.get("PORT", 5000)) # Render imposta la variabile PORT
    app.run(host="0.0.0.0 ", port=port, debug=False) # Debug=False per produzione

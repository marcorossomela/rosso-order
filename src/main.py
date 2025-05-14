import sys
import os

# Aggiunge la directory principale del progetto al path per gli import corretti
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask

# Importa db e migrate dal nostro file extensions.py
from .extensions import db, migrate

# Importa i tuoi blueprint (collezioni di rotte)
from .routes.auth import auth_bp

# Importa i tuoi modelli del database
# È FONDAMENTALE che questo import sia presente e corretto perché Flask-Migrate
# possa "vedere" le tue tabelle da creare/modificare.
from .models.user import User

def create_app():
    """Factory function per creare e configurare l'istanza dell'app Flask."""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static/')

    # Configurazione dell'applicazione
    # Carica la SECRET_KEY da una variabile d'ambiente, con un fallback per lo sviluppo.
    # NON USARE "your_default_fallback_secret_key" IN PRODUZIONE!
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "a_very_secure_default_secret_key_for_dev_only")

    # Configurazione del Database
    # Priorità alla variabile d'ambiente DATABASE_URL (usata da piattaforme come Render, Supabase).
    # Se non presente, usa un database SQLite locale per facilitare lo sviluppo.
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Alcune piattaforme (come le versioni più vecchie di Heroku o a volte Render)
        # potrebbero fornire URL che iniziano con "postgres://" invece di "postgresql://".
        # SQLAlchemy richiede "postgresql://".
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Configurazione per un database SQLite locale se DATABASE_URL non è impostata.
        # Il database verrà creato nella cartella 'instance' del tuo progetto.
        # La cartella 'instance' è il posto raccomandato da Flask per file che non dovrebbero
        # essere committati nel version control, come i database di sviluppo.
        instance_folder_path = app.instance_path
        local_db_file_path = os.path.join(instance_folder_path, "app.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{local_db_file_path}"

        # Crea la cartella 'instance' se non esiste già.
        try:
            os.makedirs(instance_folder_path)
        except OSError:
            # La cartella esiste già o c'è stato un altro errore nel crearla.
            # Se esiste già, va bene.
            if not os.path.isdir(instance_folder_path):
                raise # Solleva l'eccezione se non è una directory e la creazione è fallita

    # Disabilita una funzionalità di Flask-SQLAlchemy che non usiamo e che consuma risorse.
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inizializza le estensioni Flask (db per SQLAlchemy, migrate per Alembic) con l'app.
    # Questo deve avvenire DOPO che app.config è stata impostata, specialmente SQLALCHEMY_DATABASE_URI.
    db.init_app(app)
    migrate.init_app(app, db) # Passa sia l'app che l'istanza db a Flask-Migrate

    # Registra i Blueprint (collezioni di rotte) con l'applicazione.
    # auth_bp gestirà le rotte come /auth/login, /auth/register, ecc.
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Qui potresti registrare altri blueprint se ne avessi
    # app.register_blueprint(altro_bp, url_prefix='/altro')

    return app


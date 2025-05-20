from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User
from src.models.supplier import Supplier
from src.extensions import db

auth_bp = Blueprint('auth_bp', __name__)
login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'

@login_manager.user_loader
def load_user(user_id):
    # Usa db.session.get che supporta anche UUID (string)
    return db.session.get(User, user_id)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth_bp.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        location = request.form.get('location')

        if not email or not password or not location:
            flash('Tutti i campi sono obbligatori.', 'warning')
            return redirect(url_for('auth_bp.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email già registrata. Prova con un’altra.', 'danger')
            return redirect(url_for('auth_bp.register'))

        new_user = User(email=email, location=location)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Registrazione completata con successo!', 'success')
        return redirect(url_for('auth_bp.dashboard'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()  # Svuota eventuale sessione corrotta

    if current_user.is_authenticated:
        return redirect(url_for('auth_bp.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('auth_bp.dashboard'))
        else:
            flash('Credenziali non valide.', 'danger')
            return redirect(url_for('auth_bp.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout effettuato.', 'success')
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    suppliers = Supplier.query.filter_by(location=current_user.location).all()
    return render_template('dashboard.html', suppliers=suppliers)
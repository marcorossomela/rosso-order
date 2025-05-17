from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User
from src.extensions import db

auth_bp = Blueprint('auth_bp', __name__)

# Homepage
@auth_bp.route('/')
def index():
    return render_template('index.html')

# Registrazione
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth_bp.success'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email e password sono obbligatori.', 'warning')
            return redirect(url_for('auth_bp.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email già registrata. Prova con un’altra.', 'danger')
            return redirect(url_for('auth_bp.register'))

        new_user = User(email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash('Registrazione completata con successo!', 'success')
        return redirect(url_for('auth_bp.success'))

    return render_template('register.html')

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
    return redirect(url_for('auth_bp.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('auth_bp.dashboard'))
        else:
            flash('Credenziali non valide.', 'danger')
            return redirect(url_for('auth_bp.login'))

    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout effettuato.', 'success')
    return redirect(url_for('auth_bp.login'))

# Pagina success post-registrazione
@auth_bp.route('/success')
def success():
    if 'user_id' not in session:
        flash('Devi effettuare il login per accedere.', 'warning')
        return redirect(url_for('auth_bp.login'))
    return render_template('success.html')

# Dashboard protetta
@auth_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Devi effettuare il login per accedere alla dashboard.', 'warning')
        return redirect(url_for('auth_bp.login'))
    return render_template('dashboard.html')

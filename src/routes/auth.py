from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models.user import User  # Importa il modello User
from src.extensions import db

auth_bp = Blueprint(
    "auth_bp", __name__, template_folder="../templates", static_folder="../static"
)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from src.main import db  # Importa db per le sessioni del database
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session["logged_in"] = True
            session["username"] = user.username # Opzionale: salva username in sessione
            flash("Login successful!", "success")
            return redirect(url_for("auth_bp.success"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            # Per debug, non usare in produzione:
            # if not user:
            #     flash(f"User {username} not found.", "warning")
            # elif not user.check_password(password):
            #     flash(f"Password for user {username} incorrect.", "warning")
                
    return render_template("login.html")

@auth_bp.route("/success")
def success():
    if not session.get("logged_in"):
        flash("Please log in to access this page.", "info")
        return redirect(url_for("auth_bp.login"))
    return render_template("success.html")

@auth_bp.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("username", None) # Rimuovi username dalla sessione
    flash("You have been logged out.", "info")
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/")
def index():
    return redirect(url_for("auth_bp.login"))

# Potresti aggiungere una route per registrare un utente, ad esempio:
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "warning")
            return render_template("register.html")
        
        new_user = User(username=username)
        new_user.set_password(password) # Hash della password
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth_bp.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred during registration: {e}", "danger")
            
    return render_template("register.html") # Dovrai creare register.html


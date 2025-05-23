from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.extensions import db
from src.models.location import Location
from functools import wraps

locations_bp = Blueprint('locations_bp', __name__)

def admin_required(f):
    """Decorator per verificare che l'utente sia admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accesso negato. Solo gli admin possono accedere a questa sezione.', 'danger')
            return redirect(url_for('auth_bp.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@locations_bp.route('/manage')
@login_required
@admin_required
def manage_locations():
    """Dashboard admin per gestire le location"""
    locations = Location.query.order_by(Location.city, Location.name).all()
    
    # Raggruppa per città
    locations_by_city = {}
    for loc in locations:
        if loc.city not in locations_by_city:
            locations_by_city[loc.city] = []
        locations_by_city[loc.city].append(loc)
    
    return render_template('admin/manage_locations.html', locations_by_city=locations_by_city)

@locations_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_location():
    """Crea una nuova location"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        
        if not all([name, address, city]):
            flash('Tutti i campi sono obbligatori.', 'danger')
            return redirect(url_for('locations_bp.create_location'))
        
        # Verifica che non esista già una location con lo stesso nome nella stessa città
        existing = Location.query.filter_by(name=name, city=city).first()
        if existing:
            flash(f'Esiste già una location "{name}" a {city}.', 'warning')
            return redirect(url_for('locations_bp.create_location'))
        
        new_location = Location(
            name=name,
            address=address,
            city=city
        )
        
        try:
            db.session.add(new_location)
            db.session.commit()
            flash(f'Location "{name}" creata con successo!', 'success')
            return redirect(url_for('locations_bp.manage_locations'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore nella creazione: {str(e)}', 'danger')
    
    # Lista delle città disponibili
    cities = ['Toronto', 'Miami', 'New York', 'Chicago', 'Los Angeles', 
              'Dallas', 'Boston', 'Las Vegas', 'San Jose', 'Denver']
    
    return render_template('admin/create_location.html', cities=cities)

@locations_bp.route('/edit/<location_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_location(location_id):
    """Modifica una location esistente"""
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        
        if not all([name, address, city]):
            flash('Tutti i campi sono obbligatori.', 'danger')
            return render_template('admin/edit_location.html', location=location)
        
        # Verifica duplicati (escludendo la location corrente)
        existing = Location.query.filter(
            Location.name == name,
            Location.city == city,
            Location.id != location.id
        ).first()
        
        if existing:
            flash(f'Esiste già una location "{name}" a {city}.', 'warning')
            return render_template('admin/edit_location.html', location=location)
        
        location.name = name
        location.address = address
        location.city = city
        
        try:
            db.session.commit()
            flash('Location aggiornata con successo!', 'success')
            return redirect(url_for('locations_bp.manage_locations'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore nell\'aggiornamento: {str(e)}', 'danger')
    
    cities = ['Toronto', 'Miami', 'New York', 'Chicago', 'Los Angeles', 
              'Dallas', 'Boston', 'Las Vegas', 'San Jose', 'Denver']
    
    return render_template('admin/edit_location.html', location=location, cities=cities)

@locations_bp.route('/delete/<location_id>')
@login_required
@admin_required
def delete_location(location_id):
    """Elimina una location"""
    location = Location.query.get_or_404(location_id)
    
    # Verifica se ci sono ordini associati
    if location.orders:
        flash(f'Impossibile eliminare "{location.name}": ci sono {len(location.orders)} ordini associati.', 'warning')
        return redirect(url_for('locations_bp.manage_locations'))
    
    try:
        db.session.delete(location)
        db.session.commit()
        flash(f'Location "{location.name}" eliminata con successo.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nell\'eliminazione: {str(e)}', 'danger')
    
    return redirect(url_for('locations_bp.manage_locations'))

@locations_bp.route('/api/by-city/<city>')
@login_required
def get_locations_by_city(city):
    """API endpoint per ottenere le location di una città (per AJAX)"""
    locations = Location.query.filter_by(city=city).order_by(Location.name).all()
    return jsonify([{
        'id': loc.id,
        'name': loc.name,
        'address': loc.address,
        'display_name': f"{loc.name} - {loc.address}"
    } for loc in locations])
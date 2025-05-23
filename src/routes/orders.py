from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_mail import Message
from flask_login import login_required, current_user
from src.extensions import db, mail
from src.models.order import Order
from src.models.supplier import Supplier
from src.models.product import Product
from src.models.order_item import OrderItem
from src.models.location import Location

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    suppliers = Supplier.query.filter_by(location=current_user.location).all()
    # Ottieni location per la città dell'utente
    locations = Location.query.filter_by(city=current_user.location).order_by(Location.name).all()

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        location_id = request.form.get('location_id')  # NUOVO campo location
        notes = request.form.get('notes', '').strip()  # NUOVO campo note
        cc_email = request.form.get('cc_email', '').strip()
        
        supplier = Supplier.query.get(supplier_id)
        location = Location.query.get(location_id) if location_id else None

        # Validazioni
        if not supplier or supplier.location != current_user.location:
            flash('Fornitore non valido o non autorizzato.', 'danger')
            return redirect(url_for('orders_bp.create_order'))
        
        if location_id and (not location or location.city != current_user.location):
            flash('Location non valida o non autorizzata.', 'danger')
            return redirect(url_for('orders_bp.create_order'))

        # Raccolta prodotti
        order_items = []
        for product in supplier.products:
            qty = int(request.form.get(f'product_{product.id}', 0))
            price = float(request.form.get(f'price_{product.id}', product.price or 0))
            
            if qty > 0:
                order_items.append({
                    'product': product,
                    'quantity': qty,
                    'price': price
                })

        if not order_items:
            flash("Nessun prodotto selezionato.", 'warning')
            return redirect(url_for('orders_bp.create_order'))

        # Crea ordine con i nuovi campi
        new_order = Order(
            supplier_id=supplier_id,
            user_id=current_user.id,
            location=current_user.location,  # Città (compatibilità)
            location_id=location_id,  # NUOVO: Location specifica
            notes=notes,  # NUOVO: Note
            cc_email=cc_email
        )
        
        try:
            db.session.add(new_order)
            db.session.flush()

            # Aggiunge gli OrderItem con dati salvati per storico
            for item in order_items:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item['product'].id,
                    product_name=item['product'].name,  # Salva per storico
                    product_unit=item['product'].unit,  # Salva per storico
                    quantity=item['quantity'],
                    unit_price=item['price']
                )
                db.session.add(order_item)

            db.session.commit()

            # Prepara dati per email
            email_items = [{
                'name': i['product'].name,
                'unit': i['product'].unit,
                'quantity': i['quantity'],
                'price': i['price']
            } for i in order_items]

            custom_cc = [email.strip() for email in cc_email.split(",") if email.strip()] if cc_email else []

            # Invia email con nuovi parametri
            send_order_email(supplier, email_items, custom_cc, location, notes)
            flash("Ordine inviato con successo!", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"Errore nella creazione dell'ordine: {e}", "danger")
            return redirect(url_for('orders_bp.create_order'))

        return redirect(url_for('auth_bp.dashboard'))

    return render_template('create_order.html', suppliers=suppliers, locations=locations)

@orders_bp.route('/recent-orders')
@login_required
def recent_orders():
    if current_user.is_admin:
        orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
    else:
        orders = Order.query.filter_by(location=current_user.location).order_by(Order.created_at.desc()).limit(50).all()
    
    return render_template('recent_orders.html', orders=orders)

@orders_bp.route('/order-details/<order_id>')
@login_required
def order_details(order_id):
    """Vista dettagli ordine"""
    order = Order.query.get_or_404(order_id)
    
    # Verifica accesso
    if not current_user.is_admin and order.location != current_user.location:
        flash('Accesso negato.', 'danger')
        return redirect(url_for('orders_bp.recent_orders'))
    
    return render_template('order_details.html', order=order)

def send_order_email(supplier, order_items, custom_cc=None, location=None, notes=''):
    """
    Invia email ordine con location e note AGGIORNATA
    """
    default_cc = current_app.config.get("DEFAULT_CC_EMAILS", [])
    cc = default_cc + (custom_cc if custom_cc else [])

    # Titolo email con location
    location_name = location.name if location else current_user.location
    subject = f"Nuovo ordine per {supplier.name} - {location_name}"

    try:
        msg = Message(
            subject=subject,
            recipients=[supplier.email],
            cc=cc,
            html=render_template('email_order.html', 
                               supplier=supplier, 
                               order_items=order_items,
                               location=location,
                               location_name=location_name,
                               notes=notes,
                               user_email=current_user.email)
        )
        mail.send(msg)
        
    except Exception as e:
        raise Exception(f"Errore invio email: {str(e)}")
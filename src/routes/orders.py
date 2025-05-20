from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_mail import Message
from flask_login import login_required
from src.extensions import db, mail
from src.models.order import Order
from src.models.supplier import Supplier
from src.models.product import Product

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    suppliers = Supplier.query.all()

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        supplier = Supplier.query.get(supplier_id)

        if not supplier:
            flash('Fornitore non valido.', 'danger')
            return redirect(url_for('orders_bp.create_order'))

        # Leggi quantità e crea lista prodotti ordinati
        order_items = []
        for product in supplier.products:
            qty = int(request.form.get(f'product_{product.id}', 0))
            if qty > 0:
                order_items.append({
                    'name': product.name,
                    'unit': product.unit,
                    'quantity': qty
                })

        if not order_items:
            flash("Nessun prodotto selezionato.", 'warning')
            return redirect(url_for('orders_bp.create_order'))

        # Salva ordine nel DB
        new_order = Order(supplier_id=supplier_id)
        db.session.add(new_order)
        db.session.commit()

        # Elenco email in CC personalizzato dal form
        custom_cc = request.form.get("cc_email", "")
        custom_cc = [email.strip() for email in custom_cc.split(",") if email.strip()] if custom_cc else []

        # Invia email
        try:
            send_order_email(supplier, order_items, custom_cc)
            flash("Ordine inviato con successo!", "success")
        except Exception as e:
            flash(f"Errore invio email: {e}", "danger")

        return redirect(url_for('auth_bp.dashboard'))

    return render_template('create_order.html', suppliers=suppliers)


@orders_bp.route('/recent-orders')
@login_required

def recent_orders():
    orders = Order.query.filter_by(location=current_user.location).order_by(Order.id.desc()).all()
    return render_template('recent_orders.html', orders=orders)

def send_order_email(supplier, order_items, custom_cc=None):
    default_cc = current_app.config.get("DEFAULT_CC_EMAILS", [])
    cc = default_cc + (custom_cc if custom_cc else [])

    msg = Message(
        subject=f"Nuovo ordine per {supplier.name}",
        recipients=[supplier.email],
        cc=cc,
        html=render_template('email_order.html', supplier=supplier, order_items=order_items)
    )

    mail.send(msg)
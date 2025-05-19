from flask import Blueprint, render_template, request, redirect, url_for, flash
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
        cc_email = request.form.get('cc_email')

        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            flash('Fornitore non valido.', 'danger')
            return redirect(url_for('orders_bp.create_order'))

        # Legge quantità selezionate
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

        # Costruisci stringa "testuale" da salvare nel DB
        details = "\n".join([f"{item['name']} - {item['quantity']} {item['unit']}" for item in order_items])

        # Salva nel DB
        new_order = Order(supplier_id=supplier_id)
        db.session.add(new_order)
        db.session.commit()

        # Invia email HTML
        try:
            msg = Message(
                subject="Nuovo Ordine da Rossopomodoro",
                recipients=[supplier.email],
                cc=[cc_email] if cc_email else []
            )
            msg.html = render_template("email_order.html", supplier=supplier, order_items=order_items)
            mail.send(msg)
            flash("Ordine inviato con successo!", "success")
        except Exception as e:
            flash(f"Errore invio email: {e}", "danger")

        return redirect(url_for('auth_bp.dashboard'))

    return render_template('create_order.html', suppliers=suppliers)
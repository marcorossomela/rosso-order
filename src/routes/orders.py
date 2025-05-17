from flask import Blueprint, render_template, request, flash, redirect, url_for
from src.models.supplier import Supplier
from src.models.product import Product
from flask_mail import Message
from src.extensions import db, mail

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/orders', methods=['GET', 'POST'])
def orders():
    suppliers = Supplier.query.all()
    products = Product.query.all()

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        cc_email = request.form.get('cc_email')
        selected_supplier = Supplier.query.get(supplier_id)

        order_lines = []
        for product in products:
            qty = request.form.get(f'quantity_{product.id}')
            if qty and qty.strip() != "":
                order_lines.append(f"{product.name} ({product.unit}): {qty}")

        body = f"Ordine per {selected_supplier.name}:\n\n" + "\n".join(order_lines)

        msg = Message(
            subject="Nuovo ordine Rossopomodoro",
            recipients=[selected_supplier.email],
            cc=[cc_email] if cc_email else [],
            body=body
        )
        mail.send(msg)
        flash('Ordine inviato con successo!', 'success')
        return redirect(url_for('orders_bp.orders'))

    return render_template('orders.html', suppliers=suppliers, products=products)
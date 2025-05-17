from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.extensions import db
from src.models.supplier import Supplier
from src.models.product import Product

suppliers_bp = Blueprint('suppliers_bp', __name__)

@suppliers_bp.route('/suppliers-products', methods=['GET', 'POST'])
def manage_suppliers_products():
    if request.method == 'POST':
        # Aggiungi fornitore
        if 'supplier_name' in request.form:
            name = request.form.get('supplier_name', '').strip()
            email = request.form.get('supplier_email', '').strip()
            phone = request.form.get('supplier_phone', '').strip()
            if name and email:
                existing = Supplier.query.filter_by(email=email).first()
                if existing:
                    flash('Fornitore già presente con questa email.', 'warning')
                else:
                    db.session.add(Supplier(name=name, email=email, phone=phone))
                    db.session.commit()
                    flash('Fornitore aggiunto con successo!', 'success')
            else:
                flash('Nome e Email sono obbligatori per i fornitori.', 'danger')

        # Aggiungi prodotto
        elif 'product_name' in request.form:
            name = request.form.get('product_name', '').strip()
            unit = request.form.get('product_unit', '').strip()
            if name and unit:
                existing = Product.query.filter_by(name=name, unit=unit).first()
                if existing:
                    flash('Prodotto già presente.', 'warning')
                else:
                    db.session.add(Product(name=name, unit=unit))
                    db.session.commit()
                    flash('Prodotto aggiunto con successo!', 'success')
            else:
                flash('Nome e Unità sono obbligatori per i prodotti.', 'danger')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))
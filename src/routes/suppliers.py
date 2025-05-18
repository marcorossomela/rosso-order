# === FILE 1: suppliers.py aggiornato ===
from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.extensions import db
from src.models.supplier import Supplier
from src.models.product import Product

suppliers_bp = Blueprint('suppliers_bp', __name__)

@suppliers_bp.route('/suppliers-products', methods=['GET', 'POST'])
def manage_suppliers_products():
    if request.method == 'POST':
        # Aggiunta fornitore con prodotti base
        if 'email' in request.form and 'phone' in request.form:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()

            if name and email:
                existing = Supplier.query.filter_by(email=email).first()
                if existing:
                    flash('Fornitore già esistente con questa email.', 'warning')
                else:
                    supplier = Supplier(name=name, email=email, phone=phone)
                    db.session.add(supplier)
                    db.session.flush()

                    default_products = [
                        ('Pomodoro', 'Kg'),
                        ('Mozzarella', 'Kg'),
                        ('Farina', 'Bag'),
                        ('Olio', 'Each')
                    ]

                    for pname, unit in default_products:
                        product = Product(name=pname, unit=unit, supplier_id=supplier.id)
                        db.session.add(product)

                    db.session.commit()
                    flash('Fornitore e prodotti base aggiunti!', 'success')
            else:
                flash('Nome e email sono obbligatori per il fornitore.', 'danger')

        # Aggiunta prodotto
        elif 'supplier_id' in request.form:
            name = request.form.get('name', '').strip()
            unit = request.form.get('unit', '').strip()
            supplier_id = request.form.get('supplier_id')

            if name and unit and supplier_id:
                existing = Product.query.filter_by(name=name, unit=unit, supplier_id=supplier_id).first()
                if existing:
                    flash('Prodotto già esistente per questo fornitore.', 'warning')
                else:
                    db.session.add(Product(name=name, unit=unit, supplier_id=supplier_id))
                    db.session.commit()
                    flash('Prodotto aggiunto con successo!', 'success')
            else:
                flash('Tutti i campi sono obbligatori per aggiungere un prodotto.', 'danger')

        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)
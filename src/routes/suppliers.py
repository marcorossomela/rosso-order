from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.extensions import db
from src.models.supplier import Supplier
from src.models.product import Product

suppliers_bp = Blueprint('suppliers_bp', __name__)

# Vista principale: gestione
@suppliers_bp.route('/suppliers-products', methods=['GET', 'POST'])
def manage_suppliers_products():
    if request.method == 'POST':
        # Aggiunta fornitore
        if 'email' in request.form and 'phone' in request.form:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()

            if name and email:
                existing = Supplier.query.filter_by(email=email).first()
                if existing:
                    flash('Fornitore già esistente con questa email.', 'warning')
                else:
                    db.session.add(Supplier(name=name, email=email, phone=phone))
                    db.session.commit()
                    flash('Fornitore aggiunto con successo!', 'success')
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

    # GET
    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)

# ----------------------------
# ROUTE CANCELLAZIONE

@suppliers_bp.route('/delete-supplier/<int:supplier_id>', methods=['GET'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    flash('Fornitore eliminato con successo.', 'success')
    return redirect(url_for('suppliers_bp.manage_suppliers_products'))

@suppliers_bp.route('/delete-product/<int:product_id>', methods=['GET'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Prodotto eliminato con successo.', 'success')
    return redirect(url_for('suppliers_bp.manage_suppliers_products'))

# ----------------------------
# ROUTE MODIFICA (con form semplice GET + POST)

@suppliers_bp.route('/edit-supplier/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    if request.method == 'POST':
        supplier.name = request.form['name']
        supplier.email = request.form['email']
        supplier.phone = request.form['phone']
        db.session.commit()
        flash('Fornitore aggiornato con successo.', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))
    return render_template('edit_supplier.html', supplier=supplier)

@suppliers_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.unit = request.form['unit']
        product.supplier_id = request.form['supplier_id']
        db.session.commit()
        flash('Prodotto aggiornato con successo.', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    suppliers = Supplier.query.all()
    return render_template('edit_product.html', product=product, suppliers=suppliers)
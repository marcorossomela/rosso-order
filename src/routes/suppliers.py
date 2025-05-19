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

                    product_names = request.form.getlist('product_name[]')
                    product_units = request.form.getlist('product_unit[]')

                    for pname, unit in zip(product_names, product_units):
                        if pname and unit:
                            db.session.add(Product(
                                name=pname.strip(),
                                unit=unit.strip(),
                                supplier_id=supplier.id
                            ))

                    db.session.commit()
                    flash('Fornitore e prodotti aggiunti con successo.', 'success')
            else:
                flash('Nome e email sono obbligatori per il fornitore.', 'danger')

        # Aggiunta singolo prodotto
        elif 'supplier_id' in request.form:
            name = request.form.get('name', '').strip()
            unit = request.form.get('unit', '').strip()
            supplier_id = request.form.get('supplier_id')

            if name and unit and supplier_id:
                existing = Product.query.filter_by(
                    name=name,
                    unit=unit,
                    supplier_id=supplier_id
                ).first()
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


@suppliers_bp.route('/edit/<string:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if request.method == 'POST':
        # Aggiorna dati del fornitore
        supplier.name = request.form.get('name', '').strip()
        supplier.email = request.form.get('email', '').strip()
        supplier.phone = request.form.get('phone', '').strip()

        # Aggiunta nuovi prodotti se presenti
        product_names = request.form.getlist('product_name[]')
        product_units = request.form.getlist('product_unit[]')

        for pname, unit in zip(product_names, product_units):
            if pname.strip() and unit.strip():
                existing = Product.query.filter_by(
                    name=pname.strip(),
                    unit=unit.strip(),
                    supplier_id=supplier.id
                ).first()
                if not existing:
                    db.session.add(Product(
                        name=pname.strip(),
                        unit=unit.strip(),
                        supplier_id=supplier.id
                    ))

        db.session.commit()
        flash('Fornitore e nuovi prodotti aggiornati con successo!', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    return render_template('edit_supplier.html', supplier=supplier)

@suppliers_bp.route('/delete/<string:supplier_id>', methods=['POST', 'GET'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    # Elimina prima i prodotti associati
    Product.query.filter_by(supplier_id=supplier.id).delete()

    # Poi elimina il fornitore
    db.session.delete(supplier)
    db.session.commit()

    flash('Fornitore e prodotti associati eliminati con successo.', 'success')
    return redirect(url_for('suppliers_bp.manage_suppliers_products'))


@suppliers_bp.route('/edit-product/<string:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    suppliers = Supplier.query.all()

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.unit = request.form.get('unit', '').strip()
        product.supplier_id = request.form.get('supplier_id')
        db.session.commit()
        flash('Prodotto aggiornato con successo!', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    return render_template('edit_product.html', product=product, suppliers=suppliers)
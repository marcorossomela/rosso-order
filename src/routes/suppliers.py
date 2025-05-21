from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.extensions import db
from src.models.supplier import Supplier
from src.models.product import Product

suppliers_bp = Blueprint('suppliers_bp', __name__)

@suppliers_bp.route('/suppliers-products', methods=['GET', 'POST'])
@login_required
def manage_suppliers_products():
    if request.method == 'POST':
        # Aggiunta fornitore con prodotti
        if 'email' in request.form and 'phone' in request.form:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()

            if name and email:
                existing = Supplier.query.filter_by(email=email).first()
                if existing:
                    flash('Fornitore già esistente con questa email.', 'warning')
                else:
                    supplier = Supplier(
                        name=name,
                        email=email,
                        phone=phone,
                        location=current_user.location
                    )
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
                flash('Nome e email sono obbligatori.', 'danger')

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
                    db.session.add(Product(
                        name=name,
                        unit=unit,
                        supplier_id=supplier_id
                    ))
                    db.session.commit()
                    flash('Prodotto aggiunto con successo!', 'success')
            else:
                flash('Tutti i campi sono obbligatori.', 'danger')

        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    suppliers = Supplier.query.filter_by(location=current_user.location).all()
    return render_template('suppliers.html', suppliers=suppliers)

@suppliers_bp.route('/edit/<string:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if supplier.location != current_user.location:
        flash("Accesso negato a questo fornitore.", "danger")
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    if request.method == 'POST':
        supplier.name = request.form.get('name', '').strip()
        supplier.email = request.form.get('email', '').strip()
        supplier.phone = request.form.get('phone', '').strip()

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
        flash('Fornitore aggiornato con successo!', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    return render_template('edit_supplier.html', supplier=supplier)

@suppliers_bp.route('/delete/<string:supplier_id>', methods=['POST', 'GET'])
@login_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if supplier.location != current_user.location:
        flash("Non puoi eliminare fornitori di altre sedi.", "danger")
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    Product.query.filter_by(supplier_id=supplier.id).delete()
    db.session.delete(supplier)
    db.session.commit()

    flash('Fornitore eliminato con successo.', 'success')
    return redirect(url_for('suppliers_bp.manage_suppliers_products'))

@suppliers_bp.route('/')
@login_required
def list_suppliers():
    suppliers = Supplier.query.filter_by(location=current_user.location).all()
    return render_template('suppliers_list.html', suppliers=suppliers)

@suppliers_bp.route('/edit-product/<string:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    supplier = Supplier.query.get(product.supplier_id)

    if supplier.location != current_user.location:
        flash("Non puoi modificare prodotti di altri fornitori.", "danger")
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.unit = request.form.get('unit', '').strip()
        db.session.commit()
        flash('Prodotto aggiornato con successo!', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    return render_template('edit_product.html', product=product, suppliers=[supplier])
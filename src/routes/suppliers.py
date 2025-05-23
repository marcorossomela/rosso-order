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
                # Verifica email duplicata nella stessa location
                existing = Supplier.query.filter_by(
                    email=email, 
                    location=current_user.location
                ).first()
                
                if existing:
                    flash('Fornitore già esistente con questa email nella tua location.', 'warning')
                else:
                    supplier = Supplier(
                        name=name,
                        email=email,
                        phone=phone,
                        location=current_user.location
                    )
                    db.session.add(supplier)
                    db.session.flush()

                    # Gestione prodotti con prezzi
                    product_names = request.form.getlist('product_name[]')
                    product_units = request.form.getlist('product_unit[]')
                    product_prices = request.form.getlist('product_price[]')  # NUOVO: prezzi

                    for i, (pname, unit) in enumerate(zip(product_names, product_units)):
                        if pname.strip() and unit.strip():
                            # Ottieni prezzo se presente
                            price = 0.0
                            if i < len(product_prices) and product_prices[i]:
                                try:
                                    price = float(product_prices[i])
                                except ValueError:
                                    price = 0.0
                            
                            db.session.add(Product(
                                name=pname.strip(),
                                unit=unit.strip(),
                                price=price,  # NUOVO campo prezzo
                                supplier_id=supplier.id
                            ))

                    db.session.commit()
                    flash('Fornitore e prodotti aggiunti con successo.', 'success')
            else:
                flash('Nome e email sono obbligatori.', 'danger')

        elif 'supplier_id' in request.form:
            # Aggiunta singolo prodotto
            name = request.form.get('name', '').strip()
            unit = request.form.get('unit', '').strip()
            price = request.form.get('price', 0)
            supplier_id = request.form.get('supplier_id')

            if name and unit and supplier_id:
                # Converti prezzo
                try:
                    price = float(price) if price else 0.0
                except ValueError:
                    price = 0.0
                
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
                        price=price,  # NUOVO campo prezzo
                        supplier_id=supplier_id
                    ))
                    db.session.commit()
                    flash('Prodotto aggiunto con successo!', 'success')
            else:
                flash('Nome e unità sono obbligatori.', 'danger')

        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    # GET request - mostra suppliers con ricerca
    search_query = request.args.get('q', '').strip()
    suppliers_query = Supplier.query.filter_by(location=current_user.location)
    
    if search_query:
        suppliers_query = suppliers_query.filter(
            (Supplier.name.ilike(f'%{search_query}%')) |
            (Supplier.email.ilike(f'%{search_query}%'))
        )
    
    suppliers = suppliers_query.order_by(Supplier.name).all()
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

        # Verifica email duplicata (escludendo il supplier corrente)
        existing = Supplier.query.filter(
            Supplier.email == supplier.email,
            Supplier.location == current_user.location,
            Supplier.id != supplier.id
        ).first()
        
        if existing:
            flash('Esiste già un fornitore con questa email.', 'warning')
            return render_template('edit_supplier.html', supplier=supplier)

        # Aggiungi nuovi prodotti con prezzi
        product_names = request.form.getlist('product_name[]')
        product_units = request.form.getlist('product_unit[]')
        product_prices = request.form.getlist('product_price[]')  # NUOVO

        for i, (pname, unit) in enumerate(zip(product_names, product_units)):
            if pname.strip() and unit.strip():
                # Ottieni prezzo se presente
                price = 0.0
                if i < len(product_prices) and product_prices[i]:
                    try:
                        price = float(product_prices[i])
                    except ValueError:
                        price = 0.0
                
                existing = Product.query.filter_by(
                    name=pname.strip(),
                    unit=unit.strip(),
                    supplier_id=supplier.id
                ).first()
                
                if not existing:
                    db.session.add(Product(
                        name=pname.strip(),
                        unit=unit.strip(),
                        price=price,  # NUOVO campo prezzo
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

    # Verifica se ha ordini associati
    if supplier.orders:
        flash(f'Impossibile eliminare "{supplier.name}": ci sono {len(supplier.orders)} ordini associati.', 'warning')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    # Elimina prodotti associati
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
        
        # Gestione prezzo AGGIORNATA
        price = request.form.get('price', 0)
        try:
            product.price = float(price) if price else 0.0
        except ValueError:
            product.price = 0.0
        
        # Gestione cambio fornitore (opzionale)
        new_supplier_id = request.form.get('supplier_id')
        if new_supplier_id and new_supplier_id != product.supplier_id:
            new_supplier = Supplier.query.get(new_supplier_id)
            if new_supplier and new_supplier.location == current_user.location:
                product.supplier_id = new_supplier_id
            else:
                flash('Fornitore non valido.', 'danger')
                suppliers = Supplier.query.filter_by(location=current_user.location).all()
                return render_template('edit_product.html', product=product, suppliers=suppliers)
        
        db.session.commit()
        flash('Prodotto aggiornato con successo!', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    suppliers = Supplier.query.filter_by(location=current_user.location).all()
    return render_template('edit_product.html', product=product, suppliers=suppliers)

@suppliers_bp.route('/product/delete/<string:product_id>')
@login_required
def delete_product(product_id):
    """Elimina un prodotto"""
    product = Product.query.get_or_404(product_id)
    supplier = Supplier.query.get(product.supplier_id)
    
    # Verifica accesso
    if supplier.location != current_user.location:
        flash('Accesso negato.', 'danger')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))
    
    # Verifica se ha order_items associati
    if hasattr(product, 'order_items') and product.order_items:
        flash(f'Impossibile eliminare "{product.name}": è presente in ordini esistenti.', 'warning')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f'Prodotto "{product.name}" eliminato con successo.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nell\'eliminazione: {str(e)}', 'danger')
    
    return redirect(url_for('suppliers_bp.manage_suppliers_products'))
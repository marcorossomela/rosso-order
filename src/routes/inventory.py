from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from src.extensions import db
from src.models.inventory import InventoryItem, InventoryMeta
from src.models.supplier import Supplier
from src.models.product import Product
from src.models.order import Order
from src.models.order_item import OrderItem
import io
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from sqlalchemy import func

inventory_bp = Blueprint('inventory_bp', __name__)

def calculate_vendor_spending(month, location):
    """Calcola automaticamente la spesa dai fornitori per il mese corrente"""
    try:
        # Utilizzando il nuovo modello Order con created_at
        total_spending = db.session.query(
            func.sum(OrderItem.quantity * OrderItem.unit_price)
        ).join(Order).filter(
            Order.location == location,
            func.date_format(Order.created_at, '%Y-%m') == month
        ).scalar()
        
        return total_spending or 0
    except Exception as e:
        print(f"Errore nel calcolo vendor spending: {e}")
        # Fallback: calcola senza filtro data se i nuovi campi non esistono ancora
        try:
            total_spending = db.session.query(
                func.sum(OrderItem.quantity * OrderItem.unit_price)
            ).join(Order).filter(
                Order.location == location
            ).scalar()
            return total_spending or 0
        except:
            return 0

def get_previous_month_inventory(current_month, location, user_id):
    """Ottiene l'inventario finale del mese precedente"""
    try:
        # Converti il mese corrente in datetime per calcolare il precedente
        year, month = map(int, current_month.split('-'))
        if month == 1:
            prev_month = f"{year-1}-12"
        else:
            prev_month = f"{year}-{month-1:02d}"
        
        # Cerca i metadati del mese precedente
        prev_meta = InventoryMeta.query.filter_by(
            month=prev_month,
            location=location,
            user_id=user_id
        ).first()
        
        if prev_meta:
            # Calcola il totale inventario del mese precedente
            prev_items = InventoryItem.query.filter_by(
                month=prev_month,
                location=location,
                user_id=user_id
            ).all()
            total_prev_inventory = sum(item.total() for item in prev_items)
            return total_prev_inventory
        return 0
    except:
        return 0

@inventory_bp.route('/inventory', methods=['GET'])
@login_required
def view_inventory():
    selected_month = request.args.get('month') or datetime.now().strftime('%Y-%m')

    # Elenco mesi disponibili per il selettore
    months = db.session.query(InventoryItem.month).distinct().order_by(InventoryItem.month.desc()).all()
    months = [m[0] for m in months] if months else [selected_month]
    
    # Aggiungi il mese corrente se non presente
    if selected_month not in months:
        months.insert(0, selected_month)

    # Meta info
    if current_user.is_admin:
        location = request.args.get('admin_location') or current_user.location
        meta = InventoryMeta.query.filter_by(month=selected_month, location=location).first()
    else:
        location = current_user.location
        meta = InventoryMeta.query.filter_by(user_id=current_user.id, month=selected_month).first()

    if not meta:
        # Calcola automaticamente previous_inventory e vendor_spending
        prev_inventory = get_previous_month_inventory(selected_month, location, current_user.id)
        vendor_spending = calculate_vendor_spending(selected_month, location)
        
        meta = InventoryMeta(
            user_id=current_user.id,
            month=selected_month,
            location=location,
            previous_inventory=prev_inventory,
            vendor_spending=vendor_spending,
            credit_notes=0,
            monthly_sales=0
        )
        db.session.add(meta)
        db.session.commit()
    else:
        # Aggiorna automaticamente vendor_spending anche se il record esiste
        meta.vendor_spending = calculate_vendor_spending(selected_month, location)
        db.session.commit()

    # Caricamento fornitori e prodotti
    if current_user.is_admin:
        suppliers = Supplier.query.filter_by(location=location).all()
    else:
        suppliers = Supplier.query.filter_by(location=current_user.location).all()

    supplier_ids = [s.id for s in suppliers]
    products = Product.query.filter(Product.supplier_id.in_(supplier_ids)).all()

    items = []
    for p in products:
        item_query = InventoryItem.query.filter_by(
            month=selected_month,
            product_name=p.name,
            supplier_name=p.supplier.name
        )
        if not current_user.is_admin:
            item_query = item_query.filter_by(user_id=current_user.id)
        item = item_query.first()

        if not item:
            item = InventoryItem(
                user_id=current_user.id,
                month=selected_month,
                product_name=p.name,
                supplier_name=p.supplier.name,
                quantity=0,
                unit_price=p.unit_price or 0,  # Usa il prezzo del prodotto come default
                location=location
            )
            db.session.add(item)
            db.session.commit()
        items.append((p, item))

    # Ottieni le location uniche dai fornitori (solo per admin)
    locations = []
    if current_user.is_admin:
        locations = [row.location for row in Supplier.query.with_entities(Supplier.location).distinct().all()]

    return render_template(
        'inventory.html',
        selected_month=selected_month,
        months=months,
        inventory_meta=meta,
        inventory_items=items,
        locations=locations
    )


@inventory_bp.route('/inventory/update', methods=['POST'])
@login_required
def update_inventory():
    selected_month = request.form.get('month')
    
    # Aggiorna i meta fields
    meta_query = InventoryMeta.query.filter_by(month=selected_month)
    if not current_user.is_admin:
        meta_query = meta_query.filter_by(user_id=current_user.id)
    meta = meta_query.first()
    
    if meta:
        # Aggiorna solo i campi modificabili manualmente
        meta.credit_notes = float(request.form.get('credit_notes', 0))
        meta.monthly_sales = float(request.form.get('monthly_sales', 0))
        # previous_inventory e vendor_spending rimangono automatici
    
    # Aggiorna gli item dell'inventario
    for key in request.form:
        if key.startswith('qty_'):
            name = key.replace('qty_', '')
            item_query = InventoryItem.query.filter_by(month=selected_month, product_name=name)
            if not current_user.is_admin:
                item_query = item_query.filter_by(user_id=current_user.id)
            item = item_query.first()

            if item:
                item.quantity = float(request.form.get(key, 0))
                item.unit_price = float(request.form.get(f'price_{name}', 0))
    
    db.session.commit()
    flash("Inventario aggiornato con successo!", "success")
    return redirect(url_for('inventory_bp.view_inventory', month=selected_month))


@inventory_bp.route('/inventory/export/csv')
@login_required
def export_inventory_csv():
    selected_month = request.args.get('month') or datetime.now().strftime('%Y-%m')
    selected_location = request.args.get('location')

    query = db.session.query(
        InventoryItem.month,
        InventoryItem.product_name,
        InventoryItem.quantity,
        InventoryItem.unit_price,
        (InventoryItem.quantity * InventoryItem.unit_price).label('total'),
        InventoryItem.supplier_name,
        InventoryItem.location
    ).filter(InventoryItem.month == selected_month)

    if current_user.is_admin and selected_location:
        query = query.filter(InventoryItem.location == selected_location)
    elif not current_user.is_admin:
        query = query.filter(InventoryItem.location == current_user.location)

    df = pd.read_sql(query.statement, db.session.bind)

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    location_name = selected_location or current_user.location
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'inventory_{location_name}_{selected_month}.csv'
    )


@inventory_bp.route('/inventory/export/pdf')
@login_required
def export_inventory_pdf():
    selected_month = request.args.get('month') or datetime.now().strftime('%Y-%m')
    selected_location = request.args.get('location')

    query = db.session.query(
        InventoryItem.product_name,
        InventoryItem.quantity,
        InventoryItem.unit_price,
        (InventoryItem.quantity * InventoryItem.unit_price).label('total'),
        InventoryItem.supplier_name,
        InventoryItem.location
    ).filter(InventoryItem.month == selected_month)

    if current_user.is_admin and selected_location:
        query = query.filter(InventoryItem.location == selected_location)
    elif not current_user.is_admin:
        query = query.filter(InventoryItem.location == current_user.location)

    results = query.all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    title_location = selected_location if selected_location else current_user.location
    p.drawString(50, height - 50, f"Inventario - {selected_month} ({title_location})")
    p.setFont("Helvetica", 10)

    y = height - 80
    for item in results:
        line = f"{item.product_name} ({item.supplier_name}, {item.location}): Qty={item.quantity}, Price=${item.unit_price}, Total=${item.total}"
        p.drawString(50, y, line)
        y -= 15
        if y < 50:
            p.showPage()
            y = height - 50

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'inventory_{title_location}_{selected_month}.pdf',
        mimetype='application/pdf'
    )
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from datetime import datetime
from src.extensions import db
from src.models.inventory import InventoryItem, InventoryMeta
from src.models.supplier import Supplier
from src.models.product import Product
import io
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

inventory_bp = Blueprint('inventory_bp', __name__)

@inventory_bp.route('/inventory', methods=['GET', 'POST'])
@login_required
def view_inventory():
    selected_month = request.args.get('month') or datetime.now().strftime('%Y-%m')

    # Elenco mesi disponibili per il selettore
    months = db.session.query(InventoryItem.month).distinct().order_by(InventoryItem.month.desc()).all()
    months = [m[0] for m in months] if months else [selected_month]

    # Meta info
    if current_user.is_admin:
        meta = InventoryMeta.query.filter_by(month=selected_month, location=current_user.location).first()
    else:
        meta = InventoryMeta.query.filter_by(user_id=current_user.id, month=selected_month).first()

    if not meta:
        meta = InventoryMeta(
            user_id=current_user.id,
            month=selected_month,
            location=current_user.location,
            previous_inventory=0,
            credit_notes=0,
            monthly_sales=0
        )
        db.session.add(meta)
        db.session.commit()

    # Gestione form POST per meta info
    if request.method == 'POST':
        meta.previous_inventory = float(request.form.get('previous_inventory', 0))
        meta.credit_notes = float(request.form.get('credit_notes', 0))
        meta.monthly_sales = float(request.form.get('monthly_sales', 0))
        db.session.commit()
        flash("Dati inventario aggiornati.", "success")
        return redirect(url_for('inventory_bp.view_inventory', month=selected_month))

    # Caricamento fornitori e prodotti
    if current_user.is_admin:
        suppliers = Supplier.query.all()
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
                unit_price=0,
                location=current_user.location
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
        month=selected_month,
        months=months,
        inventory_meta=meta,
        inventory_items=items,
        locations=locations
    )


@inventory_bp.route('/inventory/update', methods=['POST'])
@login_required
def update_inventory():
    selected_month = request.form.get('month')
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
    flash("Inventario aggiornato.", "success")
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
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
        total_spending = db.session.query(
            func.sum(OrderItem.quantity * OrderItem.unit_price)
        ).join(Order).filter(
            Order.location == location,
            func.to_char(Order.created_at, 'YYYY-MM') == month
        ).scalar()

        return total_spending or 0
    except Exception as e:
        print(f"Errore nel calcolo vendor spending: {e}")
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
        year, month = map(int, current_month.split('-'))
        if month == 1:
            prev_month = f"{year-1}-12"
        else:
            prev_month = f"{year}-{month-1:02d}"

        prev_meta = InventoryMeta.query.filter_by(
            month=prev_month,
            location=location,
            user_id=user_id
        ).first()

        if prev_meta:
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

    months = db.session.query(InventoryItem.month).distinct().order_by(InventoryItem.month.desc()).all()
    months = [m[0] for m in months] if months else [selected_month]
    if selected_month not in months:
        months.insert(0, selected_month)

    if current_user.is_admin:
        location = request.args.get('admin_location') or current_user.location
        meta = InventoryMeta.query.filter_by(month=selected_month, location=location).first()
    else:
        location = current_user.location
        meta = InventoryMeta.query.filter_by(user_id=current_user.id, month=selected_month).first()

    if not meta:
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
        meta.vendor_spending = calculate_vendor_spending(selected_month, location)
        db.session.commit()

    if current_user.is_admin:
        suppliers = Supplier.query.filter_by(location=location).all()
    else:
        suppliers = Supplier.query.filter_by(location=current_user.location).all()

    supplier_ids = [s.id for s in suppliers] if suppliers else []
    products = Product.query.filter(Product.supplier_id.in_(supplier_ids)).all() if supplier_ids else []

    items = []
    for p in products:
        # Gestione sicura del supplier name
        try:
            supplier_name = p.supplier.name if p.supplier else "Fornitore Sconosciuto"
        except AttributeError:
            supplier_name = "Fornitore Sconosciuto"
            
        item_query = InventoryItem.query.filter_by(
            month=selected_month,
            product_name=p.name,
            supplier_name=supplier_name
        )
        if not current_user.is_admin:
            item_query = item_query.filter_by(user_id=current_user.id)
        item = item_query.first()

        if not item:
            # Il modello Product usa 'price', non 'unit_price'
            unit_price = float(p.price) if p.price else 0.0
            
            item = InventoryItem(
                user_id=current_user.id,
                month=selected_month,
                product_name=p.name,
                supplier_name=supplier_name,
                quantity=0,
                unit_price=unit_price,
                location=location
            )
            db.session.add(item)
            db.session.commit()
        items.append((p, item))

    locations = []
    if current_user.is_admin:
        locations = [row.location for row in Supplier.query.with_entities(Supplier.location).distinct().all()]

    total_inventory = sum(item.total() for _, item in items)

    return render_template(
        'inventory.html',
        selected_month=selected_month,
        months=months,
        inventory_meta=meta,
        inventory_items=items,
        locations=locations,
        total_inventory=total_inventory
    )

@inventory_bp.route('/update', methods=['POST'])
@login_required
def update_inventory():
    """Aggiorna l'inventario"""
    selected_month = request.form.get('month', datetime.now().strftime('%Y-%m'))
    credit_notes = float(request.form.get('credit_notes', 0))
    monthly_sales = float(request.form.get('monthly_sales', 0))

    # Aggiorna meta
    if current_user.is_admin:
        location = request.args.get('admin_location') or current_user.location
        meta = InventoryMeta.query.filter_by(month=selected_month, location=location).first()
    else:
        meta = InventoryMeta.query.filter_by(
            user_id=current_user.id, 
            month=selected_month
        ).first()
    
    if meta:
        meta.credit_notes = credit_notes
        meta.monthly_sales = monthly_sales
        
        # Aggiorna quantità e prezzi dei singoli prodotti
        for key, value in request.form.items():
            if key.startswith('qty_'):
                product_name = key[4:]  # Rimuove 'qty_'
                quantity = float(value) if value else 0
                
                # Trova l'item corrispondente
                item_query = InventoryItem.query.filter_by(
                    month=selected_month,
                    product_name=product_name
                )
                if not current_user.is_admin:
                    item_query = item_query.filter_by(user_id=current_user.id)
                
                item = item_query.first()
                if item:
                    item.quantity = quantity
            
            elif key.startswith('price_'):
                product_name = key[6:]  # Rimuove 'price_'
                price = float(value) if value else 0
                
                # Trova l'item corrispondente
                item_query = InventoryItem.query.filter_by(
                    month=selected_month,
                    product_name=product_name
                )
                if not current_user.is_admin:
                    item_query = item_query.filter_by(user_id=current_user.id)
                
                item = item_query.first()
                if item:
                    item.unit_price = price
        
        db.session.commit()
        flash('Inventario aggiornato con successo!', 'success')
    else:
        flash('Errore nell\'aggiornamento inventario.', 'danger')

    return redirect(url_for('inventory_bp.view_inventory', month=selected_month))

@inventory_bp.route('/export-csv')
@login_required
def export_inventory_csv():
    """Esporta inventario in CSV"""
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    if current_user.is_admin:
        location = request.args.get('location', current_user.location)
    else:
        location = current_user.location
    
    # Ottieni dati inventario
    items = InventoryItem.query.filter_by(
        month=selected_month,
        location=location
    ).all()
    
    if not items:
        flash('Nessun dato inventario trovato per il mese selezionato.', 'warning')
        return redirect(url_for('inventory_bp.view_inventory'))
    
    # Crea CSV
    output = io.StringIO()
    output.write("Prodotto,Fornitore,Quantità,Prezzo Unitario,Totale\n")
    
    for item in items:
        output.write(f"{item.product_name},{item.supplier_name},{item.quantity},{item.unit_price},{item.total()}\n")
    
    # Crea response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'inventario_{selected_month}_{location}.csv'
    )

@inventory_bp.route('/export-pdf')
@login_required  
def export_inventory_pdf():
    """Esporta inventario in PDF"""
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    if current_user.is_admin:
        location = request.args.get('location', current_user.location)
    else:
        location = current_user.location
    
    # Ottieni dati
    items = InventoryItem.query.filter_by(
        month=selected_month,
        location=location
    ).all()
    
    if not items:
        flash('Nessun dato inventario trovato.', 'warning')
        return redirect(url_for('inventory_bp.view_inventory'))
    
    # Crea PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.drawString(100, 750, f"Inventario {selected_month} - {location}")
    p.drawString(100, 730, "=" * 50)
    
    y = 700
    total_value = 0
    
    for item in items:
        if y < 100:  # Nuova pagina se necessario
            p.showPage()
            y = 750
            
        item_total = item.total()
        total_value += item_total
        
        p.drawString(100, y, f"{item.product_name}")
        p.drawString(300, y, f"{item.supplier_name}")
        p.drawString(450, y, f"Qty: {item.quantity}")
        p.drawString(500, y, f"€{item_total:.2f}")
        y -= 20
    
    # Totale finale
    y -= 20
    p.drawString(100, y, "=" * 50)
    y -= 20
    p.drawString(100, y, f"TOTALE INVENTARIO: €{total_value:.2f}")
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'inventario_{selected_month}_{location}.pdf'
    )
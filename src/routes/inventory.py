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
                unit_price=p.unit_price or 0,
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
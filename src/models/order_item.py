import uuid
from datetime import datetime
from src.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(
        db.String(36),
        db.ForeignKey('orders.id', name='fk_orderitems_order_id'),
        nullable=False
    )
    product_id = db.Column(
        db.String(36),
        db.ForeignKey('products.id', name='fk_orderitems_product_id'),
        nullable=True  # Può essere null se il prodotto viene eliminato
    )
    
    # Campi del prodotto salvati al momento dell'ordine (per storico)
    product_name = db.Column(db.String(120), nullable=False)
    product_unit = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    
    # NUOVI CAMPI
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def total(self):
        """Calcola il totale per questo item"""
        return round(self.quantity * self.unit_price, 2)
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} - Qty:{self.quantity} - Total:${self.total():.2f}>'
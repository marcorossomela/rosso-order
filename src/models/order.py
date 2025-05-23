import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from src.extensions import db
from src.models.order_item import OrderItem

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    supplier_id = db.Column(
        db.String(36),
        db.ForeignKey('suppliers.id', name='fk_orders_supplier_id'),
        nullable=False
    )
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', name='fk_orders_user_id'),
        nullable=True
    )
    location = db.Column(db.String(50), nullable=True)
    
    # NUOVI CAMPI AGGIUNTI
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    order_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, sent, delivered, cancelled
    notes = db.Column(db.Text, nullable=True)
    cc_email = db.Column(db.String(255), nullable=True)
    
    # Relazioni
    supplier = db.relationship('Supplier', backref='orders')
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    
    def total(self):
        """Calcola il totale dell'ordine sommando tutti gli OrderItem"""
        return sum(item.quantity * item.unit_price for item in self.items)
    
    def total_items(self):
        """Conta il numero totale di prodotti nell'ordine"""
        return len(self.items)
    
    def __repr__(self):
        return f'<Order #{self.id} - Supplier {self.supplier_id} - Total ${self.total():.2f}>'
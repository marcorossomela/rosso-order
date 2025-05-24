import uuid
from datetime import datetime
from src.extensions import db

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    supplier_id = db.Column(
        db.String(36),
        db.ForeignKey('suppliers.id', name='fk_orders_supplier_id'),
        nullable=False
    )
    # Cambiato da UUID a String per coerenza
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id', name='fk_orders_user_id'),
        nullable=True
    )
    location = db.Column(db.String(50), nullable=True)
    location_id = db.Column(
        db.String(36),
        db.ForeignKey('locations.id', name='fk_orders_location_id'),
        nullable=True
    )
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    order_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    cc_email = db.Column(db.String(255), nullable=True)
    
    # Relazioni SENZA backref per evitare conflitti
    supplier = db.relationship('Supplier', foreign_keys=[supplier_id])
    user = db.relationship('User', foreign_keys=[user_id])
    items = db.relationship('OrderItem', cascade='all, delete-orphan')
    location_detail = db.relationship('Location', foreign_keys=[location_id])
    
    def total(self):
        return sum(item.quantity * item.unit_price for item in self.items)
    
    def total_items(self):
        return len(self.items)
    
    def get_location_name(self):
        if self.location_detail:
            return f"{self.location_detail.name} - {self.location_detail.city}"
        return self.location or "N/A"
    
    def get_location_address(self):
        if self.location_detail:
            return self.location_detail.address
        return None
    
    def __repr__(self):
        location_name = self.get_location_name()
        return f'<Order {self.id} - {location_name} - ${self.total():.2f}>'
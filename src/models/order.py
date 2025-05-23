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
    location = db.Column(db.String(50), nullable=True)  # Città (per compatibilità)
    
    # NUOVO CAMPO per location specifica
    location_id = db.Column(
        db.String(36),
        db.ForeignKey('locations.id', name='fk_orders_location_id'),
        nullable=True
    )
    
    # Campi esistenti
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    order_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    cc_email = db.Column(db.String(255), nullable=True)
    
    # Relazioni
    supplier = db.relationship('Supplier', backref='orders')
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    location_detail = db.relationship('Location', backref='orders')  # NUOVA RELAZIONE
    
    def total(self):
        """Calcola il totale dell'ordine sommando tutti gli OrderItem"""
        return sum(item.quantity * item.unit_price for item in self.items)
    
    def total_items(self):
        """Conta il numero totale di prodotti nell'ordine"""
        return len(self.items)
    
    def get_location_name(self):
        """Ottiene il nome della location (specifica o città)"""
        if self.location_detail:
            return f"{self.location_detail.name} - {self.location_detail.city}"
        return self.location or "N/A"
    
    def get_location_address(self):
        """Ottiene l'indirizzo della location se disponibile"""
        if self.location_detail:
            return self.location_detail.address
        return None
    
    def __repr__(self):
        location_name = self.get_location_name()
        return f'<Order #{self.id} - {self.supplier.name} - {location_name} - ${self.total():.2f}>'
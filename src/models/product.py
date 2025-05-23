import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from src.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=db.text("gen_random_uuid()"))
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, litri, pezzi, etc.
    price = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)  # Prezzo di default
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('suppliers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name} - {self.unit} - ${self.price}>'

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'unit': self.unit,
            'price': float(self.price) if self.price else 0.00,
            'supplier_id': str(self.supplier_id),
            'created_at': self.created_at.isoformat()
        }
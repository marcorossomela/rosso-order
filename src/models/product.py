import uuid
from datetime import datetime
from src.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    # Usa String per compatibilità totale con database esistente
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, litri, pezzi, etc.
    price = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)  # Prezzo di default
    supplier_id = db.Column(db.String(36), db.ForeignKey('suppliers.id'), nullable=False)
    
    # Relazioni
    order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade='all, delete-orphan')
    
    # Aggiungi metodo per compatibilità
    @classmethod
    def get_by_id(cls, product_id):
        """Metodo sicuro per ottenere prodotto by ID"""
        return cls.query.filter(cls.id == str(product_id)).first()

    def __repr__(self):
        return f'<Product {self.name} - {self.unit} - ${self.price}>'

    def to_dict(self):
        return {
            'id': str(self.id),  # Assicura che sia sempre stringa
            'name': self.name,
            'unit': self.unit,
            'price': float(self.price) if self.price else 0.00,
            'supplier_id': str(self.supplier_id)
        }
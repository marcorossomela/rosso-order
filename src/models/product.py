import uuid
from src.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: 
        str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    supplier_id = db.Column(db.String(36), db.ForeignKey('suppliers.id'), nullable=False)

    def __repr__(self):
        return f'<Product {self.name} ({self.unit})>'
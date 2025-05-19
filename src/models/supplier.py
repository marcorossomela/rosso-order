import uuid
from src.extensions import db
from sqlalchemy.orm import backref

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: 
        str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)

    products = db.relationship('Product', backref='supplier', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref=backref('supplier', lazy=True), lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Supplier {self.name}>'
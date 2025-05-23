import uuid
from src.extensions import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(50), nullable=False)

    # Relazioni SENZA backref per evitare conflitti
    products = db.relationship('Product', cascade='all, delete-orphan')

    def get_orders(self):
        """Metodo per ottenere gli ordini di questo supplier"""
        from src.models.order import Order
        return Order.query.filter_by(supplier_id=self.id).all()

    def __repr__(self):
        return f'<Supplier {self.name}>'
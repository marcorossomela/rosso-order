import uuid
from src.extensions import db

order_items = db.Table('order_items',
    db.Column('order_id', db.String(36), db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.String(36), db.ForeignKey('products.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False)
)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    supplier_id = db.Column(db.String(36), db.ForeignKey('suppliers.id'), nullable=False)

    products = db.relationship(
        'Product', secondary=order_items,
        backref=db.backref('orders', lazy='dynamic')
    )

    def __repr__(self):
        return f'<Order #{self.id} - Supplier {self.supplier_id}>'

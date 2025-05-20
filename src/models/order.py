import uuid
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
        db.String(36),
        db.ForeignKey('users.id', name='fk_orders_user_id'),
        nullable=False
    )

    location = db.Column(db.String(50), nullable=False)

    supplier = db.relationship('Supplier', backref='orders')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order #{self.id} - Supplier {self.supplier_id} - Location {self.location}>'
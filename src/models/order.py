import uuid
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
        nullable=True  # puoi metterlo False in una migrazione futura se serve
    )

    location = db.Column(db.String(50), nullable=True)

    supplier = db.relationship('Supplier', backref='orders')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order #{self.id} - Supplier {self.supplier_id} - Location {self.location}>'
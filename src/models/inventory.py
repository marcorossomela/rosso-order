from src.extensions import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    month = db.Column(db.String(20), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    supplier_name = db.Column(db.String(120), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    location = db.Column(db.String(50), nullable=False)
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', name='fk_inventoryitem_user_id'),
        nullable=True
    )

    user = db.relationship('User', backref='inventory_items')

    def total(self):
        return round(self.unit_price * self.quantity, 2)


class InventoryMeta(db.Model):
    __tablename__ = 'inventory_meta'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    month = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    previous_inventory = db.Column(db.Float, default=0)
    vendor_spending = db.Column(db.Float, default=0)
    credit_notes = db.Column(db.Float, default=0)
    monthly_sales = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', name='fk_inventorymeta_user_id'),
        nullable=True
    )

    user = db.relationship('User', backref='inventory_meta')

    def food_cost(self):
        if self.monthly_sales > 0:
            return round(((self.vendor_spending - self.credit_notes) / self.monthly_sales) * 100, 2)
        return 0
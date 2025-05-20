from src.extensions import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), primary_key=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product')
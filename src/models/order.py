from src.extensions import db

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    details = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Order {self.id}>'
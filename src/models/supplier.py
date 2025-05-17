from src.extensions import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)

    products = db.relationship('Product', backref='supplier', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='supplier', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Supplier {self.name}>'
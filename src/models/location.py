import uuid
from datetime import datetime
from src.extensions import db

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione SENZA backref per evitare conflitti
    # Per accedere agli ordini: db.session.query(Order).filter_by(location_id=location.id).all()

    def get_orders(self):
        """Metodo per ottenere gli ordini di questa location"""
        from src.models.order import Order
        return Order.query.filter_by(location_id=self.id).all()
        
    def __repr__(self):
        return f'<Location {self.name} - {self.city}>'

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'created_at': self.created_at.isoformat()
        }
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from src.extensions import db

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=db.text("gen_random_uuid()"))
    name = db.Column(db.String(100), nullable=False)  # es. "Toronto Downtown", "Toronto North"
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)  # es. "Toronto", "Miami"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    orders = db.relationship('Order', backref='location_detail', lazy=True)

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
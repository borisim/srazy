"""
Database models for Srazy application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Event(db.Model):
    """Event model for storing sport events"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    sport = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    place = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'sport': self.sport,
            'date': self.date.isoformat() if self.date else None,
            'place': self.place,
            'difficulty': self.difficulty,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Event {self.id}: {self.sport} at {self.place}>'

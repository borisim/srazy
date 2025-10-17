"""
Database models for Srazy application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for event participants
event_participants = db.Table('event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    """User model for authentication and event participation"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_events = db.relationship('Event', backref='author', lazy='dynamic')
    participating_events = db.relationship('Event', secondary=event_participants,
                                          backref=db.backref('participants', lazy='dynamic'))
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

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
    
    # Foreign key to user
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'author': self.author.username if self.author else 'Anonymous',
            'author_id': self.author_id,
            'participant_count': self.participants.count()
        }
    
    def __repr__(self):
        return f'<Event {self.id}: {self.sport} at {self.place}>'

"""
Main application module for Srazy web application
"""
from flask import Flask, render_template, jsonify, request
import os
from pathlib import Path
from datetime import datetime

# Get the absolute path to the app directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize Flask app with proper paths
app = Flask(__name__,
           template_folder=str(BASE_DIR / 'templates'),
           static_folder=str(BASE_DIR / 'static'))

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/srazy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from app.backend.models import db, Event
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page route"""
    return render_template('contact.html')

@app.route('/events')
def events():
    """Events map page route"""
    return render_template('events.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with optional filtering"""
    try:
        query = Event.query
        
        # Apply filters if provided
        sport = request.args.get('sport')
        if sport:
            query = query.filter(Event.sport == sport)
        
        date_from = request.args.get('date_from')
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
            query = query.filter(Event.date >= date_from_dt)
        
        date_to = request.args.get('date_to')
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to)
            query = query.filter(Event.date <= date_to_dt)
        
        place = request.args.get('place')
        if place:
            query = query.filter(Event.place.ilike(f'%{place}%'))
        
        difficulty = request.args.get('difficulty')
        if difficulty:
            query = query.filter(Event.difficulty == difficulty)
        
        events = query.all()
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sport', 'date', 'place', 'difficulty', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse date
        event_date = datetime.fromisoformat(data['date'])
        
        # Create new event
        event = Event(
            sport=data['sport'],
            date=event_date,
            place=data['place'],
            difficulty=data['difficulty'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            description=data.get('description', '')
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run the application
    debug_mode = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)

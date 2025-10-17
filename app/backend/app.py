"""
Main application module for Srazy web application
"""
from flask import Flask, render_template, jsonify, request, session
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
from app.backend.models import db, Event, User
db.init_app(app)

# Session configuration
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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
        
        # Get current user from session (if logged in)
        author_id = session.get('user_id')
        
        # Create new event
        event = Event(
            sport=data['sport'],
            date=event_date,
            place=data['place'],
            difficulty=data['difficulty'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            description=data.get('description', ''),
            author_id=author_id
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify(event.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event"""
    try:
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'sport' in data:
            event.sport = data['sport']
        if 'date' in data:
            event.date = datetime.fromisoformat(data['date'])
        if 'place' in data:
            event.place = data['place']
        if 'difficulty' in data:
            event.difficulty = data['difficulty']
        if 'latitude' in data:
            event.latitude = float(data['latitude'])
        if 'longitude' in data:
            event.longitude = float(data['longitude'])
        if 'description' in data:
            event.description = data['description']
        
        db.session.commit()
        return jsonify(event.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login after registration
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/login', methods=['POST'])
def login_user():
    """Login a user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/logout', methods=['POST'])
def logout_user():
    """Logout a user"""
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/users/current', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify(user.to_dict()), 200
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/events/<int:event_id>/participate', methods=['POST'])
def participate_in_event(event_id):
    """Join/leave an event"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'Must be logged in to participate'}), 401
        
        user = User.query.get(session['user_id'])
        event = Event.query.get_or_404(event_id)
        
        # Check if user is already participating
        if event in user.participating_events:
            # Remove participation
            user.participating_events.remove(event)
            db.session.commit()
            return jsonify({
                'message': 'Removed from event',
                'participating': False,
                'participant_count': event.participants.count()
            }), 200
        else:
            # Add participation
            user.participating_events.append(event)
            db.session.commit()
            return jsonify({
                'message': 'Joined event',
                'participating': True,
                'participant_count': event.participants.count()
            }), 200
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

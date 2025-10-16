"""
Tests for event functionality in Srazy web application
"""
import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.backend.app import app
from app.backend.models import db, Event

def setup_test_db():
    """Setup test database"""
    with app.app_context():
        db.create_all()

def teardown_test_db():
    """Teardown test database"""
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_events_page():
    """Test the events page route"""
    with app.test_client() as client:
        response = client.get('/events')
        assert response.status_code == 200

def test_get_events_empty():
    """Test getting events when database is empty"""
    setup_test_db()
    try:
        with app.test_client() as client:
            response = client.get('/api/events')
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
    finally:
        teardown_test_db()

def test_create_event():
    """Test creating a new event"""
    setup_test_db()
    try:
        with app.test_client() as client:
            event_data = {
                'sport': 'Football',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'place': 'Central Park',
                'difficulty': 'Intermediate',
                'latitude': 40.785091,
                'longitude': -73.968285,
                'description': 'Friendly football match'
            }
            
            response = client.post('/api/events',
                                   data=json.dumps(event_data),
                                   content_type='application/json')
            assert response.status_code == 201
            data = response.get_json()
            assert data['sport'] == 'Football'
            assert data['place'] == 'Central Park'
            assert data['difficulty'] == 'Intermediate'
    finally:
        teardown_test_db()

def test_create_event_missing_field():
    """Test creating event with missing required field"""
    setup_test_db()
    try:
        with app.test_client() as client:
            event_data = {
                'sport': 'Football',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'place': 'Central Park'
                # Missing difficulty, latitude, longitude
            }
            
            response = client.post('/api/events',
                                   data=json.dumps(event_data),
                                   content_type='application/json')
            assert response.status_code == 400
    finally:
        teardown_test_db()

def test_filter_events_by_sport():
    """Test filtering events by sport"""
    setup_test_db()
    try:
        with app.test_client() as client:
            # Create two events with different sports
            event1 = {
                'sport': 'Football',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'place': 'Central Park',
                'difficulty': 'Intermediate',
                'latitude': 40.785091,
                'longitude': -73.968285
            }
            event2 = {
                'sport': 'Basketball',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'place': 'Downtown Court',
                'difficulty': 'Advanced',
                'latitude': 40.755091,
                'longitude': -73.998285
            }
            
            client.post('/api/events',
                       data=json.dumps(event1),
                       content_type='application/json')
            client.post('/api/events',
                       data=json.dumps(event2),
                       content_type='application/json')
            
            # Filter by Football
            response = client.get('/api/events?sport=Football')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 1
            assert data[0]['sport'] == 'Football'
    finally:
        teardown_test_db()

def test_filter_events_by_difficulty():
    """Test filtering events by difficulty"""
    setup_test_db()
    try:
        with app.test_client() as client:
            # Create events with different difficulties
            event1 = {
                'sport': 'Running',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'place': 'Park Trail',
                'difficulty': 'Beginner',
                'latitude': 40.785091,
                'longitude': -73.968285
            }
            event2 = {
                'sport': 'Running',
                'date': (datetime.now() + timedelta(days=8)).isoformat(),
                'place': 'Mountain Trail',
                'difficulty': 'Expert',
                'latitude': 40.755091,
                'longitude': -73.998285
            }
            
            client.post('/api/events',
                       data=json.dumps(event1),
                       content_type='application/json')
            client.post('/api/events',
                       data=json.dumps(event2),
                       content_type='application/json')
            
            # Filter by Beginner
            response = client.get('/api/events?difficulty=Beginner')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 1
            assert data[0]['difficulty'] == 'Beginner'
    finally:
        teardown_test_db()

if __name__ == '__main__':
    print("Running event tests...")
    
    test_events_page()
    print("✓ Events page test passed")
    
    test_get_events_empty()
    print("✓ Get events empty test passed")
    
    test_create_event()
    print("✓ Create event test passed")
    
    test_create_event_missing_field()
    print("✓ Create event missing field test passed")
    
    test_filter_events_by_sport()
    print("✓ Filter events by sport test passed")
    
    test_filter_events_by_difficulty()
    print("✓ Filter events by difficulty test passed")
    
    print("\nAll event tests passed! ✓")

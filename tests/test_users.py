"""
Tests for user functionality in Srazy web application
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.backend.app import app
from app.backend.models import db, User, Event
from datetime import datetime, timedelta

def setup_test_db():
    """Setup test database"""
    with app.app_context():
        db.create_all()

def teardown_test_db():
    """Teardown test database"""
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_user_registration():
    """Test user registration"""
    setup_test_db()
    try:
        with app.test_client() as client:
            user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123'
            }
            
            response = client.post('/api/users/register',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
            assert response.status_code == 201
            data = response.get_json()
            assert data['username'] == 'testuser'
            assert data['email'] == 'test@example.com'
            assert 'password' not in data
            assert 'password_hash' not in data
    finally:
        teardown_test_db()

def test_user_login():
    """Test user login"""
    setup_test_db()
    try:
        with app.test_client() as client:
            # Register a user first
            user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123'
            }
            client.post('/api/users/register',
                       data=json.dumps(user_data),
                       content_type='application/json')
            
            # Try to login
            login_data = {
                'username': 'testuser',
                'password': 'testpass123'
            }
            response = client.post('/api/users/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
            assert response.status_code == 200
            data = response.get_json()
            assert data['username'] == 'testuser'
    finally:
        teardown_test_db()

def test_user_logout():
    """Test user logout"""
    setup_test_db()
    try:
        with app.test_client() as client:
            # Register and login
            user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123'
            }
            client.post('/api/users/register',
                       data=json.dumps(user_data),
                       content_type='application/json')
            
            # Logout
            response = client.post('/api/users/logout')
            assert response.status_code == 200
    finally:
        teardown_test_db()

def test_event_participation():
    """Test user participating in event"""
    setup_test_db()
    try:
        with app.test_client() as client:
            # Register and login user
            user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123'
            }
            client.post('/api/users/register',
                       data=json.dumps(user_data),
                       content_type='application/json')
            
            # Create an event
            event_data = {
                'sport': 'Football',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'place': 'Central Park',
                'difficulty': 'Intermediate',
                'latitude': 40.785091,
                'longitude': -73.968285,
                'description': 'Test event'
            }
            create_response = client.post('/api/events',
                                         data=json.dumps(event_data),
                                         content_type='application/json')
            event_id = create_response.get_json()['id']
            
            # Participate in event
            response = client.post(f'/api/events/{event_id}/participate')
            assert response.status_code == 200
            data = response.get_json()
            assert data['participating'] == True
            assert data['participant_count'] == 1
            
            # Leave event
            response = client.post(f'/api/events/{event_id}/participate')
            assert response.status_code == 200
            data = response.get_json()
            assert data['participating'] == False
            assert data['participant_count'] == 0
    finally:
        teardown_test_db()

def test_event_with_author():
    """Test that events show author information"""
    setup_test_db()
    try:
        with app.test_client() as client:
            # Register and login user
            user_data = {
                'username': 'testauthor',
                'email': 'author@example.com',
                'password': 'testpass123'
            }
            client.post('/api/users/register',
                       data=json.dumps(user_data),
                       content_type='application/json')
            
            # Create an event
            event_data = {
                'sport': 'Basketball',
                'date': (datetime.now() + timedelta(days=7)).isoformat(),
                'place': 'Downtown Court',
                'difficulty': 'Advanced',
                'latitude': 40.755091,
                'longitude': -73.998285
            }
            response = client.post('/api/events',
                                  data=json.dumps(event_data),
                                  content_type='application/json')
            assert response.status_code == 201
            data = response.get_json()
            assert data['author'] == 'testauthor'
            assert 'participant_count' in data
    finally:
        teardown_test_db()

if __name__ == '__main__':
    print("Running user tests...")
    
    test_user_registration()
    print("✓ User registration test passed")
    
    test_user_login()
    print("✓ User login test passed")
    
    test_user_logout()
    print("✓ User logout test passed")
    
    test_event_participation()
    print("✓ Event participation test passed")
    
    test_event_with_author()
    print("✓ Event with author test passed")
    
    print("\nAll user tests passed! ✓")

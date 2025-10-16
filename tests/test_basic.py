"""
Basic tests for Srazy web application
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.backend.app import app

def test_app_creation():
    """Test that the Flask app is created successfully"""
    assert app is not None
    assert app.name == 'app.backend.app'

def test_home_route():
    """Test the home page route"""
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200

def test_about_route():
    """Test the about page route"""
    with app.test_client() as client:
        response = client.get('/about')
        assert response.status_code == 200

def test_contact_route():
    """Test the contact page route"""
    with app.test_client() as client:
        response = client.get('/contact')
        assert response.status_code == 200

def test_health_check():
    """Test the API health check endpoint"""
    with app.test_client() as client:
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data

def test_404_error():
    """Test 404 error handling"""
    with app.test_client() as client:
        response = client.get('/nonexistent')
        assert response.status_code == 404

if __name__ == '__main__':
    print("Running basic tests...")
    test_app_creation()
    print("✓ App creation test passed")
    
    test_home_route()
    print("✓ Home route test passed")
    
    test_about_route()
    print("✓ About route test passed")
    
    test_contact_route()
    print("✓ Contact route test passed")
    
    test_health_check()
    print("✓ Health check test passed")
    
    test_404_error()
    print("✓ 404 error test passed")
    
    print("\nAll tests passed! ✓")

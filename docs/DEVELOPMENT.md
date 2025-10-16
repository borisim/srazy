# Development Guide

## Setting Up Development Environment

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Simple method
python run.py

# Or directly
cd app/backend
python app.py
```

## Code Style

### Python

- Follow PEP 8 style guide
- Use docstrings for functions and classes
- Keep functions small and focused
- Use meaningful variable names

### JavaScript

- Use ES6+ features
- Use const/let instead of var
- Add JSDoc comments for functions
- Keep functions pure when possible

### CSS

- Use CSS variables for theming
- Follow BEM naming convention for classes
- Keep selectors simple
- Use mobile-first responsive design

## Adding Features

### Adding a New Page

1. Create template in `app/templates/`:
```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
<!-- Your content -->
{% endblock %}
```

2. Add route in `app/backend/app.py`:
```python
@app.route('/mypage')
def my_page():
    return render_template('mypage.html')
```

3. Add navigation link in `base.html`:
```html
<li><a href="/mypage">My Page</a></li>
```

### Adding an API Endpoint

```python
@app.route('/api/myendpoint')
def my_endpoint():
    return jsonify({
        'status': 'success',
        'data': {}
    })
```

## Testing

Create tests in the `tests/` directory:

```python
import pytest
from app.backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
```

Run tests:
```bash
pytest
```

## Debugging

### Enable Debug Mode

Set in environment or code:
```python
app.run(debug=True)
```

### Logging

Add logging to your code:
```python
import logging

logging.info('Information message')
logging.error('Error message')
```

## Common Issues

### Import Errors

Make sure you're in the correct directory and virtual environment is activated.

### Port Already in Use

Change the port in `app.py`:
```python
app.run(port=5001)
```

### Static Files Not Loading

Check the `STATIC_FOLDER` configuration and verify file paths.

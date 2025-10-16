# Srazy

A modern web application template with a clean architecture, designed to accelerate development of future web projects.

## Features

- **Modern Frontend**: Clean, responsive HTML5/CSS3 design with vanilla JavaScript
- **Python Backend**: Flask-based backend with modular structure
- **Template System**: Jinja2 templating with base template and inheritance
- **Responsive Design**: Mobile-first approach that works on all devices
- **API Ready**: RESTful API structure with example endpoints
- **Easy Configuration**: Environment-based configuration system

## Project Structure

```
srazy/
├── app/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── app.py          # Main Flask application
│   │   └── config.py       # Configuration settings
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Main stylesheet
│   │   ├── js/
│   │   │   └── main.js     # Main JavaScript file
│   │   └── images/         # Image assets
│   └── templates/
│       ├── base.html       # Base template
│       ├── index.html      # Home page
│       ├── about.html      # About page
│       ├── contact.html    # Contact page
│       ├── 404.html        # 404 error page
│       └── 500.html        # 500 error page
├── tests/                  # Test directory
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/borisim/srazy.git
cd srazy
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
cd app/backend
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration

The application uses environment-based configuration. You can set the following environment variables:

- `SECRET_KEY`: Secret key for Flask sessions (change in production)
- `FLASK_DEBUG`: Set to `False` in production
- `DATABASE_URL`: Database connection string (optional)

Create a `.env` file in the root directory for local development:

```env
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
```

## Development

### Running in Development Mode

```bash
cd app/backend
python app.py
```

The application will run with debug mode enabled, providing detailed error messages and auto-reloading on code changes.

### Testing

Tests can be added in the `tests/` directory. Use pytest for running tests:

```bash
pip install pytest
pytest
```

## API Endpoints

- `GET /` - Home page
- `GET /about` - About page
- `GET /contact` - Contact page
- `GET /api/health` - Health check endpoint

## Customization

### Styling

Edit `/app/static/css/style.css` to customize the appearance. The CSS uses CSS variables for easy theming:

```css
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    /* ... more variables */
}
```

### Adding New Pages

1. Create a new template in `/app/templates/`
2. Add a route in `/app/backend/app.py`
3. Update navigation in `/app/templates/base.html` if needed

### JavaScript Functionality

Add custom JavaScript in `/app/static/js/main.js` or create new JS modules as needed.

## Deployment

### Production Considerations

1. Set `FLASK_DEBUG=False`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set a strong `SECRET_KEY`
4. Use a production database (PostgreSQL, MySQL)
5. Enable HTTPS
6. Configure proper error logging

### Example with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.backend.app:app
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please open an issue on GitHub.

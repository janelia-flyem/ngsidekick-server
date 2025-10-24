# ngsidekick-server

A Flask-based server application for ngsidekick.

## Features

- Modern Flask application with application factory pattern
- CORS support for cross-origin requests
- Production-ready with Gunicorn WSGI server
- Docker containerization with multi-stage builds
- Health check endpoint for monitoring
- Comprehensive test suite

## Project Structure

```
ngsidekick-server/
├── src/
│   └── ngsidekick_server/
│       ├── __init__.py
│       ├── app.py          # Main Flask application
│       └── wsgi.py         # WSGI entry point
├── tests/
│   ├── __init__.py
│   └── test_app.py         # Test suite
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pyproject.toml          # Project dependencies and metadata
├── requirements.txt        # Convenience file (use pyproject.toml)
└── README.md
```

## Development Setup

### Prerequisites

- Python 3.12 or higher
- pip

### Installation

1. Clone the repository:
```bash
cd /path/to/ngsidekick-server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running the Development Server

```bash
# Option 1: Run directly
python src/ngsidekick_server/app.py

# Option 2: Use Flask CLI
export FLASK_APP=src/ngsidekick_server/app.py
export FLASK_ENV=development
flask run
```

The server will start on http://localhost:5000

### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=ngsidekick_server --cov-report=html
```

## Docker Deployment

### Build the Docker image

```bash
docker build -t ngsidekick-server .
```

### Run the container

```bash
docker run -p 5000:5000 ngsidekick-server
```

### Using Docker Compose (optional)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

## API Endpoints

### Root
- **GET** `/` - Returns server information and status

### Health Check
- **GET** `/health` - Health check endpoint for monitoring

### Example API
- **GET** `/api/v1/example` - Example API endpoint

## Configuration

Configuration can be managed through environment variables or by modifying the `create_app()` function in `app.py`.

## Production Deployment

For production deployment, the application uses Gunicorn with multiple workers. The Dockerfile is configured for production use with:
- Non-root user for security
- Multi-stage build for smaller image size
- Health checks
- Optimized gunicorn configuration

## License

MIT


"""Tests for the Flask application."""

import pytest
from ngsidekick_server.app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app({'TESTING': True})
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_index(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'name' in data
    assert data['name'] == 'ngsidekick-server'
    assert 'status' in data


def test_health(client):
    """Test the health check route."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_example_endpoint(client):
    """Test the example API endpoint."""
    response = client.get('/api/v1/example')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'data' in data


def test_not_found(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


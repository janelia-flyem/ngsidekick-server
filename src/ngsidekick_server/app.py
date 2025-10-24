"""Main Flask application."""

from flask import Flask, jsonify
from flask_cors import CORS


def create_app(config=None):
    """Application factory function."""
    app = Flask(__name__)
    
    # Apply default configuration
    app.config.update(
        JSON_SORT_KEYS=False,
        SECRET_KEY='dev-secret-key-change-in-production',
    )
    
    # Apply custom configuration if provided
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Register routes
    register_routes(app)
    
    return app


def register_routes(app):
    """Register application routes."""
    
    @app.route('/')
    def index():
        """Root endpoint."""
        return jsonify({
            'name': 'ngsidekick-server',
            'version': '0.1.0',
            'status': 'running'
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/api/v1/example')
    def example_endpoint():
        """Example API endpoint."""
        return jsonify({
            'message': 'This is an example endpoint',
            'data': []
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'error': 'Internal server error'}), 500


# For development server
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


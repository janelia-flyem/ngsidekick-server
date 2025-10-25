import requests
from flask import Flask, jsonify
from flask_cors import CORS
from flask_compress import Compress

from ngsidekick.segmentprops.segmentprops_selection import select_segment_properties


NAMED_PROPERTIES_FILES = {
    'male-cns-v0.9': 'gs://flyem-male-cns/v0.9/segmentation/combined_properties',
    'manc-v1.2.1': 'gs://manc-seg-v1p2/manc-seg-v1.2/segment_properties_v1.2.1',
    'flywire-v783b': 'gs://flywire-neuprint-artifacts/fafb/v783b/flywire-783b-segment-properties',
}

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

    # Enable compression
    Compress(app)
    
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


    @app.route('/tags/<properties_file>/<path:tags>/info')
    def tags_endpoint(properties_file, tags):
        info = _download_properties_file(properties_file)
        tag_list = [tag for tag in tags.split('/') if tag]
        if not tag_list:
            return jsonify({'error': 'No tags provided'}), 400
        
        subset = []
        tag_expressions = {}
        for tag in tag_list:
            if '=' in tag:
                tag_name, tag_expr = tag.split('=', 1)
                tag_name = tag_name.strip()
                tag_expr = tag_expr.strip()
                tag_expressions[tag_name] = tag_expr
            else:
                subset.append(tag.strip())
        try:
            filtered_info = select_segment_properties(info, subset, tag_expressions=tag_expressions)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        return jsonify(filtered_info)

    @app.route('/label/<properties_file>/<path:labels>/info')
    def label_endpoint(properties_file, labels):
        info = _download_properties_file(properties_file)
        label_list = [label for label in labels.split('/') if label]
        if not label_list:
            return jsonify({'error': 'No tags provided'}), 400
        
        scalar_expressions = {}
        for label in label_list:
            # FIXME: This doesn't properly handle unnamed label expressions which involve '=' or '==' internally.
            if '=' in label:
                scalar_name, scalar_expr = label.split('=', 1)
                scalar_name = scalar_name.strip()
                scalar_expr = scalar_expr.strip()
                scalar_expressions[scalar_name] = scalar_expr
            else:
                scalar_expressions['label'] = label.strip()
        try:
            filtered_info = select_segment_properties(info, [], scalar_expressions=scalar_expressions)
        except ValueError as e:
            raise
            return jsonify({'error': str(e)}), 400
        
        return jsonify(filtered_info)

    
    def _download_properties_file(properties_file):
        if properties_file in NAMED_PROPERTIES_FILES:
            properties_file = NAMED_PROPERTIES_FILES[properties_file]

        if properties_file.startswith('gs://'):
            properties_file = f'https://storage.googleapis.com/{properties_file[len("gs://"):]}'
        else:
            return jsonify({'error': 'Invalid properties file'}), 400
        
        if not properties_file.endswith('/info'):
            properties_file += '/info'
        
        r = requests.get(properties_file)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({'error': f'Failed to fetch properties file {properties_file}: {e}'}), 500
        
        info = r.json()
        return info
        

# For development server
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)


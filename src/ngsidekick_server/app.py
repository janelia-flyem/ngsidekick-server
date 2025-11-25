import os
import re
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from flask_compress import Compress

from ngsidekick.segmentprops.select_segment_properties import select_segment_properties

# https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/example-ngsidekick-server-sources.json

NAMED_PROPERTIES_FILES = {
    'male-cns-v0.9': 'gs://flyem-male-cns/v0.9/segmentation/combined_properties',

    # This properties file includes nearly all neuprint columns (much bigger)
    'male-cns-v0.9-all': 'gs://flyem-male-cns/v0.9/segmentation/comprehensive_properties',

    'manc-v1.2.3': 'gs://manc-seg-v1p2/manc-seg-v1.2/segment_properties_v1.2.3/combined_properties',
    'flywire-v783b': 'gs://flywire-neuprint-artifacts/fafb/v783b/flywire-783b-segment-properties',
}

class InvalidPropertiesFileError(Exception):
    pass

def create_app(config=None):
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
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'error': 'Internal server error'}), 500

    @app.route('/SEGPROPS/<path:all_components>')
    @app.route('/segprops/<path:all_components>')
    def segprops_endpoint(all_components):
        """
        Handle both tags and label endpoints.
        Expected patterns:
        - /segprops/<properties_file>/tags/<tags>/info
        - /segprops/<properties_file>/label/<labels>/info
        
        Since properties_file may contain slashes, we parse the path to find
        the /tags/ or /label/ delimiter.
        """
        if not all_components.endswith('/info'):
            return jsonify({'error': 'Path must end with /info'}), 400
        
        # Try to find /tags/ or /label/ in the path
        endpoint_type = None
        properties_file = None
        params = None
        
        all_components = all_components.replace('/TAGS/', '/tags/')
        all_components = all_components.replace('/LABELS/', '/label/')
        if '/tags/' in all_components:
            endpoint_type = 'tags'
            idx = all_components.rfind('/tags/')
            properties_file = all_components[:idx]
            params = all_components[idx + len('/tags/'):-len('/info')]
        elif '/label/' in all_components:
            endpoint_type = 'label'
            idx = all_components.rfind('/label/')
            properties_file = all_components[:idx]
            params = all_components[idx + len('/label/'):-len('/info')]
        else:
            return jsonify({'error': 'Path must contain /tags/ or /label/'}), 400
        
        if not properties_file:
            return jsonify({'error': 'No properties file specified'}), 400
        
        try:
            info = _download_properties_file(properties_file)
        except InvalidPropertiesFileError as e:
            raise
            return jsonify({'error': str(e)}), 400
        except:
            raise
            return jsonify({'error': 'Internal server error'}), 500
        
        if endpoint_type == 'tags':
            return _handle_tags_request(info, params)
        else:
            return _handle_label_request(info, params)
    
    def _handle_tags_request(info, tags):
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
    
    def _handle_label_request(info, labels):
        label_list = [label for label in labels.split('/') if label]
        if not label_list:
            return jsonify({'error': 'No labels provided'}), 400
        
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
            return jsonify({'error': str(e)}), 400
        
        return jsonify(filtered_info)

    
    def _download_properties_file(properties_file):
        if properties_file in NAMED_PROPERTIES_FILES:
            properties_file = NAMED_PROPERTIES_FILES[properties_file]

        # If present, drop the prefix 'precomputed://' or 'precomputed:/'
        for prefix in ['precomputed://', 'precomputed:/']:
            if properties_file.startswith(prefix):
                properties_file = properties_file[len(prefix):]
                break

        # If present, drop the suffix '|neuroglancer-precomputed'
        for suffix in ['|neuroglancer-precomputed']:
            if properties_file.endswith(suffix):
                properties_file = properties_file[:-len(suffix)]
                break

        # Somewhere the URL is being run through normpath, turning parameters 
        # containing https:// into http:/ (one slash). Fix the prefix.
        for protocol in ['gs', 'http', 'https']:
            if properties_file.startswith(f'{protocol}:/') and not properties_file.startswith(f'{protocol}://'):
                properties_file = f'{protocol}://{properties_file[len(f'{protocol}:/'):]}'
                break

        if properties_file.startswith('gs://'):
            properties_file = f'https://storage.googleapis.com/{properties_file[len("gs://"):]}'
        
        if not properties_file.endswith('/info'):
            properties_file += '/info'

        r = requests.get(properties_file)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise InvalidPropertiesFileError(f'Failed to fetch properties file {properties_file}: {e}')
        
        info = r.json()
        if info.get('@type') == "neuroglancer_segment_properties":
            return info

        # If the user provided the source to the parent segmentation info
        # instead of the segment properties file, find the referenced segment properties file.
        referenced_file = info.get('segment_properties')
        if not referenced_file:
            raise InvalidPropertiesFileError('No segment properties file referenced')

        if not re.match(r'^(gs://|http://|https://)', referenced_file):
            # Relative path.
            referenced_file = properties_file[:-len('info')] + referenced_file + '/info'
            referenced_file = os.path.normpath(referenced_file)

        return _download_properties_file(referenced_file)
        

# For development server
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)

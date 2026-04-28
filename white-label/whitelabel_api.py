"""
TigerEx White Label API
Allows admins to create and manage white label clients
"""
from flask import Blueprint, request, jsonify
import uuid
import os

whitelabel_bp = Blueprint('whitelabel', __name__)

# In-memory white label storage
white_labels = {}

@whitelabel_bp.route('/api/whitelabel/create', methods=['POST'])
def create_whitelabel():
    """Create a new white label instance"""
    data = request.json
    
    client_id = str(uuid.uuid4())[:8]
    
    white_labels[client_id] = {
        'id': client_id,
        'name': data.get('name', 'My Exchange'),
        'logo': data.get('logo', '🐯'),
        'primary_color': data.get('primaryColor', '#F0B90B'),
        'accent_color': data.get('accentColor', '#FF6B6B'),
        'domain': data.get('domain', f"{data.get('name').lower().replace(' ', '')}.tigerex.com"),
        'email': data.get('email', 'support@example.com'),
        'status': 'active',
        'features': data.get('features', {
            'spot': True,
            'futures': True,
            'margin': True,
            'p2p': True,
            'earn': True
        }),
        'custom_css': data.get('custom_css', ''),
        'custom_js': data.get('custom_js', '')
    }
    
    return jsonify({
        'success': True,
        'client_id': client_id,
        'domain': white_labels[client_id]['domain']
    })

@whitelabel_bp.route('/api/whitelabel/list', methods=['GET'])
def list_whitelabels():
    """List all white label clients"""
    return jsonify({
        'whitelabels': list(white_labels.values())
    })

@whitelabel_bp.route('/api/whitelabel/<client_id>', methods=['GET'])
def get_whitelabel(client_id):
    """Get white label config"""
    if client_id not in white_labels:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(white_labels[client_id])

@whitelabel_bp.route('/api/whitelabel/<client_id>', methods=['PUT'])
def update_whitelabel(client_id):
    """Update white label config"""
    if client_id not in white_labels:
        return jsonify({'error': 'Not found'}), 404
    
    data = request.json
    white_labels[client_id].update(data)
    
    return jsonify({
        'success': True,
        'whitelabel': white_labels[client_id]
    })

@whitelabel_bp.route('/api/whitelabel/<client_id>/generate-branding', methods=['POST'])
def generate_branding(client_id):
    """Generate branding files for white label"""
    if client_id not in white_labels:
        return jsonify({'error': 'Not found'}), 404
    
    wl = white_labels[client_id]
    
    # Generate CSS
    css = f"""
    :root {{
        --primary: {wl['primary_color']};
        --accent: {wl['accent_color']};
    }}
    """
    
    return jsonify({
        'success': True,
        'css': css,
        'branding': {
            'logo': wl['logo'],
            'name': wl['name'],
            'colors': {
                'primary': wl['primary_color'],
                'accent': wl['accent_color']
            }
        }
    })

print("White Label API loaded")

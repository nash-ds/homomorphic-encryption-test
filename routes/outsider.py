from flask import Blueprint, jsonify
from encryption.tenseal_helper import tenseal_helper
from storage.filesystem import load_file, log_action
import os
from config import UPLOAD_FOLDER

outsider_bp = Blueprint('outsider', __name__)

@outsider_bp.route('/inspect/<file_id>', methods=['GET'])
def inspect_traffic(file_id):
    """Simulate outsider intercepting network traffic"""
    try:
        # Try to find the file (encrypted or plaintext)
        encrypted_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_encrypted.bin")
        plaintext_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_plaintext.bin")
        lab_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_for_lab.bin")
        
        file_path = None
        content_type = ""
        
        if os.path.exists(encrypted_path):
            file_path = encrypted_path
            content_type = "encrypted"
        elif os.path.exists(plaintext_path):
            file_path = plaintext_path
            content_type = "plaintext"
        elif os.path.exists(lab_path):
            file_path = lab_path
            content_type = "lab_processing"
        
        if not file_path:
            return jsonify({
                'error': 'File not found',
                'file_id': file_id,
                'intercepted': False
            }), 404
        
        file_content = load_file(file_path)
        
        log_action('OUTSIDER', 'INSPECT_TRAFFIC', f'File ID: {file_id}, Type: {content_type}, Size: {len(file_content)} bytes')
        
        # Show the actual encrypted content for visual inspection
        if content_type == "encrypted" or content_type == "lab_processing":
            # This will show as binary garbage when encrypted
            content_preview = repr(file_content)[:500]
            is_readable = False
        else:
            # For plaintext, show readable content
            try:
                content_preview = file_content.decode('utf-8', errors='ignore')
                is_readable = len(content_preview.strip()) > 0
            except:
                content_preview = repr(file_content)[:500]
                is_readable = False
        
        return jsonify({
            'file_id': file_id,
            'content_type': content_type,
            'size': len(file_content),
            'is_readable': is_readable,
            'intercepted_content': content_preview,  # This shows the actual intercepted data
            'message': f'Intercepted {content_type} traffic - {"readable" if is_readable else "unreadable"} to outsider',
            'note': 'intercepted_content shows actual data transmitted over network'
        })
    
    except Exception as e:
        log_action('OUTSIDER', 'INSPECT_ERROR', str(e))
        return jsonify({'error': str(e)}), 500

@outsider_bp.route('/inspect-all', methods=['GET'])
def inspect_all_traffic():
    """Inspect all available files"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.bin'):
                file_id = filename.split('_')[0]
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file_content = load_file(file_path)
                
                # Determine content type and readability
                content_type = "encrypted" if "_encrypted" in filename else "plaintext" if "_plaintext" in filename else "lab_processing"
                
                if content_type == "encrypted" or content_type == "lab_processing":
                    content_preview = repr(file_content)[:200]
                    is_readable = False
                else:
                    try:
                        content_preview = file_content.decode('utf-8', errors='ignore')
                        is_readable = len(content_preview.strip()) > 0
                    except:
                        content_preview = repr(file_content)[:200]
                        is_readable = False
                
                files.append({
                    'file_id': file_id,
                    'filename': filename,
                    'size': len(file_content),
                    'content_type': content_type,
                    # 'is_readable': is_readable,
                    'intercepted_content': content_preview
                })
        
        log_action('OUTSIDER', 'INSPECT_ALL', f'Found {len(files)} files')
        
        return jsonify({
            'files': files,
            'total_files': len(files),
            'message': 'List of all available files for inspection'
        })
    
    except Exception as e:
        log_action('OUTSIDER', 'INSPECT_ALL_ERROR', str(e))
        return jsonify({'error': str(e)}), 500
from flask import Blueprint, request, jsonify
from encryption.tenseal_helper import tenseal_helper
from storage.filesystem import save_file, generate_file_id, log_action
from config import ENCRYPTION_ENABLED, MAX_FILE_SIZE
import os

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/upload', methods=['POST'])
def upload_medical_data():
    """Patient uploads medical data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_length > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Max size: {MAX_FILE_SIZE} bytes'}), 400
        
        file_content = file.read()
        
        # Log the upload
        log_action('PATIENT', 'UPLOAD_START', f'File size: {len(file_content)} bytes')
        
        # Encrypt if enabled
        if ENCRYPTION_ENABLED:
            # Try to encrypt with TenSEAL
            encrypted_data = tenseal_helper.encrypt_data(file_content)
            
            if encrypted_data is None:
                return jsonify({
                    'error': 'Encryption failed - TenSEAL may not be properly configured',
                    'debug': 'TenSEAL context or encryption operation failed'
                }), 500
            
            # Save encrypted data
            file_id = generate_file_id()
            filepath = save_file(encrypted_data, f"{file_id}_encrypted.bin")
            log_action('PATIENT', 'UPLOAD_COMPLETE', f'Encrypted file saved: {filepath}')
            
            return jsonify({
                'message': 'File uploaded and encrypted successfully',
                'file_id': file_id,
                'file_name': file.filename,
                'encrypted': True,
                'size': len(encrypted_data),
                'original_size': len(file_content),
                'note': 'Use this file_id for doctor operations'
            })
        else:
            # Save plaintext data
            file_id = generate_file_id()
            filepath = save_file(file_content, f"{file_id}_plaintext.bin")
            log_action('PATIENT', 'UPLOAD_COMPLETE', f'Plaintext file saved: {filepath}')
            
            return jsonify({
                'message': 'File uploaded successfully (no encryption)',
                'file_id': file_id,
                'file_name': file.filename,
                'encrypted': False,
                'size': len(file_content),
                'note': 'Use this file_id for doctor operations'
            })
    
    except Exception as e:
        log_action('PATIENT', 'UPLOAD_ERROR', str(e))
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/view-result/<file_id>', methods=['GET'])
def view_result(file_id):
    """Patient views final diagnosis result"""
    try:
        # In a real system, this would fetch the doctor's diagnosis
        # For MVP, we'll return a placeholder
        result_path = os.path.join('results', f"{file_id}_result.txt")
        
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                result = f.read()
            
            log_action('PATIENT', 'VIEW_RESULT', f'File ID: {file_id}')
            return jsonify({
                'file_id': file_id,
                'result': result,
                'status': 'completed'
            })
        else:
            return jsonify({'error': 'Result not found'}), 404
    
    except Exception as e:
        log_action('PATIENT', 'VIEW_RESULT_ERROR', str(e))
        return jsonify({'error': str(e)}), 500
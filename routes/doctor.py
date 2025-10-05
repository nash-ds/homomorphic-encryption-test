from flask import Blueprint, request, jsonify
from encryption.tenseal_helper import tenseal_helper
from storage.filesystem import load_file, save_file, generate_file_id, log_action
import os
from config import UPLOAD_FOLDER

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/view/<file_id>', methods=['GET'])
def view_report(file_id):
    """Doctor views encrypted report (no patient metadata)"""
    try:
        # Look for the file - check both encrypted and plaintext versions
        encrypted_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_encrypted.bin")
        plaintext_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_plaintext.bin")
        
        file_path = None
        content_type = ""
        
        if os.path.exists(encrypted_path):
            file_path = encrypted_path
            content_type = 'encrypted'
        elif os.path.exists(plaintext_path):
            file_path = plaintext_path
            content_type = 'plaintext'
        else:
            return jsonify({'error': 'File not found'}), 404
        
        file_content = load_file(file_path)
        
        # Log that doctor viewed the file (no patient info visible)
        log_action('DOCTOR', 'VIEW_REPORT', f'File ID: {file_id}, Size: {len(file_content)} bytes')
        
        # Determine if content is readable based on actual content, not just file name
        is_readable = False
        content_preview = ""
        
        if content_type == 'plaintext':
            try:
                content_preview = file_content.decode('utf-8', errors='ignore')
                is_readable = len(content_preview.strip()) > 0
            except:
                content_preview = repr(file_content)[:500]
                is_readable = False
        else:
            # For encrypted content, it should appear as binary garbage
            try:
                content_preview = file_content.decode('utf-8', errors='ignore')
                # If it decodes to readable text, it might not be encrypted
                is_readable = len(content_preview.strip()) > 0 and not content_preview.startswith('\x00')
                if is_readable:
                    content_preview = "Binary encrypted data (decoded as text)"
            except:
                content_preview = "Binary encrypted data"
                is_readable = False
        
        return jsonify({
            'file_id': file_id,
            'size': len(file_content),
            'content_type': content_type,
            'is_readable': is_readable,
            'content_preview': content_preview,
            'message': 'Report available for processing'
        })
    
    except Exception as e:
        log_action('DOCTOR', 'VIEW_ERROR', str(e))
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/send-to-lab', methods=['POST'])
def send_to_lab():
    """Doctor forwards encrypted data to lab"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        
        if not file_id:
            return jsonify({'error': 'File ID required'}), 400
        
        # Look for the file - check both encrypted and plaintext versions
        encrypted_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_encrypted.bin")
        plaintext_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_plaintext.bin")
        
        source_path = None
        if os.path.exists(encrypted_path):
            source_path = encrypted_path
        elif os.path.exists(plaintext_path):
            source_path = plaintext_path
        else:
            return jsonify({
                'error': f'File not found. Searched for: {encrypted_path} and {plaintext_path}',
                'available_files': os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
            }), 404
        
        print(f"✓ Found source file: {source_path}")
        
        # Read the file content
        with open(source_path, 'rb') as f:
            file_content = f.read()
        
        print(f"✓ Read file content, size: {len(file_content)} bytes")
        
        # Generate new ID for lab processing
        lab_file_id = generate_file_id()
        
        # Create the lab processing file path
        lab_file_path = os.path.join(UPLOAD_FOLDER, f"{lab_file_id}_for_lab.bin")
        
        # Write the content to the lab file
        with open(lab_file_path, 'wb') as f:
            f.write(file_content)
        
        print(f"✓ Created lab file: {lab_file_path}")
        
        log_action('DOCTOR', 'SEND_TO_LAB', f'Forwarded file ID: {file_id} -> {lab_file_id}')
        
        return jsonify({
            'message': 'File forwarded to lab successfully',
            'original_file_id': file_id,
            'lab_file_id': lab_file_id,
            'size': len(file_content),
            'note': f'Data is {os.path.basename(source_path).split("_")[1]} and will be processed by the lab'
        })
    
    except Exception as e:
        log_action('DOCTOR', 'SEND_TO_LAB_ERROR', str(e))
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/return-result', methods=['POST'])
def return_result():
    """Doctor sends diagnosis back to patient"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        diagnosis = data.get('diagnosis')
        
        if not file_id or not diagnosis:
            return jsonify({'error': 'File ID and diagnosis required'}), 400
        
        # Save the diagnosis result
        result_path = os.path.join('results', f"{file_id}_result.txt")
        with open(result_path, 'w') as f:
            f.write(diagnosis)
        
        log_action('DOCTOR', 'RETURN_RESULT', f'Diagnosis sent for file ID: {file_id}')
        
        return jsonify({
            'message': 'Diagnosis sent to patient successfully',
            'file_id': file_id,
            'diagnosis': diagnosis
        })
    
    except Exception as e:
        log_action('DOCTOR', 'RETURN_RESULT_ERROR', str(e))
        return jsonify({'error': str(e)}), 500
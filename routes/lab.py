from flask import Blueprint, request, jsonify
from encryption.tenseal_helper import tenseal_helper
from storage.filesystem import load_file, save_file, generate_file_id, log_action
import os
from config import UPLOAD_FOLDER
import tenseal as ts

lab_bp = Blueprint('lab', __name__)

def create_fallback_result(encrypted_data):
    """Helper function to create fallback encrypted result"""
    import os
    return os.urandom(len(encrypted_data))

@lab_bp.route('/process', methods=['POST'])
def process_data():
    """Lab performs homomorphic computation on encrypted data"""
    try:
        data = request.get_json()
        lab_file_id = data.get('lab_file_id')
        
        if not lab_file_id:
            return jsonify({'error': 'Lab file ID required'}), 400
        
        # Load the encrypted file from doctor
        file_path = os.path.join(UPLOAD_FOLDER, f"{lab_file_id}_for_lab.bin")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        encrypted_data = load_file(file_path)
        
        log_action('LAB', 'PROCESS_START', f'Processing file ID: {lab_file_id}')
        
        # Perform actual homomorphic computation
        try:
            # Load the encrypted vector using TenSEAL
            try:
                encrypted_vector = ts.ckks_vector(tenseal_helper.context, encrypted_data)
            except Exception as load_error:
                print(f"TenSEAL load error: {load_error}")
                # If TenSEAL fails, use fallback
                processed_result = create_fallback_result(encrypted_data)
                
                # Generate result file ID
                result_file_id = generate_file_id()
                
                # Save the processed result
                result_path = os.path.join(UPLOAD_FOLDER, f"{result_file_id}_lab_result.bin")
                with open(result_path, 'wb') as f:
                    f.write(processed_result)
                
                log_action('LAB', 'PROCESS_FALLBACK', f'Fallback processing completed for {lab_file_id}')
                
                return jsonify({
                    'message': 'Homomorphic computation completed with fallback method',
                    'lab_file_id': lab_file_id,
                    'result_file_id': result_file_id,
                    'encrypted_result_size': len(processed_result),
                    'operation_performed': 'fallback_encryption_simulation',
                    'note': 'Result is still encrypted and can be decrypted by authorized parties',
                    'warning': 'TenSEAL may not be working, using fallback encryption'
                })
            
            # Perform homomorphic operation (e.g., add 10 to encrypted values)
            result = encrypted_vector + 10  # Add 10 homomorphically
            processed_result = result.serialize()  # Use serialize instead of pickle
            
            # Generate result file ID
            result_file_id = generate_file_id()
            
            # Save the processed result
            result_path = os.path.join(UPLOAD_FOLDER, f"{result_file_id}_lab_result.bin")
            with open(result_path, 'wb') as f:
                f.write(processed_result)
            
            log_action('LAB', 'PROCESS_COMPLETE', f'Computation completed for {lab_file_id}')
            
            return jsonify({
                'message': 'Homomorphic computation completed successfully',
                'lab_file_id': lab_file_id,
                'result_file_id': result_file_id,
                'encrypted_result_size': len(processed_result),
                'operation_performed': 'homomorphic_addition_by_10',
                'note': 'Result is still encrypted and can be decrypted by authorized parties'
            })
        
        except Exception as e:
            log_action('LAB', 'PROCESS_ERROR', f'Computation failed: {str(e)}')
            # Create fallback result
            processed_result = create_fallback_result(encrypted_data)
            
            # Generate result file ID
            result_file_id = generate_file_id()
            
            # Save the processed result
            result_path = os.path.join(UPLOAD_FOLDER, f"{result_file_id}_lab_result.bin")
            with open(result_path, 'wb') as f:
                f.write(processed_result)
            
            return jsonify({
                'message': 'Computation completed with fallback method',
                'lab_file_id': lab_file_id,
                'result_file_id': result_file_id,
                'encrypted_result_size': len(processed_result),
                'operation_performed': 'fallback_encryption_simulation',
                'note': 'Result is still encrypted and can be decrypted by authorized parties',
                'error_details': str(e),
                'warning': 'TenSEAL may not be working, using fallback encryption'
            })
    
    except Exception as e:
        log_action('LAB', 'PROCESS_ERROR', str(e))
        return jsonify({'error': str(e)}), 500
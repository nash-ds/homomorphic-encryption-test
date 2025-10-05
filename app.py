from flask import Flask, jsonify, render_template, request
from flask_jwt_extended import JWTManager
from encryption.tenseal_helper import tenseal_helper
from storage.filesystem import ensure_directories, log_action
from config import UPLOAD_FOLDER, RESULTS_FOLDER, LOGS_FOLDER, ENCRYPTION_ENABLED
import os

def create_app():
    app = Flask(__name__)
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
    jwt = JWTManager(app)
    
    # Ensure directories exist
    ensure_directories()
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Register blueprints
    from routes.patient import patient_bp
    from routes.doctor import doctor_bp
    from routes.lab import lab_bp
    from routes.outsider import outsider_bp
    
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(lab_bp, url_prefix='/lab')
    app.register_blueprint(outsider_bp, url_prefix='/outsider')
    
    @app.route('/')
    def home():
        return render_template('index.html', encryption_enabled=ENCRYPTION_ENABLED)
    
    @app.route('/admin')
    def admin():
        return render_template('admin.html', encryption_enabled=ENCRYPTION_ENABLED)
    
    @app.route('/ui')
    def ui():
        return render_template('index.html', encryption_enabled=ENCRYPTION_ENABLED)
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'encryption_enabled': ENCRYPTION_ENABLED,
            'tenseal_available': tenseal_helper.context is not None
        })
    
    @app.route('/config')
    def get_config():
        return jsonify({
            'encryption_enabled': ENCRYPTION_ENABLED,
            'max_file_size': 5 * 1024 * 1024,
            'upload_folder': UPLOAD_FOLDER,
            'results_folder': RESULTS_FOLDER,
            'logs_folder': LOGS_FOLDER
        })
    
    # Log startup
    log_action('SYSTEM', 'STARTUP', f'Encryption enabled: {ENCRYPTION_ENABLED}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
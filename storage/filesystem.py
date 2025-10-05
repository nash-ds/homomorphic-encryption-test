import os
import uuid
from datetime import datetime
from config import UPLOAD_FOLDER, RESULTS_FOLDER, LOGS_FOLDER

def ensure_directories():
    """Create necessary directories"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)

def save_file(file_data, filename=None, folder=None):
    """Save file to specified folder with unique name"""
    if folder is None:
        folder = UPLOAD_FOLDER
    
    if filename is None:
        filename = f"{uuid.uuid4()}.bin"
    
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as f:
        f.write(file_data)  # file_data is now serialized bytes
    return filepath

def load_file(filepath):
    """Load file from path"""
    with open(filepath, 'rb') as f:
        return f.read()  # Return the serialized data as bytes

def generate_file_id():
    """Generate unique file ID"""
    return str(uuid.uuid4())

def log_action(role, action, details=""):
    """Log audit trail"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ROLE: {role}, ACTION: {action}, DETAILS: {details}\n"
    
    log_file = os.path.join(LOGS_FOLDER, "audit.log")
    with open(log_file, 'a') as f:
        f.write(log_entry)
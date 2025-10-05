import os

# Configuration for the medical data exchange system
ENCRYPTION_ENABLED = False  # Toggle encryption ON/OFF (True/False)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB max file size
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
LOGS_FOLDER = 'logs'

# TenSEAL parameters - using more compatible values
POLY_MOD_DEGREE = 8192
COEFF_MOD_BIT_SIZES = [60, 40, 40, 60]
SCALE = 2**40
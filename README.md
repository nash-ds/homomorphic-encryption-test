# Homomorphic Encrypted Medical Data Exchange System

## Overview

A secure medical data processing system that demonstrates homomorphic encryption using Python Flask and TenSEAL. The system allows three roles (Patient, Doctor, Lab) to securely exchange medical data while maintaining confidentiality through homomorphic encryption.

## Features

- **Homomorphic Encryption**: Uses TenSEAL for CKKS encryption scheme
- **Three-Tier System**: Patient → Doctor → Lab data flow
- **Configurable Encryption**: Toggle encryption ON/OFF in configuration
- **Network Traffic Inspection**: Outsider can monitor traffic to see encryption effectiveness
- **Modern UI**: Professional medical-themed interface with separate admin panel
- **File-based Storage**: Local filesystem storage for uploads and results

## Architecture

### Roles
- **Patient**: Uploads medical data and views diagnosis results
- **Doctor**: Views encrypted reports, forwards to lab, returns diagnosis
- **Lab**: Performs homomorphic computations on encrypted data
- **Outsider**: Network traffic inspector to demonstrate encryption effectiveness

### Data Flow
```
Patient → Doctor → Lab → Doctor → Patient
```

## Installation

1. **Clone or create the project directory**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Required packages:**
   - Flask==2.3.3
   - Flask-JWT-Extended==4.5.3
   - tenseal==0.3.14
   - numpy==1.24.3

## Configuration

### config.py
- `ENCRYPTION_ENABLED = True/False`: Toggle encryption ON/OFF
- `MAX_FILE_SIZE = 5 * 1024 * 1024`: Maximum upload size (5MB)
- `POLY_MOD_DEGREE = 8192`: TenSEAL parameter
- `COEFF_MOD_BIT_SIZES = [60, 40, 40, 60]`: Encryption parameters
- `SCALE = 2**40`: CKKS scale factor

### Folders
- `uploads/`: Stores uploaded files
- `results/`: Stores diagnosis results
- `logs/`: Stores audit logs
- `templates/`: HTML templates

## Usage

### Starting the Server
```bash
python app.py
```

### Accessing the System
- **Main UI**: http://localhost:5000
- **Admin/Outsider UI**: http://localhost:5000/admin

### User Interface Controls

#### Patient Tab
- **Upload Medical Report**: 
  - Click "Choose File" to select a medical file
  - Click "Encrypt & Upload" to upload and encrypt the file
  - The file ID will be automatically populated in the view field
- **View Diagnosis Result**:
  - Enter file ID to view the doctor's diagnosis
  - Click "View Result" to retrieve the diagnosis

#### Doctor Tab
- **View Patient Report**:
  - Enter file ID to view the patient's encrypted report
  - Click "View Report" to see the report details
- **Send to Lab**:
  - Enter file ID to forward to the lab
  - Click "Send to Lab" to forward the encrypted data
  - The lab file ID will be populated automatically
- **Return Diagnosis to Patient**:
  - Enter file ID and write the diagnosis
  - Click "Send Diagnosis" to send to the patient

#### Lab Tab
- **Process Encrypted Data**:
  - Enter lab file ID received from doctor
  - Click "Process Data" to perform homomorphic operations
  - The lab processes encrypted data without seeing actual content

#### Configuration Tab
- Shows system status and configuration details
- Displays encryption status and file locations

#### Admin/Outsider Interface
- **Intercept Traffic**: Enter file ID to see intercepted network traffic
- **List All Files**: View all available files in the system
- Shows whether traffic is readable (unencrypted) or encrypted (binary garbage)

### Testing Encryption Toggle

1. **With Encryption ON**:
   - Upload a file as patient
   - Outsider sees binary garbage when intercepting traffic
   - Data is securely encrypted end-to-end

2. **With Encryption OFF**:
   - Set `ENCRYPTION_ENABLED = False` in config.py
   - Restart the application
   - Upload a file as patient
   - Outsider sees readable medical data when intercepting traffic

## Technical Details

### Homomorphic Operations
- **Addition**: `encrypted_data + 10` (adds 10 to encrypted values)
- **Multiplication**: `encrypted_data * scalar` (multiplies encrypted values)
- **Averages**: Computes average of encrypted values

### Security Features
- End-to-end encryption when enabled
- Doctor never sees patient identifiers
- Network traffic inspection demonstrates encryption effectiveness
- Audit logging for all actions
- File size limits for security

### Error Handling
- Graceful fallback when TenSEAL is unavailable
- Proper error messages for debugging
- File integrity checks
- Network traffic validation

## File Structure

```
medical_he/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html         # Main UI
│   └── admin.html         # Admin/Outsider UI
├── routes/
│   ├── patient.py         # Patient endpoints
│   ├── doctor.py          # Doctor endpoints
│   ├── lab.py             # Lab endpoints
│   └── outsider.py        # Outsider endpoints
├── encryption/
│   └── tenseal_helper.py  # TenSEAL wrapper
├── storage/
│   └── filesystem.py      # File storage utilities
├── uploads/               # Uploaded files
├── results/               # Diagnosis results
└── logs/                  # Audit logs
```

## Troubleshooting

### Common Issues
- **File Not Found**: Ensure the correct file ID is used
- **Encryption Errors**: Check TenSEAL installation and version compatibility
- **UI Not Loading**: Clear browser cache and restart the server
- **Network Traffic**: Check file naming conventions in uploads folder

### Debugging
- Check server console for detailed error messages
- Enable Flask debug mode for development
- Monitor the audit log in `logs/audit.log`
- Use browser developer tools for UI debugging

## Security Considerations

- **Production Use**: Add proper authentication and HTTPS
- **Key Management**: Implement secure key storage for production
- **Input Validation**: Additional validation for production environments
- **Rate Limiting**: Add rate limiting for API endpoints

## Demonstration Points

1. **Data Confidentiality**: Show difference between encrypted vs plaintext traffic
2. **Homomorphic Processing**: Lab processes encrypted data without decryption
3. **Role Separation**: Each role has specific permissions and data access
4. **Network Security**: Outsider cannot read encrypted traffic
5. **Configuration Toggle**: Demonstrate encryption ON/OFF effect

## License

This project is for educational and demonstration purposes only. Adapt as needed for your specific requirements.

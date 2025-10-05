import tenseal as ts
import numpy as np
import base64

class TenSEALHelper:
    def __init__(self):
        self.context = None
        self._setup_context()
    
    def _setup_context(self):
        """Initialize the TenSEAL context for CKKS encryption - Version 0.3.16"""
        try:
            self.context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                8192,
                1032193,
                [60, 40, 40, 60],
                ts.ENCRYPTION_TYPE.ASYMMETRIC,
                None
            )
            self.context.generate_galois_keys()
            self.context.global_scale = 2**40
            print("✓ TenSEAL context created successfully!")
        except Exception as e:
            print(f"✗ Context setup failed: {e}")
            self.context = None
    
    def encrypt_data(self, data):
        """Encrypt data - returns serialized encrypted vector"""
        try:
            if self.context is None:
                return None
            
            # Convert to simple numerical data
            if isinstance(data, bytes):
                # Convert first few bytes to numbers
                numerical_data = [float(b) for b in data[:20]] or [1.0]
            elif isinstance(data, str):
                numerical_data = [float(ord(c)) for c in data[:20]] or [1.0]
            elif isinstance(data, (int, float)):
                numerical_data = [float(data)]
            else:
                numerical_data = [1.0]
            
            # Encrypt and return serialized data
            encrypted = ts.ckks_vector(self.context, numerical_data)
            return encrypted.serialize()  # Return serialized bytes directly
        except Exception as e:
            print(f"✗ Encryption failed: {e}")
            return None
    
    def load_encrypted_vector(self, serialized_data):
        """Load encrypted vector from serialized data"""
        try:
            if self.context is None:
                raise Exception("No context")
            return ts.ckks_vector(self.context, serialized_data)
        except Exception as e:
            print(f"✗ Load failed: {e}")
            raise e

# Global instance
tenseal_helper = TenSEALHelper()
# Secure-Signature-Hashing (SSH)

## Overview
SigTrack-Encryptor is a Python-based cryptographic system that generates a unique and secure digital signature based on a user's handwritten signature. It uses SHA-256 hashing along with timestamp embedding to ensure security and uniqueness. This system can be applied to digital authentication, contract signing, and secure identity verification.

## Features
- Secure digital signature generation using SHA-256
- Unique hashing based on signature strokes and timestamp
- Signature verification mechanism
- Supports Base64 encoding for easy storage and transmission

## Installation

Ensure you have Python 3.7+ installed. You can install dependencies using:

```sh
pip install hashlib json base64 datetime
```

## Usage

### 1. Generate a Signature
Use `generate_encrypted_signature.py` to create a secure signature hash.

```python
import hashlib
import json
import base64
from datetime import datetime

def generate_encrypted_signature(user_id, signature_points):
    """
    Generate an encrypted signature using SHA-256.
    :param user_id: User identifier
    :param signature_points: Signature stroke data [(x, y, timestamp), ...]
    :return: Encrypted signature dictionary
    """
    signature_str = json.dumps(signature_points, separators=(',', ':'))
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    raw_data = f"{user_id}|{timestamp}|{signature_str}"
    
    hash_object = hashlib.sha256(raw_data.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    encrypted_signature = base64.b64encode(hash_hex.encode()).decode()
    
    return {
        "UserID": user_id,
        "Timestamp": timestamp,
        "Hash": encrypted_signature
    }

# Example
user_id = "user_id"
signature_data = [(10, 20, 1706872330), (30, 40, 1706872331), (50, 60, 1706872332)]
encrypted_signature = generate_encrypted_signature(user_id, signature_data)
print(encrypted_signature)
```

### 2. Verify a Signature
Use `verify_signature.py` to check the authenticity of a given signature.

```python
import hashlib
import json
import base64

def verify_signature(user_id, signature_points, timestamp, given_signature):
    """
    Verify if the given signature is valid.
    :param user_id: User ID
    :param signature_points: Signature data [(x, y, timestamp), ...]
    :param timestamp: Timestamp of signature
    :param given_signature: Provided encrypted hash
    :return: True if valid, False otherwise
    """
    signature_str = json.dumps(signature_points, separators=(',', ':'))
    raw_data = f"{user_id}|{timestamp}|{signature_str}"
    hash_object = hashlib.sha256(raw_data.encode('utf-8'))
    computed_hash_hex = hash_object.hexdigest()
    computed_signature = base64.b64encode(computed_hash_hex.encode()).decode()
    return computed_signature == given_signature

# Example Verification
is_valid = verify_signature(user_id, signature_data, encrypted_signature["Timestamp"], encrypted_signature["Hash"])
print("Signature is valid" if is_valid else "Signature is invalid")
```

## Applications
- **Digital Contracts**: Secure electronic agreements
- **Financial Transactions**: Signature-based transaction authentication
- **Identity Verification**: Secure authentication for online accounts
- **Logistics & Delivery**: Proof of receipt for shipments

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

For contributions, please submit a pull request or report issues in the GitHub repository.

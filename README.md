# Secure Signature Hashing (SSH)

## Overview
This project, **Secure Signature Hashing (SSH)**, presents a novel approach to encrypted digital signatures using temporal and spatial data. It consists of two Python scripts:
- **SSH-Crypto.py**: A GUI-based tool enabling users to input and sign a message digitally. The signature is captured as a series of coordinates and hashed using SHA-256.
- **SSH-Vrfy.py**: A verification tool that loads the generated signature JSON file and reconstructs the signature to verify its authenticity.

## Features
- **Graphical Signature Input**: Users can draw a signature on a canvas.
- **Timestamp-Based Hashing**: The signature is combined with a message and timestamp before hashing.
- **JSON Storage**: The hashed data and signature coordinates are stored in JSON format.
- **Signature Verification**: The stored JSON file can be loaded to reconstruct the signature.

## Installation
### Prerequisites
Ensure you have Python 3 installed and the required dependencies:
```bash
pip install numpy opencv-python PyQt5
```

### Running the Application
#### Step 1: Generate Signature
Run the signing application:
```bash
python SSH-Crypto.py
```
1. Enter your message.
2. Draw your signature.
3. Click 'Generate Hash & Save JSON'.
4. The generated JSON file will be stored in `Generated_Hash/`.

#### Step 2: Verify Signature
Run the verification application:
```bash
python SSH-Vrfy.py
```
1. Click 'Load JSON Signature File'.
2. Select the JSON file from `Generated_Hash/`.
3. The signature will be reconstructed and displayed.

## Mathematical Concepts
### Secure Hash Algorithm (SHA-256)
A signature is converted into a series of coordinate points \( (x_i, y_i) \) which are serialized into JSON format:
\[
H = \text{SHA-256}(\text{JSON}([x_1, y_1], [x_2, y_2], \dots))
\]
SHA-256 ensures that even a minor change in the signature results in a completely different hash.

### Cryptographic Integrity
Given a message \( M \) and a signature \( S \), the hash is computed as:
\[
H = \text{SHA-256}(M \parallel S \parallel T)
\]
where \( T \) is the timestamp. This ensures that the signature is time-sensitive and resistant to tampering.

### Signature Verification
The verification process involves:
1. Loading \( H \) from the JSON file.
2. Recomputing \( H' \) from the signature points.
3. If \( H = H' \), the signature is valid.

## File Structure
```
.
├── SSH-Crypto.py     # Signing tool
├── SSH-Vrfy.py       # Verification tool
├── Signature_Image/  # Stored signature images
├── Generated_Hash/   # Stored JSON hash files
└── README.md         # Documentation
```

## Future Enhancements
- Implement public-key cryptography (RSA/ECDSA) for digital signatures.
- Improve UI/UX with real-time signature smoothing.
- Add a feature to compare the similarity between signatures.

## License
This project is released under the [MIT License](LICENSE).

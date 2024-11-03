import os
import sys
import base64
import shutil
from getpass import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

WALLETS_DIR = 'wallets'
ENCRYPTED_DIR = 'encrypted_wallets'
KEY_FILE = 'encryption.key'

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a secret key from the given password and salt using PBKDF2 HMAC.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Fernet requires a 32-byte key
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def generate_salt() -> bytes:
    """
    Generates a 16-byte salt.
    """
    return os.urandom(16)

def save_key(key: bytes, filepath: str):
    """
    Saves the encryption key to a file.
    """
    with open(filepath, 'wb') as key_file:
        key_file.write(key)

def load_key(filepath: str) -> bytes:
    """
    Loads the encryption key from a file.
    """
    with open(filepath, 'rb') as key_file:
        return key_file.read()

def encrypt_file(file_path: str, fernet: Fernet) -> None:
    """
    Encrypts the contents of the given file using Fernet.
    """
    try:
        with open(file_path, 'rb') as file:
            data = file.read()
        encrypted_data = fernet.encrypt(data)
        with open(file_path, 'wb') as file:
            file.write(encrypted_data)
        print(f"Encrypted: {file_path}")
    except Exception as e:
        print(f"Failed to encrypt {file_path}: {str(e)}")

def main():
    if not os.path.exists(WALLETS_DIR):
        print(f"The directory '{WALLETS_DIR}' does not exist. Please ensure wallet files are present.")
        sys.exit(1)
    
    # Prompt user for password
    password = getpass("Enter encryption password: ")
    confirm_password = getpass("Confirm encryption password: ")
    
    if password != confirm_password:
        print("Passwords do not match. Exiting.")
        sys.exit(1)
    
    # Check if key file already exists
    if os.path.exists(KEY_FILE):
        print(f"Encryption key file '{KEY_FILE}' already exists. Aborting to prevent overwriting.")
        sys.exit(1)
    
    # Generate salt and derive key
    salt = generate_salt()
    key = derive_key(password, salt)
    
    # Save the salt
    with open('salt.bin', 'wb') as salt_file:
        salt_file.write(salt)
    
    # Create Fernet instance with the derived key
    fernet = Fernet(key)
    
    # Create encrypted directory if it doesn't exist
    os.makedirs(ENCRYPTED_DIR, exist_ok=True)
    
    # Iterate through each wallet file and encrypt
    for filename in os.listdir(WALLETS_DIR):
        file_path = os.path.join(WALLETS_DIR, filename)
        encrypted_path = os.path.join(ENCRYPTED_DIR, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as file:
                    data = file.read()
                encrypted_data = fernet.encrypt(data)
                with open(encrypted_path, 'wb') as file:
                    file.write(encrypted_data)
                print(f"Encrypted: {filename}")
            except Exception as e:
                print(f"Failed to encrypt {filename}: {str(e)}")
                continue
    
    print("\nAll wallet files have been encrypted and moved to the 'encrypted_wallets/' directory.")
    print("Salt saved to 'salt.bin'. Keep it secure!")

if __name__ == "__main__":
    main()

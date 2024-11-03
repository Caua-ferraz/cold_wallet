import os
import sys
import base64
from getpass import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

ENCRYPTED_DIR = 'encrypted_wallets'
SALT_FILE = 'salt.bin'

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a secret key from the given password and salt using PBKDF2 HMAC.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def load_salt(filepath: str) -> bytes:
    """
    Loads the salt from a file.
    """
    if not os.path.exists(filepath):
        print(f"Salt file '{filepath}' not found. Cannot derive key.")
        sys.exit(1)
    with open(filepath, 'rb') as salt_file:
        return salt_file.read()

def decrypt_file(file_path: str, fernet: Fernet) -> str:
    """
    Decrypts the contents of the given encrypted file using Fernet.
    """
    try:
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        print(f"Failed to decrypt {os.path.basename(file_path)}. Incorrect password or corrupted file.")
        return None

def main():
    if not os.path.exists(ENCRYPTED_DIR):
        print(f"The directory '{ENCRYPTED_DIR}' does not exist. Please ensure wallet files are encrypted.")
        sys.exit(1)
    
    if not os.path.exists(SALT_FILE):
        print(f"Salt file '{SALT_FILE}' not found.")
        sys.exit(1)
    
    # Prompt user for password
    password = getpass("Enter decryption password: ")
    
    # Load salt and derive key
    salt = load_salt(SALT_FILE)
    key = derive_key(password, salt)
    
    # Create Fernet instance with the derived key
    fernet = Fernet(key)
    
    # Track if any decryption was successful
    success = False
    
    # Iterate through each encrypted wallet file and decrypt
    for filename in os.listdir(ENCRYPTED_DIR):
        file_path = os.path.join(ENCRYPTED_DIR, filename)
        if os.path.isfile(file_path):
            decrypted_content = decrypt_file(file_path, fernet)
            if decrypted_content:
                print(f"\n--- {filename} ---")
                print(decrypted_content)
                print("--------------------\n")
                success = True
            else:
                print(f"Could not decrypt {filename}.")
    
    if success:
        print("All accessible wallet files have been decrypted.")
    else:
        print("No wallet files were decrypted. Please check your password and try again.")

if __name__ == "__main__":
    main()

import serial
import time
import os
import sys
from access_wallet import decrypt_file, derive_key, load_salt
from cryptography.fernet import Fernet

# Configuration
SERIAL_PORT = 'COM3'  # Replace with your Arduino's COM port
BAUD_RATE = 115200
TIMEOUT = 1  # in seconds

ENCRYPTED_DIR = 'encrypted_wallets'
SALT_FILE = 'salt.bin'

def initialize_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)  # Wait for connection to establish
        print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port {SERIAL_PORT}: {e}")
        sys.exit(1)

def load_encryption_key():
    # Prompt user for password
    from getpass import getpass
    password = getpass("Enter decryption password: ")
    
    # Load salt
    if not os.path.exists(SALT_FILE):
        print(f"Salt file '{SALT_FILE}' not found.")
        sys.exit(1)
    with open(SALT_FILE, 'rb') as f:
        salt = f.read()
    
    # Derive key
    key = derive_key(password, salt)
    fernet = Fernet(key)
    return fernet

def listen_and_respond(ser, fernet):
    while True:
        if ser.in_waiting > 0:
            command = ser.readline().decode().strip()
            print(f"Received command: {command}")
            
            if command.startswith("GET_ADDRESS:"):
                _, crypto = command.split(":")
                address = get_wallet_address(crypto.upper(), fernet)
                if address:
                    response = f"ADDRESS:{crypto.upper()}:{address}\n"
                    ser.write(response.encode())
                    print(f"Sent address for {crypto.upper()}: {address}")
                else:
                    response = f"ADDRESS:{crypto.upper()}:FAILED\n"
                    ser.write(response.encode())
                    print(f"Failed to retrieve address for {crypto.upper()}")
            # Implement other command handlers here
        time.sleep(0.1)

def get_wallet_address(crypto, fernet):
    encrypted_path = os.path.join(ENCRYPTED_DIR, f"{crypto.lower()}_wallet.txt")
    if not os.path.exists(encrypted_path):
        print(f"Encrypted wallet file '{encrypted_path}' not found.")
        return None
    
    decrypted_content = decrypt_file(encrypted_path, fernet)
    if decrypted_content:
        # Extract the address from the decrypted content
        lines = decrypted_content.splitlines()
        for line in lines:
            if "Address:" in line:
                _, address = line.split(":", 1)
                return address.strip()
    return None

def main():
    ser = initialize_serial()
    fernet = load_encryption_key()
    print("Listening for commands from Arduino...")
    listen_and_respond(ser, fernet)

if __name__ == "__main__":
    main() 
# DIY Hardware Cryptocurrency Wallet

A secure, DIY hardware wallet solution for BTC, ETH, BNB, and SOL cryptocurrencies.

## Table of Contents

- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Setup Instructions](#setup-instructions)
  - [1. Hardware Setup](#1-hardware-setup)
  - [2. Software Setup](#2-software-setup)
  - [3. Running the System](#3-running-the-system)
- [Usage Guide](#usage-guide)
  - [Generating Wallets](#generating-wallets)
  - [Accessing Wallet Addresses](#accessing-wallet-addresses)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

## Hardware Requirements

- **Arduino Board**: Arduino Mega 2560 or ESP32
- **SD Card Module**: Compatible with your Arduino board
- **OLED Display**: SSD1306 128x64
- **Buttons**: 4 Push Buttons (UP, DOWN, SELECT, BACK)
- **Secure Element** (Optional): ATECC608A for enhanced security
- **Power Supply**: 16340 Battery (3.7V) or suitable power source
- **Miscellaneous**:
  - Breadboard or Custom PCB
  - Jumper Wires
  - USB-C Connector (for data & charging)
  - SD Card (formatted to FAT32)

## Software Requirements

- **Python 3.8+**
- **Arduino IDE**: For uploading firmware to Arduino
- **Python Libraries**:
  - `pyserial`
  - `cryptography`
  - `bitcoinlib`
  - `web3`
  - `solders`
- **Arduino Libraries**:
  - `Adafruit GFX Library`
  - `Adafruit SSD1306`
  - `SD Library` (included with Arduino IDE)
  - `Crypto Library` (e.g., [Arduino Cryptography Library](https://github.com/rweather/arduinolibs/tree/master/Crypto))
  - `EEPROM Library` (included with Arduino IDE)

## Setup Instructions

### 1. Hardware Setup

1. **Connect the SD Card Module**:
   - **VCC** → 5V
   - **GND** → GND
   - **MISO** → Pin 50 (Arduino Mega) or appropriate MISO pin for ESP32
   - **MOSI** → Pin 51 (Arduino Mega) or appropriate MOSI pin for ESP32
   - **SCK** → Pin 52 (Arduino Mega) or appropriate SCK pin for ESP32
   - **CS** → Pin 53 (Arduino Mega) or another digital pin (e.g., GPIO 5 for ESP32)

2. **Connect the OLED Display**:
   - **VCC** → 3.3V or 5V
   - **GND** → GND
   - **SDA** → Pin 20 (Arduino Mega) or GPIO 21 (ESP32)
   - **SCL** → Pin 21 (Arduino Mega) or GPIO 22 (ESP32)

3. **Connect the Buttons**:
   - **UP** → Pin 2
   - **DOWN** → Pin 3
   - **SELECT** → Pin 4
   - **BACK** → Pin 5 (Optional)

4. **Power Supply**:
   - Connect the battery or power source to the Arduino to power the device.

5. **Final Assembly**:
   - Ensure all connections are secure.
   - Optionally solder the components onto a custom PCB for a more permanent setup.

### 2. Software Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/diy-hardware-wallet.git
   cd diy-hardware-wallet
   ```

2. **Install Python Dependencies**:
   Ensure you have Python 3.8+ installed. Then install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Arduino Libraries**:
   - Open the Arduino IDE.
   - Install the following libraries via the Library Manager:
     - `Adafruit GFX Library`
     - `Adafruit SSD1306`
     - `Crypto` (if available)
     - `ArduinoJson` (optional for advanced features)

4. **Format the SD Card**:
   - Ensure the SD card is formatted to FAT32.
   - Create a folder named `encrypted_wallets` in the root directory of the SD card.
   - Place your encrypted wallet files (`btc_wallet.txt`, `eth_wallet.txt`, etc.) inside the `encrypted_wallets` folder.

5. **Upload Firmware to Arduino**:
   - Open `hardware_wallet.ino` in the Arduino IDE.
   - Select the correct board and COM port.
   - Upload the firmware.

### 3. Running the System

1. **Generate Wallets**:
   ```bash
   python generate_wallets.py
   ```
   - Follow the prompts to generate wallets for BTC, ETH, BNB, and SOL.
   - This will create wallet files in the `wallets/` directory.

2. **Encrypt Wallets**:
   ```bash
   python encrypt_wallets.py
   ```
   - Enter and confirm a strong encryption password.
   - This encrypts the wallet files and moves them to `encrypted_wallets/`.

3. **Transfer Encrypted Wallets to SD Card**:
   - Copy the `encrypted_wallets` folder from your PC to the SD card inserted into the Arduino.

4. **Start the Hardware Interface**:
   ```bash
   python hardware_interface.py
   ```
   - Enter the decryption password used during encryption when prompted.
   - The script will listen for commands from the Arduino.

5. **Operate the Hardware Wallet**:
   - Navigate the menu using the UP and DOWN buttons.
   - Select options using the SELECT button.
   - The device will read encrypted wallet files from the SD card, decrypt them using the PIN, and display wallet addresses on the OLED screen.

---

## Usage Guide

### Generating Wallets

1. **Run Wallet Generation Script**:
   ```bash
   python generate_wallets.py
   ```
2. **Follow Prompts**:
   - Choose which wallets to generate.
   - Confirm actions as prompted.

### Accessing Wallet Addresses

1. **Run Hardware Interface Script**:
   ```bash
   python hardware_interface.py
   ```
2. **Operate Hardware Wallet**:
   - Select the desired cryptocurrency from the menu.
   - The Arduino will read the encrypted wallet file from the SD card.
   - Enter your PIN to decrypt and display the wallet address on the OLED screen.

3. **Repeat for Other Cryptos**:
   - Extend the Arduino menu and Python script to handle other cryptocurrencies as needed.

---

## Security Features

1. **Hardware Security**:
   - **Secure Storage**: Private keys are encrypted and stored securely on the SD card.
   - **PIN Protection**: Access to the device is protected by a PIN code.
   - **Offline Operations**: Critical operations like signing are handled securely.

2. **Software Security**:
   - **Encryption**: Wallet data is encrypted using AES-256-CBC.
   - **Key Derivation**: Uses SHA-256 hashing of the PIN for key derivation (consider implementing PBKDF2 for enhanced security).
   - **Data Integrity**: Ensure encrypted data is tamper-proof.

---

## Troubleshooting

1. **SD Card Initialization Failed**:
   - Ensure the SD card is properly formatted to FAT32.
   - Check all wiring connections between the SD card module and Arduino.
   - Verify the `SD_CS_PIN` in the Arduino code matches your wiring.

2. **Decryption Failed**:
   - Verify that the correct PIN is entered.
   - Ensure that the encrypted wallet files are not corrupted.
   - Check that the encryption method in `encrypt_wallets.py` matches the decryption method on the Arduino.

3. **Display Issues**:
   - Verify OLED connections.
   - Ensure the correct I2C address (`0x3C`) is used in the Arduino code.
   - Check for loose wires or poor solder joints.

4. **Button Non-Responsive**:
   - Check button connections.
   - Ensure pull-up resistors are enabled (`INPUT_PULLUP`).
   - Debounce buttons in software if necessary.

5. **Serial Communication Issues**:
   - Ensure the correct COM port is selected in `hardware_interface.py`.
   - Close other applications that might be using the COM port.

---

## Contributing

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/YourFeature
   ```
3. **Commit Your Changes**
   ```bash
   git commit -m "Add Your Feature"
   ```
4. **Push to the Branch**
   ```bash
   git push origin feature/YourFeature
   ```
5. **Open a Pull Request**

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an experimental project intended for educational purposes. Use at your own risk. Always verify transactions and keep secure backups. The author is not liable for any losses or damages resulting from the use of this project.

---
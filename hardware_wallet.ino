#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SD.h>
#include <EEPROM.h>
#include <Crypto.h>
#include <AES.h>
#include <SHA256.h>
#include <base64.h>
#include <string.h>

// Display settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET     4
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// SD card settings
const int SD_CS_PIN = 53; // Adjust based on your wiring
File encryptedFile;

// Button pins
#define BUTTON_UP     2
#define BUTTON_DOWN   3
#define BUTTON_SELECT 4
#define BUTTON_BACK   5 // Optional

// States for menu
enum WalletState {
    MENU,
    DISPLAY_ADDRESS,
    SIGN_TRANSACTION,
    SETTINGS
};

WalletState currentState = MENU;
int menuPosition = 0;
const int MAX_MENU_ITEMS = 4;

// PIN handling
char pin[5] = "1234"; // Default PIN, should be set by the user
bool isLocked = true;

// Secure storage structure (Extend as needed)
struct WalletData {
    bool isInitialized;
} wallet;

void setup() {
    Serial.begin(115200); // Increased baud rate for faster communication
    
    // Initialize display
    if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println(F("SSD1306 allocation failed"));
        for(;;);
    }
    display.clearDisplay();
    
    // Initialize SD card
    if (!SD.begin(SD_CS_PIN)) {
        displayError("SD Card Init Failed");
        Serial.println("SD Card Initialization Failed!");
        for(;;);
    }
    Serial.println("SD Card Initialized.");
    
    // Setup buttons
    pinMode(BUTTON_UP, INPUT_PULLUP);
    pinMode(BUTTON_DOWN, INPUT_PULLUP);
    pinMode(BUTTON_SELECT, INPUT_PULLUP);
    pinMode(BUTTON_BACK, INPUT_PULLUP); // Optional
    
    // Initialize wallet
    EEPROM.get(0, wallet.isInitialized);
    if (!wallet.isInitialized) {
        initializeWallet();
    }
    
    // Show welcome screen
    displayWelcome();
}

void loop() {
    if (isLocked) {
        handlePinEntry();
        return;
    }
    
    handleButtons();
    handleSerialCommands();
    updateDisplay();
    delay(100);
}

void handleButtons() {
    if (digitalRead(BUTTON_UP) == LOW) {
        menuPosition = (menuPosition - 1 + MAX_MENU_ITEMS) % MAX_MENU_ITEMS;
        delay(200);
    }
    
    if (digitalRead(BUTTON_DOWN) == LOW) {
        menuPosition = (menuPosition + 1) % MAX_MENU_ITEMS;
        delay(200);
    }
    
    if (digitalRead(BUTTON_SELECT) == LOW) {
        handleMenuSelect();
        delay(200);
    }
    
    // Optional: Handle BACK button
    if (digitalRead(BUTTON_BACK) == LOW) {
        if (currentState != MENU) {
            currentState = MENU;
        }
        delay(200);
    }
}

void handleMenuSelect() {
    switch(menuPosition) {
        case 0:
            currentState = DISPLAY_ADDRESS;
            requestWalletAddress("btc_wallet.txt");
            break;
        case 1:
            currentState = DISPLAY_ADDRESS;
            requestWalletAddress("eth_wallet.txt");
            break;
        case 2:
            currentState = DISPLAY_ADDRESS;
            requestWalletAddress("bnb_wallet.txt");
            break;
        case 3:
            currentState = DISPLAY_ADDRESS;
            requestWalletAddress("sol_wallet.txt");
            break;
    }
}

void updateDisplay() {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,0);
    
    if (currentState == MENU) {
        // Draw menu
        const char* menuItems[] = {
            "Show BTC Address",
            "Show ETH Address",
            "Show BNB Address",
            "Show SOL Address"
        };
        
        for (int i = 0; i < MAX_MENU_ITEMS; i++) {
            if (i == menuPosition) {
                display.print("> ");
            } else {
                display.print("  ");
            }
            display.println(menuItems[i]);
        }
    }
    
    display.display();
}

void displayWelcome() {
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,10);
    display.println("Hardware");
    display.println("Wallet");
    display.display();
    delay(2000);
}

void displayError(const char* message) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,0);
    display.println("Error:");
    display.println(message);
    display.display();
    delay(3000);
}

void displayMessage(const char* message) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0,0);
    display.println(message);
    display.display();
    delay(2000);
    currentState = MENU;
}

void handlePinEntry() {
    static char enteredPin[5] = "0000";
    static int pinPosition = 0;
    
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0,0);
    display.println("Enter PIN:");
    display.println(enteredPin);
    display.display();
    
    if (digitalRead(BUTTON_UP) == LOW) {
        enteredPin[pinPosition] = ((enteredPin[pinPosition] - '0' + 1) % 10) + '0';
        delay(200);
    }
    
    if (digitalRead(BUTTON_DOWN) == LOW) {
        enteredPin[pinPosition] = ((enteredPin[pinPosition] - '0' + 9) % 10) + '0';
        delay(200);
    }
    
    if (digitalRead(BUTTON_SELECT) == LOW) {
        pinPosition++;
        if (pinPosition >= 4) {
            if (strcmp(enteredPin, pin) == 0) {
                isLocked = false;
                display.clearDisplay();
                display.println("Unlocked!");
                display.display();
                delay(1000);
            } else {
                display.clearDisplay();
                display.println("Wrong PIN!");
                display.display();
                delay(1000);
            }
            pinPosition = 0;
            strcpy(enteredPin, "0000");
        }
        delay(200);
    }
}

void initializeWallet() {
    wallet.isInitialized = true;
    EEPROM.put(0, wallet);
    displayMessage("Wallet Initialized");
}

void requestWalletAddress(const char* walletFile) {
    // Read encrypted wallet file from SD card
    encryptedFile = SD.open(walletFile, FILE_READ);
    if (!encryptedFile) {
        displayError("Failed to open wallet file");
        currentState = MENU;
        return;
    }
    
    // Read the encrypted data (assuming first line contains the encrypted string)
    String encryptedData = "";
    if (encryptedFile.available()) {
        encryptedData = encryptedFile.readStringUntil('\n');
    }
    encryptedFile.close();
    
    if (encryptedData.length() == 0) {
        displayError("Encrypted data empty");
        currentState = MENU;
        return;
    }
    
    // Extract the encrypted string after the ""
    int separatorIndex = encryptedData.indexOf('|');
    if (separatorIndex == -1) {
        displayError("Invalid file format");
        currentState = MENU;
        return;
    }
    String encryptedString = encryptedData.substring(separatorIndex + 1);
    
    // Prompt user for decryption password (reuse PIN as password)
    if (!decryptAndDisplay(encryptedString)) {
        displayError("Decryption Failed");
    }
}

bool decryptAndDisplay(String encryptedString) {
    // Convert the encrypted string from Base64 to byte array
    int len = encryptedString.length();
    byte encryptedBytes[len];
    base64_decode(encryptedString.c_str(), encryptedBytes, len);
    
    // Derive key from PIN (simple example; consider using a proper KDF)
    byte key[32];
    sha256(pin, strlen(pin), key); // Simple SHA256 hash of PIN
    
    // Initialize AES decryption (assuming AES-256-CBC used by Fernet)
    AES aesDecrypt;
    aesDecrypt.set_key(key, 32);
    
    // For CBC mode, you need the IV; assume it's the first 16 bytes
    byte iv[16];
    memcpy(iv, encryptedBytes, 16);
    
    aesDecrypt.set_iv(iv);
    
    // Decrypt the data (excluding the IV)
    int encryptedDataLen = len - 16;
    byte decryptedBytes[encryptedDataLen];
    aesDecrypt.decryptCBC(encryptedBytes + 16, decryptedBytes, encryptedDataLen);
    
    // Null-terminate the decrypted data
    decryptedBytes[encryptedDataLen] = '\0';
    
    // Convert decrypted bytes to string
    String decryptedString = "";
    for (int i = 0; i < encryptedDataLen; i++) {
        decryptedString += (char)decryptedBytes[i];
    }
    
    // Display the decrypted address
    displayDecryptedAddress(decryptedString);
    return true;
}

void displayDecryptedAddress(String address) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0,0);
    display.println("Wallet Address:");
    
    // Display address with wrapping if necessary
    int cursorY = 10;
    int charsPerLine = 22; // Adjust based on display size
    for (int i = 0; i < address.length(); i += charsPerLine) {
        int len = min(charsPerLine, address.length() - i);
        display.setCursor(0, cursorY);
        display.println(address.substring(i, i + len));
        cursorY += 10;
    }
    
    display.display();
    delay(5000); // Display for 5 seconds
    currentState = MENU;
} 
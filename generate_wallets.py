import os
from bitcoinlib.wallets import Wallet as BTCWallet
from web3 import Web3
from solders.keypair import Keypair
from cryptography.fernet import Fernet
import time

def get_user_confirmation(message):
    while True:
        response = input(f"{message} (yes/no): ").lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        print("Please enter 'yes' or 'no'")

def generate_btc_wallet():
    try:
        wallet_name = 'BTC_ColdWallet'
        try:
            # Check if wallet exists
            BTCWallet(wallet_name)
            if get_user_confirmation(f"Wallet '{wallet_name}' already exists. Create a new one?"):
                wallet_name = f'BTC_ColdWallet_{int(time.time())}'
                wallet = BTCWallet.create(wallet_name, network='bitcoin')
            else:
                wallet = BTCWallet(wallet_name)
        except:
            # Wallet doesn't exist, create new one
            wallet = BTCWallet.create(wallet_name, network='bitcoin')
        
        key = wallet.get_key()
        # Verify the address length
        address = key.address
        if not address.startswith(('1', '3', 'bc1')) or len(address) < 26:
            print(f"Warning: Generated Bitcoin address '{address}' may be invalid.")
        return key.key_private, address
    except Exception as e:
        print(f"Error generating BTC wallet: {str(e)}")
        return None, None

def generate_eth_wallet():
    try:
        w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-PROJECT-ID'))
        account = w3.eth.account.create()
        return account._private_key.hex(), account.address
    except Exception as e:
        print(f"Error generating ETH wallet: {str(e)}")
        return None, None

def generate_bnb_wallet():
    try:
        bnb_w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
        account = bnb_w3.eth.account.create()
        return account._private_key.hex(), account.address
    except Exception as e:
        print(f"Error generating BNB wallet: {str(e)}")
        return None, None

def generate_solana_wallet():
    try:
        keypair = Keypair()
        secret_key = keypair.secret()
        public_key = keypair.pubkey()
        return secret_key.hex(), str(public_key)
    except Exception as e:
        print(f"Error generating Solana wallet: {str(e)}")
        return None, None

def save_private_key(filename, key, address=None):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Convert bytes to hex string if needed
        if isinstance(key, bytes):
            key = key.hex()
        
        # Save both private key and address
        with open(filename, 'w') as f:
            f.write(f"Private Key: {key}\n")
            if address:
                f.write(f"Address: {address}\n")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {str(e)}")
        return False

# Add network initialization and deployment functions
def init_networks():
    try:
        # Initialize BTC mainnet
        # The 'network_defined_set' might not be necessary if specifying the network explicitly
        # from bitcoinlib.wallets import network_defined_set
        # network_defined_set('bitcoin')
        
        # Initialize Ethereum node connection
        eth_w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-PROJECT-ID'))
        
        # Initialize BNB node connection
        bnb_w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
        
        # Initialize Solana connection
        from solana.rpc.api import Client
        solana_client = Client("https://api.mainnet-beta.solana.com")
        
        return {
            'eth': eth_w3,
            'bnb': bnb_w3,
            'sol': solana_client
        }
    except Exception as e:
        print(f"Error initializing networks: {str(e)}")
        return None

def deploy_wallet(network, private_key, address):
    try:
        if network == 'btc':
            # BTC doesn't need deployment, just network broadcasting
            print(f"No deployment steps required for {network.upper()} wallet.")
        
        elif network in ['eth', 'bnb']:
            # For ETH and BNB, you might want to send a small amount for gas
            print(f"No deployment steps implemented for {network.upper()} wallet.")
        
        elif network == 'sol':
            # For Solana, you might want to create the account on-chain
            print(f"No deployment steps implemented for {network.upper()} wallet.")
        
    except Exception as e:
        print(f"Error deploying {network.upper()} wallet: {str(e)}")

def main():
    try:
        # Initialize networks first
        networks = init_networks()
        if not networks:
            print("Failed to initialize networks. Continuing with wallet generation only...")

        # Create wallets directory
        os.makedirs('wallets', exist_ok=True)

        # Dictionary to store wallet generation functions
        wallet_generators = {
            'BTC': (generate_btc_wallet, 'wallets/btc_wallet.txt'),
            'ETH': (generate_eth_wallet, 'wallets/eth_wallet.txt'),
            'BNB': (generate_bnb_wallet, 'wallets/bnb_wallet.txt'),
            'SOL': (generate_solana_wallet, 'wallets/sol_wallet.txt')
        }

        # Generate each wallet
        for crypto, (generator_func, filename) in wallet_generators.items():
            if get_user_confirmation(f"Generate {crypto} wallet?"):
                print(f"\nGenerating {crypto} wallet...")
                key, address = generator_func()
                
                if key is not None:
                    if save_private_key(filename, key, address):
                        print(f"{crypto} Wallet Generated Successfully!")
                        print(f"Saved to: {filename}")
                    else:
                        print(f"Failed to save {crypto} wallet information.")
                else:
                    print(f"Failed to generate {crypto} wallet.")
                
                print("-" * 50)

                # After generating each wallet, add:
                if networks:
                    deploy_wallet(crypto.lower(), key, address)

        print("\nWallet generation complete!")
        print("Please store your wallet information securely!")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main() 
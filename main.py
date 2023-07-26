from typing import Optional
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
import time

target_zeros = int(input('\nEnter number of zeros after "0x" : ')) # Number of 0 after 0x
n_wallets = int(input("Enter number of wallets : ")) # Number of wallets
print()

def generate_evm_wallet(target_zeros, n_wallets):

    wallets = {
        'mnemonics' : [],
        'addresses' : [],
        'keys' : [],
    }

    for i in range(n_wallets):

        start = time.perf_counter()

        while True:

            # Generate english mnemonic words
            MNEMONIC: str = generate_mnemonic(language="english", strength=128)
            # Secret passphrase/password for mnemonic
            PASSPHRASE: Optional[str] = None  # "meherett"

            # Initialize Ethereum mainnet BIP44HDWallet
            bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
            # Get Ethereum BIP44HDWallet from mnemonic
            bip44_hdwallet.from_mnemonic(
                mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE
            )
            # Clean default BIP44 derivation indexes/paths
            bip44_hdwallet.clean_derivation()
            mnemonics = bip44_hdwallet.mnemonic()

            # Derivation from Ethereum BIP44 derivation path
            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=EthereumMainnet, account=0, change=False, address=0
            )
            # Drive Ethereum BIP44HDWallet
            bip44_hdwallet.from_path(path=bip44_derivation)
            # Print address_index, path, address and private_key
            address = bip44_hdwallet.address()
            key = bip44_hdwallet.private_key()
            # Clean derivation indexes/paths
            bip44_hdwallet.clean_derivation() 

            if address.startswith("0x" + "0" * target_zeros):
                print(f'{address} : {int((time.perf_counter() - start))} sec.')
                wallets["mnemonics"].append(mnemonics)
                wallets["addresses"].append(address)
                wallets["keys"].append(f'{key}')
                break

    file_keys = open(f"key.txt", "w")
    file_addr = open(f"address.txt", "w")
    file_seed = open(f"seed.txt", "w")

    for x in wallets["mnemonics"]:
        file_seed.write(f'{str(x)}\n')

    for x in wallets["addresses"]:
        file_addr.write(f'{str(x)}\n')

    for x in wallets["keys"]:
        file_keys.write(f'0x{str(x)}\n')

    file_keys.close()
    file_addr.close()
    file_seed.close()

    print(f'\nThe result is written to key.txt address.txt seed.txt')

if __name__ == "__main__":
    generate_evm_wallet(target_zeros, n_wallets)
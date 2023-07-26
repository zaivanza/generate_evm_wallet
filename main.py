from typing import Optional
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from concurrent.futures import ProcessPoolExecutor
from mnemonic import Mnemonic
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import multiprocessing


def generate_wallet(target_zeros, total_wallets, wallets):
    mnemo = Mnemonic("english")

    while len(wallets["addresses"]) < total_wallets:
        start = time.perf_counter()

        MNEMONIC: str = mnemo.generate(strength=128)
        PASSPHRASE: Optional[str] = None

        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
        bip44_hdwallet.from_mnemonic(
            mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE
        )

        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=0
        )
        bip44_hdwallet.from_path(path=bip44_derivation)
        address = bip44_hdwallet.address()
        print(address)
        key = bip44_hdwallet.private_key()
        bip44_hdwallet.clean_derivation()

        address_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        address_hash.update(address.encode('utf-8'))
        address_hash_digest = address_hash.finalize()

        if address_hash_digest.startswith(b'\x00' * target_zeros):
            with wallets.get_lock():
                print(f'{address} : {int((time.perf_counter() - start))} sec.')
                wallets["mnemonics"].append(MNEMONIC)
                wallets["addresses"].append(address)
                wallets["keys"].append(f'{key}')


def main():
    print('\t\t25k wallets in 1m30s')
    title = "tg: @fraggdiller / @retrodropTools"
    print("╔" + "═" * 36 + "╗")
    print("║" + title.center(36) + "║")
    print("╚" + "═" * 36 + "╝")
    target_zeros = int(input('\nEnter number of zeros after "0x" : '))  # Number of 0 after 0x
    n_wallets = int(input("Enter number of wallets : "))  # Number of wallets
    print()

    manager = multiprocessing.Manager()
    wallets = manager.dict()
    wallets["mnemonics"] = manager.list()
    wallets["addresses"] = manager.list()
    wallets["keys"] = manager.list()

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(generate_wallet, target_zeros, n_wallets, wallets) for _ in range(10)]

    with open("key.txt", "w") as file_keys, open("address.txt", "w") as file_addr, open("seed.txt", "w") as file_seed:
        for x in wallets["mnemonics"]:
            file_seed.write(f'{str(x)}\n')

        for x in wallets["addresses"]:
            file_addr.write(f'{str(x)}\n')

        for x in wallets["keys"]:
            file_keys.write(f'0x{str(x)}\n')

    print(f'\nThe result is written to key.txt address.txt seed.txt')


if __name__ == "__main__":
    main()

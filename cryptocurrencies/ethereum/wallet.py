#!/usr/bin/env python3

from swap.providers.ethereum.wallet import (
    Wallet, DEFAULT_PATH
)
from swap.utils import (
    generate_entropy, generate_passphrase
)

# Choose network mainnet, ropsten, kovan, rinkeby or testnet
NETWORK: str = "ropsten"  # Default to mainnet
# Choose strength 128, 160, 192, 224 or 256
STRENGTH: int = 160  # Default is 128
# Choose language english, french, italian, spanish, chinese_simplified, chinese_traditional, japanese or korean
LANGUAGE: str = "english"  # Default is english
# Set passphrase length
LENGTH: int = 32  # Default is 32
# Generate new entropy hex string
ENTROPY: str = generate_entropy(strength=STRENGTH)
# Generate new passphrase
PASSPHRASE: str = generate_passphrase(length=LENGTH)
# Ethereum ERC20 token address
TOKEN_ADDRESS: str = "0xa6f89f08cC9d112870E2561F1A8D750681DB59f1"

# Initialize Ethereum wallet
wallet: Wallet = Wallet(network=NETWORK)
# Get Ethereum wallet from entropy
wallet.from_entropy(
    entropy=ENTROPY, language=LANGUAGE, passphrase=PASSPHRASE
)
# Drive Ethereum wallet from path
wallet.from_path(path=DEFAULT_PATH)

# Print all Ethereum wallet info's
print("Strength:", wallet.strength())
print("Entropy:", wallet.entropy())
print("Mnemonic:", wallet.mnemonic())
print("Language:", wallet.language())
print("Passphrase:", wallet.passphrase())
print("Seed:", wallet.seed())
print("Root XPrivate Key:", wallet.root_xprivate_key())
print("Root XPublic Key:", wallet.root_xpublic_key())
print("XPrivate Key:", wallet.xprivate_key())
print("XPublic Key:", wallet.xpublic_key())
print("Uncompressed:", wallet.uncompressed())
print("Compressed:", wallet.compressed())
print("Chain Code:", wallet.chain_code())
print("Private Key:", wallet.private_key())
print("Public Key:", wallet.public_key())
print("Wallet Important Format:", wallet.wif())
print("Hash:", wallet.hash())
print("Finger Print:", wallet.finger_print())
print("Path:", wallet.path())
print("Address:", wallet.address())
print("Balance:", wallet.balance(unit="Ether"), "Ether")
print("ERC20 Balance:", wallet.erc20_balance(token_address=TOKEN_ADDRESS))

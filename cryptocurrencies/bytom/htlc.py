#!/usr/bin/env python3

from swap.providers.bytom.htlc import HTLC
from swap.providers.bytom.assets import BTM as ASSET
from swap.providers.bytom.rpc import get_balance
from swap.providers.bytom.utils import amount_converter
from swap.utils import sha256

# Choose network mainnet, solonet or testnet
NETWORK: str = "mainnet"
# Secret key hash
SECRET_HASH: str = sha256("Hello Meheret!")
# Recipient Bytom public key
RECIPIENT_PUBLIC_KEY: str = "3e0a377ae4afa031d4551599d9bb7d5b27f4736d77f78cac4d476f0ffba5ae3e"
# Sender Bytom public key
SENDER_PUBLIC_KEY: str = "91ff7f525ff40874c4f47f0cab42e46e3bf53adad59adef9558ad1b6448f22e2"
# Expiration block (Sequence)
SEQUENCE: int = 1000

print("=" * 10, "Hash Time Lock Contract (HTLC) between Sender and Recipient")

# Initialize Bytom HTLC
htlc: HTLC = HTLC(network=NETWORK)
# Build HTLC contract
htlc.build_htlc(
    secret_hash=SECRET_HASH,
    recipient_public_key=RECIPIENT_PUBLIC_KEY,
    sender_public_key=SENDER_PUBLIC_KEY,
    sequence=SEQUENCE
)

# Print all Bytom HTLC info's
print("HTLC Bytecode:", htlc.bytecode())
print("HTLC OP_Code:", htlc.opcode())
print("HTLC Hash:", htlc.hash())
print("HTLC Address:", htlc.address())

# Get the balance of HTLC contract (BTM amount)
print("HTLC Balance:", amount_converter(amount=get_balance(
    address=htlc.address(), asset=ASSET, network=NETWORK
), symbol="NEU2BTM"), "BTM")

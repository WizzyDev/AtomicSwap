#!/usr/bin/env python3

from btcpy.structs.script import (
    ScriptSig, Script
)
from btcpy.structs.transaction import (
    MutableTransaction, Sequence, TxIn, TxOut
)
from btcpy.structs.address import Address
from btcpy.setup import setup as stp
from btcpy.structs.script import (
    P2pkhScript, P2shScript
)
from base64 import b64decode
from typing import (
    Union, Optional
)

import requests
import cryptos
import json
import datetime

from ...utils import clean_transaction_raw
from ...exceptions import (
    AddressError, NetworkError, APIError, SymbolError, TransactionRawError
)
from ..config import bitcoin

# Bitcoin config
config = bitcoin()


def amount_converter(amount: Union[int, float], symbol: str = "SATOSHI2BTC") -> Union[int, float]:
    """
    Amount converter

    :param amount: Bitcoin amount.
    :type amount: Union[int, float]
    :param symbol: Bitcoin symbol, default to SATOSHI2BTC.
    :type symbol: str
    :returns: float -- BTC asset amount.

    >>> from swap.providers.bitcoin.utils import amount_converter
    >>> amount_converter(amount=10_000_000, symbol="SATOSHI2BTC")
    0.1
    """

    if symbol not in ["BTC2mBTC", "BTC2SATOSHI", "mBTC2BTC", "mBTC2SATOSHI", "SATOSHI2BTC", "SATOSHI2mBTC"]:
        raise SymbolError(f"Invalid '{symbol}' symbol/type",
                          "choose only 'BTC2mBTC', 'BTC2SATOSHI', 'mBTC2BTC', "
                          "'mBTC2SATOSHI', 'SATOSHI2BTC' or 'SATOSHI2mBTC' symbols.")

    # Constant values
    BTC, mBTC, SATOSHI = (1, 1000, 100_000_000)

    if symbol == "BTC2mBTC":
        return float((amount * mBTC) / BTC)
    elif symbol == "BTC2SATOSHI":
        return int((amount * SATOSHI) / BTC)
    elif symbol == "mBTC2BTC":
        return float((amount * BTC) / mBTC)
    elif symbol == "mBTC2SATOSHI":
        return int((amount * SATOSHI) / mBTC)
    elif symbol == "SATOSHI2BTC":
        return float((amount * BTC) / SATOSHI)
    elif symbol == "SATOSHI2mBTC":
        return int((amount * mBTC) / SATOSHI)


def fee_calculator(transaction_input: int = 1, transaction_output: int = 1) -> int:
    """
    Bitcoin fee calculator.

    :param transaction_input: transaction input numbers, defaults to 1.
    :type transaction_input: int
    :param transaction_output: transaction output numbers, defaults to 1.
    :type transaction_output: int
    :returns: int -- Bitcoin fee (SATOSHI amount).

    >>> from swap.providers.bitcoin.utils import fee_calculator
    >>> fee_calculator(2, 9)
    1836
    """

    # 444 input 102 output
    transaction_input = ((transaction_input - 1) * 444) + 576
    transaction_output = ((transaction_output - 1) * 102)
    return transaction_input + transaction_output


def is_network(network: str) -> bool:
    """
    Check Bitcoin network.

    :param network: Bitcoin network.
    :type network: str
    :returns: bool -- Bitcoin valid/invalid network.

    >>> from swap.providers.bitcoin.utils import is_network
    >>> is_network("testnet")
    True
    """

    if not isinstance(network, str):
        raise TypeError(f"Network must be str, not '{type(network)}' type.")
    return network in ["mainnet", "testnet"]


def is_address(address: str, network: Optional[str] = None) -> bool:
    """
    Check Bitcoin address.

    :param address: Bitcoin address.
    :type address: str
    :param network: Bitcoin network, defaults to None.
    :type network: str
    :returns: bool -- Bitcoin valid/invalid address.

    >>> from swap.providers.bitcoin.utils import is_address
    >>> is_address("mrmtGq2HMmqAogSsGDjCtXUpxrb7rHThFH", "testnet")
    True
    """

    if not isinstance(address, str):
        raise TypeError(f"Address must be str, not '{type(address)}' type.")

    if network is None:
        for boolean in [True, False]:
            valid = False
            if cryptos.Bitcoin(testnet=boolean).is_address(address):
                valid = True
                break
        return valid

    if not is_network(network=network):
        raise NetworkError(f"Invalid Bitcoin '{network}' network",
                           "choose only 'mainnet' or 'testnet' networks.")

    if network == "mainnet":
        return cryptos.Bitcoin(testnet=False).is_address(address)
    elif network == "testnet":
        return cryptos.Bitcoin(testnet=True).is_address(address)


def is_transaction_raw(transaction_raw: str) -> bool:
    """
    Check Bitcoin transaction raw.

    :param transaction_raw: Bitcoin transaction raw.
    :type transaction_raw: str
    :returns: bool -- Bitcoin valid/invalid transaction raw.

    >>> from swap.providers.bitcoin.utils import is_transaction_raw
    >>> is_transaction_raw("...")
    True
    """

    if not isinstance(transaction_raw, str):
        raise TypeError(f"Transaction raw must be str, not '{type(transaction_raw)}' type.")

    try:
        transaction_raw = clean_transaction_raw(transaction_raw)
        decoded_transaction_raw = b64decode(transaction_raw.encode())
        loads_transaction_raw = json.loads(decoded_transaction_raw.decode())
        return loads_transaction_raw["type"] in [
            "bitcoin_fund_unsigned", "bitcoin_fund_signed",
            "bitcoin_claim_unsigned", "bitcoin_claim_signed",
            "bitcoin_refund_unsigned", "bitcoin_refund_signed"
        ]
    except:
        return False


def decode_transaction_raw(transaction_raw: str, offline: bool = True,
                           headers: dict = config["headers"], timeout: int = config["timeout"]) -> dict:
    """
    Decode Bitcoin transaction raw.

    :param transaction_raw: Bitcoin transaction raw.
    :type transaction_raw: str
    :param offline: Offline decode, defaults to True.
    :type offline: bool
    :param headers: Request headers, default to common headers.
    :type headers: dict
    :param timeout: Request timeout, default to 60.
    :type timeout: int
    :returns: dict -- Decoded Bitcoin transaction raw.

    >>> from swap.providers.bitcoin.utils import decode_transaction_raw
    >>> transaction_raw = "eyJmZWUiOiA2NzgsICJyYXciOiAiMDIwMDAwMDAwMTg4OGJlN2VjMDY1MDk3ZDk1NjY0NzYzZjI3NmQ0MjU1NTJkNzM1ZmIxZDk3NGFlNzhiZjcyMTA2ZGNhMGYzOTEwMTAwMDAwMDAwZmZmZmZmZmYwMjEwMjcwMDAwMDAwMDAwMDAxN2E5MTQyYmIwMTNjM2U0YmViMDg0MjFkZWRjZjgxNWNiNjVhNWMzODgxNzhiODdiY2RkMGUwMDAwMDAwMDAwMTk3NmE5MTQ2NGE4MzkwYjBiMTY4NWZjYmYyZDRiNDU3MTE4ZGM4ZGE5MmQ1NTM0ODhhYzAwMDAwMDAwIiwgIm91dHB1dHMiOiBbeyJhbW91bnQiOiA5ODQ5NDYsICJuIjogMSwgInNjcmlwdCI6ICI3NmE5MTQ2NGE4MzkwYjBiMTY4NWZjYmYyZDRiNDU3MTE4ZGM4ZGE5MmQ1NTM0ODhhYyJ9XSwgIm5ldHdvcmsiOiAidGVzdG5ldCIsICJ0eXBlIjogImJpdGNvaW5fZnVuZF91bnNpZ25lZCJ9"
    >>> decode_transaction_raw(transaction_raw)
    {'fee': 678, 'type': 'bitcoin_fund_unsigned', 'tx': {'hex': '0200000001888be7ec065097d95664763f276d425552d735fb1d974ae78bf72106dca0f3910100000000ffffffff02102700000000000017a9142bb013c3e4beb08421dedcf815cb65a5c388178b87bcdd0e00000000001976a91464a8390b0b1685fcbf2d4b457118dc8da92d553488ac00000000', 'txid': 'abc70fd3466aec9478ea3115200a84f993204ad1f614fe08e92ecc5997a0d3ba', 'hash': 'abc70fd3466aec9478ea3115200a84f993204ad1f614fe08e92ecc5997a0d3ba', 'size': 117, 'vsize': 117, 'version': 2, 'locktime': 0, 'vin': [{'txid': '91f3a0dc0621f78be74a971dfb35d75255426d273f766456d9975006ece78b88', 'vout': 1, 'scriptSig': {'asm': '', 'hex': ''}, 'sequence': '4294967295'}], 'vout': [{'value': '0.00010000', 'n': 0, 'scriptPubKey': {'asm': 'OP_HASH160 2bb013c3e4beb08421dedcf815cb65a5c388178b OP_EQUAL', 'hex': 'a9142bb013c3e4beb08421dedcf815cb65a5c388178b87', 'type': 'p2sh', 'address': '2MwEDybGC34949zgzWX4M9FHmE3crDSUydP'}}, {'value': '0.00974268', 'n': 1, 'scriptPubKey': {'asm': 'OP_DUP OP_HASH160 64a8390b0b1685fcbf2d4b457118dc8da92d5534 OP_EQUALVERIFY OP_CHECKSIG', 'hex': '76a91464a8390b0b1685fcbf2d4b457118dc8da92d553488ac', 'type': 'p2pkh', 'address': 'mphBPZf15cRFcL5tUq6mCbE84XobZ1vg7Q'}}]}, 'network': 'testnet'}
    """

    if not is_transaction_raw(transaction_raw=transaction_raw):
        raise TransactionRawError("Invalid Bitcoin transaction raw.")

    transaction_raw = clean_transaction_raw(transaction_raw)
    decoded_transaction_raw = b64decode(transaction_raw.encode())
    loaded_transaction_raw = json.loads(decoded_transaction_raw.decode())

    decoded_transaction: Optional[dict] = None

    if offline:
        stp(loaded_transaction_raw["network"], strict=True)
        tx = MutableTransaction.unhexlify(loaded_transaction_raw["raw"])
        decoded_transaction = tx.to_json()
    else:
        url = f"{config[loaded_transaction_raw['network']]['blockcypher']['url']}/txs/decode"
        parameter = dict(token=config[loaded_transaction_raw["network"]]["blockcypher"]["token"])
        data = dict(tx=loaded_transaction_raw["raw"])
        response = requests.post(
            url=url, data=json.dumps(data), params=parameter, headers=headers, timeout=timeout
        )
        decoded_transaction = response.json()

    return dict(
        fee=loaded_transaction_raw["fee"],
        type=loaded_transaction_raw["type"],
        tx=decoded_transaction,
        network=loaded_transaction_raw["network"]
    )


def submit_transaction_raw(transaction_raw: str, headers: dict = config["headers"],
                           timeout: int = config["timeout"]) -> dict:
    """
    Submit transaction raw to Bitcoin blockchain.

    :param transaction_raw: Bitcoin transaction raw.
    :type transaction_raw: str
    :param headers: Request headers, default to common headers.
    :type headers: dict
    :param timeout: Request timeout, default to 60.
    :type timeout: int
    :returns: dict -- Bitcoin transaction id, fee, type and date.

    >>> from swap.providers.bitcoin.utils import submit_transaction_raw
    >>> transaction_raw = "eyJmZWUiOiA2NzgsICJyYXciOiAiMDIwMDAwMDAwMTg4OGJlN2VjMDY1MDk3ZDk1NjY0NzYzZjI3NmQ0MjU1NTJkNzM1ZmIxZDk3NGFlNzhiZjcyMTA2ZGNhMGYzOTEwMTAwMDAwMDAwZmZmZmZmZmYwMjEwMjcwMDAwMDAwMDAwMDAxN2E5MTQyYmIwMTNjM2U0YmViMDg0MjFkZWRjZjgxNWNiNjVhNWMzODgxNzhiODdiY2RkMGUwMDAwMDAwMDAwMTk3NmE5MTQ2NGE4MzkwYjBiMTY4NWZjYmYyZDRiNDU3MTE4ZGM4ZGE5MmQ1NTM0ODhhYzAwMDAwMDAwIiwgIm91dHB1dHMiOiBbeyJhbW91bnQiOiA5ODQ5NDYsICJuIjogMSwgInNjcmlwdCI6ICI3NmE5MTQ2NGE4MzkwYjBiMTY4NWZjYmYyZDRiNDU3MTE4ZGM4ZGE5MmQ1NTM0ODhhYyJ9XSwgIm5ldHdvcmsiOiAidGVzdG5ldCIsICJ0eXBlIjogImJpdGNvaW5fZnVuZF91bnNpZ25lZCJ9"
    >>> submit_transaction_raw(transaction_raw)
    {'fee': '...', 'type': '...', 'transaction_id': '...', 'network': '...', 'date': '...'}
    """

    if not is_transaction_raw(transaction_raw=transaction_raw):
        raise TransactionRawError("Invalid Bitcoin transaction raw.")

    transaction_raw = clean_transaction_raw(transaction_raw)
    decoded_transaction_raw = b64decode(transaction_raw.encode())
    loaded_transaction_raw = json.loads(decoded_transaction_raw.decode())

    url = f"{config[loaded_transaction_raw['network']]['smartbit']}/pushtx"
    data = dict(hex=loaded_transaction_raw["raw"])
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=timeout
    )
    response_json = response.json()
    if "success" in response_json and not response_json["success"]:
        raise APIError(response_json["error"]["message"], response_json["error"]["code"])
    elif "success" in response_json and response_json["success"]:
        return dict(
            fee=loaded_transaction_raw["fee"],
            type=loaded_transaction_raw["type"],
            transaction_id=response_json["txid"],
            network=loaded_transaction_raw["network"],
            date=str(datetime.datetime.utcnow())
        )
    else:
        raise APIError("Unknown Bitcoin submit payment error.")


def get_address_hash(address: str, script: bool = False) -> Union[str, P2pkhScript, P2shScript]:
    """
    Get hash from address.

    :param address: Bitcoin address.
    :type address: str
    :param script: Return script (P2pkhScript, P2shScript), default to False.
    :type script: bool
    :returns: str -- Bitcoin address hash.

    >>> from swap.providers.bitcoin.utils import get_address_hash
    >>> get_address_hash(address="mrmtGq2HMmqAogSsGDjCtXUpxrb7rHThFH", script=False)
    "7b7c4431a43b612a72f8229935c469f1f6903658"
    """

    if not is_address(address=address):
        raise AddressError(f"Invalid Bitcoin '{address}' address.")

    loaded_address = Address.from_string(address)
    get_type = loaded_address.get_type()
    if not script:
        return loaded_address.hash.hex()
    if str(get_type) == "p2pkh":
        return P2pkhScript(loaded_address)
    elif str(get_type) == "p2sh":
        return P2shScript(loaded_address)


def _get_previous_transaction_indexes(utxos: list, amount: int) -> list:
    temp_amount = int()
    previous_transaction_indexes = list()
    for index, utxo in enumerate(utxos):
        temp_amount += utxo["value"]
        if temp_amount > (amount + fee_calculator((index + 1), 2)):
            previous_transaction_indexes.append(index)
            break
        previous_transaction_indexes.append(index)
    return previous_transaction_indexes


def _build_inputs(utxos: list, previous_transaction_indexes: Optional[list] = None) -> tuple:
    inputs, amount = [], 0
    for index, utxo in enumerate(utxos):
        if previous_transaction_indexes is None or index in previous_transaction_indexes:
            amount += utxo["value"]
            inputs.append(
                TxIn(
                    txid=utxo["tx_hash"],
                    txout=utxo["tx_output_n"],
                    script_sig=ScriptSig.empty(),
                    sequence=Sequence.max()
                )
            )
    return inputs, amount


def _build_outputs(utxos: list, previous_transaction_indexes: Optional[list] = None, only_dict: bool = False) -> list:
    outputs = []
    for index, utxo in enumerate(utxos):
        if previous_transaction_indexes is None or index in previous_transaction_indexes:
            outputs.append(
                TxOut(
                    value=utxo["value"],
                    n=utxo["tx_output_n"],
                    script_pubkey=Script.unhexlify(
                        hex_string=utxo["script"]
                    )
                )
                if not only_dict else
                dict(
                    value=utxo["value"],
                    tx_output_n=utxo["tx_output_n"],
                    script=utxo["script"]
                )
            )
    return outputs

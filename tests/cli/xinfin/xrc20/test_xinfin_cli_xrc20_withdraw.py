#!/usr/bin/env python3

import json
import os

from swap.cli.__main__ import main as cli_main
from swap.providers.xinfin.utils import is_transaction_raw

# Test Values
base_path = os.path.dirname(__file__)
file_path = os.path.abspath(os.path.join(base_path, "..", "..", "..", "values.json"))
values = open(file_path, "r")
_ = json.loads(values.read())
values.close()


def test_xinfin_cli_xrc20_withdraw(cli_tester):

    xrc20_withdraw = cli_tester.invoke(
        cli_main, [
            "xinfin",
            "withdraw",
            "--address", _["xinfin"]["wallet"]["recipient"]["address"],
            "--transaction-hash", _["xinfin"]["xrc20_transaction_hash"],
            "--secret-key", _["xinfin"]["xrc20_htlc"]["secret"]["key"],
            "--network", _["xinfin"]["network"],
            "--xrc20", True
        ]
    )
    assert xrc20_withdraw.exit_code == 0
    assert is_transaction_raw(xrc20_withdraw.output)

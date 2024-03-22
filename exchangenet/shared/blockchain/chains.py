import json
import os

from .evm import EvmChain, Token


# read bittex_abi.json file and store it in a variable
current_dir = os.path.dirname(__file__)
with open(os.path.join(current_dir, 'abis/bittex_abi.json')) as abi_file:
    bittex_abi = json.load(abi_file)

chains = {
    "bnb": EvmChain(
        rpc_url="https://bsc-dataseed.binance.org/",
        chain_id=56,
        chain_name="Binance Smart Chain",
        bittex_contract_address="0x0",
        bittex_abi="",
        available_tokens=[
            Token(
                symbol="USDT",
                name="Tether USD",
                address="0x55d398326f99059fF775485246999027B3197955",
                decimals=18
            ),
            Token(
                symbol="ETH",
                name="Ether",
                address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                decimals=18
            )
        ]
    ),
    "bnb_test": EvmChain(
        rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545/",
        chain_id=97,
        chain_name="Binance Smart Chain Testnet",
        bittex_contract_address="0xE08DD76D35D27b80Ebc2C3221d5A98bFd02d8080",
        bittex_abi=bittex_abi["abi"],
        available_tokens=[
            Token(
                symbol="USDT",
                name="Tether USD",
                address="0x337610d27c682e347c9cd60bd4b3b107c9d34ddd",
                decimals=18
            ),
            Token(
                symbol="WETH",
                name="Wrapped Ether",
                address="0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",
                decimals=18
            )
        ],
        is_testnet=True
    ),
}

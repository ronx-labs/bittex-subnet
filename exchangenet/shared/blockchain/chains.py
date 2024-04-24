import json
import os

from .evm import EvmChain, Token
from .abis import BITTEX_ABI


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
        bittex_contract_address="0x2C9Ce1543A4eb3bE45636103F1BFaaE31B0E906b",
        bittex_abi=BITTEX_ABI,
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
                address="0xd66c6B4F0be8CE5b39D52E0Fd1344c389929B378",
                decimals=18
            )
        ],
        is_testnet=True
    ),
}

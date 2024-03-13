from typing import Optional, List, Dict
from pydantic import BaseModel


class Token(BaseModel):
    address: str
    name: str
    symbol: str
    decimals: int


class EvmChain:
    def __init__(self, rpc_url: str, chain_id: int, chain_name: str, bittex_contract: str, available_tokens: List[Token]):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.chain_name = chain_name
        self.bittex_contract = bittex_contract
        self.available_tokens = available_tokens

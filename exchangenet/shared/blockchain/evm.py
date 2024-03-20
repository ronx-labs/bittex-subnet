from web3 import Web3
from eth_account.messages import encode_defunct

from typing import Optional, List, Dict
from pydantic import BaseModel


class Token(BaseModel):
    address: str
    name: str
    symbol: str
    decimals: int


class EvmChain:
    def __init__(self, rpc_url: str, chain_id: int, chain_name: str, bittex_contract: str, available_tokens: List[Token], is_testnet: bool = False):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.chain_name = chain_name
        self.bittex_contract = bittex_contract
        self.available_tokens = available_tokens
        self.is_testnet = is_testnet
        self.web3_provider = Web3(Web3.HTTPProvider(rpc_url))
        
    def get_token_by_address(self, address: str) -> Optional[Token]:
        for token in self.available_tokens:
            if token.address == address:
                return token
        return None
    
    def get_token_by_symbol(self, symbol: str) -> Optional[Token]:
        for token in self.available_tokens:
            if token.symbol == symbol:
                return token
        return None
    
    def is_token_available(self, address: str) -> bool:
        return self.get_token_by_address(address) is not None

    def transfer_token(self, from_address: str, to_address: str, token_address: str, amount: int, private_key: str) -> str:
        pass
    
    def sign_message(self, message: str, private_key: bytes) -> bytes:
        signable_msg = encode_defunct(text=message)
        signed_message = self.web3_provider.eth.account.sign_message(signable_msg, private_key)
        return signed_message.signature.hex()

    def verify_signature(self, message: str, signature: bytes, public_address: bytes) -> bool:
        signable_msg = encode_defunct(text=message)
        recovered_address = self.web3_provider.eth.account.recover_message(signable_msg, signature=signature)
        return recovered_address.lower() == '0x' + public_address.hex()

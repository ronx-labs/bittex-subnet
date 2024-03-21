from web3 import Web3
from eth_account.messages import encode_defunct

from typing import Optional, List, Dict
from pydantic import BaseModel


ZERO_ADDRESS = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")

class Token(BaseModel):
    address: str
    name: str
    symbol: str
    decimals: int
    
class Swap(BaseModel):
    swap_id: bytes
    input_token_address: str
    output_token_address: str
    top_bidders: List[str]
    winner: str
    amount: int
    timestamp: int


class EvmChain:
    def __init__(self, rpc_url: str, chain_id: int, chain_name: str, bittex_contract_address: str, bittex_abi: str, available_tokens: List[Token], is_testnet: bool = False):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.chain_name = chain_name
        self.bittex_contract_address = bittex_contract_address
        self.bittex_abi = bittex_abi
        self.available_tokens = available_tokens
        self.is_testnet = is_testnet
        
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
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
        signed_message = self.web3.eth.account.sign_message(signable_msg, private_key)
        return signed_message.signature.hex()

    def verify_signature(self, message: str, signature: bytes, public_address: bytes) -> bool:
        signable_msg = encode_defunct(text=message)
        recovered_address = self.web3.eth.account.recover_message(signable_msg, signature=signature)
        return recovered_address.lower() == '0x' + public_address.hex()

    def create_swap(self, input_token_address: str, output_token_address: str, amount: int, account_address: str, private_key: str) -> bytes:
        bittex_contract = self.web3.eth.contract(address=self.bittex_contract_address, abi=self.bittex_abi)
        
        # Build transaction
        nonce = self.web3.eth.get_transaction_count(account_address)
        transaction = bittex_contract.functions.createSwap(self.web3.to_checksum_address(input_token_address), self.web3.to_checksum_address(output_token_address), amount).build_transaction({
            'chainId': self.chain_id,
            'gas': 2000000,
            'gasPrice': self.web3.to_wei('50', 'gwei'),
            'nonce': nonce,
        })

        # Sign transaction
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=private_key)

        # Send transaction
        txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Get transaction receipt (optional)
        txn_receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash)
        
        # Assuming the event name is 'SwapCreated' and it emits the bytes32 value
        event = bittex_contract.events.SwapCreated().process_receipt(txn_receipt)
        swap_id = event[0].args.swapId
        return swap_id
    
    def get_swap(self, swap_id: bytes) -> Swap:
        bittex_contract = self.web3.eth.contract(address=self.bittex_contract_address, abi=self.bittex_abi)
        raw_swap_info = bittex_contract.functions.swaps(swap_id).call()
        swap = Swap(
            swap_id=swap_id,
            input_token_address=raw_swap_info[0],
            output_token_address=raw_swap_info[1],
            top_bidders=raw_swap_info[2:5],
            winner=raw_swap_info[5],
            amount=raw_swap_info[6],
            timestamp=raw_swap_info[7]
        )
        return swap

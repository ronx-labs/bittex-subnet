from web3 import Web3
from web3.exceptions import TransactionNotFound
from web3.middleware import geth_poa_middleware
from web3._utils.events import EventLogErrorFlags
import unittest
import json

from typing import Dict

from exchangenet.shared.blockchain.chains import chains
from exchangenet.shared.blockchain.evm import EvmChain, Token

# from neurons.validators.utils.utils import get_miner_distributions, count_run_id_per_hotkey, count_hotkeys_per_ip, generate_challenge_to_check
# from neurons.nodes.bitcoin.node_utils import process_in_memory_txn_for_indexing
# from neurons.nodes.factory import NodeFactory
# from neurons.miners.bitcoin.funds_flow.graph_creator import GraphCreator
# from insights.protocol import NETWORK_BITCOIN


class TestUtils(unittest.TestCase):

    def test_create_swap(self):

        # Connect to an Ethereum node
        bnb_testnet = chains["bnb_test"]

        w3 = bnb_testnet.web3_provider

        bittex_contract = w3.eth.contract(address=bnb_testnet.bittex_contract_address, abi=bnb_testnet.bittex_abi)

        TO_ADDRESS = '0x84F16beCf5d694cC494cEAe8258463Da97E5ED9A'  # Adjust the to address 


        # Replace with your private key
        private_key = 'db544f6b1484455b64246ac3f566a0acbf8a9161796974404af14ce8882ef025'

        # Check if the private key is provided
        if not private_key:
            raise ValueError("Private key not provided.")

        # Inject PoA middleware for networks using Proof of Authority consensus
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Check for connection to the Ethereum network
        if not w3.is_connected():
            raise ConnectionError("Failed to connect to HTTPProvider")

        # Define transaction details
        token_amount = w3.to_wei(1, 'ether')  # Adjust the amount as needed

        # Get the nonce for the transaction
        my_address = w3.eth.account.from_key(private_key).address
        nonce = w3.eth.get_transaction_count(my_address)

        swap_id = bittex_contract.functions.createSwap(my_address, TO_ADDRESS, token_amount).call()

        # Convert bytes32 to hex string
        hex_string = w3.to_hex(swap_id)

        print(hex_string)

        print(f'swaps: {bittex_contract.functions.swaps(hex_string).call()}')


    def test_send(self):
        # Connect to an Ethereum node
        bnb_testnet = chains["bnb_test"]
        evm = EvmChain(rpc_url=bnb_testnet.rpc_url, chain_id=bnb_testnet.chain_id, chain_name=bnb_testnet.chain_name, bittex_contract=bnb_testnet.bittex_contract, available_tokens=bnb_testnet.available_tokens, is_testnet=bnb_testnet.is_testnet)

        w3 = evm.web3_provider

        # Load the contract ABI and address
        contract_address = '0x123456789ABCDEF...'
        contract_abi = [
            # Add your contract ABI here
            # Example: {'constant': False, 'inputs': [{'name': 'inputToken', 'type': 'address'}, ...], 'name': 'swapTokens', 'outputs': [{'name': 'swapId', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}
        ]

        contract = w3.eth.contract(address=contract_address, abi=contract_abi)

        # Input parameters
        input_token = 'ETH'
        input_address = '0x1234'
        output_token = 'USDT'
        output_address = '0x5678'
        input_amount = 100

        # Call the smart contract function for token swapping
        tx_hash = contract.functions.swap_tokens(input_address, input_token, output_address, output_token, input_amount).transact()

        # Get the swap ID from the transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        swap_id = tx_receipt['events']['SwapCompleted']['swapId']

        print(f'Swap ID: {swap_id}')
        
    def test_token_transfer(self):
    
        # Connect to an Ethereum node
        bnb_testnet = chains["bnb_test"]
        evm = EvmChain(rpc_url=bnb_testnet.rpc_url, chain_id=bnb_testnet.chain_id, chain_name=bnb_testnet.chain_name, bittex_contract=bnb_testnet.bittex_contract, available_tokens=bnb_testnet.available_tokens, is_testnet=bnb_testnet.is_testnet)

        w3 = evm.web3_provider

        # Load the contract ABI and address
        contract_address = '0x123456789ABCDEF...'
        contract_abi = [
            # Add your contract ABI here
            # Example: {'constant': False, 'inputs': [{'name': 'inputToken', 'type': 'address'}, ...], 'name': 'swapTokens', 'outputs': [{'name': 'swapId', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}
        ]

        contract = w3.eth.contract(address=contract_address, abi=contract_abi)

        # Input parameters
        input_token = 'ETH'
        input_address = '0x1234'
        output_token = 'USDT'
        output_address = '0x5678'
        input_amount = 100

        # Call the smart contract function for token swapping
        tx_hash = contract.functions.swap_tokens(input_address, input_token, output_address, output_token, input_amount).transact()

        # Get the swap ID from the transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        swap_id = tx_receipt['events']['SwapCompleted']['swapId']

        print(f'Swap ID: {swap_id}')

    def test_get_transaction_info(self):

        bnb_testnet = chains["bnb_test"]
        evm = EvmChain(rpc_url=bnb_testnet.rpc_url, chain_id=bnb_testnet.chain_id, chain_name=bnb_testnet.chain_name, bittex_contract=bnb_testnet.bittex_contract, available_tokens=bnb_testnet.available_tokens, is_testnet=bnb_testnet.is_testnet)

        w3 = evm.web3_provider

        # Load the contract ABI and address
        contract_address = '0x123456789ABCDEF...'
        contract_abi = [
            # Add your contract ABI here
            # Example: {'constant': False, 'inputs': [{'name': 'inputToken', 'type': 'address'}, ...], 'name': 'swapTokens', 'outputs': [{'name': 'swapId', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}
        ]

        contract = w3.eth.contract(address=contract_address, abi=contract_abi)

        trx_hash = '0x'
        trx = w3.eth.get_transaction(trx_hash) # This only means you sent the transaction. It does not mean it succeeded.
        trx_block_number = trx.blockNumber
        trx_unix_ts = w3.eth.get_block(trx_block_number).timestamp
        status : int = -1
        while True:
            try:
                '''
                https://web3py.readthedocs.io/en/stable/web3.eth.html#methods
                Returns the transaction receipt specified by transaction_hash. If the transaction has not yet been mined throws web3.exceptions.TransactionNotFound.
                If status in response equals 1 the transaction was successful. If it is equals 0 the transaction was reverted by EVM.
                '''
                trx_receipt = w3.eth.get_transaction_receipt(trx_hash)
                status = trx_receipt['status']
                if status == 0 or status == 1:
                    logs_summary = []

                    logs = contract.events.Transfer().process_receipt(trx_receipt, EventLogErrorFlags.Warn)
                    for log in logs:
                        transaction_type = log.event
                        sender_address = log.args['from']
                        destination_address = log.args['to']
                        amount = log.args['value']

                        logs_summary.append( {
                            'transaction_type' : transaction_type,
                            'sender_address' : sender_address,
                            'destination_address' : destination_address,
                            'amount' : amount
                        })

                    gas_used_in_units = trx_receipt['gasUsed']
                    gas_price = w3.eth.gas_price
                    gas_used_in_wei = gas_used_in_units * gas_price
                    gas_used_in_coin = gas_used_in_wei / (evm.available_tokens[0].decimals * evm.available_tokens[0].decimals)
                    break
            except TransactionNotFound:
                # Transaction not found!
                pass

        trx_status : str = "Pending"
        if status==1:
            trx_status = "Confirmmed"
        elif status==0:
            trx_status = "Reverted"

        transaction_report : Dict = {
            'trx_hash' : trx_hash,
            'trx_block_number'  : trx.blockNumber,
            'status' : trx_status,
            'trx_unix_ts' : trx_unix_ts,
            'gas' : {
                'gas_used_in_units' : gas_used_in_units,
                'gas_price' : gas_price,
                'gas_used_in_wei' : gas_used_in_wei,
                'gas_used_in_coin' : gas_used_in_coin # this is ETH on Ethereum
            },
            'logs' : logs_summary
        }

        print(transaction_report)

if __name__ == '__main__':
    unittest.main()
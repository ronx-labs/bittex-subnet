import unittest
import os

from web3 import Web3

from exchangenet.shared.blockchain.chains import chains
from exchangenet.shared.blockchain.evm import Swap, ZERO_ADDRESS


class TestEvm(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_sign_verify_message(self):
        bnb_test_chain = chains['bnb_test']

        # Test Case 1
        private_key = bytes.fromhex('5a01713ebfe789aa1a32bd5df9fce8f7e726adcfdf669aa778cd53e9f7ebb7c3')
        public_address = bytes.fromhex('97EA56126d8c67168F01989f101F7282b07417Ba')
        
        signature = bnb_test_chain.sign_message('Random message', private_key)
        is_valid = bnb_test_chain.verify_signature('Random message', signature, public_address)
        self.assertEqual(is_valid, True)

        # Test Case 2
        private_key = bytes.fromhex('5a01713ebfe789aa1a32bd5df9fce8f7e726adcfdf669aa778cd53e9f7ebb7c3')
        public_address = bytes.fromhex('97EA56126d8c67168F01989f101F7282b07417B6')
        
        signature = bnb_test_chain.sign_message('Random message', private_key)
        is_valid = bnb_test_chain.verify_signature('Random message', signature, public_address)
        self.assertEqual(is_valid, False)
        
    def test_create_swap(self):
        bnb_test_chain = chains['bnb_test']
        weth_token_address = Web3.to_checksum_address(bnb_test_chain.get_token_by_symbol('WETH').address)
        usdt_token_address = Web3.to_checksum_address(bnb_test_chain.get_token_by_symbol('USDT').address)
        amount = 100
        account_address = Web3.to_checksum_address('0x97EA56126d8c67168F01989f101F7282b07417Ba')
        private_key = '5a01713ebfe789aa1a32bd5df9fce8f7e726adcfdf669aa778cd53e9f7ebb7c3'
        
        # Create swap
        swap_id = bnb_test_chain.create_swap(weth_token_address, usdt_token_address, amount, account_address, private_key);
        # Get swap info
        swap = bnb_test_chain.get_swap(swap_id)
        # Assert equal
        expected_swap = Swap(
            swap_id=swap_id,
            input_token_address=weth_token_address,
            output_token_address=usdt_token_address,
            top_bidders=[ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS],
            winner=ZERO_ADDRESS,
            amount=amount,
            timestamp=swap.timestamp
        )
        self.assertDictEqual(swap.__dict__, expected_swap.__dict__)
        
    def test_make_bid(self):
        bnb_test_chain = chains['bnb_test']
        weth_token_address = Web3.to_checksum_address(bnb_test_chain.get_token_by_symbol('WETH').address)
        usdt_token_address = Web3.to_checksum_address(bnb_test_chain.get_token_by_symbol('USDT').address)
        amount = 10 ** 15
        expected_bid_amount = 10 ** 14 * 2
        account_address = Web3.to_checksum_address('0x97EA56126d8c67168F01989f101F7282b07417Ba')
        private_key = '5a01713ebfe789aa1a32bd5df9fce8f7e726adcfdf669aa778cd53e9f7ebb7c3'
        
        # Create swap
        swap_id = bnb_test_chain.create_swap(weth_token_address, usdt_token_address, amount, account_address, private_key)
        # Make bid
        bnb_test_chain.make_bid(swap_id, expected_bid_amount, account_address, private_key)
        # Try to make bid again from the same account
        bnb_test_chain.make_bid(swap_id, expected_bid_amount * 2, account_address, private_key)
        # Assert equal
        bid_amount = bnb_test_chain.get_bid_amount(swap_id, account_address)
        self.assertEqual(bid_amount, expected_bid_amount)

if __name__ == '__main__':
    unittest.main()

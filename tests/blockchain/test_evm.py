import unittest
import os

from web3 import Web3

from exchangenet.shared.blockchain.chains import chains
from exchangenet.shared.blockchain.evm import Swap, ZERO_ADDRESS


class TestEvm(unittest.TestCase):
    def setUp(self) -> None:
        self.bnb_test_chain = chains['bnb_test']
        self.weth_token_address = Web3.to_checksum_address(self.bnb_test_chain.get_token_by_symbol('WETH').address)
        self.usdt_token_address = Web3.to_checksum_address(self.bnb_test_chain.get_token_by_symbol('USDT').address)
        self.account_address = Web3.to_checksum_address('0x97EA56126d8c67168F01989f101F7282b07417Ba')
        self.private_key = '5a01713ebfe789aa1a32bd5df9fce8f7e726adcfdf669aa778cd53e9f7ebb7c3'
        self.account_address2 = Web3.to_checksum_address('0x4e080B50da7238e2Ff653BB562E1B8186B5A58A0')
        self.private_key2 = 'a5a74c43f8b65afaf705479b30cbd397e02b8f8eb1a31ebc50970a005b9421ef'

    def test_sign_verify_message(self):
        # Test Case 1
        signature = self.bnb_test_chain.sign_message('Random message', bytes.fromhex(self.private_key))
        is_valid = self.bnb_test_chain.verify_signature('Random message', signature, bytes.fromhex(self.account_address[2:]))
        self.assertEqual(is_valid, True)

        # Test Case 2        
        signature = self.bnb_test_chain.sign_message('Random message', bytes.fromhex(self.private_key))
        is_valid = self.bnb_test_chain.verify_signature('Random message', signature, bytes.fromhex(self.account_address2[2:]))
        self.assertEqual(is_valid, False)
        
    def test_create_swap(self):
        amount = 10 ** 14 * 2
        
        # Create swap
        swap_id = self.bnb_test_chain.create_swap(self.weth_token_address, self.usdt_token_address, amount, self.account_address, self.private_key);
        # Get swap info
        swap = self.bnb_test_chain.get_swap(swap_id)
        # Assert equal
        expected_swap = Swap(
            swap_id=swap_id,
            input_token_address=self.weth_token_address,
            output_token_address=self.usdt_token_address,
            top_bidders=[ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS],
            winner=ZERO_ADDRESS,
            amount=amount,
            timestamp=swap.timestamp
        )
        self.assertDictEqual(swap.__dict__, expected_swap.__dict__)
        
    def test_make_bid(self):
        amount = 10 ** 14 * 3
        expected_bid_amount = 10 ** 15 * 4
        
        # Create swap
        swap_id = self.bnb_test_chain.create_swap(self.weth_token_address, self.usdt_token_address, amount, self.account_address, self.private_key)
        # Make bid
        self.bnb_test_chain.make_bid(swap_id, expected_bid_amount, self.account_address, self.private_key)
        # Try to make bid again from the same account
        self.bnb_test_chain.make_bid(swap_id, expected_bid_amount * 2, self.account_address, self.private_key)
        # Assert equal
        bid_amount = self.bnb_test_chain.get_bid_amount(swap_id, self.account_address)
        self.assertEqual(bid_amount, expected_bid_amount)
        
    def test_finalize_swap(self):
        amount = 10 ** 14 * 6
        expected_bid_amount = 10 ** 15 * 7
        
        # Create swap
        swap_id = self.bnb_test_chain.create_swap(self.weth_token_address, self.usdt_token_address, amount, self.account_address, self.private_key)
        # Make bid
        self.bnb_test_chain.make_bid(swap_id, expected_bid_amount, self.account_address2, self.private_key2)
        # Finalize swap
        self.bnb_test_chain.finalize_swap(swap_id, self.account_address, self.private_key)
        # Assert equal
        winner = self.bnb_test_chain.get_winner(swap_id)
        self.assertEqual(winner, self.account_address2)

if __name__ == '__main__':
    unittest.main()

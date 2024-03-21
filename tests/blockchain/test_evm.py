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
        from_address = Web3.to_checksum_address('0x337610d27c682e347c9cd60bd4b3b107c9d34ddd')
        to_address = Web3.to_checksum_address('0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd')
        amount = 100
        account_address = Web3.to_checksum_address('0x97EA56126d8c67168F01989f101F7282b07417Ba')
        private_key = '5a01713ebfe789aa1a32bd5df9fce8f7e726adcfdf669aa778cd53e9f7ebb7c3'
        
        # Create swap
        swap_id = bnb_test_chain.create_swap(from_address, to_address, amount, account_address, private_key);
        # Get swap info
        swap = bnb_test_chain.get_swap(swap_id)
        # Assert equal
        expected_swap = Swap(
            swap_id=swap_id,
            input_token_address=from_address,
            output_token_address=to_address,
            top_bidders=[ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS],
            winner=ZERO_ADDRESS,
            amount=amount,
            timestamp=swap.timestamp
        )
        self.assertDictEqual(swap.__dict__, expected_swap.__dict__)

if __name__ == '__main__':
    unittest.main()

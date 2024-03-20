import unittest
import os

from exchangenet.shared.blockchain.chains import chains


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


if __name__ == '__main__':
    unittest.main()

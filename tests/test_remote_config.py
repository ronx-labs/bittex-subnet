import unittest
import os
from exchangenet.shared.remote_config import MinerConfig, ValidatorConfig

class TestConfigurations(unittest.TestCase):

    def test_miner_config_load_and_values(self):
        # Create an instance of MinerConfig
        miner_config = MinerConfig()
        miner_config.load_and_get_config_values()

        # Check if the configuration values are as expected
        self.assertIsNotNone(miner_config.blacklisted_hotkeys)
        self.assertIsInstance(miner_config.blacklisted_hotkeys, list)
        self.assertIsNotNone(miner_config.whitelisted_hotkeys)
        self.assertIsInstance(miner_config.whitelisted_hotkeys, list)

    def test_validator_config_load_and_values(self):
        # Create an instance of ValidatorConfig
        validator_config = ValidatorConfig()
        validator_config.load_and_get_config_values()

        # Check if the configuration values are as expected
        self.assertIsNotNone(validator_config.example)
        self.assertIsInstance(validator_config.example, int)

    def tearDown(self):
        # Clean up any files created or modified during the tests
        if os.path.exists("miner.json"):
            pass #os.remove("miner.json")
        if os.path.exists("validator.json"):
            pass #os.remove("validator.json")

if __name__ == '__main__':
    unittest.main()
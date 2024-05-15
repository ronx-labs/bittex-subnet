import os
import time
import json
import requests
import bittensor as bt
import threading
# Constants for configuration URLs

UPDATE_INTERVAL = 3600  # Time interval for updating configuration in seconds
MAX_RETRIES = 10
RETRY_INTERVAL = 5


class RemoteConfig:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(RemoteConfig, cls).__new__(cls)
        return cls._instances[cls]

    def __init__(self):
        self.config_cache = None
        self.last_update_time = 0
        self.config_url = None
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._update_config_periodically)
        self.thread.daemon = True
        self.thread.start()

    def dump_values(self):
        attributes = {attr: getattr(self, attr) for attr in dir(self) if not attr.startswith('__') and not callable(getattr(self, attr))}
        return attributes

    def _update_config_periodically(self):
        time.sleep(UPDATE_INTERVAL)
        while not self.stop_event.is_set():
            self.load_remote_config()
            time.sleep(UPDATE_INTERVAL)

    def load_remote_config(self):
        if self.config_url is None:
            return

        current_time = time.time()
        if current_time - self.last_update_time >= UPDATE_INTERVAL or self.config_cache is None:
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    response = requests.get(self.config_url, timeout=10)
                    response.raise_for_status()
                    self.config_cache = response.json()

                    file_name = os.path.basename(self.config_url)
                    dir_path = os.path.dirname(os.path.abspath(__file__))
                    file_path = os.path.join(dir_path, file_name)
                    with open(file_path, 'w') as file:
                        json.dump(self.config_cache, file)

                    self.last_update_time = current_time
                    bt.logging.success(f"Updated config from {self.config_url}")
                    break  # Break the loop if successful
                except requests.exceptions.RequestException as e:
                    retries += 1
                    bt.logging.error(f"Attempt {retries} failed to update config from {self.config_url}: {e}")
                    if retries < MAX_RETRIES:
                        time.sleep(RETRY_INTERVAL)
                except Exception as e:
                    bt.logging.error(f"Non-retryable error occurred: {e}")
                    break

    def get_config_value(self, key, default=None):
        if self.config_cache:
            keys = key.split('.') if '.' in key else [key]
            value = self.config_cache
            for k in keys:
                if k in value:
                    value = value[k]
                else:
                    return default
            return value
        return default

    def stop_update_thread(self):
        self.stop_event.set()
        self.thread.join()


class MinerConfig(RemoteConfig):
    def __init__(self):
        super().__init__()
        
        # URL for the remote configuration
        self.config_url = os.getenv("MINER_REMOTE_CONFIG_URL", 'https://exchangenet.s3.us-east-2.amazonaws.com/miner_config.json')

        self.whitelisted_hotkeys = None
        self.blacklisted_hotkeys = None

    def load_and_get_config_values(self):
        # Load remote configuration
        self.load_remote_config()

        self.blacklisted_hotkeys = self.get_config_value('blacklisted_hotkeys', ["5GcBK8PDrVifV1xAf4Qkkk6KsbsmhDdX9atvk8vyKU8xdU63"])
        self.whitelisted_hotkeys = self.get_config_value('whitelisted_hotkeys', ["5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"])
        
        return self
    
    def get_config_variable(self): # this is a dummy method for retrieving a config variable
        return self.get_config_value(f'An example config variable.', 1000)


class ValidatorConfig(RemoteConfig):
    def __init__(self):
        super().__init__()

        # URL for the remote configuration
        self.config_url = os.getenv("VALIDATOR_REMOTE_CONFIG_URL", 'https://exchangenet.s3.us-east-2.amazonaws.com/validator_config.json')
        self.app_hotkey = self.get_config_value('app_hotkey', "5DjuugH43nbGCs6LrEVjxXqZVezTQQk5adZTbmvAv9KhG6dP")
        self.total_reward_weight = self.get_config_value('total_reward_factor', 0.1)
        self.weekly_reward_weight = self.get_config_value('weekly_reward_factor', 0.05)
        self.top_bidder_reward_rate = self.get_config_value('top_bidder_reward_rate', 1.5)
        self.winner_reward_rate = self.get_config_value('winner_reward_rate', 2.0)

        self.example = None
        self.challenge_timeout = None
        
    def load_and_get_config_values(self):
        self.load_remote_config()

        # Retrieve specific configuration values
        self.example = self.get_config_value('example_variable', 1)
        self.challenge_timeout = self.get_config_value('challenge_timeout', 100)
        
        return self

    def get_config_variable(self): # this is a dummy method for retrieving a config variable
        return self.get_config_value(f'An example config variable.', 1000)

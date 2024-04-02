import bittensor as bt
from abc import ABC, abstractmethod
from uniswap import Uniswap

import os
from dotenv import load_dotenv


class BaseMinerUtil(ABC):
    """
    Base class for Bittensor miners.

    This class is abstract and should be inherited by a subclass.
    It contains the core logic for customizing conditions and workflow for making a transaction.

    Miners are encouraged to override the methods within this class to tailor the functionality to their specific needs. For instance, miners can implement their own strategies such as purchasing assets and withdrawing them from a CEX platform when tokens are insufficient, or dynamically adjusting bid amounts based on quote values. 
    """

    def __init__(self):
        load_dotenv()
        bt.logging.info("Initializing miner utils...")

    @abstractmethod
    def adjust_bid_amount(self, *args, **kwargs):
        """
        Adjust the bid amount based on the quote amount.

        Args can be included:
            input_token (str): The input token.
            output_token (str): The output token.
            amount (int): The amount to be adjusted.
            provider (str): The provider to be used.

        """
        bt.logging.info("Adjusting bid amount...")

    @abstractmethod
    def check_balance(self, *args, **kwargs):
        """
        Check the balance of the token.

        Args can be included:
            token (str): The token to be checked.
            amount (int): The amount to be checked.
            provider (str): The provider to be used.

        """
        bt.logging.info("Checking balance...")

    @abstractmethod
    def search_tokens(self, *args, **kwargs):
        """
        Search for the token.

        Args can be included:
            token (str): The token to be searched.
            provider (str): The provider to be used.

        """
        bt.logging.info("Searching tokens...")

    @abstractmethod
    def purchase_assets(self, *args, **kwargs) -> bool:
        """
        Purchase assets.

        Args can be included:
            token (str): The token to be purchased.
            amount (int): The amount to be purchased.
            provider (str): The provider to be used.

        """
        bt.logging.info("Purchasing assets...")

    
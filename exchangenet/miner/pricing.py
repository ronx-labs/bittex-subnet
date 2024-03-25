import os

from uniswap import Uniswap
from dotenv import load_dotenv


def get_output_amount(input_token: str, output_token: str, amount: int, provider: str):
    uniswap = Uniswap(None, None, version=2, provider=provider)
    return uniswap.get_price_input(input_token, output_token, amount)

def adjust_bid_amount(input_token: str, output_token: str, amount: int, provider: str):
    quote_amount = get_output_amount(input_token, output_token, amount, provider)
    load_dotenv()
        
    # A miner can adjust the bid amount based on the quote amount
    # Any logic can be implemented here
    adjustment_factor = os.getenv("ADJUSTMENT_FACTOR")
    bid_amount = int(quote_amount * adjustment_factor)
    
    return bid_amount
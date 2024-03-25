from uniswap import Uniswap

def get_output_amount(input_token: str, output_token: str, amount: int, provider: str):
    uniswap = Uniswap(None, None, version=2, provider=provider)
    return uniswap.get_price_input(input_token, output_token, amount)

def adjust_bid_amount(input_token: str, output_token: str, amount: int, provider: str):
    quote_amount = get_output_amount(input_token, output_token, amount, provider)
    
    # A miner can adjust the bid amount based on the quote amount
    # Any logic can be implemented here
    bid_amount = int(quote_amount * 1.05)
    
    return bid_amount
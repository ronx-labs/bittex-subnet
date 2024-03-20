# The MIT License (MIT)
# Copyright © 2024 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import bittensor as bt
from exchangenet.validator.get_info import get_deposit_info

def calculate_score(deposit_info: dict) -> float:
    """
    Calculate the score of the miner based on the deposit information.

    Args:
    - deposit_info (dict): A dictionary containing the deposit information.

    Returns:
    - float: The score of the miner.
    """

    score = deposit_info["deposit_amount"] / 100

    return score

def set_weights(self, deposit_info: dict):
    """
    Set the weights of the miner based on the deposit information.

    Args:
    - deposit_info (dict): A dictionary containing the deposit information.
    """

    score = calculate_score(deposit_info)

    self.weights = score

    bt.logging.info(f"Set weights: {self.weights}")

    return self.weights
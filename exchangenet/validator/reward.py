# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

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

import torch
from typing import List

import bittensor as bt

from exchangenet.protocol import SwapRequest, SwapNotification
from exchangenet.shared.blockchain.chains import chains

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


def reward(query: SwapRequest, response: SwapNotification) -> float:
    # Get swap_id and account_address from the query and response
    swap_id = bytes.fromhex(query.swap_id)
    account_address = response.output[0]
    encrypted_swap_id = response.output[1]
    
    # Get swap information from the chain
    bnb_test_chain = chains['bnb_test']
    bid_amount = bnb_test_chain.get_bid_amount(swap_id)
    isVerified = bnb_test_chain.verify_swap(swap_id, encrypted_swap_id, bytes.fromhex(account_address))
    winner = str(bnb_test_chain.get_winner(swap_id))

    if isVerified:
        if account_address == winner:
            return bid_amount / 50
        return bid_amount / 100
    
    return 0


def get_rewards(
    self,
    query: SwapRequest,
    responses: List[SwapNotification],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given query and responses.

    Args:
    - query (int): The query sent to the miner.
    - responses (List[float]): A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given query and responses.
    """
    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(
        [reward(query, response) for response in responses]
    ).to(self.device)

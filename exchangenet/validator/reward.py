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
import bittensor as bt
import base64
import os

from typing import List, Tuple

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


def reward(self, swap_id: bytes, info: Tuple[int, str, str]) -> float:
    # Get account_address and encrypted_swap_id rom the query and response
    account_address = info[1]
    encrypted_swap_id = info[2]
    encrypted_swap_id = base64.b64decode(encrypted_swap_id)

    # Verify the account address
    chain_name = self.swap_id_chain[swap_id]
    chain = chains[chain_name]
    is_verified = chain.verify_signature(chain.web3.to_hex(swap_id), encrypted_swap_id, bytes.fromhex(account_address[2:]))

    if not is_verified:
        return 0.0

    # Get the bid amount and winner of the swap
    bid_amount = chain.get_bid_amount(swap_id, account_address)
    winner = chain.get_winner(swap_id)
    
    bt.logging.info(f"Winner: {winner}")

    return bid_amount * self.config.neuron.winner_reward_rate if account_address == winner else bid_amount

def get_rewards(
    self,
    swap_id: bytes,
    sign_info_list: List[Tuple[int, str, str]]
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
        [reward(self, swap_id, sign_info) for sign_info in sign_info_list if sign_info[0] >= 0]
    ).to(self.device)

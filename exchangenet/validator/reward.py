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


def get_total_reward_factor(self, uids: List[int], uid: int) -> float:
    # Get the hotkey address of miner
    hotkey_address = self.metagraph.hotkeys[uid]
    hotkey_address_list = [self.metagraph.hotkeys[uid] for uid in uids]
    uid_count = len(uids)
    if uid_count == 0:
        return 0.0

    # Get the total transaction count and amount of the miner
    total_transaction_count = int(self.loop.run_until_complete(self.storage.retrieve_total_stats(hotkey_address, "total_transaction_count")))
    total_transaction_amount = int(self.loop.run_until_complete(self.storage.retrieve_total_stats(hotkey_address, "total_transaction_amount")))

    # Get the total transaction count and amount of all the miners
    total_transaction_counts = [int(self.loop.run_until_complete(self.storage.retrieve_total_stats(hotkey_address, "total_transaction_count"))) 
                                for hotkey_address in hotkey_address_list]
    total_transaction_amounts = [int(self.loop.run_until_complete(self.storage.retrieve_total_stats(hotkey_address, "total_transaction_amount"))) 
                                 for hotkey_address in hotkey_address_list]

    # Get the rank of the miner based on the total transaction count and amount
    count_rank = sorted(total_transaction_amounts).index(total_transaction_amount)
    amount_rank = sorted(total_transaction_counts).index(total_transaction_count)

    # Calculate the total reward factor based on the rank
    total_reward_factor = self.total_reward_weight * (count_rank + amount_rank) / uid_count
    return total_reward_factor

def get_weekly_reward_factor(self, uids: List[int], uid: int) -> float:
    # Get the hotkey address of miner
    hotkey_address = self.metagraph.hotkeys[uid]
    hotkey_address_list = [self.metagraph.hotkeys[uid] for uid in uids]
    uid_count = len(uids)
    if uid_count == 0:
        return 0.0

    # Get the weekly transaction count and amount of the miner
    transaction_count_queue = self.loop.run_until_complete(self.storage.retrieve_weekly_stats(hotkey_address, "weekly_transaction_count"))
    weekly_transaction_count = sum(int(next(iter(dict.values()))) for dict in transaction_count_queue)
    transaction_amount_queue = self.loop.run_until_complete(self.storage.retrieve_weekly_stats(hotkey_address, "weekly_transaction_amount"))
    weekly_transaction_amount = sum(int(next(iter(dict.values()))) for dict in transaction_amount_queue)

    # Get the weekly transaction count and amount of all the miners
    transaction_count_queues = [self.loop.run_until_complete(self.storage.retrieve_weekly_stats(hotkey_address, "weekly_transaction_count"))
                                for hotkey_address in hotkey_address_list]
    weekly_transaction_counts = [sum(int(next(iter(dict.values()))) for dict in transaction_count_queue) for transaction_count_queue in transaction_count_queues]
    transaction_amount_queues = [self.loop.run_until_complete(self.storage.retrieve_weekly_stats(hotkey_address, "weekly_transaction_amount"))
                                 for hotkey_address in hotkey_address_list]
    weekly_transaction_amounts = [sum(int(next(iter(dict.values()))) for dict in transaction_amount_queue) for transaction_amount_queue in transaction_amount_queues]

    # Get the rank of the miner based on the weekly transaction count and amount
    count_rank = sorted(weekly_transaction_amounts).index(weekly_transaction_amount)
    amount_rank = sorted(weekly_transaction_counts).index(weekly_transaction_count)

    # Calculate the weekly reward factor based on the rank
    weekly_reward_factor = self.weekly_reward_weight * (count_rank + amount_rank) / uid_count
    return weekly_reward_factor

def reward(self, swap_id: bytes, info: Tuple[int, str, str], uids: List[int]) -> float:
    # Get account_address and encrypted_swap_id rom the query and response
    uid = info[0]
    account_address = info[1]
    encrypted_swap_id = info[2]
    encrypted_swap_id = base64.b64decode(encrypted_swap_id)

    # Verify the account address
    swap_info = self.loop.run_until_complete(self.storage.retrieve_swap(bytes.hex(swap_id)))
    chain = chains[swap_info["chain_name"]]
    is_verified = chain.verify_signature(chain.web3.to_hex(swap_id), encrypted_swap_id, bytes.fromhex(account_address[2:]))

    if not is_verified:
        return 0.0

    # Get the bid amount and winner of the swap
    base_reward = chain.get_bid_amount(swap_id, account_address)
    winner = chain.get_winner(swap_id)
    
    bt.logging.info(f"Winner: {winner}")
    hotkey = self.loop.run_until_complete(self.storage.retrieve_hotkey(winner))
    bt.logging.info(f"Hotkey: {hotkey}")

    total_reward_factor = get_total_reward_factor(self, uids, uid)
    weekly_reward_factor = get_weekly_reward_factor(self, uids, uid)

    # Calculate the reward based on the total and weekly reward factors
    reward = base_reward * (1 + total_reward_factor + weekly_reward_factor)    

    return reward * self.config.neuron.winner_reward_rate if account_address == winner else reward

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

    # Get the uids of the miners who responded to the query.
    uids = [sign_info[0] for sign_info in sign_info_list if sign_info[0] >= 0]

    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(
        [reward(self, swap_id, sign_info, uids) for sign_info in sign_info_list if sign_info[0] >= 0]
    ).to(self.device)

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

import bittensor as bt
import time
import json

from collections import deque
from datetime import datetime, timedelta

from exchangenet.validator.reward import get_rewards
from exchangenet.shared.blockchain.chains import chains
from exchangenet.shared.blockchain.evm import ZERO_ADDRESS
from exchangenet.miner.pricing import get_output_amount


async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    # Log the start time for monitoring purposes.
    start_time = time.time()

    # Retrieve all the swap_ids from the swap pool.
    swaps = self.loop.run_until_complete(self.storage.retrieve_swaps())

    for swap in swaps:
        try:
            bt.logging.debug(f"Swap: {swap}")
            swap_info = await self.storage.retrieve_swap(swap)
            
            swap_id = bytes.fromhex(swap)
            bt.logging.info(f"Checking a swap with swap_id {swap_id}: ")
            bt.logging.debug(f"Swap info: {swap_info['chain_name']}")
            bt.logging.debug(f"Swap info: {swap_info['sign_info_list']}")
            
            chain = chains[swap_info["chain_name"]]
            if chain.is_finalized(swap_id) or chain.is_expired(swap_id):
                winner = chain.get_winner(swap_id)
                if winner != ZERO_ADDRESS:
                    # Get the hotkey for the swap_id.
                    hotkey = await self.storage.retrieve_hotkey(winner)

                    # Get the transaction amount converted to USDT.
                    usdt_address = chain.web3.to_checksum_address(chain.get_token_by_symbol("USDT").address)
                    output_token_address = chain.web3.to_checksum_address(chain.get_swap(swap_id).output_token_address)
                    bid_amount = chain.get_bid_amount(swap_id, winner)
                    transaction_amount = get_output_amount(output_token_address, usdt_address, bid_amount, chain.rpc_url)

                    # Get the current date.
                    current_date = datetime.now().date().toordinal()

                    # Update the transaction count and amount for the hotkey.
                    total_transaction_count = await self.storage.retrieve_total_stats(hotkey, 'total_transaction_count')
                    total_transaction_amount = await self.storage.retrieve_total_stats(hotkey, 'total_transaction_amount')
                    weekly_transaction_count = await self.storage.retrieve_weekly_stats(hotkey, 'weekly_transaction_count')
                    weekly_transaction_amount = await self.storage.retrieve_weekly_stats(hotkey, 'weekly_transaction_amount')

                    total_transaction_count = int(total_transaction_count) + 1
                    total_transaction_amount = int(total_transaction_amount) + transaction_amount
 
                    if current_date - int(list(weekly_transaction_count[0].keys())[0]) > 7:
                        weekly_transaction_count.popleft()
                        weekly_transaction_count.append({current_date: 1})
                    else:
                        if int(list(weekly_transaction_count[-1].keys())[0]) == current_date:
                            weekly_transaction_count[-1][current_date] = int(weekly_transaction_count[-1][current_date]) + 1
                        else:
                            weekly_transaction_count.append({current_date: 1})

                    if current_date - int(list(weekly_transaction_amount[0].keys())[0]) > 7:
                        weekly_transaction_amount.popleft()
                        weekly_transaction_amount.append({current_date: transaction_amount})
                    else:
                        if int(list(weekly_transaction_amount[-1].keys())[0]) == current_date:
                            weekly_transaction_amount[-1][current_date] = int(weekly_transaction_amount[-1][current_date]) + transaction_amount
                        else:
                            weekly_transaction_amount.append({current_date: transaction_amount})

                    # Store the updated transaction count and amount in the validator storage.
                    self.loop.run_until_complete(self.storage.store_total_stats(hotkey, 'total_transaction_count', total_transaction_count))
                    self.loop.run_until_complete(self.storage.store_total_stats(hotkey, 'total_transaction_amount', total_transaction_amount))  
                    self.loop.run_until_complete(self.storage.store_weekly_stats(hotkey, 'weekly_transaction_count', weekly_transaction_count))
                    self.loop.run_until_complete(self.storage.store_weekly_stats(hotkey, 'weekly_transaction_amount', weekly_transaction_amount))

                # Get swap info from swap_id.
                sign_info_list = swap_info["sign_info_list"]
                bt.logging.debug(f"Sign info list: {sign_info_list}")
                
                # Adjust the scores based on responses from miners.
                rewards = get_rewards(self, swap_id, sign_info_list)
                bt.logging.info(f"Scored responses: {rewards}")
                
                # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
                uids = [sign_info[0] for sign_info in sign_info_list if sign_info[0] >= 0]
                self.update_scores(rewards, uids)

                # Delete the swap_id from the swap pool.
                await self.storage.delete_swap(swap)
            
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            continue
    
    time.sleep(20)

    forward_time = time.time() - start_time
    bt.logging.info(f"Forward time: {forward_time:.2f}s")

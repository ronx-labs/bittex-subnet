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

from exchangenet.validator.reward import get_rewards
from exchangenet.shared.blockchain.chains import chains


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
    swaps = self.loop.run_until_complete(self.storage.get_all_data('validator_swap_pool'))
    for swap in swaps:
        try:
            swap_id = bytes.fromhex(swap)
            bt.logging.info(f"Checking a swap with swap_id {swap_id}: ")

            chain_name = await self.storage.retrieve_data('validator_swap_pool', swap)
            chain = chains[chain_name]
            bt.logging.debug(f"Chain: {chain}")
            if chain.is_finalized(swap_id) or chain.is_expired(swap_id):
                    # Get swap info from swap_id.
                    sign_info_list = await self.storage.retrieve_data(swap, 'response')
                    sign_info_list = json.loads(sign_info_list)
                    bt.logging.debug(f"Sign info list: {sign_info_list}")
                    
                    # Adjust the scores based on responses from miners.
                    rewards = get_rewards(self, swap_id, sign_info_list)
                    bt.logging.info(f"Scored responses: {rewards}")
                    
                    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
                    uids = [sign_info[0] for sign_info in sign_info_list if sign_info[0] >= 0]
                    self.update_scores(rewards, uids)

                    # Delete the swap_id from the swap pool.
                    await self.storage.delete_data('validator_swap_pool', swap)
            
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            continue
    
    time.sleep(20)

    forward_time = time.time() - start_time
    bt.logging.info(f"Forward time: {forward_time:.2f}s")

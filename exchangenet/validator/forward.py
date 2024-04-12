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

from exchangenet.protocol import SwapRequest, SwapNotification
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

    # Log the results for monitoring purposes.
    # bt.logging.info(f"Received responses: {responses}")

    async for swap_id in self.database.scan_iter("*"):
        bt.logging.info(f"Checking a swap with swap_id {swap_id}: ")
        chain = chains[self.swap_id_chain[swap_id]]
        if chain.is_finalized(swap_id) or chain.is_expired(swap_id):
            # Get swap info from swap_id.
            serialized_data = self.database.get(swap_id)
            sign_info_list = json.loads(serialized_data)
            
            # Adjust the scores based on responses from miners.
            rewards = get_rewards(self, swap_id, sign_info_list)
            bt.logging.info(f"Scored responses: {rewards}")
            
            # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
            uids = [sign_info[0] for sign_info in sign_info_list if sign_info[0] >= 0]
            self.update_scores(rewards, uids)

            # Delete the swap from the database.
            self.database.delete(swap_id)
    
    time.sleep(5)

    forward_time = time.time() - start_time
    bt.logging.info(f"Forward time: {forward_time:.2f}s")

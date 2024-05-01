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


import time
import typing

# Bittensor
import bittensor as bt

import exchangenet
from exchangenet.validator import forward
from exchangenet.base.validator import BaseValidatorNeuron
from exchangenet.utils.uids import get_available_uids
from exchangenet.protocol import SwapRequest, SwapNotification, Pricing
from exchangenet.shared.remote_config import ValidatorConfig
from exchangenet.validator.storage import ValidatorStorage



class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)
        self.remote_config = ValidatorConfig().load_and_get_config_values()

        bt.logging.info("load_state()")
        self.load_state()
        
        self.storage = ValidatorStorage()

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        # TODO(developer): Rewrite this function based on your protocol definition.
        return await forward(self)

    async def swap_request(self, query: SwapRequest) -> SwapRequest:
        """
        The swap_request function is called by the validator every time swap requests are received.
        It sends the swap notification to the miners 

        Args:
            synapse (exchangenet.protocol.SwapRequest): The incoming swap request.
        """
            
        # TODO(developer): Define how the validator selects a miner to query, how often, etc.
        # get_random_uids is an example method, but you can replace it with your own.
        miner_uids = get_available_uids(self)
        bt.logging.info(f"Selected miners: {miner_uids}")

        # The dendrite client queries the network.
        responses = await self.dendrite(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            # Construct a query based on swapId.
            synapse=SwapNotification(chain_name=query.chain_name, swap_id=query.swap_id),
            # All responses have the deserialize function called on them before returning.
            # You are encouraged to define your own deserialization function.
            deserialize=True
        )

        sign_info_list = []

        for response in responses:
            # Store the responses to use in the reward function.
            sign_info_list.append(response.output)

            # Store the hotkey of the miner along with the account address of the miner to use in the reward function.
            miner_hotkey = self.metagraph.hotkeys[response.output[0]]
            miner_account_address = response.output[1]
            self.loop.run_until_complete(self.storage.store_hotkey(miner_account_address, miner_hotkey))

            # Log the responses for monitoring purposes.
            bt.logging.info(f"response: {response}")
            bt.logging.debug(f"sign_info_list: {sign_info_list}")
        
        swap_info = {
            "chain_name": query.chain_name,
            "sign_info_list": sign_info_list
        }

        self.loop.run_until_complete(self.storage.store_swap(query.swap_id[2:], swap_info))
        query.output = True           
        return query

    async def swap_discovery(self, query: Pricing) -> Pricing:
        """
        The swap_discovery function is called by the validator every time swap discovery requests are received.
        It sends the swap discovery notification to the miners.

        Args:
            synapse (exchangenet.protocol.Pricing): The incoming swap discovery request.
        """
        # TODO(developer): Define how the validator selects a miner to query, how often, etc.
        # get_random_uids is an example method, but you can replace it with your own.
        miner_uids = get_available_uids(self)
        bt.logging.info(f"Selected miners: {miner_uids}")

        # The dendrite client queries the network.
        responses = await self.dendrite(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            # Construct a query based on swapId.
            synapse=Pricing(input_token=query.input_token, output_token=query.output_token, amount=query.amount, output=query.output, network=query.network),
            # All responses have the deserialize function called on them before returning.
            # You are encouraged to define your own deserialization function.
            deserialize=True
        )

        pricing_list = []

        for response in responses:
            # Log the responses for monitoring purposes.
            bt.logging.info(f"response: {response}")

            pricing_list.append(response.output)
        pricing_list.sort()
        query.output = pricing_list[-1]
        return query

    async def swap_request_blacklist(
        self, synapse: exchangenet.protocol.SwapRequest
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (exchangenet.protocol.SwapRequest): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        # TODO(developer): Define how miners should blacklist requests.
        if synapse.dendrite.hotkey == self.remote_config.app_hotkey:
            return False, "Hotkey recognized!"
        else:
            return True, "Unrecognized hotkey"

    
    async def swap_request_priority(self, synapse: exchangenet.protocol.SwapRequest) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (exchangenet.protocol.SwapRequest): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        # TODO(developer): Define how miners should prioritize requests.
        priority = 1
        if synapse.dendrite.hotkey == self.remote_config.app_hotkey:
            priority = 1000
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", priority
        )
        return priority

    async def swap_discovery_blacklist(
        self, synapse: exchangenet.protocol.Pricing
    ) -> typing.Tuple[bool, str]:
        """
        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. 

        Args:
            synapse (exchangenet.protocol.Pricing): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.
        """
        if synapse.dendrite.hotkey == self.remote_config.app_hotkey:
            return False, "Hotkey recognized!"
        else:
            return True, "Unrecognized hotkey"

    async def swap_discovery_priority(self, synapse: exchangenet.protocol.Pricing) -> float:
        """
        Args:
            synapse (exchangenet.protocol.Pricing): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.
        """
        priority = 1
        if synapse.dendrite.hotkey == self.remote_config.app_hotkey:
            priority = 1000
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", priority
        )
        return priority


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)

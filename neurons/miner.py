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
import bittensor as bt
import base64

from dotenv import load_dotenv

import exchangenet

from exchangenet.base.miner import BaseMinerNeuron
from exchangenet.shared.blockchain.chains import chains
from exchangenet.miner.pricing import adjust_bid_amount
from exchangenet.miner.storage import MinerStorage


class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)
        load_dotenv()
        self.env_wallet = {
            "address": self.config.wallet.address,
            "private_key": self.config.wallet.private_key
        }

        self.storage = MinerStorage(self.env_wallet["address"])
        # self.loop.run_until_complete(self.storage.delete_swaps())

    async def discovery(
        self, synapse: exchangenet.protocol.Pricing
    ) -> exchangenet.protocol.Pricing:
        """
        Processes the incoming 'Pricing' synapse that contains pricing discovery request.
        A miner receives this synapse when a user wants to swap tokens.
        Then miner quotes the price for the swap and returns the output amount.
        
        Args:
            synapse (exchangenet.protocol.Pricing): The synapse object containing discovery request info.

        Returns:
            exchangenet.protocol.Pricing: The synapse object containing pricing output amount.
        """
        chain = chains[synapse.network]

        # Get the token information from the swap
        input_token_address = chain.web3.to_checksum_address(synapse.input_token)
        output_token_address = chain.web3.to_checksum_address(synapse.output_token)
        
        # Adjust the bid amount
        bid_amount = adjust_bid_amount(input_token_address, output_token_address, synapse.amount, chain.rpc_url)
        bt.logging.info(f"Pricing discovery amount: {bid_amount}")
        
        synapse.output = bid_amount
        
        return synapse

    async def withdraw(self):
        """
        The withdraw function is called by the miner every time step.

        It enables miners withdraw their bids from finalized or expired swaps.

        Args:
            self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the miner.

        """
        swaps = self.loop.run_until_complete(self.storage.retrieve_swaps())
        
        try:
            for swap in swaps:
                chain_name = await self.storage.retrieve_swap(swap)
                chain = chains[chain_name]

                swap_id = bytes.fromhex(swap)

                if chain.get_winner(swap_id) == self.env_wallet["address"]:
                    await self.storage.delete_swap(swap)
                elif (chain.is_finalized(swap_id) or chain.is_expired(swap_id)):
                    try:
                        bt.logging.info(f"Withdrawing bid from swap {swap_id}.")
                        chain.withdraw_bid(swap_id, chain.web3.to_checksum_address(self.env_wallet["address"]), self.env_wallet["private_key"])
                        
                        # TODO: what if withdraw failed?
                        
                        bt.logging.success(f"Withdrew bid from swap {swap_id}. Deleting swap from the database...")
                        await self.storage.delete_swap(swap)
                        
                    except Exception as e:
                        bt.logging.error(f"Failed to withdraw bid from swap {swap_id}. Error: {e}")
                        continue

        except Exception as e:
            bt.logging.error(f"Error withdrawing bids: {e}.")
            time.sleep(1)

    async def forward(
        self, synapse: exchangenet.protocol.SwapNotification
    ) -> exchangenet.protocol.SwapNotification:
        """
        Processes the incoming 'SwapNotification' synapse containing 'swap_id' field.
        A miner should get swap info from the smart contract with 'swap_id' and make a transaction to the smart contract.
        Then it should return the public address from which the transaction was made and encrypted message
        signed by its private key to claim the ownership of the address.

        Args:
            synapse (exchangenet.protocol.SwapNotification): The synapse object containing the 'swap_id'.

        Returns:
            exchangenet.protocol.SwapNotification: The synapse object with the 'output' field which contains the public address and encrypted message.
        """
        chain = chains[synapse.chain_name]
        swap_id = bytes.fromhex(synapse.swap_id[2:])
        bt.logging.info(f"Processing swap {swap_id} on chain {synapse.chain_name}.")
        
        # Get the token information from the swap
        input_token_address = chain.web3.to_checksum_address(chain.get_swap(swap_id).input_token_address)
        output_token_address = chain.web3.to_checksum_address(chain.get_swap(swap_id).output_token_address)
        amount = chain.get_swap(swap_id).amount
        
        # Adjust the bid amount
        bid_amount = adjust_bid_amount(input_token_address, output_token_address, amount, chain.rpc_url)
        bt.logging.info(f"Bid amount: {bid_amount}")
                
        # Make a bid on the swap
        try:
            bt.logging.info("Making bid...")
            chain.make_bid(swap_id, bid_amount, chain.web3.to_checksum_address(self.env_wallet["address"]), self.env_wallet["private_key"])
            bt.logging.info("Bid made successfully.")
            bt.logging.info(chain.get_bid_amount(swap_id, chain.web3.to_checksum_address(self.env_wallet["address"])))
        except Exception as e:
            bt.logging.error(f"Error making bid: {e}. Failed to make a bid on swap {chain.web3.to_hex(swap_id)}.")
            return synapse
        
        try:
            # Encrypt the swap_id with the miner's private key
            encrypted_swap_id = chain.sign_message(chain.web3.to_hex(swap_id), bytes.fromhex(self.env_wallet["private_key"]))

            # Set the output fields of the synapse
            synapse.output = self.uid, self.env_wallet["address"], base64.b64encode(encrypted_swap_id).decode('utf-8')
        except Exception as e:
            bt.logging.error(f"Error encrypting swap_id: {e}. Failed to encrypt swap_id {chain.web3.to_hex(swap_id)}.")

        # Store swap info in the swap pool
        self.loop.run_until_complete(self.storage.store_swap(synapse.swap_id[2:], synapse.chain_name))
            
        return synapse

    async def swap_notification_blacklist(
        self, synapse: exchangenet.protocol.SwapNotification
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (exchangenet.protocol.SwapNotification): A synapse object constructed from the headers of the incoming request.

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
        uid = self.metagraph.hotkeys.index( synapse.dendrite.hotkey)
        if not self.config.blacklist.allow_non_registered and synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"
        
        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def swap_notification_priority(self, synapse: exchangenet.protocol.SwapNotification) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (exchangenet.protocol.SwapNotification): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority

    async def discovery_blacklist(
        self, synapse: exchangenet.protocol.Pricing
    ) -> typing.Tuple[bool, str]:
        """
        Blacklist function for the `Pricing` synapse. This function determines whether an incoming request should be blacklisted and thus ignored.

        Args:
            synapse (exchangenet.protocol.Pricing): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.
        """
        uid = self.metagraph.hotkeys.index( synapse.dendrite.hotkey)
        if not self.config.blacklist.allow_non_registered and synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"
        
        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def discovery_priority(self, synapse: exchangenet.protocol.Pricing) -> float:
        """
        Priority function for the `Pricing` synapse. This function determines the order in which requests are handled. More valuable or higher-priority requests are processed before others.

        Args:
            synapse (exchangenet.protocol.Pricing): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.
        """
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        ) # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority

# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(5)

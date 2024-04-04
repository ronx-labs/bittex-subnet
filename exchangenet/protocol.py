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

import typing
import pydantic
import bittensor as bt

from exchangenet.shared.blockchain.evm import ZERO_ADDRESS
class SwapRequest(bt.Synapse):
    """
    A swap request protocol representation which uses bt.Synapse as its base.
    A user sends this request to the validator to notify that they want to swap tokens.
    """

    # Name of the chain on which the swap is to be made.
    chain_name: str = pydantic.Field(
        description="Name of the chain on which the swap is to be made"
    )

    # Swap id of the swap created on the smart contract.
    swap_id: str = pydantic.Field(
        description="Id of the swap created on the smart contract"
    )

    # Output is a boolean value which is True if the swap is created and False otherwise.
    output: bool = pydantic.Field(
        description="Output of the swap request"
    )

class SwapNotification(bt.Synapse):
    """
    A swap notification protocol representation which uses bt.Synapse as its base.
    A validator sends this notification to the miner after a swap has been created on the smart contract.
    """

    # Name of the chain on which the swap is to be made.
    chain_name: str = pydantic.Field(
        description="Name of the chain on which the swap is to be made"
    )

    # Swap id of the swap created on the smart contract.
    swap_id: str = pydantic.Field(
        description="Id of the swap created on the smart contract"
    )
    
    # Output is a tuple containing the uid and public address of the miner and encrypted swap_id
    # Encrypted swap_id is used for verifying the ownership of the address.
    output: typing.Tuple[int, str, str] = pydantic.Field(
        description="Output of the swap notification",
        default=(-1, ZERO_ADDRESS, '')
    )

class FinalizeSwap(bt.Synapse):
    """
    A finalize swap protocol representation which uses bt.Synapse as its base.
    A validator sends this notification to the miner once the user has confirmed to finalize the swap.
    """

    # A string respresenting the swap id of the swap created on the smart contract.
    swap_id: str = pydantic.Field(
        description="Id of the swap created on the smart contract"
    )

    # A string representing the transaction id that is made by the randomly seleted miners.
    transaction_id: str = pydantic.Field(
        description="Id of the transaction made by the randomly selected miners"
    )

    # Input and Output tokens are the number of tokens that are being swapped.
    input_token: dict = pydantic.Field({
        "type": "ETH",
        "amount": 3,
        "address": "0x1234567890"
        },
        description="Amount of tokens that users want to swap",
        example={
            "type": "ETH", 
            "amount": 3, 
            "address": "0x1234567890"
        }
    )
    output_token: dict = pydantic.Field({
        "type": "USDT",
        "amount": 100,
        "address": "0x1234567890"
        },
        description="Amount of tokens that users receive after the swap",
        example={
            "type": "USDT", 
            "amount": 100, 
            "address": "0x1234567890"
        },
    )

    # Output is a boolean value which is True if the swap is finalized and False otherwise.
    output: bool = pydantic.Field(
        description="Output of the finalize swap"
    )
import streamlit as st
import bittensor as bt
import random
import asyncio
import os

from dotenv import load_dotenv
from web3 import Web3

from exchangenet.shared.blockchain.chains import chains
from exchangenet.shared.blockchain.evm import Swap, ZERO_ADDRESS
from exchangenet.protocol import SwapRequest
from exchangenet.utils.uids import get_query_api_nodes


load_dotenv()

async def request_swap(swap_id: str):
    """
    Retrieves the axons of query API nodes based on their availability and stake.

    Args:
        wallet (bittensor.wallet): The wallet instance to use for querying nodes.
        metagraph (bittensor.metagraph, optional): The metagraph instance containing network information.
        n (float, optional): The fraction of top nodes to consider based on stake. Defaults to 0.1.
        timeout (int, optional): The timeout in seconds for pinging nodes. Defaults to 3.
        uids (Union[List[int], int], optional): The specific UID(s) of the API node(s) to query. Defaults to None.

    Returns:
        list: A list of axon objects for the available API nodes.
    """
    wallet = bt.wallet(name="vali", hotkey="vali_hotkey")
    dendrite = bt.dendrite(wallet=wallet)

    synapse = SwapRequest(swap_id=swap_id, output=False)
    metagraph = bt.subtensor("ws://127.0.0.1:9946/").metagraph(netuid=1)
    vali_axons = await get_query_api_nodes(dendrite=dendrite, metagraph=metagraph)
    axons = random.choices(vali_axons, k=1)

    responses = await dendrite(
        axons=[metagraph.axons[uid] for uid in axons],
        synapse=synapse,
    )
    for response in responses:
        print(f"response: {responses}")


if __name__ == '__main__':
    with st.form("create_swap_form", border=False):
        account_address = st.text_input("Enter your account address")
        private_key = st.text_input("Enter your private key")
        input_token_address = st.text_input("Enter your input token address")
        output_token_address = st.text_input("Enter your output token address")
        input_token_amount = st.number_input("Enter the amount of input token to swap")

        chain = chains[os.getenv("NETWORK_MODE")]

        # Check for connection to the Ethereum network
        if not bnb_test_chain.web3.is_connected():
            raise ConnectionError("Failed to connect to HTTPProvider")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        if col1.form_submit_button("Create swap", type="primary", use_container_width=True):
            if inputTokenAddress and outputTokenAddress and inputTokenAmount:
                from_address = Web3.to_checksum_address(inputTokenAddress)
                to_address = Web3.to_checksum_address(outputTokenAddress)
                amount = int(inputTokenAmount)
                
                # Create swap
                swap_id = bnb_test_chain.create_swap(from_address, to_address, amount, account_address, private_key)

                # Get swap info
                st.session_state.swap_id = Web3.to_hex(swap_id)
                st.session_state.swap = bnb_test_chain.get_swap(swap_id)

                st.write("Swap ID: " + st.session_state.swap_id)

        if col2.form_submit_button("Request swap", type="primary", use_container_width=True):
            # Request swap if swap exists
            if st.session_state.swap is not None:
                asyncio.run(request_swap(st.session_state.swap_id))

                st.session_state.swap_requested = True
                st.write("Swap requested")

        
        if col3.form_submit_button("Finalize swap", type="primary", use_container_width=True):
            # Finalize swap
            bnb_test_chain.finalize_swap(st.session_state.swap_id, account_address, private_key)
            
            winner = bnb_test_chain.get_winner(st.session_state.swap_id)
            st.write("Winner: " + winner)
                
            

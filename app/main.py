import streamlit as st
import bittensor as bt
import random
import asyncio
from Crypto.Hash import keccak

from exchangenet.shared.blockchain.chains import chains
from exchangenet.protocol import SwapRequest
from exchangenet.utils.uids import get_query_api_nodes


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
    bt.logging.info(f"vali_axons: =================================={vali_axons}")
    axons = random.choices(vali_axons, k=1)

    responses = await dendrite(
        axons=[metagraph.axons[uid] for uid in axons],
        synapse=synapse,
    )
    for response in responses:
        print(f"response: {response.dendrite.dict()}")


if __name__ == '__main__':
    st.session_state.swap_id = None

    with st.form("create_swap_form", border=False):
        inputTokenAddress = st.text_input("Enter your input token address")
        outputTokenAddress = st.text_input("Enter your output token address")
        inputTokenAmount = st.number_input("Enter the amount of input token to swap")

        bnb_testnet = chains["bnb_test"]

        w3 = bnb_testnet.web3

        bittex_contract = w3.eth.contract(address=bnb_testnet.bittex_contract_address, abi=bnb_testnet.bittex_abi)

        # Check for connection to the Ethereum network
        if not w3.is_connected():
            raise ConnectionError("Failed to connect to HTTPProvider")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        if col1.form_submit_button("Create swap", type="primary", use_container_width=True):
            if inputTokenAddress and outputTokenAddress and inputTokenAmount:
                st.session_state.swap = {
                    "inputTokenAddress": inputTokenAddress,
                    "outputTokenAddress": outputTokenAddress,
                    "inputTokenAmount": inputTokenAmount,
                }

                st.session_state.swap_id = bittex_contract.functions.createSwap(st.session_state.swap["inputTokenAddress"], st.session_state.swap["outputTokenAddress"], int(st.session_state.swap["inputTokenAmount"])).call()
                
                # Convert bytes32 to hex string
                hex_string = w3.to_hex(st.session_state.swap_id)

                # Calculate the keccak256 hash
                hash_object = keccak.new(digest_bits=256)
                hash_object.update(st.session_state.swap_id)
                keccak256_hash = hash_object.hexdigest()

                print(st.session_state.swap_id)
                print(keccak256_hash)

                print(f'swaps: {bittex_contract.functions.swaps(bytes.fromhex(keccak256_hash)).call()}')

                st.write("Swap ID: " + hex_string)

        if col3.form_submit_button("Request swap", type="primary", use_container_width=True):
            asyncio.run(request_swap(str(st.session_state.swap_id)))

            st.write("Swap requested")
            

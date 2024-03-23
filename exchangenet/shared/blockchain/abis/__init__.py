import os
import json


current_dir = os.path.dirname(__file__)

with open(os.path.join(current_dir, 'bittex.json')) as abi_file:
    BITTEX_ABI = json.load(abi_file)

with open(os.path.join(current_dir, 'erc20.json')) as abi_file:
    ERC20_ABI = json.load(abi_file)

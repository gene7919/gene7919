import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

BASE_RPC_URL = os.getenv("BASE_RPC_URL")  # es: https://mainnet.base.org
TOKEN_ADDRESS = Web3.to_checksum_address("0x63800f370b04ce132333c05d811663b80cec788e")

# ABI minimale ERC-20 per balance e transfer
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function",
    },
]

w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
token = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)


def get_balance(address: str) -> int:
    checksum = Web3.to_checksum_address(address)
    return token.functions.balanceOf(checksum).call()


def send_reward(from_private_key: str, to_address: str, amount_wei: int) -> str:
    account = w3.eth.account.from_key(from_private_key)
    checksum_to = Web3.to_checksum_address(to_address)

    tx = token.functions.transfer(checksum_to, amount_wei).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "maxFeePerGas": w3.to_wei("0.5", "gwei"),
            "maxPriorityFeePerGas": w3.to_wei("0.1", "gwei"),
            "chainId": 8453,  # Base mainnet
        }
    )

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()

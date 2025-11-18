import re

def is_valid_wallet_address(address: str) -> bool:
    pattern = r"^0x[a-fA-F0-9]{40}$"
    return bool(re.match(pattern, address))
# app/services/user_service.py

from app.db.db import get_data, add_data

import logging

def get_user(user_id: int):
    return get_data("users", user_id) or {}


def get_wallets(user_id: int):
    try:
        user = get_user(user_id)
    except Exception as e:
        logging.error(f"[USER SERVICE ERROR] get_wallets: {e}")
        return []
    
    return user.get("wallets", [])


def find_wallet(user_id: int, wallet: str):
    try:
        wallets = get_wallets(user_id)
        for w in wallets:
            if w["address"].lower() == wallet.lower():
                return w
    except Exception as e:
        logging.error(f"[USER SERVICE ERROR] find_wallet: {e}")

    return None


def wallet_exists(user_id: int, wallet: str):
    return find_wallet(user_id, wallet) is not None


def add_wallet(user_id: int, wallet_address: str, last_hash: str = None, wallet_name: str = None):
    try:
        user = get_user(user_id)
        wallets = user.get("wallets", [])

        if not wallet_exists(user_id, wallet_address):
            wallets.append({
                "address": wallet_address,
                "name": wallet_name,
                "last_seen_hash": last_hash
            })

        add_data("users", user_id, {"wallets": wallets})
    except Exception as e:
        logging.error(f"[USER SERVICE ERROR] add_wallet: {e}")
    

def update_last_seen(user_id: int, wallet: str, tx_hash: str):
    try:
        wallets = get_wallets(user_id)

        for w in wallets:
            if w["address"].lower() == wallet.lower():
                w["last_seen_hash"] = tx_hash

        add_data("users", user_id, {"wallets": wallets})
    except Exception as e:
        logging.error(f"[USER SERVICE ERROR] update_last_seen: {e}")
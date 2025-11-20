import asyncio

from datetime import datetime

from app.services.user_service import get_user, find_wallet, update_last_seen
from app.utils.scraper import check_new_activity

async def wallet_watcher(user_id: int, address: str, bot):
    
    print(f"[WATCH] Started watcher for {address}")

    try:
        while True:

            print(address)

            data = await check_new_activity(address)
            
            if data:
                latest_data = data[0]
                latest_hash = latest_data["transactionHash"]

                # user = get_user(user_id)
                wallet = find_wallet(user_id, address)

                if not wallet:
                    return
            
                last_seen = wallet.get("last_seen_hash")

                if not last_seen:
                    update_last_seen(user_id, address, latest_hash)

                elif latest_hash != last_seen:
                    
                    name = wallet.get("name") or (address[:6] + "..." + address[-4:])

                    response = f"""🔔 New trade — {name}\nMarket: {latest_data['title']}\nAction: {latest_data['side'].capitalize()} / {latest_data['outcome'] if latest_data['outcome'] and len(latest_data['outcome']) > 0 else latest_data['type']}\nAmount: ${latest_data['usdcSize']:.2f}\nPrice: {latest_data['price']:.2f}\nTimestamp: {datetime.fromtimestamp(float(latest_data['timestamp'])).strftime('%H:%M')} UTC"""

                    await bot.send_message(
                        chat_id=user_id,
                        text=response
                    )

                    print(f"[NEW] Activity for {address}: {latest_hash}")

                    update_last_seen(user_id, address, latest_hash)
            
            await asyncio.sleep(60)
    except Exception as e:
        print(f"[WATCH ERROR] Watcher for {address} stopped: {e}")
        

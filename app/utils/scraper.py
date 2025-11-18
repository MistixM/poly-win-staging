import requests

from fake_useragent import UserAgent
from app.services.user_service import update_last_seen

async def check_new_activity(address: str):
    ua = UserAgent()
    random_user_agent = ua.random

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://polymarket.com',
        'priority': 'u=1, i',
        'referer': 'https://polymarket.com/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Chromium";v="142"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': random_user_agent,
    }

    params = {
        'user': address,
        'limit': '25',
        'offset': '0',
    }

    response = requests.get('https://data-api.polymarket.com/activity', params=params, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except Exception as e:
            print(f"Error while sending request for check activity: {e}")
            return
    else:
        print(f"Error: Received status code {response.status_code} for address {address}")
        return

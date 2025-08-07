#!/usr/bin/env python3

import urllib.request
import urllib.error
import json
import sys
from datetime import datetime

def get_btc_price():
    apis = [
        ('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', lambda x: f"${float(x['price']):,.2f}", "Binance"),
        ('https://api.coindesk.com/v1/bpi/currentprice/BTC.json', lambda x: x['bpi']['USD']['rate'], "CoinDesk"),
        ('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', lambda x: f"${x['bitcoin']['usd']:,.2f}", "CoinGecko")
    ]
    
    for api_url, price_extractor, provider in apis:
        try:
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                price = price_extractor(data)
                return price, provider
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            continue
    
    print("Error: Unable to fetch BTC price from any API")
    return None, None

def main():
    print("Bitcoin Price Tracker")
    print("=" * 20)
    
    price, provider = get_btc_price()
    if price:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Current BTC Price: {price}")
        print(f"Data Provider: {provider}")
        print(f"Last Updated: {timestamp}")
    else:
        print("Failed to fetch BTC price")
        sys.exit(1)

if __name__ == "__main__":
    main()
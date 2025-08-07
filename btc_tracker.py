#!/usr/bin/env python3

import urllib.request
import urllib.error
import json
import sys
from datetime import datetime, timedelta
import time

def get_btc_price():
    apis = [
        ('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', lambda x: f"${float(x['price']):,.2f}", lambda x: float(x['price']), "Binance"),
        ('https://api.coindesk.com/v1/bpi/currentprice/BTC.json', lambda x: x['bpi']['USD']['rate'], lambda x: float(x['bpi']['USD']['rate'].replace(',', '').replace('$', '')), "CoinDesk"),
        ('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', lambda x: f"${x['bitcoin']['usd']:,.2f}", lambda x: float(x['bitcoin']['usd']), "CoinGecko")
    ]
    
    for api_url, price_formatter, price_raw, provider in apis:
        try:
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                formatted_price = price_formatter(data)
                raw_price = price_raw(data)
                return formatted_price, raw_price, provider
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            continue
    
    print("Error: Unable to fetch BTC price from any API")
    return None, None, None

def get_historical_prices():
    end_time = int(time.time() * 1000)
    start_time = end_time - (2 * 60 * 60 * 1000)  # 2 hours ago
    
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&startTime={start_time}&endTime={end_time}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            prices = []
            for kline in data:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                close_price = float(kline[4])
                prices.append((timestamp, close_price))
            return prices
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Warning: Could not fetch historical data: {e}")
        return []

def create_ascii_graph(prices):
    if len(prices) < 2:
        return "Insufficient data for graph"
    
    graph_height = 8
    graph_width = 50
    
    # Extract price values
    price_values = [price[1] for price in prices]
    min_price = min(price_values)
    max_price = max(price_values)
    price_range = max_price - min_price
    
    if price_range == 0:
        return "Price remained constant"
    
    # Create the graph
    graph_lines = []
    for row in range(graph_height):
        line = ""
        for col in range(graph_width):
            if col < len(prices):
                price = price_values[col]
                # Normalize price to graph height (inverted for display)
                normalized = (price - min_price) / price_range
                height_pos = int(normalized * (graph_height - 1))
                
                if height_pos == (graph_height - 1 - row):
                    line += "●"
                elif height_pos > (graph_height - 1 - row):
                    line += "│"
                else:
                    line += " "
            else:
                line += " "
        graph_lines.append(line)
    
    # Add price labels
    result = []
    result.append(f"\n2-Hour Price Trend (${min_price:,.2f} - ${max_price:,.2f}):")
    result.append("┌" + "─" * graph_width + "┐")
    
    for i, line in enumerate(graph_lines):
        price_at_level = min_price + (price_range * (graph_height - 1 - i) / (graph_height - 1))
        result.append(f"│{line}│ ${price_at_level:>8,.0f}")
    
    result.append("└" + "─" * graph_width + "┘")
    
    # Add time labels
    if len(prices) >= 2:
        start_time = prices[0][0].strftime("%H:%M")
        end_time = prices[-1][0].strftime("%H:%M")
        time_label = f"  {start_time}" + " " * (graph_width - len(start_time) - len(end_time)) + f"{end_time}"
        result.append(time_label)
    
    # Add trend indicator
    if len(prices) >= 2:
        price_change = price_values[-1] - price_values[0]
        percent_change = (price_change / price_values[0]) * 100
        trend = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
        result.append(f"\nTrend: {trend} ${price_change:+.2f} ({percent_change:+.2f}%)")
    
    return "\n".join(result)

def main():
    print("Bitcoin Price Tracker")
    print("=" * 20)
    
    formatted_price, raw_price, provider = get_btc_price()
    if formatted_price:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Current BTC Price: {formatted_price}")
        print(f"Data Provider: {provider}")
        print(f"Last Updated: {timestamp}")
        
        # Fetch and display historical data
        print("\nFetching 2-hour price history...")
        historical_prices = get_historical_prices()
        
        if historical_prices:
            graph = create_ascii_graph(historical_prices)
            print(graph)
        else:
            print("Could not display price trend - historical data unavailable")
    else:
        print("Failed to fetch BTC price")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import urllib.request
import urllib.error
import json
import sys
import argparse
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

def get_historical_prices(hours=2, include_ohlc=False):
    end_time = int(time.time() * 1000)
    start_time = end_time - (hours * 60 * 60 * 1000)  # specified hours ago
    
    # Choose appropriate interval based on timeframe
    if hours <= 2:
        interval = "5m"
    elif hours <= 12:
        interval = "15m"
    elif hours <= 48:
        interval = "1h"
    else:
        interval = "4h"
    
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={interval}&startTime={start_time}&endTime={end_time}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            prices = []
            for kline in data:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                if include_ohlc:
                    open_price = float(kline[1])
                    high_price = float(kline[2])
                    low_price = float(kline[3])
                    close_price = float(kline[4])
                    prices.append((timestamp, open_price, high_price, low_price, close_price))
                else:
                    close_price = float(kline[4])
                    prices.append((timestamp, close_price))
            return prices
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Warning: Could not fetch historical data: {e}")
        return []

def create_ascii_graph(prices, hours=2):
    if len(prices) < 2:
        return "Insufficient data for graph"
    
    graph_height = 10
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
            # Map column to price data index
            if len(prices) > 1:
                price_index = int((col / (graph_width - 1)) * (len(prices) - 1))
                price = price_values[price_index]
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
    hour_text = f"{hours}-Hour" if hours != 1 else "1-Hour"
    result.append(f"\n{hour_text} Price Trend (${min_price:,.2f} - ${max_price:,.2f}):")
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

def create_candlestick_chart(ohlc_data, hours=2):
    if len(ohlc_data) < 2:
        return "Insufficient data for candlestick chart"
    
    chart_height = 15
    chart_width = min(50, len(ohlc_data))  # Limit width but show all candles if few
    
    # Extract all prices to find range
    all_prices = []
    for candle in ohlc_data:
        timestamp, open_price, high_price, low_price, close_price = candle
        all_prices.extend([open_price, high_price, low_price, close_price])
    
    min_price = min(all_prices)
    max_price = max(all_prices)
    price_range = max_price - min_price
    
    if price_range == 0:
        return "Price remained constant"
    
    # Select candles to display (evenly distributed across chart width)
    if len(ohlc_data) > chart_width:
        step = len(ohlc_data) / chart_width
        selected_candles = []
        for i in range(chart_width):
            idx = int(i * step)
            selected_candles.append(ohlc_data[idx])
    else:
        selected_candles = ohlc_data
    
    # Create the chart
    chart_lines = []
    for row in range(chart_height):
        line = ""
        for col in range(len(selected_candles)):
            timestamp, open_price, high_price, low_price, close_price = selected_candles[col]
            
            # Normalize prices to chart height (inverted for display)
            norm_high = int(((high_price - min_price) / price_range) * (chart_height - 1))
            norm_low = int(((low_price - min_price) / price_range) * (chart_height - 1))
            norm_open = int(((open_price - min_price) / price_range) * (chart_height - 1))
            norm_close = int(((close_price - min_price) / price_range) * (chart_height - 1))
            
            current_row = chart_height - 1 - row
            
            # Determine candle type and body
            is_bullish = close_price >= open_price
            body_top = max(norm_open, norm_close)
            body_bottom = min(norm_open, norm_close)
            
            if current_row == norm_high and current_row > body_top:
                # High wick above body
                line += "│"
            elif current_row == norm_low and current_row < body_bottom:
                # Low wick below body
                line += "│"
            elif body_bottom <= current_row <= body_top:
                # Body of the candle
                if is_bullish:
                    if body_top == body_bottom:  # Doji
                        line += "─"
                    else:
                        line += "█"  # Solid fill for bullish
                else:
                    line += "▒"  # Hollow/light fill for bearish
            elif body_top < current_row <= norm_high or norm_low <= current_row < body_bottom:
                # Wicks
                line += "│"
            else:
                line += " "
        chart_lines.append(line)
    
    # Add labels and formatting
    result = []
    hour_text = f"{hours}-Hour" if hours != 1 else "1-Hour"
    result.append(f"\n{hour_text} Candlestick Chart (${min_price:,.2f} - ${max_price:,.2f}):")
    result.append("┌" + "─" * len(selected_candles) + "┐")
    
    for i, line in enumerate(chart_lines):
        price_at_level = min_price + (price_range * (chart_height - 1 - i) / (chart_height - 1))
        result.append(f"│{line}│ ${price_at_level:>8,.0f}")
    
    result.append("└" + "─" * len(selected_candles) + "┘")
    
    # Add time labels
    if len(selected_candles) >= 2:
        start_time = selected_candles[0][0].strftime("%H:%M")
        end_time = selected_candles[-1][0].strftime("%H:%M")
        time_label = f"  {start_time}" + " " * (len(selected_candles) - len(start_time) - len(end_time)) + f"{end_time}"
        result.append(time_label)
    
    # Add trend and candle legend
    if len(ohlc_data) >= 2:
        start_close = ohlc_data[0][4]  # First close
        end_close = ohlc_data[-1][4]   # Last close
        price_change = end_close - start_close
        percent_change = (price_change / start_close) * 100
        trend = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
        result.append(f"\nTrend: {trend} ${price_change:+.2f} ({percent_change:+.2f}%)")
        result.append("Legend: ▒ Bearish  █ Bullish  │ Wicks  ─ Doji")
    
    return "\n".join(result)

def main():
    parser = argparse.ArgumentParser(description='Bitcoin Price Tracker with customizable timeframes')
    parser.add_argument('-H', '--hours', type=int, default=2, 
                       help='Number of hours to fetch price history (default: 2)')
    parser.add_argument('-c', '--candles', action='store_true',
                       help='Show Japanese candlestick chart instead of line chart')
    
    args = parser.parse_args()
    hours = max(1, args.hours)  # Ensure at least 1 hour
    
    print("Bitcoin Price Tracker")
    print("=" * 20)
    
    formatted_price, raw_price, provider = get_btc_price()
    if formatted_price:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Current BTC Price: {formatted_price}")
        print(f"Data Provider: {provider}")
        print(f"Last Updated: {timestamp}")
        
        # Fetch and display historical data
        hour_text = f"{hours} hour{'s' if hours != 1 else ''}"
        print(f"\nFetching {hour_text} price history...")
        
        if args.candles:
            historical_data = get_historical_prices(hours, include_ohlc=True)
            if historical_data:
                chart = create_candlestick_chart(historical_data, hours)
                print(chart)
            else:
                print("Could not display candlestick chart - historical data unavailable")
        else:
            historical_prices = get_historical_prices(hours)
            if historical_prices:
                graph = create_ascii_graph(historical_prices, hours)
                print(graph)
            else:
                print("Could not display price trend - historical data unavailable")
    else:
        print("Failed to fetch BTC price")
        sys.exit(1)

if __name__ == "__main__":
    main()
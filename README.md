# Bitcoin Price Tracker

A command-line Bitcoin price tracker with ASCII visualizations, supporting both line charts and Japanese candlestick charts.

## Features

- **Real-time BTC price**: Fetches current Bitcoin price from multiple APIs
- **Customizable timeframes**: View price history from 1 hour to multiple days
- **Two chart types**:
  - Line chart: Simple price trend visualization
  - Japanese candlesticks: Trader-friendly OHLC (Open, High, Low, Close) data
- **Multiple data sources**: Falls back between Binance, CoinDesk, and CoinGecko APIs
- **Smart intervals**: Automatically selects appropriate time intervals based on timeframe
- **Terminal-based**: Runs entirely in the command line with ASCII graphics

## Installation

No external dependencies required! The script uses only Python standard library modules.

```bash
git clone https://github.com/chico10117/scripts.git
cd scripts
chmod +x btc_tracker.py
```

## Usage

### Basic Usage

```bash
# Default: 2-hour line chart
python3 btc_tracker.py

# Show help
python3 btc_tracker.py --help
```

### Customizable Timeframes

```bash
# 1 hour
python3 btc_tracker.py -H 1

# 6 hours  
python3 btc_tracker.py -H 6

# 24 hours (1 day)
python3 btc_tracker.py -H 24

# 168 hours (1 week)
python3 btc_tracker.py -H 168
```

### Japanese Candlestick Charts

```bash
# 2-hour candlestick chart
python3 btc_tracker.py -c

# 6-hour candlesticks
python3 btc_tracker.py -c -H 6

# 24-hour candlesticks
python3 btc_tracker.py --candles --hours 24
```

## Chart Types

### Line Chart
Shows price trend as connected dots with vertical bars:
```
2-Hour Price Trend ($115,439.12 - $116,828.29):
┌──────────────────────────────────────────────────┐
│                                     ●●           │ $ 116,828
│                                   ●●││      ●●   │ $ 116,674
│                                ●●●││││●●●●●●││●● │ $ 116,520
│                  ●●  ●●  ●●●●●●│││││││││││││││││●│ $ 116,365
│               ●●●││●●││●●│││││││││││││││││││││││││ $ 116,211
└──────────────────────────────────────────────────┘
```

### Japanese Candlestick Chart
Shows OHLC data with traditional candlestick representation:
```
2-Hour Candlestick Chart ($115,294.72 - $116,828.93):
┌────────────────────────┐
│                 │      │ $ 116,829
│                 █▒  █▒ │ $ 116,701
│               █─█▒█─█▒▒│ $ 116,573
│            █▒█│ ▒█│  ▒│ $ 116,445
│        █▒█▒█│          │ $ 116,317
└────────────────────────┘

Legend: ▒ Bearish  █ Bullish  │ Wicks  ─ Doji
```

## Command Line Options

```
usage: btc_tracker.py [-h] [-H HOURS] [-c]

Bitcoin Price Tracker with customizable timeframes

options:
  -h, --help         show this help message and exit
  -H, --hours HOURS  Number of hours to fetch price history (default: 2)
  -c, --candles      Show Japanese candlestick chart instead of line chart
```

## Data Sources & Intervals

The script automatically chooses appropriate time intervals based on the requested timeframe:

- **≤2 hours**: 5-minute intervals
- **≤12 hours**: 15-minute intervals  
- **≤48 hours**: 1-hour intervals
- **>48 hours**: 4-hour intervals

### API Sources (in priority order):
1. **Binance** (primary) - Fast and reliable
2. **CoinDesk** - Fallback option
3. **CoinGecko** - Secondary fallback

## Output Information

Each run displays:
- Current BTC price with data provider
- Last updated timestamp
- Price trend visualization
- Price range (min/max) for the timeframe
- Overall trend with percentage change
- Directional emoji indicators (📈📉➡️)

## Examples

### Quick Price Check
```bash
python3 btc_tracker.py -H 1
```

### Weekly Trading Analysis
```bash
python3 btc_tracker.py -c -H 168
```

### Intraday Scalping View
```bash
python3 btc_tracker.py -c -H 4
```

## Technical Notes

- **Price Type**: Uses closing prices for each time interval
- **No Dependencies**: Built with Python standard library only
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Network Required**: Fetches live data from cryptocurrency APIs
- **Graceful Fallbacks**: Continues to work even if some APIs are unavailable

## License

Open source - feel free to modify and distribute.

---

*Built with Python 3 and ASCII art for maximum terminal compatibility.*
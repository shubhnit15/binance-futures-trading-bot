# Binance Futures Testnet Trading Bot (USDT-M)

A highly structured, production-ready Python command-line utility for executing MARKET and LIMIT orders on the **Binance Futures Testnet (USDT-M)**. Features rigorous input validations, interactive setup fallbacks, dual-handler detailed logging, and clean, descriptive trading exception parsing.

---

## Features
- **Target Platform:** Binance Futures Testnet (USDT-M) via the default endpoints configured through `python-binance`.
- **Modes of Operation:** 
  1. **Direct CLI mode:** Execute fast trades by providing explicit CLI command arguments.
  2. **Interactive Wizard mode:** If arguments are missing or incomplete, the bot automatically transitions into a high-fidelity interactive terminal wizard (using `questionary`) to guide your inputs.
- **Rigorously Validated:** Safe input bounds checking for symbols, order types, order sides, positive float values, and mandatory prices for Limit trades.
- **Detailed Logging:** Full requests, network parameters, raw API JSON responses, and errors are logged to `bot.log` while rendering neat status feedback directly to the console.
- **Graceful Error Handling:** Specially handles API failures, network timeouts, invalid API keys, insufficient margin (`-2019`), and precision errors (`-1111`/`-1013`).

---

## Directory Structure
```
trading_bot/
  ├── .env                   # Local secret credentials (API key/secret)
  ├── requirements.txt       # Pinpointed dependencies
  ├── README.md              # Documentation and execution guide
  ├── cli.py                 # CLI entry point (Click + Questionary)
  └── bot/
      ├── __init__.py        # Exposes modules cleanly
      ├── client.py          # Futures Testnet client and connection checking
      ├── orders.py          # Futures order creation and exception translating
      ├── validators.py      # Local input verification rules
      └── logging_config.py  # Logger setup for stdout & bot.log files
```

---

## Installation & Setup

Follow these steps to set up and run the bot locally:

### 1. Prerequisite
Ensure you have **Python 3.10+** installed on your system.

### 2. Create and Activate Virtual Environment
Open your terminal in the `trading_bot` directory and run:

**On Windows (Command Prompt/PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

### 4. Setup Secrets Configuration
Rename or configure the `.env` template to insert your actual **Binance Futures Testnet API Key** and **Secret**:
1. Get your free testnet credentials from the [Binance Futures Testnet](https://testnet.binancefuture.com) dashboard.
2. Open the `.env` file and replace the template values:
```env
BINANCE_API_KEY=your_actual_binance_testnet_api_key
BINANCE_API_SECRET=your_actual_binance_testnet_api_secret
```

---

## Execution Guide

### Mode A: Interactive Fallback Menu
If you run the program without parameters, or with incomplete arguments, it will launch the visual terminal wizard:
```bash
python cli.py
```
*Simply follow the beautiful selection menus and confirmations inside your terminal.*

### Mode B: Direct Command-line Arguments

#### 1. Placing a MARKET Buy Order
Place a Market Buy order for `0.005 BTCUSDT` contract:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.005
```

#### 2. Placing a LIMIT Sell Order
Place a Limit Sell order for `0.002 BTCUSDT` contract at a price of `70500` USDT:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 70500.0
```

#### CLI Help Flag
To see all options and help descriptions, run:
```bash
python cli.py --help
```

---

## System Assertions & Precision Assumptions

1. **Testnet Only Boundary:** To prevent accidental real-money losses, the API client forces `testnet=True`. Running this bot will never touch or place orders on your Binance Production/Mainnet accounts.
2. **Asset Precision Rules:** 
   - Binance Futures operates with a set of filters per asset symbol. These filters specify the step size (e.g., minimum fraction of a coin you can trade) and price step (e.g., tick size).
   - *Lot Size Constraints:* If the quantity input has more decimal places than allowed by the symbol's `LOT_SIZE` (e.g., trying to trade 0.0005 BTC when the minimum tick allows only 3 decimals), the trade will be rejected by the Binance API.
   - The bot handles this gracefully by catching Binance error codes `-1111` and `-1013`, translating them into simple, clear warnings on screen suggesting the user check asset tick sizes.
3. **Execution Execution Speed:** Limit orders are initialized with the `GTC` (Good 'Til Cancelled) time in force setting. This guarantees that they remain active in the order book until fully executed or manually cancelled.
4. **Log Retention:** All raw API request arguments, logs, warnings, and responses are appended continuously to `bot.log`. Check this log file for comprehensive troubleshooting.

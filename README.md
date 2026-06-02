# Binance Futures Testnet Trading Bot (USDT-M)

A highly structured, production-ready Python command-line utility for executing MARKET and LIMIT orders on the **Binance Futures Testnet (USDT-M)**. Features rigorous input validations, interactive setup fallbacks, dual-handler detailed logging, and clean, descriptive trading exception parsing.

---

## 🛠️ Features

- **Target Platform:** Binance Futures Testnet (USDT-M) via the default endpoints configured through `python-binance`.
- **Dual Execution Modes:** 
  1. **Mode A: Interactive Fallback Menu:** A guided wizard using `questionary` that walks you through parameter setup step-by-step with live validation.
  2. **Mode B: Direct Command-line Arguments:** High-speed execution by supplying parameters as CLI options directly in your terminal.
- **Rigorously Validated:** Safe input bounds checking for symbols, order types, order sides, positive float values, and mandatory prices for Limit trades.
- **Detailed Logging:** Full requests, network parameters, raw API JSON responses, and errors are logged to `bot.log` while rendering neat status feedback directly to the console.
- **Graceful Error Handling:** Specially handles API failures, network timeouts, invalid API keys, insufficient margin (`-2019`), and precision errors (`-1111`/`-1013`).

---

## 📁 Directory Structure

```
trading_bot/
  ├── .env                   # Local secret credentials (API key/secret)
  ├── .gitignore             # Git rules protecting credentials and virtual environments
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

## 📥 Installation & Setup

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

## 🚀 Detailed Execution Guide

This bot supports two distinct modes of execution depending on your preference.

### Mode A: Interactive Fallback Menu (Guided Wizard)

If you run the program without parameters, or with incomplete arguments, the bot automatically detects the missing variables and launches a guided, visual terminal wizard. This is perfect for beginners or manual traders who want immediate validation feedback at every step.

#### How to Trigger
Simply run:
```bash
python cli.py
```

#### Step-by-Step Flow:
1. **Connectivity Check:** The bot instantly pings the Binance server and checks your credentials. If your `.env` keys are missing or invalid, it prints a clean error and stops before prompting you.
2. **Symbol Prompt:**
   ```
   Enter Trading Symbol (e.g., BTCUSDT):
   ```
   *Type the coin pair (case-insensitive). The wizard checks that the input is alphanumeric and non-empty.*
3. **Side Selection:**
   ```
   Select Side:
   > BUY
     SELL
   ```
   *Use the up/down arrow keys and hit Enter to select your trade direction.*
4. **Order Type Selection:**
   ```
   Select Order Type:
   > MARKET
     LIMIT
   ```
   *Select how you want the order executed.*
5. **Quantity Input:**
   ```
   Enter Quantity (BTCUSDT contracts):
   ```
   *Type your trade contract size. The wizard will immediately reject negative numbers or letters, prompting you to enter a positive number.*
6. **Price Input (Only if LIMIT selected):**
   ```
   Enter Limit Price (USDT):
   ```
   *Type your target buy/sell price. The wizard will validate that the price is a positive number before moving on.*
7. **Final Confirmation:**
   ```
   Do you want to submit this order to the Testnet? (y/N)
   ```
   *A safety prompt ensuring you don't place trades by mistake. Hit `y` to execute or `n` to abort safely.*

---

### Mode B: Direct Command-line Arguments (High-Speed Mode)

For programmatic execution, algorithmic traders, shell scripts, or fast manual execution, you can bypass the interactive wizard entirely by providing all required options directly in the terminal command.

If even one required parameter is omitted, the CLI gracefully alerts you and redirects you to **Mode A** to complete the missing fields.

#### Parameters Table:
| Option | Short Flag | Type | Description |
| :--- | :--- | :--- | :--- |
| `--symbol` | `-s` | String | Alphanumeric trading pair symbol (e.g., `BTCUSDT`, `ETHUSDT`) |
| `--side` | `-d` | Choice | Order direction. Must be either `BUY` or `SELL` (case-insensitive) |
| `--type` | `-t` | Choice | Order execution type. Must be either `MARKET` or `LIMIT` (case-insensitive) |
| `--quantity`| `-q` | Float | The number of contracts/coins to buy or sell (must be greater than 0) |
| `--price` | `-p` | Float | The target execution price. **Mandatory** when `--type` is `LIMIT` |

#### Copy-Pasteable Command Examples:

##### 1. Placing a MARKET Buy Order
Buy `0.005 BTC` immediately at the best available current market price:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.005
```

##### 2. Placing a LIMIT Sell Order
Place a Limit order to sell `0.002 BTC` when the market price rises to `71,500.00` USDT:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 71500.0
```

##### 3. Placing a MARKET Sell Order (Short Position)
Enter a short position for `0.05 ETH` immediately:
```bash
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 0.05
```

##### 4. Review command arguments
To inspect help guidelines and flags:
```bash
python cli.py --help
```

---

## ⚠️ System Assertions & Precision Assumptions

1. **Testnet Only Boundary:** To prevent accidental real-money losses, the API client forces `testnet=True`. Running this bot will never touch or place orders on your Binance Production/Mainnet accounts.
2. **Asset Precision Rules:** 
   - Binance Futures operates with a set of filters per asset symbol. These filters specify the step size (e.g., minimum fraction of a coin you can trade) and price step (e.g., tick size).
   - *Lot Size Constraints:* If the quantity input has more decimal places than allowed by the symbol's `LOT_SIZE` (e.g., trying to trade 0.0005 BTC when the minimum tick allows only 3 decimals), the trade will be rejected by the Binance API.
   - The bot handles this gracefully by catching Binance error codes `-1111` and `-1013`, translating them into simple, clear warnings on screen suggesting the user check asset tick sizes.
3. **Execution Execution Speed:** Limit orders are initialized with the `GTC` (Good 'Til Cancelled) time in force setting. This guarantees that they remain active in the order book until fully executed or manually cancelled.
4. **Log Retention:** All raw API request arguments, logs, warnings, and responses are appended continuously to `bot.log`. Check this log file for comprehensive troubleshooting.

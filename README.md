# Binance Futures Order Bot

Minimal CLI trading bot for Binance USDT-M Futures (testnet-ready).

Setup
-
1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. make your own `.env` and fill your API keys:

```text
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_here
USE_TESTNET=True
```

Run the bot
-
Run the CLI from the project root. Examples:

Check connection and wallet balance:

```bash
python -m src.main check
```

Place a market order (example):

```bash
python -m src.main market BTCUSDT BUY 0.001
```

Place a limit order:

```bash
python -m src.main limit BTCUSDT SELL 0.001 60000
```

Run a TWAP split (5 slices, 10s between slices):

```bash
python -m src.main twap BTCUSDT BUY 0.01 5 10
```

Logs
-
All operations and errors are appended to `bot.log`.

Advanced features
-
- Stop-Limit:

```bash
python -m src.main stoplimit BTCUSDT BUY 0.01 30000 30010
```

- OCO (TP+SL) via app polling:

```bash
python -m src.main oco BTCUSDT BUY 0.01 35000 29000
```

- Grid starter:

```bash
python -m src.main grid BTCUSDT 25000 35000 5 0.001
```

Packaging
-
Create the required zip for submission:

```powershell
Compress-Archive -Path * -DestinationPath YourName_binance_bot.zip
Backtester (offline dataset)
-
Put your `historical_data.csv` in the `data/` folder. A sample file is included at `data/historical_data.csv`.

Run the backtester to simulate TWAP or Grid and generate PnL charts:

```powershell
python -m src.advanced.backtester twap 0.01 5
python -m src.advanced.backtester grid 5
```

The charts will be saved under `data/` as `twap_pnl.png` and `grid_pnl.png`. Include these in `report.pdf`.

Switching to Testnet (fix -2015)
-
Generate Testnet API keys at https://testnet.binance.vision and set them in `.env`. Ensure `USE_TESTNET=True` in `.env` (it's the default). Your `src/config.py` respects this variable and will connect to testnet when enabled.

```


Security
-
Do NOT commit `.env` to version control. `.gitignore` is included to help.

# hemasree-binance-bot

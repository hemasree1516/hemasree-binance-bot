import os
import logging
from dotenv import load_dotenv, find_dotenv
from binance.client import Client

# 1. This finds the .env file even if you are in a different folder
load_dotenv(find_dotenv())

# 2. Get API Keys
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
# Default to False unless user explicitly enables testnet in .env
USE_TESTNET = os.getenv('USE_TESTNET', 'False').lower() in ('1', 'true', 'yes')

# 3. DEBUG CHECK: This will help us see if keys are missing
if not API_KEY or not API_SECRET:
    print("❌ ERROR: API Keys not found! Check your .env file. See .env.example")
else:
    print("✅ API Keys loaded successfully.")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

try:
    # Add a JSON-like structured logger for convenience
    import json
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            base = {
                'time': self.formatTime(record),
                'level': record.levelname,
                'message': record.getMessage()
            }
            if record.exc_info:
                base['exception'] = self.formatException(record.exc_info)
            return json.dumps(base)

    fh = logging.FileHandler('bot.log')
    fh.setFormatter(JsonFormatter())
    logger.addHandler(fh)
except Exception:
    # best-effort; fallback to default formatting
    pass

def get_client():
    client = Client(API_KEY, API_SECRET, testnet=USE_TESTNET)
    try:
        # When using futures testnet, python-binance may still keep the
        # default production FUTURES URL. Force the well-known testnet
        # endpoints so futures methods use testnet when requested.
        if USE_TESTNET:
            try:
                client.API_URL = 'https://testnet.binance.vision/api'
            except Exception:
                pass
            # apply a futures testnet URL (best-effort; keys must be testnet keys)
            try:
                client.FUTURES_API_URL = 'https://testnet.binancefuture.com'
                client.FUTURES_URL = 'https://testnet.binancefuture.com'
            except Exception:
                pass

        # expose current API URLs for diagnostics
        api_url = getattr(client, 'API_URL', None)
        fut_url = getattr(client, 'FUTURES_API_URL', None) or getattr(client, 'FUTURES_URL', None)
        logger.info('Created Binance Client (testnet=%s) api_url=%s futures_api=%s', USE_TESTNET, api_url, fut_url)
    except Exception:
        pass
    return client

from src.config import get_client, logger

def check_connection():
    client = get_client()
    try:
        # This only requires 'Enable Reading' permission
        info = client.futures_account_balance()
        print("✅ CONNECTION SUCCESS!")
        print(f"Your Wallet Balance: {info[0]['balance']} USDT")
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {str(e)}")

if __name__ == "__main__":
    check_connection()
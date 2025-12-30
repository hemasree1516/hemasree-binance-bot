import sys
from src.config import get_client, logger

def place_market_order(symbol, side, quantity):
    client = get_client()
    try:
        logger.info(f"Attempting {side} Market Order for {symbol}...")
        order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side.upper(),
            type='MARKET',
            quantity=quantity
        )
        logger.info(f"SUCCESS: Order ID {order['orderId']} executed.")
        return order
    except Exception as e:
        logger.error(f"FAILED: {str(e)}")

if __name__ == "__main__":
    # Example usage: python src/market_orders.py BTCUSDT BUY 0.01
    if len(sys.argv) > 3:
        place_market_order(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python market_orders.py <symbol> <side> <qty>")
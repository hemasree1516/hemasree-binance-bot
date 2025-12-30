import sys
from src.config import get_client, logger

def place_limit_order(symbol, side, quantity, price, time_in_force='GTC'):
    client = get_client()
    try:
        logger.info(f"Attempting {side} Limit Order for {symbol} @ {price}...")

        order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side.upper(),
            type='LIMIT',
            timeInForce=time_in_force,
            quantity=quantity,
            price=str(price)
        )
        logger.info(f"SUCCESS: Limit Order ID {order['orderId']} placed.")
        return order
    except Exception as e:
        logger.error(f"FAILED: {str(e)}")


if __name__ == "__main__":
    # Example usage: python src/limit_orders.py BTCUSDT BUY 0.01 40000
    if len(sys.argv) > 4:
        place_limit_order(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: python limit_orders.py <symbol> <side> <qty> <price>")

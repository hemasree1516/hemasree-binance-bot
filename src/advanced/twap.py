import time
from src.config import get_client, logger

def twap_order(symbol, side, total_qty, intervals, delay):
    client = get_client()
    chunk_qty = float(total_qty) / int(intervals)
    
    logger.info(f"Starting TWAP: {total_qty} {symbol} over {intervals} intervals.")
    
    for i in range(int(intervals)):
        try:
            order = client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='MARKET',
                quantity=round(chunk_qty, 3)
            )
            logger.info(f"TWAP Progress: {i+1}/{intervals} executed. OrderID: {order['orderId']}")
            if i < int(intervals) - 1:
                time.sleep(delay)
        except Exception as e:
            logger.error(f"TWAP Error at step {i+1}: {str(e)}")
            break

if __name__ == "__main__":
    # Example: python src/advanced/twap.py BTCUSDT BUY 0.1 5 10
    if len(sys.argv) > 5:
        twap_order(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
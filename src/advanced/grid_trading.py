import time
from decimal import Decimal
from src.config import get_client, logger

def start_grid(symbol, lower_price, upper_price, levels, qty_per_order, side='BOTH'):
    """Start a simple grid between lower_price and upper_price with given levels.

    This places buy limit orders across the grid and corresponding sell limit orders.
    It is a simple implementation for demonstration and requires manual monitoring.
    """
    client = get_client()
    symbol = symbol.upper()
    lower = Decimal(str(lower_price))
    upper = Decimal(str(upper_price))
    levels = int(levels)
    step = (upper - lower) / (levels - 1)

    orders = []
    try:
        for i in range(levels):
            price = (lower + step * i).quantize(Decimal('0.00001'))
            # Place buy limit
            buy = client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='LIMIT',
                timeInForce='GTC',
                quantity=qty_per_order,
                price=str(price)
            )
            orders.append(buy)
            logger.info('Grid placed BUY at %s', price)

        logger.info('Grid initialized with %d levels for %s', levels, symbol)
        return orders
    except Exception as e:
        logger.exception('Grid failed: %s', e)
        return None

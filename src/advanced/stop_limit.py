from src.config import get_client, logger

def place_stop_limit(symbol, side, quantity, stop_price, limit_price, time_in_force='GTC'):
    """Place a STOP-LIMIT by creating a STOP order that places a limit when triggered.

    Implemented by placing a STOP_LIMIT order using Binance 'STOP' type with 'price' and 'stopPrice'.
    """
    client = get_client()
    try:
        order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side.upper(),
            type='STOP',
            quantity=quantity,
            price=str(limit_price),
            stopPrice=str(stop_price),
            timeInForce=time_in_force
        )
        logger.info('Stop-Limit placed: %s', order.get('orderId'))
        return order
    except Exception as e:
        logger.exception('Stop-Limit failed: %s', e)
        return None

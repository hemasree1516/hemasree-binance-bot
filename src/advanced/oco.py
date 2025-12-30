import time
from src.config import get_client, logger

def place_oco(symbol, side, quantity, tp_price, sl_price, poll_interval=2, timeout=300):
    """Place a take-profit limit and a stop-market (stop-loss) and cancel the other when one fills.

    Note: Binance Futures doesn't have a single OCO endpoint; this implements an app-level OCO via polling.
    """
    client = get_client()
    side = side.upper()
    try:
        logger.info('Placing OCO orders for %s %s qty=%s TP=%s SL=%s', symbol, side, quantity, tp_price, sl_price)

        # Place take-profit (LIMIT) order
        tp_order = client.futures_create_order(
            symbol=symbol.upper(),
            side='SELL' if side == 'BUY' else 'BUY',
            type='LIMIT',
            timeInForce='GTC',
            quantity=quantity,
            price=str(tp_price)
        )

        # Place stop-loss (STOP_MARKET) order
        sl_order = client.futures_create_order(
            symbol=symbol.upper(),
            side='SELL' if side == 'BUY' else 'BUY',
            type='STOP_MARKET',
            stopPrice=str(sl_price),
            quantity=quantity
        )

        tp_id = tp_order['orderId']
        sl_id = sl_order['orderId']
        start = time.time()

        # Poll for fills
        while time.time() - start < timeout:
            tp_status = client.futures_get_order(symbol=symbol.upper(), orderId=tp_id)
            sl_status = client.futures_get_order(symbol=symbol.upper(), orderId=sl_id)

            if tp_status.get('status') == 'FILLED':
                logger.info('TP filled. Cancelling SL %s', sl_id)
                client.futures_cancel_order(symbol=symbol.upper(), orderId=sl_id)
                return {'filled':'tp', 'order': tp_status}

            if sl_status.get('status') in ('FILLED','PARTIALLY_FILLED'):
                logger.info('SL filled. Cancelling TP %s', tp_id)
                client.futures_cancel_order(symbol=symbol.upper(), orderId=tp_id)
                return {'filled':'sl', 'order': sl_status}

            time.sleep(poll_interval)

        logger.warning('OCO timeout reached; leaving both orders active')
        return {'filled':None}

    except Exception as e:
        logger.exception('OCO placement failed: %s', e)
        return None

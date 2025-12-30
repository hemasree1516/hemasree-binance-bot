from decimal import Decimal, getcontext
from src.config import logger

getcontext().prec = 18

def _find_filter(filters, filter_type):
    for f in filters:
        if f.get('filterType') == filter_type:
            return f
    return None

def validate_symbol(client, symbol):
    try:
        info = client.futures_exchange_info()
        for s in info.get('symbols', []):
            if s['symbol'].upper() == symbol.upper():
                return s
    except Exception as e:
        logger.error('validate_symbol error: %s', e)
    return None

def validate_quantity(symbol_info, qty):
    try:
        qty = Decimal(str(qty))
        lot = _find_filter(symbol_info['filters'], 'LOT_SIZE')
        if not lot:
            return False, 'LOT_SIZE filter not found'
        min_qty = Decimal(lot['minQty'])
        max_qty = Decimal(lot['maxQty'])
        step = Decimal(lot['stepSize'])
        if qty < min_qty or qty > max_qty:
            return False, f'Quantity {qty} outside [{min_qty}, {max_qty}]'
        # check step alignment
        remainder = (qty - min_qty) % step
        if remainder != 0:
            return False, f'Quantity {qty} not multiple of step {step}'
        return True, ''
    except Exception as e:
        return False, str(e)

def validate_price(symbol_info, price):
    try:
        price = Decimal(str(price))
        tick = _find_filter(symbol_info['filters'], 'PRICE_FILTER')
        if not tick:
            return False, 'PRICE_FILTER not found'
        min_price = Decimal(tick['minPrice'])
        max_price = Decimal(tick['maxPrice'])
        tick_size = Decimal(tick['tickSize'])
        if price < min_price or price > max_price:
            return False, f'Price {price} outside [{min_price}, {max_price}]'
        remainder = (price - min_price) % tick_size
        if remainder != 0:
            return False, f'Price {price} not aligned to tickSize {tick_size}'
        return True, ''
    except Exception as e:
        return False, str(e)

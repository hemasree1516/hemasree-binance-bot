import pytest
from src.validation import validate_symbol, validate_quantity, validate_price


class FakeClient:
    def __init__(self, symbols):
        self._symbols = symbols

    def futures_exchange_info(self):
        return {'symbols': self._symbols}


def make_symbol(symbol='BTCUSDT'):
    return {
        'symbol': symbol,
        'filters': [
            {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'},
            {'filterType': 'PRICE_FILTER', 'minPrice': '0.01', 'maxPrice': '1000000', 'tickSize': '0.01'},
        ]
    }


def test_validate_symbol_found():
    client = FakeClient([make_symbol()])
    res = validate_symbol(client, 'BTCUSDT')
    assert res is not None and res['symbol'] == 'BTCUSDT'


def test_validate_symbol_not_found():
    client = FakeClient([make_symbol('ETHUSDT')])
    assert validate_symbol(client, 'BTCUSDT') is None


def test_validate_quantity_valid():
    symbol = make_symbol()
    ok, msg = validate_quantity(symbol, '0.005')
    assert ok


def test_validate_quantity_too_small():
    symbol = make_symbol()
    ok, msg = validate_quantity(symbol, '0.0001')
    assert not ok


def test_validate_quantity_step_mismatch():
    symbol = make_symbol()
    ok, msg = validate_quantity(symbol, '0.0025')
    assert not ok


def test_validate_price_valid():
    symbol = make_symbol()
    ok, msg = validate_price(symbol, '100.00')
    assert ok


def test_validate_price_out_of_range():
    symbol = make_symbol()
    ok, msg = validate_price(symbol, '1000001')
    assert not ok


def test_validate_price_tick_mismatch():
    symbol = make_symbol()
    ok, msg = validate_price(symbol, '100.005')
    assert not ok

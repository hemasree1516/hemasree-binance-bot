import time
from src.advanced.oco import place_oco
from src.advanced.stop_limit import place_stop_limit
from src.advanced.grid_trading import start_grid


def test_place_oco_tp_filled(monkeypatch):
    class FakeOCOClient:
        def __init__(self):
            self.get_calls = 0
            self.tp_id = 101
            self.sl_id = 202

        def futures_create_order(self, **kwargs):
            if kwargs.get('type') == 'LIMIT':
                return {'orderId': self.tp_id}
            return {'orderId': self.sl_id}

        def futures_get_order(self, symbol, orderId):
            self.get_calls += 1
            if orderId == self.tp_id:
                if self.get_calls >= 2:
                    return {'orderId': orderId, 'status': 'FILLED'}
                return {'orderId': orderId, 'status': 'NEW'}
            return {'orderId': orderId, 'status': 'NEW'}

        def futures_cancel_order(self, symbol, orderId):
            return {'orderId': orderId, 'status': 'CANCELED'}

    import src.advanced.oco as oco_mod
    monkeypatch.setattr(oco_mod, 'get_client', lambda: FakeOCOClient(), raising=False)

    res = place_oco('BTCUSDT', 'BUY', 0.001, tp_price=50000, sl_price=40000, poll_interval=0.01, timeout=1)
    assert res is not None
    assert res.get('filled') == 'tp'


def test_place_stop_limit_calls_client(monkeypatch):
    class FakeClient:
        def __init__(self):
            self.called = False

        def futures_create_order(self, **kwargs):
            self.called = True
            return {'orderId': 55}

    fake = FakeClient()
    import src.advanced.stop_limit as sl_mod
    monkeypatch.setattr(sl_mod, 'get_client', lambda: fake, raising=False)

    order = place_stop_limit('BTCUSDT', 'SELL', 0.001, stop_price=30000, limit_price=29900)
    assert order is not None
    assert fake.called


def test_start_grid_places_levels(monkeypatch):
    calls = []

    class FakeGridClient:
        def futures_create_order(self, **kwargs):
            calls.append(kwargs)
            return {'orderId': len(calls)}

    import src.advanced.grid_trading as grid_mod
    monkeypatch.setattr(grid_mod, 'get_client', lambda: FakeGridClient(), raising=False)

    orders = start_grid('BTCUSDT', 25000, 26000, 5, 0.001)
    assert orders is not None
    assert len(orders) == 5
    assert len(calls) == 5

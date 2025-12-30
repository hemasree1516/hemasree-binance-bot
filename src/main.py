import argparse
import sys
from src.config import logger
from src.check_account import check_connection
from src.market_orders import place_market_order
from src.limit_orders import place_limit_order
from src.advanced.twap import twap_order


def main():
    parser = argparse.ArgumentParser(description='Binance Futures Order Bot CLI')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('check', help='Check connection and wallet balance')

    mk = sub.add_parser('market', help='Place a MARKET order')
    mk.add_argument('symbol')
    mk.add_argument('side', choices=['BUY', 'SELL'])
    mk.add_argument('quantity')

    lm = sub.add_parser('limit', help='Place a LIMIT order')
    lm.add_argument('symbol')
    lm.add_argument('side', choices=['BUY', 'SELL'])
    lm.add_argument('quantity')
    lm.add_argument('price')

    tw = sub.add_parser('twap', help='Run a TWAP order')
    tw.add_argument('symbol')
    tw.add_argument('side', choices=['BUY', 'SELL'])
    tw.add_argument('total_qty')
    tw.add_argument('intervals', type=int)
    tw.add_argument('delay', type=int, help='seconds between slices')

    sl = sub.add_parser('stoplimit', help='Place a STOP-LIMIT order')
    sl.add_argument('symbol')
    sl.add_argument('side', choices=['BUY', 'SELL'])
    sl.add_argument('quantity')
    sl.add_argument('stop_price')
    sl.add_argument('limit_price')

    oco = sub.add_parser('oco', help='Place OCO (TP+SL) via app-level polling')
    oco.add_argument('symbol')
    oco.add_argument('side', choices=['BUY', 'SELL'])
    oco.add_argument('quantity')
    oco.add_argument('tp_price')
    oco.add_argument('sl_price')

    grid = sub.add_parser('grid', help='Start a simple grid')
    grid.add_argument('symbol')
    grid.add_argument('lower')
    grid.add_argument('upper')
    grid.add_argument('levels')
    grid.add_argument('qty')

    args = parser.parse_args()

    if args.command == 'check':
        check_connection()
    elif args.command == 'market':
        place_market_order(args.symbol, args.side, args.quantity)
    elif args.command == 'limit':
        place_limit_order(args.symbol, args.side, args.quantity, args.price)
    elif args.command == 'twap':
        twap_order(args.symbol, args.side, args.total_qty, args.intervals, args.delay)
    elif args.command == 'stoplimit':
        from src.advanced.stop_limit import place_stop_limit
        place_stop_limit(args.symbol, args.side, args.quantity, args.stop_price, args.limit_price)
    elif args.command == 'oco':
        from src.advanced.oco import place_oco
        place_oco(args.symbol, args.side, args.quantity, args.tp_price, args.sl_price)
    elif args.command == 'grid':
        from src.advanced.grid_trading import start_grid
        start_grid(args.symbol, args.lower, args.upper, args.levels, args.qty)
    else:
        parser.print_help()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception('Unhandled error in CLI: %s', e)
        sys.exit(1)

import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

DATA_PATH = Path(__file__).parents[2] / 'data' / 'historical_data.csv'


def load_data(path=DATA_PATH):
    df = pd.read_csv(path, parse_dates=['Timestamp IST'])
    return df


def apply_slippage(price, side, slippage_pct):
    s = float(slippage_pct) / 100.0
    if side.upper() == 'BUY':
        return price * (1.0 + s)
    else:
        return price * (1.0 - s)


def simulate_twap(total_qty, intervals, side='BUY', slippage_pct=0.02, fee_pct=0.04, out_dir=None):
    df = load_data()
    df = df.sort_values('Timestamp IST').reset_index(drop=True)
    intervals = int(intervals)
    chunk = float(total_qty) / intervals
    slice_df = df.head(intervals).copy()
    executed = []
    total_notional = 0.0
    total_fees = 0.0

    for _, row in slice_df.iterrows():
        market_price = float(row['Execution Price'])
        exec_price = apply_slippage(market_price, side, slippage_pct)
        notional = exec_price * chunk
        fee = notional * (fee_pct / 100.0)
        total_notional += notional
        total_fees += fee
        executed.append({'ts': row['Timestamp IST'], 'exec_price': exec_price, 'qty': chunk, 'fee': fee})

    avg_price = total_notional / float(total_qty)
    last_price = float(df['Execution Price'].iloc[-1])

    if side.upper() == 'BUY':
        pnl = (last_price - avg_price) * float(total_qty) - total_fees
    else:
        pnl = (avg_price - last_price) * float(total_qty) - total_fees

    res_df = pd.DataFrame(executed)
    res_df['cumulative_fee'] = res_df['fee'].cumsum()
    res_df['cumulative_qty'] = res_df['qty'].cumsum()
    res_df['avg_price_so_far'] = (res_df['exec_price'] * res_df['qty']).cumsum() / res_df['cumulative_qty']

    if not out_dir:
        out_dir = Path(__file__).parents[2] / 'data'
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = out_dir / 'twap_pnl.png'
    plt.figure(figsize=(8, 4))
    plt.plot(pd.to_datetime(res_df['ts']), res_df['avg_price_so_far'], marker='o', label='avg_exec_price')
    plt.axhline(last_price, color='green', linestyle='--', label='last_price')
    plt.title(f'TWAP average exec price vs last price (pnl={pnl:.4f})')
    plt.xlabel('Timestamp IST')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(img)
    plt.close()
    return {'executions': res_df, 'avg_price': avg_price, 'pnl': pnl}, img


def simulate_grid(lower_price, upper_price, levels, qty_per_order, slippage_pct=0.02, fee_pct=0.04, out_dir=None):
    df = load_data()
    df = df.sort_values('Timestamp IST').reset_index(drop=True)
    lower = float(lower_price)
    upper = float(upper_price)
    levels = int(levels)
    step = (upper - lower) / max(1, (levels - 1))
    grid_prices = [lower + i * step for i in range(levels)]

    fills = []
    for price in grid_prices:
        filled_idx = None
        buy_price_market = None
        for idx, row in df.iterrows():
            if float(row['Execution Price']) <= price:
                filled_idx = idx
                buy_price_market = float(row['Execution Price'])
                break

        if filled_idx is None:
            continue

        buy_price = apply_slippage(buy_price_market, 'BUY', slippage_pct)
        buy_fee = buy_price * float(qty_per_order) * (fee_pct / 100.0)

        sell_price_market = None
        for idx2 in range(filled_idx + 1, len(df)):
            p2 = float(df.at[idx2, 'Execution Price'])
            if p2 > buy_price_market:
                sell_price_market = p2
                break
        if sell_price_market is None:
            sell_price_market = float(df['Execution Price'].iloc[-1])

        sell_price = apply_slippage(sell_price_market, 'SELL', slippage_pct)
        sell_fee = sell_price * float(qty_per_order) * (fee_pct / 100.0)

        pnl = (sell_price - buy_price) * float(qty_per_order) - (buy_fee + sell_fee)
        fills.append({'level_price': price, 'buy_ts': df.at[filled_idx, 'Timestamp IST'], 'buy_price': buy_price, 'sell_price': sell_price, 'pnl': pnl})

    res_df = pd.DataFrame(fills)

    if not out_dir:
        out_dir = Path(__file__).parents[2] / 'data'
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = out_dir / 'grid_pnl.png'
    plt.figure(figsize=(8, 4))
    if not res_df.empty:
        plt.bar(res_df['level_price'].astype(str), res_df['pnl'])
    plt.title('Grid PnL per filled level')
    plt.xlabel('Grid Level Price')
    plt.ylabel('PnL')
    plt.tight_layout()
    plt.savefig(img)
    plt.close()
    return {'fills': res_df, 'total_pnl': res_df['pnl'].sum() if not res_df.empty else 0.0}, img


def cli():
    import argparse
    parser = argparse.ArgumentParser(description='Backtester for TWAP and Grid using historical CSV')
    sub = parser.add_subparsers(dest='cmd')
    t = sub.add_parser('twap')
    t.add_argument('total_qty')
    t.add_argument('intervals', type=int)
    t.add_argument('--side', choices=['BUY', 'SELL'], default='BUY')
    t.add_argument('--slippage', type=float, default=0.02, help='slippage percent')
    t.add_argument('--fee', type=float, default=0.04, help='fee percent')

    g = sub.add_parser('grid')
    g.add_argument('lower')
    g.add_argument('upper')
    g.add_argument('levels', type=int)
    g.add_argument('qty')
    g.add_argument('--slippage', type=float, default=0.02)
    g.add_argument('--fee', type=float, default=0.04)

    args = parser.parse_args()
    if args.cmd == 'twap':
        res, img = simulate_twap(args.total_qty, args.intervals, side=args.side, slippage_pct=args.slippage, fee_pct=args.fee)
        print('TWAP simulation complete. Chart saved to', img)
        print('Pnl:', res['pnl'])
    elif args.cmd == 'grid':
        res, img = simulate_grid(args.lower, args.upper, args.levels, args.qty, slippage_pct=args.slippage, fee_pct=args.fee)
        print('Grid simulation complete. Chart saved to', img)
        print('Total PnL:', res['total_pnl'])
    else:
        parser.print_help()


if __name__ == '__main__':
    cli()

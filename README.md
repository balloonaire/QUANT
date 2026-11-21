# 4Q Crypto Research Lab v3.1 — Hybrid Live Chart Intelligence

Research-only simulator. No real orders, prediction-market wagers, account connections, signing, or investment recommendations.

## Files
- `index.html`: mobile-first static dashboard (GitHub Pages compatible), preserving v3.0 features and 11 coins: BTC ETH SOL ARB ASTER AVAX DOT INJ TIA ARKM FIL.
- `server.py`: optional Python 3.10+ public-data gateway, including `/api/candles`.
- `test_v3.py`, `test_v31.py`: offline deterministic gateway tests.

## Launch
1. Extract ZIP; upload `index.html` to a GitHub Pages repository, enable Pages from main/root. Demo/backtesting and CSV import work without the gateway.
2. To run locally: `python server.py` (listens on loopback port 8787); serve HTML with `python -m http.server 8000` and visit `http://localhost:8000`.
3. For custom live candles, set Gateway URL in dashboard to `http://localhost:8787`, choose a coin and interval, click **Load candles**. To publish live feeds on GitHub Pages, deploy a separate secured HTTPS gateway and set `ALLOWED_ORIGIN` to your Pages origin. Do not put API secrets in HTML.
4. For TradingView, choose **TradingView embedded** in Chart source; its widget requires third-party scripts and network access. TradingView symbol support varies.
5. For historical paper simulation using real OHLCV closes, load candles then click **Backtest these candles**. This explicitly replaces the selected coin's demo data; other coins retain their original demo/imported data. Do not mix cross-coin correlations from different timestamps.

## v3.1 chart features
- Independent TradingView Advanced Chart embed, plus custom Lightweight Charts (v5 CDN); switchable per chart.
- Binance public market-data endpoint via Python gateway for 300 recent OHLCV bars; 1m, 5m, 15m, 1h, 4h, 1d, 1w. Some pairs (especially ASTER) may be unsupported. Failed requests report unavailable rather than inventing candles. Refresh is polling, not tick-level streaming.
- EMA 20/50 and Bollinger 20/2 overlays; RSI 14 and MACD 12/26/9 numerical readouts. Paper decision markers are shown only after an explicit backtest on matching exchange candle data.
- Full-screen button, responsive layout, optional refresh, candle CSV export. Liquidity context shows latest *snapshots* of USDT supply and BTC dominance; no invented historical overlays. DXY remains unavailable pending verified feed.
- v3.0 stablecoin supply, global market cap, public BTC/ETH/SOL address research, user-imported labeled whale transfers and exchange flows, heuristic signals, synthetic and imported historical backtests, paper portfolio and CSV exports preserved.

## Data provenance and limitations
- `GET /api/candles?coin=SOL&interval=1h` returns `{data:[{time,open,high,low,close,volume}],fetched_at,stale,source,caveat}`. Gateway caches for 30 seconds. Time is Unix UTC seconds. Last bar may be incomplete.
- `GET /api/market`, `/api/stablecoins`, `/api/global`, `/api/dxy`, `/api/wallet?chain=...&address=...` retain v3.0 semantics.
- Binance public market-data availability depends on geography, API policy and symbol listings; rate limits and errors are surfaced. TradingView embeds may be blocked by browsers, CSP, network policy, or provider restrictions. CDN availability required for custom chart rendering.
- Chart candles and TradingView may use different exchange feeds, time zones or pricing. No promise of exact matching. External data is not continuously collected by GitHub Pages alone.
- No real-time DXY source is included; DXY is not a measure of USD money flow. USDT circulating supply does not equal net exchange inflow; BTC dominance is market-cap share. Cross-market correlations require aligned historical timestamps.
- Wallet checks are public address statistics only, not chain-wide whale discovery. Exchange labels must be externally verified; imported transfers may double count.
- Backtesting is a simplified exposure model with friction, not a calibrated prediction or Polymarket settlement model. No walk-forward or out-of-sample validation. Simulated returns do not imply future profits.
- For production: HTTPS, API authentication, per-user quotas, provider terms review, secret management, monitoring, persistence and independent data QA.

## Tests
`python test_v3.py && python test_v31.py`
Extract inline JavaScript and run `node --check` to verify syntax. Browser smoke testing may be blocked by the execution environment's local-network policy; this is not evidence of browser validation.

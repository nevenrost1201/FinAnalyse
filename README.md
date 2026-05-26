# FinAnalyse

**An education & analysis tool for private investors** — fundamental stock analysis, portfolio
backtesting, and a structured learning academy, all in one Streamlit app.

> **Not investment advice.** FinAnalyse is an educational and analytical tool. All data is provided
> without warranty and may be delayed. Investing carries risk, including total loss.

---

## What it does

- **Dashboard** — live market overview (indices, crypto, commodities, FX) with clean sparkline mini-charts and a ticker search.
- **Single Analysis** — enter a ticker and get a **Quality Score**, **Value Score** and **PEG**, a verdict, qualitative templates (moat, risks), a data-verification tab and a downloadable investment memo. **Sector-aware scoring**: banks & insurers are valued via book value (P/B) and equity ratio instead of P/E and EV/EBITDA.
- **My Portfolio** — enter your real holdings for an exact value, money-weighted return (XIRR), a backtest of your mix (return p.a., Sharpe, max drawdown), value-since-purchase chart, a **scenario projection** (conservative / base / optimistic) and a cluster-risk / allocation overview.
- **Portfolio & Backtest** — test any stock mix historically with risk/return metrics and projections.
- **Learn** — two tracks:
  - *Fundamental analysis* (27 lessons, each with a 5–10 question test) plus an optional AI tutor.
  - *Portfolio Academy* — a structured **~38-hour** program across 8 modules and 26 lessons (foundations, risk & return, diversification & allocation, modern portfolio theory, costs & taxes, behaviour, withdrawal strategies, hands-on projects), each with a practical exercise.
- **Crypto** — educational portraits of 14 major cryptocurrencies plus the key concepts (blockchain, wallets, PoW/PoS, volatility, regulation).
- **Calculators** — compound interest / savings plan, emergency fund, fee impact, German tax estimator, withdrawal / 4% rule, position sizing, and a diversification lab.
- **Trilingual UI** (German / English / French) and a dark, premium theme.

## Tech stack

Python · Streamlit · yfinance · pandas · numpy · scipy · altair (optional: OpenAI for the AI tutor).

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501).

## Deploy (free public link)

1. Push this repo to GitHub (include `app.py`, `requirements.txt`, the `.streamlit/` folder).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, select the repo and `app.py`, and click **Deploy**.
3. You get a public URL you can share for testing.

### Optional API keys (Settings → Secrets, or `.streamlit/secrets.toml`)

```toml
OPENAI_API_KEY = "..."   # enables the AI tutor & AI company overview
NEWS_API_KEY   = "..."   # enables portfolio news
NEWS_PROVIDER  = "finnhub"   # or "marketaux"
```

Everything works without these keys — the AI/news sections simply show a hint instead.

## Project structure

```
app.py                 # the Streamlit app (all UI + logic)
test_app.py            # logic tests (run: python3 test_app.py)
requirements.txt       # dependencies
.streamlit/config.toml # dark theme
code_map.py            # prints an up-to-date map of the codebase
ANLEITUNG.md           # user & developer guide (German)
```

## Tests

```bash
python3 test_app.py    # should end with "ALLE TESTS BESTANDEN"
```

## Data & legal

Market data comes from Yahoo Finance via `yfinance` and is **not licensed for commercial
redistribution**; it can also be rate-limited. For any public/commercial use, switch to a licensed
data provider and have the legal texts reviewed by a lawyer. This project is for **education only and
is not investment advice**.

## License

Add a license of your choice (e.g. MIT) before publishing.

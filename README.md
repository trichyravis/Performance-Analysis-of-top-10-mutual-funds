
# Top 25 Mutual Fund Performance Analytics

Mountain Path Academy Streamlit dashboard using the Ravi1 navy-and-gold design system.

## Features

- Balanced 25-fund universe: five Direct–Growth schemes in each of five equity categories
- Five-year minimum NAV-history eligibility rule
- Category-relative selection score using five-year CAGR, Sharpe ratio, rolling-return consistency, downside risk and maximum drawdown
- Transparent AUM limitation: neutral weight until a verified dated scheme-AUM dataset is supplied
- Dynamic ranking across 1Y, 3Y, 5Y, YTD and available history
- CAGR, volatility, Sharpe, Sortino, VaR, CVaR and maximum drawdown
- Calendar-year and rolling-return analysis
- Lump-sum and SIP simulation
- Correlation heatmap and fund-level diagnostics
- Composite educational score, methodology sheet and Excel/CSV downloads
- Responsive Ravi1 navigation, profile footer and user guide

## Deploy

1. Upload `app.py`, `requirements.txt`, `.streamlit/config.toml` and this README to a GitHub repository.
2. In Streamlit Community Cloud, choose the repository and set the main file to `app.py`.
3. Deploy. Use **Refresh live NAV data** if the public NAV endpoint briefly times out.

Data is retrieved from the public MFAPI endpoint. This project is for education and is not investment advice.

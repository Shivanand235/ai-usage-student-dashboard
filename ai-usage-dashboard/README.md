# AI Usage & Impact Dashboard

## Stack
Python + pandas for reproducible cleaning; HTML/CSS/JavaScript + Chart.js for an interactive static dashboard; GitHub Pages for hosting.

## Run locally
1. Install Python 3.11+ and pandas: `python -m pip install pandas`
2. Run `python scripts/clean_data.py`
3. Open the project folder in VS Code and use Live Server to serve `index.html`. Do not open the HTML directly from disk because browser `fetch()` can be blocked.

## Publish
1. Confirm the data owner permits public publication. GitHub Pages requires a public repository for this free workflow, so the code and included data may be visible to anyone.
2. Create a public repository named `ai-usage-dashboard`.
3. Push the project files to the `main` branch.
4. In **Settings → Pages**, select **Deploy from a branch**, branch `main`, folder `/ (root)`, then Save.
5. Wait for the deployment, open the live link, and test charts, filters, table search, CSV download and mobile layout.

## Project structure
- `data/raw/`: original CSV (unchanged)
- `data/clean/`: cleaned CSV and JSON used by the dashboard
- `scripts/clean_data.py`: rerunnable cleaning pipeline
- `assets/app.js`: KPIs, charts, filters and searchable table
- `assets/style.css`: responsive styling
- `index.html`: dashboard page
- `cleaning_log.txt`: cleaning actions from the latest run

## Cleaning notes
The script removes exact duplicates, converts number-like text, standardises selected labels, blanks values beyond the task's plausibility limits, adds Age_Group, Usage_Band, Paid_User and Income_Band, then exports CSV and JSON. Missing values are not filled with averages.

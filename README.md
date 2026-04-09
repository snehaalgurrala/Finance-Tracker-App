# Personal Finance Tracker

A personal finance tracker web application built with Streamlit, Python, and SQLite.

## Features
- **Secure Authentication:** Simple username and encrypted password login mapping using `bcrypt`.
- **Dashboard:** Overview of your account balance, total income, expenses, and portfolio health.
- **Expense & Income Tracker:** Manage day-to-day transactions with category tags and date filtering. Track how much you spend and earn.
- **Portfolio Manager:** Keep track of your investments (Stocks, Mutual funds, Crypto etc.) with asset grouping, cap size, and current valuation vs invested metrics.
- **Interactive Visualizations:** Powered by Plotly to provide excellent aesthetic insights through pie charts and bar graphs.
- **Export Capabilities:** Export your expense and portfolio data directly to ready-to-view MS Excel (.xlsx) files easily.

## Local Setup

### 1. Create a virtual environment (Optional but Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```

## Database
This application uses a local SQLite database named `finance_tracker.db` by default. It will automatically be created on the very first run in your repository directory.
To upgrade to PostgreSQL in the future, simply modify the `DATABASE_URL` environment variable within `database.py` to point to a valid PG connection string. 

## Data Backup
Since the data is stored in a SQLite file locally (`finance_tracker.db`), please periodically copy and backup this file to avoid data loss.

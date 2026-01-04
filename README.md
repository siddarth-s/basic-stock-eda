# Stock EDA - Exploratory Data Analysis Tool

A modular Python tool for stock market analysis with customizable trading strategies.

## Features

- **Interactive UI**: Simple Jupyter notebook interface with widgets
- **Multiple Strategies**: DCA, lump sum, intraday trading
- **Modular Design**: Easy to add custom strategies
- **Visual Analytics**: Stock price charts and performance metrics
- **Real Data**: Uses yfinance for historical stock data

## Quick Start

```bash
# Run setup (installs uv, creates venv, installs dependencies)
python setup.py

# Activate environment
source .venv/bin/activate

# Start Jupyter
jupyter notebook

# Open stock_analysis.ipynb and select 'stock-eda' kernel
```

## Project Structure

```
stock-eda/
├── strategies/          # Trading strategy modules
│   ├── __init__.py
│   ├── base.py         # Base strategy class
│   ├── dca_friday.py   # DCA every Friday
│   ├── buy_once.py     # Lump sum investment
│   ├── intraday.py     # Buy 4pm, sell 9am
│   ├── intraday_hold_profit.py  # Intraday, only sell when profitable
│   └── earnings_play.py # Earnings-based trading
├── tests/              # Unit tests
│   ├── conftest.py     # Test fixtures
│   ├── test_base.py
│   ├── test_buy_once.py
│   ├── test_dca_friday.py
│   ├── test_intraday.py
│   ├── test_intraday_hold_profit.py
│   └── test_earnings_play.py
├── stock_analysis.ipynb # Main notebook with UI
├── setup.py            # Environment setup script
├── pyproject.toml      # Dependencies
├── pytest.ini          # Pytest configuration
└── README.md
```

## Usage

1. Open `stock_analysis.ipynb` in Jupyter
2. Run all cells to display the UI
3. Enter:
   - **Ticker**: Stock symbol (e.g., AAPL, MSFT)
   - **Start/End Date**: Date range for analysis
   - **Amount**: Investment amount in USD
   - **Strategy**: Select from dropdown
4. Click "Analyze" to see results

## Adding Custom Strategies

Create a new file in `strategies/` inheriting from `BaseStrategy`:

```python
from strategies.base import BaseStrategy
import pandas as pd

class MyStrategy(BaseStrategy):
    """Your custom strategy."""
    
    def execute(self, data: pd.DataFrame, amount: float) -> dict:
        # Implement your logic
        return {
            'shares': shares_bought,
            'total_cost': total_spent,
            'final_value': current_value,
            'transactions': transaction_list
        }
```

Register in `strategies/__init__.py` and the notebook will automatically detect it.

## Requirements

- Python 3.10+
- uv (installed automatically by setup.py)

## Dependencies

- yfinance: Stock data
- pandas/numpy: Data processing
- matplotlib: Visualization
- ipywidgets: Interactive UI
- jupyter: Notebook environment
- pytest: Testing framework (dev dependency)

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=strategies --cov-report=html

# Run specific test file
pytest tests/test_buy_once.py

# Run with verbose output
pytest -v
```

To install dev dependencies including pytest:

```bash
pip install -e ".[dev]"
```

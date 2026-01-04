# Stock EDA Testing

This directory contains comprehensive unit tests for all trading strategies.

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=strategies --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_buy_once.py
```

### Run with verbose output:
```bash
pytest -v
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_base.py` - Tests for BaseStrategy abstract class
- `test_buy_once.py` - Tests for Buy All At Once strategy
- `test_dca_friday.py` - Tests for DCA Every Friday strategy
- `test_intraday.py` - Tests for Intraday (4PM-9AM) strategy
- `test_intraday_hold_profit.py` - Tests for Intraday Hold Profit strategy
- `test_earnings_play.py` - Tests for Earnings Play strategy

## Test Coverage

Each strategy is tested for:
- Basic execution and correct output structure
- Edge cases (empty data, single day, etc.)
- Strategy-specific logic (e.g., only buying on Fridays for DCA)
- Mathematical correctness (shares, costs, gains)
- Transaction integrity (buy/sell pairs, timing)

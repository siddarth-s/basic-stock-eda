"""Pytest configuration and shared fixtures."""

import pytest
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    # Filter to business days only
    dates = dates[dates.weekday < 5]
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': [100 + i * 0.1 for i in range(len(dates))],
        'High': [102 + i * 0.1 for i in range(len(dates))],
        'Low': [98 + i * 0.1 for i in range(len(dates))],
        'Close': [101 + i * 0.1 for i in range(len(dates))],
        'Volume': [1000000] * len(dates)
    })
    
    return data


@pytest.fixture
def volatile_stock_data():
    """Create volatile stock data with ups and downs."""
    dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
    dates = dates[dates.weekday < 5][:30]
    
    # Create price pattern that goes up and down
    import numpy as np
    base_price = 100
    prices = []
    for i in range(len(dates)):
        # Sine wave pattern for volatility
        variation = 10 * np.sin(i / 3)
        prices.append(base_price + variation)
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': [p - 1 for p in prices],
        'High': [p + 2 for p in prices],
        'Low': [p - 2 for p in prices],
        'Close': prices,
        'Volume': [1000000] * len(dates)
    })
    
    return data


@pytest.fixture
def declining_stock_data():
    """Create declining stock data."""
    dates = pd.date_range(start='2023-01-01', periods=60, freq='D')
    dates = dates[dates.weekday < 5][:30]
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': [100 - i * 0.5 for i in range(len(dates))],
        'High': [102 - i * 0.5 for i in range(len(dates))],
        'Low': [98 - i * 0.5 for i in range(len(dates))],
        'Close': [100 - i * 0.5 for i in range(len(dates))],
        'Volume': [1000000] * len(dates)
    })
    
    return data


@pytest.fixture
def empty_stock_data():
    """Create empty stock data."""
    return pd.DataFrame({
        'Date': pd.DatetimeIndex([]),
        'Open': [],
        'High': [],
        'Low': [],
        'Close': [],
        'Volume': []
    })


@pytest.fixture
def investment_amount():
    """Standard investment amount for testing."""
    return 10000.0

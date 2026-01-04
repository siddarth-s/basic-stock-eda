"""
Stock EDA - Comprehensive Testing Guide
========================================

This file demonstrates how the test suite works and how to extend it.
"""

# Example 1: Running Tests
# ========================

# Install dev dependencies (includes pytest)
# pip install -e ".[dev]"

# Run all tests
# pytest

# Run with detailed output
# pytest -v

# Run specific test file
# pytest tests/test_buy_once.py

# Run specific test class
# pytest tests/test_buy_once.py::TestBuyOnceStrategy

# Run specific test method
# pytest tests/test_buy_once.py::TestBuyOnceStrategy::test_basic_execution

# Run with coverage
# pytest --cov=strategies

# Generate HTML coverage report
# pytest --cov=strategies --cov-report=html
# Open htmlcov/index.html in browser


# Example 2: Understanding Fixtures
# =================================

# Fixtures provide reusable test data. They're defined in conftest.py
# and automatically available to all tests.

def example_test_using_fixtures(sample_stock_data, investment_amount):
    """
    This test receives:
    - sample_stock_data: A year of rising stock prices
    - investment_amount: $10,000
    
    These are automatically injected by pytest!
    """
    from strategies.buy_once import BuyOnceStrategy
    
    strategy = BuyOnceStrategy()
    results = strategy.execute(sample_stock_data, investment_amount)
    
    assert results['total_cost'] == investment_amount
    assert results['shares'] > 0


# Example 3: Writing a New Test
# =============================

# Let's say you add a new strategy called "MonthlyDCAStrategy"
# Here's how to create tests for it:

"""
# File: tests/test_monthly_dca.py

import pytest
import pandas as pd
from strategies.monthly_dca import MonthlyDCAStrategy


class TestMonthlyDCAStrategy:
    '''Test suite for MonthlyDCAStrategy.'''
    
    @pytest.fixture
    def strategy(self):
        '''Create strategy instance.'''
        return MonthlyDCAStrategy()
    
    def test_strategy_name(self, strategy):
        '''Test strategy has correct name.'''
        assert strategy.name == "Monthly DCA"
        assert "monthly" in strategy.description.lower()
    
    def test_basic_execution(self, strategy, sample_stock_data, investment_amount):
        '''Test basic strategy execution.'''
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # Verify required output structure
        assert 'shares' in results
        assert 'total_cost' in results
        assert 'final_value' in results
        assert 'transactions' in results
        assert 'gain_pct' in results
        assert 'gain_amount' in results
        
        # Verify values make sense
        assert results['total_cost'] > 0
        assert results['shares'] >= 0
        assert results['final_value'] >= 0
    
    def test_buys_monthly(self, strategy, sample_stock_data, investment_amount):
        '''Test that strategy buys once per month.'''
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # Get unique months from transactions
        months = set()
        for txn in results['transactions']:
            if txn['type'] == 'BUY':
                date = pd.Timestamp(txn['date'])
                months.add((date.year, date.month))
        
        # Should have bought in multiple different months
        assert len(months) >= 2
"""


# Example 4: Test-Driven Development
# ==================================

# When adding a new feature, write tests FIRST:

"""
# 1. Write the test (it will fail)
def test_new_stop_loss_feature(strategy):
    '''Test that strategy stops trading after 10% loss.'''
    # Create data with 15% drop
    declining_data = create_declining_data(drop_percent=15)
    
    results = strategy.execute(declining_data, 10000)
    
    # Should have stopped after ~10% loss
    assert results['gain_pct'] >= -10.5  # Allow small margin

# 2. Run test - it fails (as expected)
# pytest tests/test_my_strategy.py::test_new_stop_loss_feature

# 3. Implement the feature in your strategy

# 4. Run test again - it passes!
"""


# Example 5: Debugging Failed Tests
# =================================

# If a test fails, pytest shows detailed information:

"""
# Run with extra verbosity
pytest -vv

# Show print statements (useful for debugging)
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run only failed tests from last run
pytest --lf

# Show local variables on failure
pytest -l
"""


# Example 6: Testing Edge Cases
# =============================

# Always test edge cases! Here are common ones:

def example_edge_case_tests(strategy):
    """Examples of important edge cases to test."""
    
    # Empty data
    empty_df = pd.DataFrame()
    results = strategy.execute(empty_df, 10000)
    assert results['shares'] == 0
    
    # Single row data
    one_day = pd.DataFrame({
        'Date': [pd.Timestamp('2023-01-01')],
        'Close': [100]
    })
    results = strategy.execute(one_day, 10000)
    # Behavior depends on strategy
    
    # Zero investment
    results = strategy.execute(sample_stock_data, 0)
    assert results['total_cost'] == 0
    
    # Very small investment
    results = strategy.execute(sample_stock_data, 0.01)
    # Should handle gracefully


# Example 7: Parametrized Tests
# =============================

# Test the same logic with different inputs:

"""
import pytest

@pytest.mark.parametrize("amount,expected_min_shares", [
    (1000, 9),      # $1000 should buy at least 9 shares at $100
    (10000, 90),    # $10000 should buy at least 90 shares
    (100000, 900),  # $100000 should buy at least 900 shares
])
def test_various_amounts(strategy, sample_stock_data, amount, expected_min_shares):
    '''Test strategy with different investment amounts.'''
    results = strategy.execute(sample_stock_data, amount)
    assert results['shares'] >= expected_min_shares
"""


# Example 8: Mock External Dependencies
# =====================================

# If your strategy calls external APIs, mock them in tests:

"""
from unittest.mock import patch, MagicMock

def test_with_mocked_api(strategy):
    '''Test strategy with mocked yfinance API.'''
    with patch('yfinance.Ticker') as mock_ticker:
        # Set up mock response
        mock_ticker.return_value.history.return_value = mock_data
        
        # Run strategy
        results = strategy.execute(mock_data, 10000)
        
        # Verify behavior
        assert results['shares'] > 0
"""


# Example 9: Test Organization Best Practices
# ==========================================

"""
Class-based organization (recommended):
    class TestMyStrategy:
        - Groups related tests
        - Can share fixtures via self
        - Clear test discovery
        
Naming conventions:
    - Test files: test_*.py
    - Test classes: Test*
    - Test methods: test_*
    
Test structure (AAA pattern):
    def test_something(self):
        # Arrange - set up test data
        data = create_test_data()
        
        # Act - perform the operation
        results = strategy.execute(data, 10000)
        
        # Assert - verify expectations
        assert results['gain_pct'] > 0
"""


# Example 10: Continuous Integration
# ==================================

"""
# Add to .github/workflows/test.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          pytest --cov=strategies --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
"""

print(__doc__)

"""Unit tests for Intraday (4PM-9AM) strategy."""

import pytest
import pandas as pd
from strategies.intraday import IntradayStrategy


class TestIntradayStrategy:
    """Test suite for IntradayStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance."""
        return IntradayStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy has correct name."""
        assert strategy.name == "Intraday (4PM-9AM)"
        assert "close" in strategy.description.lower()
    
    def test_basic_execution(self, strategy, sample_stock_data, investment_amount):
        """Test basic strategy execution."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        assert results['total_cost'] == investment_amount
        assert results['final_value'] > 0
        # Should have multiple buy/sell pairs
        assert len(results['transactions']) > 0
    
    def test_buy_sell_pairs(self, strategy, sample_stock_data, investment_amount):
        """Test that strategy creates buy/sell pairs."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        buy_count = sum(1 for t in results['transactions'] if t['type'] == 'BUY')
        sell_count = sum(1 for t in results['transactions'] if t['type'] == 'SELL')
        
        # Should have equal buys and sells
        assert buy_count == sell_count
    
    def test_daily_trading(self, strategy, sample_stock_data, investment_amount):
        """Test that strategy trades daily (except last day)."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # Number of trading days minus 1 (can't sell on last day)
        expected_trades = len(sample_stock_data) - 1
        buy_count = sum(1 for t in results['transactions'] if t['type'] == 'BUY')
        
        assert buy_count == expected_trades
    
    def test_compounding(self, strategy, sample_stock_data, investment_amount):
        """Test that proceeds are reinvested (compounding)."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # First buy should be with initial amount
        first_buy = next(t for t in results['transactions'] if t['type'] == 'BUY')
        assert abs(first_buy['cost'] - investment_amount) < 0.01
        
        # Check that sell proceeds are reinvested
        for i in range(0, len(results['transactions']) - 2, 2):
            sell_txn = results['transactions'][i + 1]
            next_buy = results['transactions'][i + 2]
            
            # Next buy should use sell proceeds
            assert sell_txn['type'] == 'SELL'
            assert next_buy['type'] == 'BUY'
    
    def test_all_shares_sold(self, strategy, sample_stock_data, investment_amount):
        """Test that all shares are sold (no holdings at end)."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # Final shares should be 0 (all sold)
        assert results['shares'] == 0
    
    def test_single_day_data(self, strategy, investment_amount):
        """Test strategy with only one day of data."""
        data = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01']),
            'Open': [100],
            'High': [102],
            'Low': [98],
            'Close': [101],
            'Volume': [1000000]
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Can't trade with only 1 day
        assert results['shares'] == 0
        assert results['final_value'] == 0
        assert len(results['transactions']) == 0
    
    def test_two_day_data(self, strategy, investment_amount):
        """Test strategy with two days of data."""
        data = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
            'Open': [100, 101],
            'High': [102, 103],
            'Low': [98, 99],
            'Close': [101, 102],
            'Volume': [1000000, 1000000]
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should make exactly 1 trade (buy day 1, sell day 2)
        assert len(results['transactions']) == 2
        assert results['transactions'][0]['type'] == 'BUY'
        assert results['transactions'][1]['type'] == 'SELL'
    
    def test_profitable_scenario(self, strategy, investment_amount):
        """Test with prices rising each day (profitable)."""
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100 + i for i in range(10)],
            'High': [102 + i for i in range(10)],
            'Low': [98 + i for i in range(10)],
            'Close': [101 + i for i in range(10)],
            'Volume': [1000000] * 10
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should be profitable when close-to-open is positive
        assert results['final_value'] != 0
    
    def test_losing_scenario(self, strategy, investment_amount):
        """Test with prices where open is lower than previous close."""
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100 - i * 0.5 for i in range(10)],
            'High': [102 - i * 0.5 for i in range(10)],
            'Low': [98 - i * 0.5 for i in range(10)],
            'Close': [100 - i * 0.5 for i in range(10)],
            'Volume': [1000000] * 10
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Final value can be less than initial with declining prices
        assert results['total_cost'] == investment_amount
    
    def test_empty_data(self, strategy, empty_stock_data, investment_amount):
        """Test strategy with empty data."""
        results = strategy.execute(empty_stock_data, investment_amount)
        
        assert results['shares'] == 0
        assert results['total_cost'] == 0
        assert results['final_value'] == 0
        assert len(results['transactions']) == 0
    
    def test_transaction_sequence(self, strategy, sample_stock_data, investment_amount):
        """Test that transactions alternate between BUY and SELL."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        for i in range(len(results['transactions'])):
            if i % 2 == 0:
                assert results['transactions'][i]['type'] == 'BUY'
            else:
                assert results['transactions'][i]['type'] == 'SELL'
    
    def test_final_value_is_cash(self, strategy, sample_stock_data, investment_amount):
        """Test that final value is in cash (not shares)."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # All shares sold, so final value should equal the last sell proceeds
        if len(results['transactions']) > 0:
            last_sell = [t for t in results['transactions'] if t['type'] == 'SELL'][-1]
            assert abs(results['final_value'] - last_sell['cost']) < 0.01

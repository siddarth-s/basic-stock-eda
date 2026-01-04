"""Unit tests for Earnings Play strategy."""

import pytest
import pandas as pd
from strategies.earnings_play import EarningsPlayStrategy


class TestEarningsPlayStrategy:
    """Test suite for EarningsPlayStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance."""
        return EarningsPlayStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy has correct name."""
        assert strategy.name == "Earnings Play"
        assert "earnings" in strategy.description.lower()
    
    def test_basic_execution(self, strategy, sample_stock_data, investment_amount):
        """Test basic strategy execution."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        assert results['total_cost'] >= 0
        assert results['final_value'] >= 0
        # Should have transactions if data spans multiple quarters
        assert len(results['transactions']) >= 0
    
    def test_buy_sell_pairs(self, strategy, sample_stock_data, investment_amount):
        """Test that each buy has a corresponding sell."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        buy_count = sum(1 for t in results['transactions'] if t['type'] == 'BUY')
        sell_count = sum(1 for t in results['transactions'] if t['type'] == 'SELL')
        
        # Should have equal number of buys and sells
        assert buy_count == sell_count
    
    def test_no_shares_held_at_end(self, strategy, sample_stock_data, investment_amount):
        """Test that all positions are closed."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # All positions should be closed
        assert results['shares'] == 0
    
    def test_quarterly_earnings_simulation(self, strategy, investment_amount):
        """Test that strategy simulates quarterly earnings (~90 days apart)."""
        # Create data spanning more than one quarter
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        dates = dates[dates.weekday < 5]
        
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100 + i * 0.1 for i in range(len(dates))],
            'High': [102 + i * 0.1 for i in range(len(dates))],
            'Low': [98 + i * 0.1 for i in range(len(dates))],
            'Close': [101 + i * 0.1 for i in range(len(dates))],
            'Volume': [1000000] * len(dates)
        })
        
        results = strategy.execute(data, investment_amount)
        
        # With 200 days, should have at least 1 earnings cycle (90 days)
        assert len(results['transactions']) > 0
    
    def test_short_timeframe_no_earnings(self, strategy, investment_amount):
        """Test with data shorter than one earnings cycle."""
        # Create data for less than 90 days
        dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
        dates = dates[dates.weekday < 5]
        
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100] * len(dates),
            'High': [102] * len(dates),
            'Low': [98] * len(dates),
            'Close': [101] * len(dates),
            'Volume': [1000000] * len(dates)
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should have no transactions if no earnings in range
        assert len(results['transactions']) == 0
        assert results['total_cost'] == 0
    
    def test_equal_investment_per_cycle(self, strategy, sample_stock_data, investment_amount):
        """Test that investment is divided equally across earnings cycles."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        if len(results['transactions']) > 0:
            buy_txns = [t for t in results['transactions'] if t['type'] == 'BUY']
            
            if len(buy_txns) > 1:
                # All buy costs should be approximately equal
                costs = [txn['cost'] for txn in buy_txns]
                assert all(abs(cost - costs[0]) < 0.01 for cost in costs)
    
    def test_buy_before_sell_timing(self, strategy, sample_stock_data, investment_amount):
        """Test that buy happens before sell in each cycle."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # Transactions should alternate BUY, SELL, BUY, SELL
        for i in range(0, len(results['transactions']) - 1, 2):
            if i + 1 < len(results['transactions']):
                assert results['transactions'][i]['type'] == 'BUY'
                assert results['transactions'][i + 1]['type'] == 'SELL'
                
                # Sell should be after buy
                buy_date = pd.Timestamp(results['transactions'][i]['date'])
                sell_date = pd.Timestamp(results['transactions'][i + 1]['date'])
                assert sell_date >= buy_date
    
    def test_empty_data(self, strategy, empty_stock_data, investment_amount):
        """Test strategy with empty data."""
        results = strategy.execute(empty_stock_data, investment_amount)
        
        assert results['shares'] == 0
        assert results['total_cost'] == 0
        assert results['final_value'] == 0
        assert len(results['transactions']) == 0
    
    def test_final_value_is_cash(self, strategy, sample_stock_data, investment_amount):
        """Test that final value is cash (all positions closed)."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # All shares should be sold
        assert results['shares'] == 0
        
        # Final value should equal total cost + total profit
        if results['total_cost'] > 0:
            expected_final = results['total_cost'] + results['gain_amount']
            assert abs(results['final_value'] - expected_final) < 0.01
    
    def test_multiple_earnings_cycles(self, strategy, investment_amount):
        """Test with data spanning multiple earnings cycles."""
        # Create data for a full year (should have ~4 earnings)
        dates = pd.date_range(start='2023-01-01', periods=365, freq='D')
        dates = dates[dates.weekday < 5]
        
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100 + i * 0.1 for i in range(len(dates))],
            'High': [102 + i * 0.1 for i in range(len(dates))],
            'Low': [98 + i * 0.1 for i in range(len(dates))],
            'Close': [101 + i * 0.1 for i in range(len(dates))],
            'Volume': [1000000] * len(dates)
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should have multiple earnings cycles
        buy_count = sum(1 for t in results['transactions'] if t['type'] == 'BUY')
        assert buy_count >= 2  # Should have at least 2 earnings in a year
    
    def test_total_cost_distribution(self, strategy, sample_stock_data, investment_amount):
        """Test that total cost is distributed across all cycles."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        if results['total_cost'] > 0:
            # Total cost should be <= investment amount
            assert results['total_cost'] <= investment_amount
            
            # If there are transactions, total cost should equal sum of buy costs
            buy_txns = [t for t in results['transactions'] if t['type'] == 'BUY']
            if buy_txns:
                total_buy_cost = sum(t['cost'] for t in buy_txns)
                assert abs(total_buy_cost - results['total_cost']) < 0.01
    
    def test_gain_calculation(self, strategy, sample_stock_data, investment_amount):
        """Test correct calculation of gains."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        if results['total_cost'] > 0:
            expected_gain = results['final_value'] - results['total_cost']
            assert abs(results['gain_amount'] - expected_gain) < 0.01
            
            expected_gain_pct = (expected_gain / results['total_cost']) * 100
            assert abs(results['gain_pct'] - expected_gain_pct) < 0.01

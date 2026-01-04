"""Unit tests for DCA Every Friday strategy."""

import pytest
import pandas as pd
from strategies.dca_friday import DCAFridayStrategy


class TestDCAFridayStrategy:
    """Test suite for DCAFridayStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance."""
        return DCAFridayStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy has correct name."""
        assert strategy.name == "DCA Every Friday"
        assert "Friday" in strategy.description
    
    def test_basic_execution(self, strategy, sample_stock_data, investment_amount):
        """Test basic strategy execution."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        assert results['total_cost'] <= investment_amount  # May be less if rounding
        assert results['shares'] > 0
        assert results['final_value'] > 0
        assert len(results['transactions']) > 0
    
    def test_only_buys_on_fridays(self, strategy, sample_stock_data, investment_amount):
        """Test that all purchases are on Fridays."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        for txn in results['transactions']:
            date = pd.Timestamp(txn['date'])
            assert date.weekday() == 4  # Friday is weekday 4
    
    def test_equal_amounts_per_friday(self, strategy, sample_stock_data, investment_amount):
        """Test that equal amounts are invested each Friday."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        if len(results['transactions']) > 0:
            # All transaction costs should be equal (within rounding)
            costs = [txn['cost'] for txn in results['transactions']]
            assert all(abs(cost - costs[0]) < 0.01 for cost in costs)
    
    def test_total_cost_distribution(self, strategy, sample_stock_data, investment_amount):
        """Test that total cost is distributed across Fridays."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # Count Fridays in data
        sample_stock_data['Date'] = pd.to_datetime(sample_stock_data['Date'])
        num_fridays = (sample_stock_data['Date'].dt.weekday == 4).sum()
        
        if num_fridays > 0:
            expected_cost_per_friday = investment_amount / num_fridays
            
            for txn in results['transactions']:
                assert abs(txn['cost'] - expected_cost_per_friday) < 0.01
    
    def test_no_fridays_in_range(self, strategy, investment_amount):
        """Test strategy when there are no Fridays in data."""
        # Create data with only Mondays
        dates = pd.date_range(start='2023-01-02', periods=4, freq='W-MON')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100] * 4,
            'High': [102] * 4,
            'Low': [98] * 4,
            'Close': [101] * 4,
            'Volume': [1000000] * 4
        })
        
        results = strategy.execute(data, investment_amount)
        
        assert results['shares'] == 0
        assert results['total_cost'] == 0
        assert results['final_value'] == 0
        assert len(results['transactions']) == 0
    
    def test_single_friday(self, strategy, investment_amount):
        """Test strategy with only one Friday."""
        # Create data with one Friday
        dates = pd.date_range(start='2023-01-06', periods=1, freq='W-FRI')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100],
            'High': [102],
            'Low': [98],
            'Close': [101],
            'Volume': [1000000]
        })
        
        results = strategy.execute(data, investment_amount)
        
        assert len(results['transactions']) == 1
        assert results['total_cost'] == investment_amount
        assert results['transactions'][0]['cost'] == investment_amount
    
    def test_shares_accumulation(self, strategy, sample_stock_data, investment_amount):
        """Test that shares are accumulated across all Fridays."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        # Sum up shares from all transactions
        total_shares = sum(txn['shares'] for txn in results['transactions'])
        
        assert abs(results['shares'] - total_shares) < 0.0001
    
    def test_declining_market(self, strategy, declining_stock_data, investment_amount):
        """Test DCA in declining market (should perform better than lump sum)."""
        results = strategy.execute(declining_stock_data, investment_amount)
        
        assert results['shares'] > 0
        assert results['total_cost'] > 0
        # In declining market, DCA may still have losses but buys more shares at lower prices
    
    def test_volatile_market(self, strategy, volatile_stock_data, investment_amount):
        """Test DCA in volatile market."""
        results = strategy.execute(volatile_stock_data, investment_amount)
        
        assert results['shares'] > 0
        assert results['total_cost'] > 0
        assert len(results['transactions']) > 0
    
    def test_empty_data(self, strategy, empty_stock_data, investment_amount):
        """Test strategy with empty data."""
        results = strategy.execute(empty_stock_data, investment_amount)
        
        assert results['shares'] == 0
        assert results['total_cost'] == 0
        assert results['final_value'] == 0
        assert len(results['transactions']) == 0
    
    def test_all_transactions_are_buys(self, strategy, sample_stock_data, investment_amount):
        """Test that DCA strategy only has BUY transactions."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        for txn in results['transactions']:
            assert txn['type'] == 'BUY'
    
    def test_final_value_calculation(self, strategy, sample_stock_data, investment_amount):
        """Test correct calculation of final portfolio value."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        last_price = sample_stock_data.iloc[-1]['Close']
        expected_final_value = results['shares'] * last_price
        
        assert abs(results['final_value'] - expected_final_value) < 0.01

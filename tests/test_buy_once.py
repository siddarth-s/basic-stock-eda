"""Unit tests for Buy All At Once strategy."""

import pytest
import pandas as pd
from strategies.buy_once import BuyOnceStrategy


class TestBuyOnceStrategy:
    """Test suite for BuyOnceStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance."""
        return BuyOnceStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy has correct name."""
        assert strategy.name == "Buy All At Once"
        assert "Lump sum" in strategy.description
    
    def test_basic_execution(self, strategy, sample_stock_data, investment_amount):
        """Test basic strategy execution with rising prices."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        assert results['total_cost'] == investment_amount
        assert results['shares'] > 0
        assert results['final_value'] > 0
        assert len(results['transactions']) == 1
        assert results['transactions'][0]['type'] == 'BUY'
        
        # With rising prices, should be profitable
        assert results['gain_amount'] > 0
        assert results['gain_pct'] > 0
    
    def test_single_buy_transaction(self, strategy, sample_stock_data, investment_amount):
        """Test that strategy makes exactly one buy transaction."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        buy_txns = [t for t in results['transactions'] if t['type'] == 'BUY']
        assert len(buy_txns) == 1
        
        # Should buy on first day
        first_date = sample_stock_data.iloc[0]['Date']
        assert pd.Timestamp(buy_txns[0]['date']) == pd.Timestamp(first_date)
    
    def test_shares_calculation(self, strategy, sample_stock_data, investment_amount):
        """Test correct calculation of shares purchased."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        first_price = sample_stock_data.iloc[0]['Close']
        expected_shares = investment_amount / first_price
        
        assert abs(results['shares'] - expected_shares) < 0.0001
    
    def test_final_value_calculation(self, strategy, sample_stock_data, investment_amount):
        """Test correct calculation of final portfolio value."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        first_price = sample_stock_data.iloc[0]['Close']
        last_price = sample_stock_data.iloc[-1]['Close']
        shares = investment_amount / first_price
        expected_final_value = shares * last_price
        
        assert abs(results['final_value'] - expected_final_value) < 0.01
    
    def test_declining_market(self, strategy, declining_stock_data, investment_amount):
        """Test strategy with declining market."""
        results = strategy.execute(declining_stock_data, investment_amount)
        
        assert results['total_cost'] == investment_amount
        assert results['shares'] > 0
        assert results['gain_amount'] < 0  # Should have loss
        assert results['gain_pct'] < 0
    
    def test_empty_data(self, strategy, empty_stock_data, investment_amount):
        """Test strategy with empty data."""
        results = strategy.execute(empty_stock_data, investment_amount)
        
        assert results['shares'] == 0
        assert results['total_cost'] == 0
        assert results['final_value'] == 0
        assert len(results['transactions']) == 0
        assert results['gain_pct'] == 0
        assert results['gain_amount'] == 0
    
    def test_small_investment(self, strategy, sample_stock_data):
        """Test strategy with small investment amount."""
        small_amount = 100.0
        results = strategy.execute(sample_stock_data, small_amount)
        
        assert results['total_cost'] == small_amount
        assert results['shares'] > 0
        assert results['final_value'] > 0
    
    def test_large_investment(self, strategy, sample_stock_data):
        """Test strategy with large investment amount."""
        large_amount = 1000000.0
        results = strategy.execute(sample_stock_data, large_amount)
        
        assert results['total_cost'] == large_amount
        assert results['shares'] > 0
        assert results['final_value'] > 0
    
    def test_gain_percentage_calculation(self, strategy, sample_stock_data, investment_amount):
        """Test gain percentage is calculated correctly."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        expected_gain_pct = (results['gain_amount'] / investment_amount) * 100
        assert abs(results['gain_pct'] - expected_gain_pct) < 0.01
    
    def test_transaction_details(self, strategy, sample_stock_data, investment_amount):
        """Test transaction contains all required details."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        txn = results['transactions'][0]
        assert 'date' in txn
        assert 'type' in txn
        assert 'price' in txn
        assert 'shares' in txn
        assert 'cost' in txn
        assert txn['cost'] == investment_amount

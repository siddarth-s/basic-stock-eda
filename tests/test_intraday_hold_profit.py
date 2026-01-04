"""Unit tests for Intraday Hold Profit strategy."""

import pytest
import pandas as pd
from strategies.intraday_hold_profit import IntradayHoldProfitStrategy


class TestIntradayHoldProfitStrategy:
    """Test suite for IntradayHoldProfitStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance."""
        return IntradayHoldProfitStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy has correct name."""
        assert strategy.name == "Intraday Hold Profit"
        assert "profitable" in strategy.description.lower() or "breakeven" in strategy.description.lower()
    
    def test_basic_execution(self, strategy, sample_stock_data, investment_amount):
        """Test basic strategy execution."""
        results = strategy.execute(sample_stock_data, investment_amount)
        
        assert results['total_cost'] == investment_amount
        assert results['final_value'] > 0
        assert len(results['transactions']) > 0
    
    def test_only_sells_when_profitable(self, strategy, investment_amount):
        """Test that strategy only sells when price >= buy price."""
        # Create data where open is sometimes lower than previous close
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100, 99, 101, 98, 102, 97, 103, 96, 104, 105],  # Varying opens
            'High': [102, 101, 103, 100, 104, 99, 105, 98, 106, 107],
            'Low': [98, 97, 99, 96, 100, 95, 101, 94, 102, 103],
            'Close': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],  # Constant close
            'Volume': [1000000] * 10
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Check that all sells are at price >= corresponding buy price
        buy_price = None
        for txn in results['transactions']:
            if txn['type'] == 'BUY':
                buy_price = txn['price']
            elif txn['type'] == 'SELL':
                assert txn['price'] >= buy_price, "Sold at a loss!"
    
    def test_holds_losing_position(self, strategy, investment_amount):
        """Test that strategy holds position when open < buy price."""
        # Create scenario where stock opens lower for several days
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100, 95, 94, 93, 105],  # Opens low, then recovers
            'High': [102, 97, 96, 95, 107],
            'Low': [98, 93, 92, 91, 103],
            'Close': [100, 96, 95, 94, 106],
            'Volume': [1000000] * 5
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should buy on day 1 at close (100)
        # Should NOT sell on days 2-4 (opens at 95, 94, 93 < 100)
        # Should sell on day 5 (opens at 105 > 100)
        
        buy_txns = [t for t in results['transactions'] if t['type'] == 'BUY']
        sell_txns = [t for t in results['transactions'] if t['type'] == 'SELL']
        
        # Should have fewer sells than potential days due to holding
        assert len(sell_txns) < len(dates) - 1
    
    def test_reinvests_after_profitable_sell(self, strategy, investment_amount):
        """Test that proceeds are reinvested after selling."""
        dates = pd.date_range(start='2023-01-01', periods=6, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100, 105, 100, 105, 100, 105],
            'High': [102, 107, 102, 107, 102, 107],
            'Low': [98, 103, 98, 103, 98, 103],
            'Close': [100, 104, 100, 104, 100, 104],
            'Volume': [1000000] * 6
        })
        
        results = strategy.execute(data, investment_amount)
        
        # After each sell, should buy again
        buy_count = sum(1 for t in results['transactions'] if t['type'] == 'BUY')
        sell_count = sum(1 for t in results['transactions'] if t['type'] == 'SELL')
        
        # Should reinvest after sells (except possibly at the end)
        assert buy_count >= sell_count
    
    def test_holds_until_end_if_unprofitable(self, strategy, investment_amount):
        """Test that shares are held if never profitable."""
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100, 95, 94, 93, 92],  # Always opens lower
            'High': [102, 97, 96, 95, 94],
            'Low': [98, 93, 92, 91, 90],
            'Close': [100, 96, 95, 94, 93],
            'Volume': [1000000] * 5
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should have shares at the end (never sold)
        assert results['shares'] > 0
    
    def test_breakeven_sells(self, strategy, investment_amount):
        """Test that strategy sells at breakeven (price == buy price)."""
        dates = pd.date_range(start='2023-01-01', periods=3, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100, 100, 100],  # Opens at exactly buy price
            'High': [102, 102, 102],
            'Low': [98, 98, 98],
            'Close': [100, 100, 100],
            'Volume': [1000000] * 3
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should sell at breakeven
        sell_txns = [t for t in results['transactions'] if t['type'] == 'SELL']
        assert len(sell_txns) > 0
    
    def test_empty_data(self, strategy, empty_stock_data, investment_amount):
        """Test strategy with empty data."""
        results = strategy.execute(empty_stock_data, investment_amount)
        
        assert results['shares'] == 0
        assert results['total_cost'] == 0
        assert results['final_value'] == 0
        assert len(results['transactions']) == 0
    
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
        
        # Can't sell with only 1 day
        assert len(results['transactions']) == 0
    
    def test_two_day_profitable(self, strategy, investment_amount):
        """Test with two days where second open > first close."""
        data = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
            'Open': [100, 105],
            'High': [102, 107],
            'Low': [98, 103],
            'Close': [101, 106],
            'Volume': [1000000, 1000000]
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should buy and sell
        assert len(results['transactions']) == 2
        assert results['transactions'][0]['type'] == 'BUY'
        assert results['transactions'][1]['type'] == 'SELL'
    
    def test_two_day_unprofitable(self, strategy, investment_amount):
        """Test with two days where second open < first close."""
        data = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
            'Open': [100, 95],
            'High': [102, 97],
            'Low': [98, 93],
            'Close': [101, 96],
            'Volume': [1000000, 1000000]
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should buy but not sell
        buy_txns = [t for t in results['transactions'] if t['type'] == 'BUY']
        sell_txns = [t for t in results['transactions'] if t['type'] == 'SELL']
        
        assert len(buy_txns) == 1
        assert len(sell_txns) == 0
        assert results['shares'] > 0  # Still holding
    
    def test_final_value_with_holdings(self, strategy, investment_amount):
        """Test final value calculation when still holding shares."""
        dates = pd.date_range(start='2023-01-01', periods=3, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Open': [100, 95, 94],
            'High': [102, 97, 96],
            'Low': [98, 93, 92],
            'Close': [100, 96, 95],
            'Volume': [1000000] * 3
        })
        
        results = strategy.execute(data, investment_amount)
        
        # Should still be holding shares
        assert results['shares'] > 0
        
        # Final value should be shares * last close price
        expected_final_value = results['shares'] * data.iloc[-1]['Close']
        assert abs(results['final_value'] - expected_final_value) < 0.01
    
    def test_no_losses_in_sells(self, strategy, volatile_stock_data, investment_amount):
        """Test that no sell transaction results in a loss."""
        results = strategy.execute(volatile_stock_data, investment_amount)
        
        # Track buy prices and ensure no sell is below its corresponding buy
        buy_price = None
        for txn in results['transactions']:
            if txn['type'] == 'BUY':
                buy_price = txn['price']
            elif txn['type'] == 'SELL':
                assert txn['price'] >= buy_price, f"Sold at {txn['price']} but bought at {buy_price}"

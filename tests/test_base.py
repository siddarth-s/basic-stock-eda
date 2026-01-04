"""Unit tests for BaseStrategy class."""

import pytest
import pandas as pd
from strategies.base import BaseStrategy


class ConcreteStrategy(BaseStrategy):
    """Concrete implementation of BaseStrategy for testing."""
    
    def __init__(self):
        super().__init__(name="Test Strategy", description="Test description")
    
    def execute(self, data: pd.DataFrame, amount: float) -> dict:
        """Simple implementation for testing."""
        return {
            'shares': 10.0,
            'total_cost': amount,
            'final_value': amount * 1.1,
            'transactions': [],
            **self.calculate_metrics(amount, amount * 1.1)
        }


class TestBaseStrategy:
    """Test suite for BaseStrategy base class."""
    
    @pytest.fixture
    def strategy(self):
        """Create concrete strategy instance."""
        return ConcreteStrategy()
    
    def test_initialization(self, strategy):
        """Test strategy initialization."""
        assert strategy.name == "Test Strategy"
        assert strategy.description == "Test description"
    
    def test_calculate_metrics_profit(self, strategy):
        """Test metrics calculation with profit."""
        total_cost = 10000.0
        final_value = 11000.0
        
        metrics = strategy.calculate_metrics(total_cost, final_value)
        
        assert metrics['gain_amount'] == 1000.0
        assert abs(metrics['gain_pct'] - 10.0) < 0.01
    
    def test_calculate_metrics_loss(self, strategy):
        """Test metrics calculation with loss."""
        total_cost = 10000.0
        final_value = 9000.0
        
        metrics = strategy.calculate_metrics(total_cost, final_value)
        
        assert metrics['gain_amount'] == -1000.0
        assert abs(metrics['gain_pct'] - (-10.0)) < 0.01
    
    def test_calculate_metrics_breakeven(self, strategy):
        """Test metrics calculation at breakeven."""
        total_cost = 10000.0
        final_value = 10000.0
        
        metrics = strategy.calculate_metrics(total_cost, final_value)
        
        assert metrics['gain_amount'] == 0.0
        assert metrics['gain_pct'] == 0.0
    
    def test_calculate_metrics_zero_cost(self, strategy):
        """Test metrics calculation with zero cost."""
        total_cost = 0.0
        final_value = 0.0
        
        metrics = strategy.calculate_metrics(total_cost, final_value)
        
        assert metrics['gain_amount'] == 0.0
        assert metrics['gain_pct'] == 0.0
    
    def test_execute_returns_required_keys(self, strategy):
        """Test that execute returns all required keys."""
        data = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01']),
            'Open': [100],
            'High': [102],
            'Low': [98],
            'Close': [101],
            'Volume': [1000000]
        })
        
        results = strategy.execute(data, 10000.0)
        
        required_keys = ['shares', 'total_cost', 'final_value', 'transactions', 
                        'gain_pct', 'gain_amount']
        for key in required_keys:
            assert key in results
    
    def test_abstract_class_cannot_instantiate(self):
        """Test that BaseStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseStrategy("Test", "Description")

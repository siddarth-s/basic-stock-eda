"""Intraday trading strategy: Buy at 4PM, only sell at 9AM if profitable or breakeven."""

import pandas as pd
from typing import Dict
from strategies.base import BaseStrategy

class IntradayHoldProfitStrategy(BaseStrategy):
    """Buy at market close (4PM), sell at market open (9:30AM) only if profitable/breakeven."""
    
    def __init__(self):
        super().__init__(
            name="Intraday Hold Profit",
            description="Buy at close, sell at next open only when profitable or breakeven"
        )
    
    def execute(self, data: pd.DataFrame, amount: float) -> Dict:
        """
        Execute intraday hold profit strategy.
        
        Strategy:
        - Buy at close (4PM) each day with available cash
        - Sell at next open (9:30AM) only if price >= buy price
        - If selling at a loss, hold the position until profitable
        - Reinvest proceeds when selling
        
        Note: Uses Close price as buy (4PM) and next day's Open as sell (9:30AM).
        """
        data = data.copy()
        data['Date'] = pd.to_datetime(data['Date'])
        
        if len(data) < 2:
            return {
                'shares': 0,
                'total_cost': 0,
                'final_value': 0,
                'transactions': [],
                'gain_pct': 0,
                'gain_amount': 0
            }
        
        transactions = []
        cash = amount
        shares_held = 0
        buy_price = 0
        
        # Trade each day
        for i in range(len(data)):
            current_row = data.iloc[i]
            current_date = current_row['Date']
            
            # Check if we should sell existing position (at open)
            if shares_held > 0 and i > 0:
                sell_price = current_row['Open']  # 9:30AM
                
                # Only sell if profitable or breakeven
                if sell_price >= buy_price:
                    proceeds = shares_held * sell_price
                    
                    transactions.append({
                        'date': current_date,
                        'type': 'SELL',
                        'price': sell_price,
                        'shares': shares_held,
                        'cost': proceeds
                    })
                    
                    cash += proceeds
                    shares_held = 0
            
            # Buy at close if we have cash and not at the last day
            if cash > 0 and i < len(data) - 1:
                buy_price = current_row['Close']  # 4PM
                shares_to_buy = cash / buy_price
                cost = shares_to_buy * buy_price
                
                transactions.append({
                    'date': current_date,
                    'type': 'BUY',
                    'price': buy_price,
                    'shares': shares_to_buy,
                    'cost': cost
                })
                
                shares_held = shares_to_buy
                cash = 0
        
        # Calculate final value
        if shares_held > 0:
            # Still holding shares, value them at last close price
            final_value = shares_held * data.iloc[-1]['Close']
        else:
            final_value = cash
        
        # Calculate metrics
        metrics = self.calculate_metrics(amount, final_value)
        
        return {
            'shares': shares_held,
            'total_cost': amount,
            'final_value': final_value,
            'transactions': transactions,
            **metrics
        }

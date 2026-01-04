"""Trading strategy implementations."""

from strategies.base import BaseStrategy
from strategies.dca_friday import DCAFridayStrategy
from strategies.buy_once import BuyOnceStrategy
from strategies.intraday import IntradayStrategy
from strategies.intraday_hold_profit import IntradayHoldProfitStrategy
from strategies.earnings_play import EarningsPlayStrategy

# Available strategies
STRATEGIES = {
    'DCA Every Friday': DCAFridayStrategy(),
    'Buy All At Once': BuyOnceStrategy(),
    'Intraday (4PM-9AM)': IntradayStrategy(),
    'Intraday Hold Profit': IntradayHoldProfitStrategy(),
    'Earnings Play': EarningsPlayStrategy(),
}

__all__ = ['BaseStrategy', 'STRATEGIES']

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from config.settings import settings
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """Advanced stock analysis with time-based predictions using Groww API."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self._groww_client = None
    
    def _get_groww_client(self):
        """Lazy load Groww API client."""
        if self._groww_client is None:
            from .groww_api import groww_client
            self._groww_client = groww_client
        return self._groww_client
    
    def _get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get stock data from Groww API with caching."""
        cache_key = f"{symbol}_data"
        current_time = datetime.now()
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (current_time - timestamp).seconds < self.cache_timeout:
                return cached_data
        
        try:
            client = self._get_groww_client()
            
            # Get current price and OHLC data
            try:
                price_data = client.get_stock_price(symbol)
                if price_data and price_data.get('current_price', 0) > 0:
                    self.cache[cache_key] = (price_data, current_time)
                    return price_data
            except Exception as e:
                logger.debug(f"Failed to get price data for {symbol}: {str(e)}")
            
            logger.warning(f"No data found for {symbol}")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            return {}
    
    def _calculate_technical_indicators(self, price_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate technical indicators from current price data."""
        if not price_data or price_data.get('current_price', 0) <= 0:
            return {}
        
        current_price = price_data.get('current_price', 0)
        open_price = price_data.get('open_price', current_price)
        high_price = price_data.get('high_price', current_price)
        low_price = price_data.get('low_price', current_price)
        close_price = price_data.get('close_price', current_price)
        change_percent = price_data.get('change_percent', 0)
        volume = price_data.get('volume', 0)
        
        # Calculate intraday metrics
        day_range = high_price - low_price if high_price > 0 and low_price > 0 else 0
        price_position = ((current_price - low_price) / day_range) if day_range > 0 else 0.5
        
        # Simple momentum indicators based on day's movement
        price_vs_open = ((current_price - open_price) / open_price) if open_price > 0 else 0
        
        # Estimate volatility from day range
        volatility = (day_range / current_price) if current_price > 0 else 0
        
        return {
            'current_price': current_price,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'day_range': day_range,
            'price_position': price_position,  # 0-1, where 0 is at low, 1 is at high
            'price_vs_open': price_vs_open,
            'change_percent': change_percent / 100 if change_percent else 0,
            'volume': volume,
            'volatility': volatility,
            'momentum_score': self._calculate_momentum_score(price_data)
        }
    
    def _calculate_momentum_score(self, price_data: Dict[str, Any]) -> float:
        """Calculate a momentum score from price data (0-100)."""
        current_price = price_data.get('current_price', 0)
        open_price = price_data.get('open_price', current_price)
        high_price = price_data.get('high_price', current_price)
        low_price = price_data.get('low_price', current_price)
        change_percent = price_data.get('change_percent', 0)
        
        if current_price <= 0:
            return 50.0
        
        # Score based on multiple factors
        score = 50.0  # Neutral baseline
        
        # Factor 1: Price change (±20 points)
        score += min(max(change_percent, -20), 20)
        
        # Factor 2: Position in day's range (±15 points)
        day_range = high_price - low_price
        if day_range > 0:
            position = (current_price - low_price) / day_range
            score += (position - 0.5) * 30  # -15 to +15
        
        # Factor 3: Current vs open (±15 points)
        if open_price > 0:
            vs_open = ((current_price - open_price) / open_price) * 100
            score += min(max(vs_open * 3, -15), 15)
        
        return min(max(score, 0), 100)
    
    def _predict_return_for_days(self, price_data: Dict[str, Any], days: int) -> float:
        """Predict stock return for specified number of days using simple heuristics."""
        if not price_data or price_data.get('current_price', 0) <= 0:
            return 0.0
        
        try:
            indicators = self._calculate_technical_indicators(price_data)
            
            # Simple prediction based on current momentum and technical indicators
            momentum_score = indicators.get('momentum_score', 50)
            change_percent = indicators.get('change_percent', 0)
            price_position = indicators.get('price_position', 0.5)
            volatility = indicators.get('volatility', 0.02)
            
            # Base prediction on momentum (convert 0-100 scale to expected return)
            # More conservative: Momentum 50 = 0% return, 75 = ~8% return, 25 = -8% return
            base_return = (momentum_score - 50) / 50 * 0.08
            
            # Adjust for position in day's range (smaller impact)
            # Being near high suggests strength, near low suggests potential
            position_adjustment = (price_position - 0.5) * 0.02
            
            # Adjust for current day's change (reduced weight)
            change_adjustment = change_percent * 0.15
            
            # Scale by time horizon (with diminishing returns for longer periods)
            time_factor = min(days / settings.expected_return_days, 1.5)
            
            # Combine factors
            predicted_return = (base_return + position_adjustment + change_adjustment) * time_factor
            
            # Add small random variance based on volatility
            noise = np.random.normal(0, volatility * 0.3)
            predicted_return += noise
            
            # Cap predictions at more reasonable levels (-20% to +25%)
            return min(max(predicted_return, -0.20), 0.25)
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return 0.0
    
    def _analyze_single_stock(self, symbol: str) -> Dict[str, Any]:
        """Analyze a single stock with time-based predictions."""
        try:
            price_data = self._get_stock_data(symbol)
            if not price_data or price_data.get('current_price', 0) <= 0:
                return {'symbol': symbol, 'error': 'No data available'}
            
            # Get technical indicators
            indicators = self._calculate_technical_indicators(price_data)
            
            # Predict returns for the configured time horizon
            days = settings.expected_return_days
            predicted_return = self._predict_return_for_days(price_data, days)
            
            # Calculate technical score based on momentum
            momentum_score = indicators.get('momentum_score', 50)
            
            # Normalize to -1 to 1 scale
            technical_score = (momentum_score - 50) / 50
            
            # Price position in day's range
            price_position = indicators.get('price_position', 0.5)
            
            # Risk assessment
            volatility = indicators.get('volatility', 0.02)
            risk_score = min(volatility / 0.05, 1.0)  # Normalize to 0-1 (5% volatility = max risk)
            
            change_percent = indicators.get('change_percent', 0)
            
            analysis = {
                'symbol': symbol,
                'current_price': indicators.get('current_price', 0),
                'open_price': indicators.get('open_price', 0),
                'high_price': indicators.get('high_price', 0),
                'low_price': indicators.get('low_price', 0),
                'predicted_return_{}d'.format(days): predicted_return,
                'technical_score': technical_score,
                'risk_score': risk_score,
                'momentum_score': momentum_score,
                'volatility': volatility,
                'change_percent': change_percent,
                'price_position': price_position,
                'price_vs_open': indicators.get('price_vs_open', 0),
                'day_range': indicators.get('day_range', 0),
                'volume': indicators.get('volume', 0),
                'analysis_confidence': 'MEDIUM',  # Always MEDIUM as we only have current day data
                'recommendation': self._generate_recommendation(predicted_return, technical_score, risk_score),
                'reasoning': self._generate_reasoning(predicted_return, technical_score, risk_score, days)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    def _generate_recommendation(self, predicted_return: float, technical_score: float, risk_score: float) -> str:
        """Generate buy/sell/hold recommendation."""
        min_return = settings.min_expected_return
        
        # Strong buy conditions
        if predicted_return >= min_return and technical_score > 0.2 and risk_score < 0.7:
            return 'STRONG_BUY'
        
        # Buy conditions
        elif predicted_return >= min_return * 0.7 and technical_score > 0.1:
            return 'BUY'
        
        # Strong sell conditions
        elif predicted_return < -min_return * 0.5 and technical_score < -0.2:
            return 'STRONG_SELL'
        
        # Sell conditions
        elif predicted_return < -min_return * 0.3 or technical_score < -0.1:
            return 'SELL'
        
        else:
            return 'HOLD'
    
    def _generate_reasoning(self, predicted_return: float, technical_score: float, risk_score: float, days: int) -> List[str]:
        """Generate human-readable reasoning for the recommendation."""
        reasoning = []
        
        # Return prediction reasoning
        if predicted_return >= settings.min_expected_return:
            reasoning.append(f"Predicted return of {predicted_return:.2%} in {days} days meets target of {settings.min_expected_return:.2%}")
        elif predicted_return > 0:
            reasoning.append(f"Positive predicted return of {predicted_return:.2%} in {days} days, but below target")
        else:
            reasoning.append(f"Negative predicted return of {predicted_return:.2%} in {days} days")
        
        # Technical analysis reasoning
        if technical_score > 0.2:
            reasoning.append("Strong positive technical indicators")
        elif technical_score > 0:
            reasoning.append("Moderately positive technical signals")
        elif technical_score < -0.2:
            reasoning.append("Strong negative technical indicators")
        else:
            reasoning.append("Mixed technical signals")
        
        # Risk assessment reasoning
        if risk_score > 0.8:
            reasoning.append("High volatility - elevated risk")
        elif risk_score < 0.3:
            reasoning.append("Low volatility - stable stock")
        else:
            reasoning.append("Moderate volatility")
        
        return reasoning
    
    def predict_returns_for_days(self, symbol: str, days: int) -> Dict[str, Any]:
        """
        Predict returns for a stock over a specified number of days.
        This is a wrapper method for compatibility with the portfolio analysis script.
        """
        try:
            analysis = self._analyze_single_stock(symbol)
            
            # Extract the relevant predictions
            predicted_return = analysis.get(f'predicted_return_{days}d', 0)
            confidence = analysis.get('analysis_confidence', 'MEDIUM')
            
            return {
                'predicted_return': predicted_return,
                'confidence': confidence,
                'technical_score': analysis.get('technical_score', 0.5),
                'risk_score': analysis.get('risk_score', 0.5),
                'recommendation': analysis.get('recommendation', 'HOLD'),
                'reasoning': analysis.get('reasoning', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to predict returns for {symbol}: {str(e)}")
            return {
                'predicted_return': 0,
                'confidence': 'LOW',
                'technical_score': 0.5,
                'risk_score': 0.8,
                'recommendation': 'HOLD',
                'reasoning': [f'Analysis failed: {str(e)}']
            }

    def analyze_portfolio_performance(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze portfolio performance with time-based predictions."""
        try:
            analyzed_holdings = []
            total_value = 0
            total_pnl = 0
            
            for holding in holdings:
                symbol = holding.get('symbol', '')
                if not symbol:
                    continue
                
                # Analyze individual stock
                analysis = self._analyze_single_stock(symbol)
                
                # Combine with holding data
                combined_analysis = {
                    **holding,
                    **analysis,
                    'current_value': holding.get('current_value', 0),
                    'investment_value': holding.get('investment_value', 0),
                    'pnl': holding.get('pnl', 0),
                    'quantity': holding.get('quantity', 0)
                }
                
                analyzed_holdings.append(combined_analysis)
                total_value += holding.get('current_value', 0)
                total_pnl += holding.get('pnl', 0)
            
            # NEW STRATEGY: Sort ALL holdings by predicted return (lowest first) for selling
            # Don't filter by minimum expected return threshold
            all_holdings_sorted = sorted(
                analyzed_holdings, 
                key=lambda x: x.get(f'predicted_return_{settings.expected_return_days}d', 0)
            )
            
            # Select worst performers to sell up to MAX_INVESTMENT_AMOUNT
            sell_candidates = []
            total_sell_value = 0
            max_sell = settings.max_investment_amount
            
            for stock in all_holdings_sorted:
                if total_sell_value >= max_sell:
                    break
                    
                current_value = stock.get('current_value', 0)
                remaining_budget = max_sell - total_sell_value
                
                if current_value <= remaining_budget:
                    # Sell entire holding
                    sell_candidates.append(stock)
                    total_sell_value += current_value
                else:
                    # Partial sale if stock value exceeds remaining budget
                    partial_quantity = int((remaining_budget / current_value) * stock.get('quantity', 0))
                    if partial_quantity > 0:
                        partial_stock = stock.copy()
                        partial_stock['quantity'] = partial_quantity
                        partial_stock['current_value'] = remaining_budget
                        partial_stock['sale_type'] = 'partial'
                        sell_candidates.append(partial_stock)
                        total_sell_value += remaining_budget
                        break
            
            # Identify which holdings are underperformers (for reporting)
            underperformers = [
                h for h in analyzed_holdings 
                if h.get(f'predicted_return_{settings.expected_return_days}d', 0) < 0
            ]
            
            portfolio_analysis = {
                'total_holdings': len(analyzed_holdings),
                'total_portfolio_value': total_value,
                'total_pnl': total_pnl,
                'pnl_percentage': (total_pnl / (total_value - total_pnl)) * 100 if total_value > total_pnl else 0,
                'analyzed_holdings': analyzed_holdings,
                'underperformers': underperformers,
                'sell_candidates': sell_candidates,
                'total_sell_value': total_sell_value,
                'worst_performers_sold': len(sell_candidates),
                'selling_strategy': f'Sell {len(sell_candidates)} worst performing stocks worth ₹{total_sell_value:,.0f}',
                'analysis_timestamp': datetime.now().isoformat(),
                'time_horizon_days': settings.expected_return_days,
                'target_return': settings.min_expected_return
            }
            
            return portfolio_analysis
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def find_high_potential_stocks(self, budget: float, stock_universe: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Find stocks with high potential returns in the specified time frame."""
        try:
            # Default stock universe (Indian stocks)
            if stock_universe is None:
                stock_universe = [
                    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                    'ICICIBANK.NS', 'KOTAKBANK.NS', 'LT.NS', 'SBIN.NS', 'BHARTIARTL.NS',
                    'ASIANPAINT.NS', 'MARUTI.NS', 'TITAN.NS', 'NESTLEIND.NS', 'HCLTECH.NS',
                    'WIPRO.NS', 'ULTRACEMCO.NS', 'TECHM.NS', 'POWERGRID.NS', 'NTPC.NS'
                ]
            
            opportunities = []
            
            for symbol in stock_universe:
                try:
                    analysis = self._analyze_single_stock(symbol)
                    
                    if 'error' in analysis:
                        continue
                    
                    predicted_return = analysis.get(f'predicted_return_{settings.expected_return_days}d', 0)
                    
                    # Filter for high-potential stocks
                    if (predicted_return >= settings.min_expected_return and 
                        analysis.get('recommendation') in ['BUY', 'STRONG_BUY']):
                        
                        current_price = analysis.get('current_price', 0)
                        if current_price > 0:
                            max_shares = int(budget / current_price)
                            investment_amount = min(budget, max_shares * current_price)
                            
                            opportunity = {
                                **analysis,
                                'investment_amount': investment_amount,
                                'max_shares': max_shares,
                                'expected_value_gain': investment_amount * predicted_return,
                                'roi_score': predicted_return / analysis.get('risk_score', 0.5),  # Risk-adjusted return
                            }
                            
                            opportunities.append(opportunity)
                            
                except Exception as e:
                    logger.warning(f"Failed to analyze {symbol}: {str(e)}")
                    continue
            
            # Sort by ROI score (risk-adjusted return)
            opportunities.sort(key=lambda x: x['roi_score'], reverse=True)
            
            return opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error(f"High potential stock search failed: {str(e)}")
            return []

# Global analyzer instance
stock_analyzer = StockAnalyzer() 
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import logging
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from config.settings import settings
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """Advanced stock analysis with time-based predictions."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def _get_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """Get stock data with caching and proper Indian symbol formatting."""
        cache_key = f"{symbol}_{period}"
        current_time = datetime.now()
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (current_time - timestamp).seconds < self.cache_timeout:
                return cached_data
        
        try:
            # Try different symbol formats for Indian stocks
            symbol_formats = [
                f"{symbol}.NS",  # NSE format
                f"{symbol}.BO",  # BSE format  
                symbol           # Direct symbol
            ]
            
            for symbol_format in symbol_formats:
                try:
                    ticker = yf.Ticker(symbol_format)
                    data = ticker.history(period=period)
                    if not data.empty and len(data) > 10:  # Ensure we have sufficient data
                        logger.info(f"Got data for {symbol} using format {symbol_format}")
                        self.cache[cache_key] = (data, current_time)
                        return data
                except Exception as e:
                    logger.debug(f"Failed to get data for {symbol_format}: {str(e)}")
                    continue
            
            logger.warning(f"No data found for {symbol} in any format")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive technical indicators."""
        if data.empty or len(data) < 20:
            return {}
        
        # Price-based indicators
        current_price = data['Close'].iloc[-1]
        sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = data['Close'].rolling(window=50).mean().iloc[-1] if len(data) >= 50 else sma_20
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # MACD
        ema_12 = data['Close'].ewm(span=12).mean()
        ema_26 = data['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        macd_histogram = (macd - signal).iloc[-1]
        
        # Bollinger Bands
        bb_middle = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        # Volume indicators
        avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = data['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Volatility
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized
        
        # Trend analysis
        price_change_1d = (data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] if len(data) >= 2 else 0
        price_change_5d = (data['Close'].iloc[-1] - data['Close'].iloc[-6]) / data['Close'].iloc[-6] if len(data) >= 6 else 0
        price_change_20d = (data['Close'].iloc[-1] - data['Close'].iloc[-21]) / data['Close'].iloc[-21] if len(data) >= 21 else 0
        
        return {
            'current_price': current_price,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'macd_histogram': macd_histogram,
            'bb_position': bb_position,
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'price_change_1d': price_change_1d,
            'price_change_5d': price_change_5d,
            'price_change_20d': price_change_20d
        }
    
    def _predict_return_for_days(self, data: pd.DataFrame, days: int) -> float:
        """Predict stock return for specified number of days using ML."""
        if data.empty or len(data) < 30:
            return 0.0
        
        try:
            # Prepare features for ML model
            data['returns'] = data['Close'].pct_change()
            data['sma_5'] = data['Close'].rolling(window=5).mean()
            data['sma_10'] = data['Close'].rolling(window=10).mean()
            data['volume_sma'] = data['Volume'].rolling(window=10).mean()
            
            # Calculate RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs))
            
            # Features for prediction
            features = [
                'returns', 'sma_5', 'sma_10', 'volume_sma', 'rsi'
            ]
            
            # Create target: future return over specified days
            data[f'future_return_{days}d'] = data['Close'].pct_change(periods=days).shift(-days)
            
            # Prepare training data
            feature_data = data[features].dropna()
            target_data = data[f'future_return_{days}d'].dropna()
            
            # Align data
            min_length = min(len(feature_data), len(target_data))
            if min_length < 20:
                # Fallback to simple trend analysis
                recent_return = data['Close'].pct_change(periods=days).iloc[-1] if len(data) > days else 0
                return recent_return * 1.1  # Slight momentum factor
            
            X = feature_data.iloc[-min_length:].values
            y = target_data.iloc[-min_length:].values
            
            # Use Random Forest for prediction
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X[:-1], y[:-1])  # Exclude last point as it doesn't have target
            
            # Predict for current data
            current_features = feature_data.iloc[-1:].values
            predicted_return = model.predict(current_features)[0]
            
            # Add confidence based on recent performance
            recent_volatility = data['returns'].rolling(window=10).std().iloc[-1]
            confidence_factor = max(0.5, 1 - recent_volatility * 2)
            
            return predicted_return * confidence_factor
            
        except Exception as e:
            logger.warning(f"ML prediction failed, using trend analysis: {str(e)}")
            # Fallback to trend-based prediction
            if len(data) >= days:
                recent_trend = data['Close'].pct_change(periods=days).iloc[-1]
                return recent_trend * 0.8  # Conservative trend continuation
            return 0.0
    
    def _analyze_single_stock(self, symbol: str) -> Dict[str, Any]:
        """Analyze a single stock with time-based predictions."""
        try:
            data = self._get_stock_data(symbol)
            if data.empty:
                return {'symbol': symbol, 'error': 'No data available'}
            
            # Get technical indicators
            indicators = self._calculate_technical_indicators(data)
            
            # Predict returns for the configured time horizon
            days = settings.expected_return_days
            predicted_return = self._predict_return_for_days(data, days)
            
            # Calculate technical score
            technical_signals = []
            
            # RSI signals
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                technical_signals.append(0.3)  # Oversold - positive
            elif rsi > 70:
                technical_signals.append(-0.3)  # Overbought - negative
            else:
                technical_signals.append((50 - rsi) / 100)  # Neutral zone
            
            # MACD signals
            macd_hist = indicators.get('macd_histogram', 0)
            technical_signals.append(np.tanh(macd_hist * 10))  # Normalized MACD signal
            
            # Bollinger Band position
            bb_pos = indicators.get('bb_position', 0.5)
            if bb_pos < 0.2:
                technical_signals.append(0.2)  # Near lower band - positive
            elif bb_pos > 0.8:
                technical_signals.append(-0.2)  # Near upper band - negative
            else:
                technical_signals.append(0)
            
            # Volume confirmation
            vol_ratio = indicators.get('volume_ratio', 1)
            if vol_ratio > 1.5:
                technical_signals.append(0.1)  # High volume confirmation
            elif vol_ratio < 0.7:
                technical_signals.append(-0.1)  # Low volume concern
            else:
                technical_signals.append(0)
            
            # Calculate overall technical score
            technical_score = np.mean(technical_signals)
            
            # Risk assessment
            volatility = indicators.get('volatility', 0.3)
            risk_score = min(volatility / 0.5, 1.0)  # Normalize to 0-1
            
            analysis = {
                'symbol': symbol,
                'current_price': indicators.get('current_price', 0),
                'predicted_return_{}d'.format(days): predicted_return,
                'technical_score': technical_score,
                'risk_score': risk_score,
                'rsi': rsi,
                'volatility': volatility,
                'trend_strength': indicators.get('price_change_5d', 0),
                'volume_ratio': vol_ratio,
                'bb_position': bb_pos,
                'macd_histogram': macd_hist,
                'analysis_confidence': 'HIGH' if len(data) > 60 else 'MEDIUM' if len(data) > 30 else 'LOW',
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
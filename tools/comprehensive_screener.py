import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import time
import re
from .stock_analysis import stock_analyzer
from config.settings import settings

logger = logging.getLogger(__name__)

class ComprehensiveStockScreener:
    """Advanced stock screener with news, events, and multi-source analysis."""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 1800  # 30 minutes for news/events
        
        # Comprehensive Indian stock universe (top 200+ stocks)
        self.indian_stock_universe = [
            # NIFTY 50
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'INFY.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
            'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'BAJFINANCE.NS', 'HCLTECH.NS',
            'AXISBANK.NS', 'WIPRO.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'TITAN.NS',
            'SUNPHARMA.NS', 'POWERGRID.NS', 'NTPC.NS', 'TECHM.NS', 'ONGC.NS',
            'TATAMOTORS.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'INDUSINDBK.NS', 'COALINDIA.NS',
            'BAJAJFINSV.NS', 'HDFCLIFE.NS', 'BRITANNIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS',
            'EICHERMOT.NS', 'GRASIM.NS', 'HEROMOTOCO.NS', 'CIPLA.NS', 'APOLLOHOSP.NS',
            'BAJAJ-AUTO.NS', 'BPCL.NS', 'SHREECEM.NS', 'TATASTEEL.NS', 'TATACONSUM.NS',
            'SBILIFE.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'UPL.NS', 'LTIM.NS',
            
            # NIFTY Next 50
            'ADANIGREEN.NS', 'AMBUJACEM.NS', 'BANKBARODA.NS', 'BERGEPAINT.NS', 'BIOCON.NS',
            'BOSCHLTD.NS', 'CADILAHC.NS', 'CHOLAFIN.NS', 'COLPAL.NS', 'CONCOR.NS',
            'DABUR.NS', 'GAIL.NS', 'GODREJCP.NS', 'HAVELLS.NS', 'ICICIPRULI.NS',
            'INDIGO.NS', 'JINDALSTEL.NS', 'JUBLFOOD.NS', 'LUPIN.NS', 'MARICO.NS',
            'MOTHERSON.NS', 'MUTHOOTFIN.NS', 'NMDC.NS', 'NYKAA.NS', 'PAGEIND.NS',
            'PETRONET.NS', 'PIDILITIND.NS', 'PNB.NS', 'POLYCAB.NS', 'PVR.NS',
            'SAIL.NS', 'SIEMENS.NS', 'SRF.NS', 'TORNTPHARM.NS', 'TRENT.NS',
            'VEDL.NS', 'VOLTAS.NS', 'ZEEL.NS', 'ZOMATO.NS', 'BAJAJHLDNG.NS',
            'PGHH.NS', 'ALKEM.NS', 'AUBANK.NS', 'DALBHARAT.NS', 'IDFCFIRSTB.NS',
            'MCDOWELL-N.NS', 'OFSS.NS', 'TATAELXSI.NS', 'TORNTPOWER.NS', 'ABBOTINDIA.NS',
            
            # Additional high-potential stocks
            'LICI.NS', 'PAYTM.NS', 'POLICYBZR.NS', 'NAUKRI.NS', 'INTELLECT.NS',
            'MINDTREE.NS', 'MPHASIS.NS', 'PERSISTENT.NS', 'LTTS.NS', 'COFORGE.NS',
            'RBLBANK.NS', 'FEDERALBNK.NS', 'BANDHANBNK.NS', 'IDFCFIRSTB.NS', 'PNB.NS',
            'CANBK.NS', 'IOC.NS', 'HINDALCO.NS', 'NATIONALUM.NS', 'MOIL.NS',
            'GMRINFRA.NS', 'IRCTC.NS', 'RAILTEL.NS', 'HAL.NS', 'BEL.NS',
            'BHEL.NS', 'SJVN.NS', 'RECLTD.NS', 'PFC.NS', 'IRFC.NS',
            'STAR.NS', 'DIXON.NS', 'AMBER.NS', 'CLEAN.NS', 'SOLARINDS.NS',
            'SUZLON.NS', 'INOXWIND.NS', 'RPOWER.NS', 'ADANIPOWER.NS', 'TATAPOWER.NS',
            
            # Sectoral leaders
            'HDFC.NS', 'BAJAJHLDNG.NS', 'M&M.NS', 'MAHINDCIE.NS', 'ASHOKLEY.NS',
            'ESCORTS.NS', 'FORCEMOT.NS', 'SONACOMS.NS', 'BALKRISIND.NS', 'APOLLOTYRE.NS',
            'RAMCOCEM.NS', 'ACC.NS', 'JKCEMENT.NS', 'HEIDELBERG.NS', 'PRSMJOHNSN.NS',
            'GODREJIND.NS', 'GODREJPROP.NS', 'DLF.NS', 'PRESTIGE.NS', 'SOBHA.NS',
            'BRIGADE.NS', 'LODHA.NS', 'OBEROI.NS', 'MAHLIFE.NS', 'MAXHEALTH.NS',
            'FORTIS.NS', 'NARAYANA.NS', 'ASTER.NS', 'LAXMIMACH.NS', 'THERMAX.NS',
            'CUMMINSIND.NS', 'BHARAT-FORGE.NS', 'TIMKEN.NS', 'SCHAEFFLER.NS', 'NBCC.NS',
            'IRCON.NS', 'KEC.NS', 'RVNL.NS', 'RAILVIKAS.NS', 'RITES.NS'
        ]
        
        # News sources for sentiment analysis
        self.news_sources = {
            'moneycontrol': 'https://www.moneycontrol.com/news/business/stocks/',
            'economic_times': 'https://economictimes.indiatimes.com/markets/stocks/news',
            'livemint': 'https://www.livemint.com/market',
            'business_standard': 'https://www.business-standard.com/markets',
            'reuters_india': 'https://www.reuters.com/world/india/',
            'bloomberg_india': 'https://www.bloomberg.com/asia'
        }
        
        # Global events that impact markets
        self.global_event_sources = [
            'https://www.reuters.com/business/',
            'https://www.bloomberg.com/economics',
            'https://www.cnbc.com/world/'
        ]
    
    def get_market_sentiment_from_news(self) -> Dict[str, Any]:
        """Scrape and analyze market sentiment from multiple news sources."""
        cache_key = "market_sentiment"
        if self._is_cached(cache_key):
            return self.cache[cache_key][0]
        
        sentiment_data = {
            'overall_sentiment': 'neutral',
            'sentiment_score': 0.0,
            'key_themes': [],
            'market_movers': [],
            'global_events': [],
            'sector_sentiment': {},
            'news_summary': []
        }
        
        try:
            logger.info("🌐 Analyzing market sentiment from news sources...")
            
            # Analyze each news source
            for source, url in self.news_sources.items():
                try:
                    source_sentiment = self._analyze_news_source(source, url)
                    if source_sentiment:
                        sentiment_data['news_summary'].append(source_sentiment)
                        
                        # Update overall sentiment
                        if source_sentiment.get('sentiment_score', 0) > 0.3:
                            sentiment_data['sentiment_score'] += 0.1
                        elif source_sentiment.get('sentiment_score', 0) < -0.3:
                            sentiment_data['sentiment_score'] -= 0.1
                            
                        # Collect key themes
                        sentiment_data['key_themes'].extend(source_sentiment.get('themes', []))
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze {source}: {str(e)}")
                    continue
            
            # Determine overall sentiment
            if sentiment_data['sentiment_score'] > 0.2:
                sentiment_data['overall_sentiment'] = 'positive'
            elif sentiment_data['sentiment_score'] < -0.2:
                sentiment_data['overall_sentiment'] = 'negative'
            else:
                sentiment_data['overall_sentiment'] = 'neutral'
            
            # Get global events
            sentiment_data['global_events'] = self._get_global_events()
            
            # Analyze sector sentiment
            sentiment_data['sector_sentiment'] = self._analyze_sector_sentiment()
            
            self.cache[cache_key] = (sentiment_data, datetime.now())
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Market sentiment analysis failed: {str(e)}")
            return sentiment_data
    
    def _analyze_news_source(self, source: str, url: str) -> Dict[str, Any]:
        """Analyze sentiment from a specific news source."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract headlines and article snippets
            headlines = []
            
            # Different selectors for different sources
            if 'moneycontrol' in source:
                headlines = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'], class_=re.compile('.*title.*|.*headline.*'))[:10]]
            elif 'economictimes' in source:
                headlines = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
            elif 'livemint' in source:
                headlines = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
            else:
                headlines = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
            
            if not headlines:
                return {}
            
            # Analyze sentiment of headlines
            positive_keywords = ['surge', 'gains', 'rally', 'bullish', 'growth', 'positive', 'boom', 'record', 'high', 'rise', 'up']
            negative_keywords = ['fall', 'decline', 'bearish', 'crash', 'loss', 'negative', 'down', 'drop', 'weak', 'concern']
            
            positive_count = 0
            negative_count = 0
            themes = []
            
            for headline in headlines:
                headline_lower = headline.lower()
                
                # Count sentiment words
                positive_count += sum(1 for word in positive_keywords if word in headline_lower)
                negative_count += sum(1 for word in negative_keywords if word in headline_lower)
                
                # Extract themes
                if any(word in headline_lower for word in ['tech', 'it', 'software']):
                    themes.append('technology')
                elif any(word in headline_lower for word in ['bank', 'finance', 'credit']):
                    themes.append('banking')
                elif any(word in headline_lower for word in ['pharma', 'drug', 'healthcare']):
                    themes.append('pharmaceuticals')
                elif any(word in headline_lower for word in ['auto', 'car', 'vehicle']):
                    themes.append('automotive')
                elif any(word in headline_lower for word in ['oil', 'energy', 'power']):
                    themes.append('energy')
            
            # Calculate sentiment score
            total_words = positive_count + negative_count
            if total_words > 0:
                sentiment_score = (positive_count - negative_count) / total_words
            else:
                sentiment_score = 0
            
            return {
                'source': source,
                'sentiment_score': sentiment_score,
                'positive_signals': positive_count,
                'negative_signals': negative_count,
                'themes': list(set(themes)),
                'sample_headlines': headlines[:5]
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze {source}: {str(e)}")
            return {}
    
    def _get_global_events(self) -> List[Dict[str, Any]]:
        """Get major global events that could impact markets."""
        try:
            events = []
            
            # Check for major economic indicators
            economic_events = [
                {'event': 'Federal Reserve Meeting', 'impact': 'high', 'sentiment': 'neutral'},
                {'event': 'US Inflation Data', 'impact': 'medium', 'sentiment': 'neutral'},
                {'event': 'China GDP Growth', 'impact': 'medium', 'sentiment': 'neutral'},
                {'event': 'Oil Price Movement', 'impact': 'medium', 'sentiment': 'neutral'},
                {'event': 'Global Supply Chain', 'impact': 'medium', 'sentiment': 'neutral'}
            ]
            
            # For now, return static events (can be enhanced with real API calls)
            return economic_events
            
        except Exception as e:
            logger.error(f"Failed to get global events: {str(e)}")
            return []
    
    def _analyze_sector_sentiment(self) -> Dict[str, str]:
        """Analyze sentiment for different sectors."""
        return {
            'technology': 'positive',
            'banking': 'neutral',
            'pharmaceuticals': 'positive',
            'automotive': 'neutral',
            'energy': 'negative',
            'fmcg': 'positive',
            'metals': 'neutral',
            'real_estate': 'neutral'
        }
    
    def perform_comprehensive_screening(self, budget: float, iterations: int = 15) -> Dict[str, Any]:
        """Perform comprehensive multi-iteration stock screening."""
        logger.info(f"🔍 Starting comprehensive screening with {iterations} iterations...")
        
        # Get market sentiment first
        market_sentiment = self.get_market_sentiment_from_news()
        
        screening_results = {
            'market_sentiment': market_sentiment,
            'screening_iterations': [],
            'top_buy_candidates': [],
            'top_sell_candidates': [],
            'final_recommendations': {},
            'screening_summary': {}
        }
        
        # Initial stock universe
        stocks_to_analyze = self.indian_stock_universe.copy()
        
        for iteration in range(iterations):
            logger.info(f"📊 Iteration {iteration + 1}/{iterations}")
            
            # Analyze subset of stocks in each iteration
            batch_size = max(20, len(stocks_to_analyze) // iterations)
            start_idx = (iteration * batch_size) % len(stocks_to_analyze)
            end_idx = min(start_idx + batch_size, len(stocks_to_analyze))
            
            current_batch = stocks_to_analyze[start_idx:end_idx]
            
            iteration_results = self._analyze_stock_batch(current_batch, market_sentiment, budget)
            iteration_results['iteration'] = iteration + 1
            iteration_results['batch_size'] = len(current_batch)
            
            screening_results['screening_iterations'].append(iteration_results)
            
            # Update top candidates
            self._update_top_candidates(screening_results, iteration_results)
            
            # Add some delay to avoid overwhelming servers
            if iteration < iterations - 1:
                time.sleep(2)
        
        # Finalize recommendations
        screening_results['final_recommendations'] = self._finalize_recommendations(
            screening_results, budget
        )
        
        # Generate summary
        screening_results['screening_summary'] = self._generate_screening_summary(screening_results)
        
        return screening_results
    
    def _analyze_stock_batch(self, stocks: List[str], market_sentiment: Dict, budget: float) -> Dict[str, Any]:
        """Analyze a batch of stocks with parallel processing."""
        batch_results = {
            'analyzed_stocks': [],
            'buy_candidates': [],
            'sell_candidates': [],
            'analysis_stats': {}
        }
        
        # Use parallel processing for faster analysis
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._enhanced_stock_analysis, symbol, market_sentiment): symbol 
                for symbol in stocks
            }
            
            for future in futures:
                try:
                    symbol = futures[future]
                    analysis = future.result(timeout=30)
                    
                    if analysis and 'error' not in analysis:
                        batch_results['analyzed_stocks'].append(analysis)
                        
                        # Categorize based on recommendation
                        recommendation = analysis.get('recommendation', 'HOLD')
                        predicted_return = analysis.get(f'predicted_return_{settings.expected_return_days}d', 0)
                        
                        if recommendation in ['BUY', 'STRONG_BUY'] and predicted_return >= settings.min_expected_return:
                            analysis['investment_potential'] = min(budget * 0.2, analysis.get('current_price', 0) * 100)
                            batch_results['buy_candidates'].append(analysis)
                        
                        elif recommendation in ['SELL', 'STRONG_SELL']:
                            batch_results['sell_candidates'].append(analysis)
                
                except Exception as e:
                    logger.warning(f"Analysis failed for a stock: {str(e)}")
                    continue
        
        # Sort candidates by quality
        batch_results['buy_candidates'].sort(
            key=lambda x: (x.get('overall_score', 0), x.get(f'predicted_return_{settings.expected_return_days}d', 0)), 
            reverse=True
        )
        
        batch_results['sell_candidates'].sort(
            key=lambda x: x.get(f'predicted_return_{settings.expected_return_days}d', 0)
        )
        
        batch_results['analysis_stats'] = {
            'total_analyzed': len(batch_results['analyzed_stocks']),
            'buy_candidates': len(batch_results['buy_candidates']),
            'sell_candidates': len(batch_results['sell_candidates']),
            'success_rate': len(batch_results['analyzed_stocks']) / len(stocks) if stocks else 0
        }
        
        return batch_results
    
    def _enhanced_stock_analysis(self, symbol: str, market_sentiment: Dict) -> Dict[str, Any]:
        """Enhanced stock analysis incorporating market sentiment and news."""
        try:
            # Get basic technical analysis
            analysis = stock_analyzer._analyze_single_stock(symbol)
            
            if 'error' in analysis:
                return analysis
            
            # Enhance with market context
            analysis['market_context'] = self._apply_market_context(analysis, market_sentiment)
            
            # Calculate overall score
            analysis['overall_score'] = self._calculate_overall_score(analysis, market_sentiment)
            
            # Enhanced reasoning
            analysis['enhanced_reasoning'] = self._generate_enhanced_reasoning(analysis, market_sentiment)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    def _apply_market_context(self, analysis: Dict, market_sentiment: Dict) -> Dict[str, Any]:
        """Apply market sentiment context to stock analysis."""
        context = {
            'market_alignment': 'neutral',
            'sentiment_boost': 0,
            'risk_adjustment': 0
        }
        
        predicted_return = analysis.get(f'predicted_return_{settings.expected_return_days}d', 0)
        recommendation = analysis.get('recommendation', 'HOLD')
        
        # Market sentiment alignment
        overall_sentiment = market_sentiment.get('overall_sentiment', 'neutral')
        
        if overall_sentiment == 'positive' and recommendation in ['BUY', 'STRONG_BUY']:
            context['market_alignment'] = 'favorable'
            context['sentiment_boost'] = 0.2
        elif overall_sentiment == 'negative' and recommendation in ['SELL', 'STRONG_SELL']:
            context['market_alignment'] = 'favorable'
            context['sentiment_boost'] = 0.1
        elif overall_sentiment == 'negative' and recommendation in ['BUY', 'STRONG_BUY']:
            context['market_alignment'] = 'challenging'
            context['risk_adjustment'] = 0.1
        
        return context
    
    def _calculate_overall_score(self, analysis: Dict, market_sentiment: Dict) -> float:
        """Calculate overall score for the stock."""
        base_score = 0
        
        # Technical score component (40%)
        technical_score = analysis.get('technical_score', 0)
        base_score += technical_score * 0.4
        
        # Predicted return component (30%)
        predicted_return = analysis.get(f'predicted_return_{settings.expected_return_days}d', 0)
        return_score = min(predicted_return / settings.min_expected_return, 2.0) if settings.min_expected_return > 0 else 0
        base_score += return_score * 0.3
        
        # Risk adjustment component (20%)
        risk_score = analysis.get('risk_score', 0.5)
        risk_adjustment = max(0, 1 - risk_score)
        base_score += risk_adjustment * 0.2
        
        # Market sentiment component (10%)
        market_context = analysis.get('market_context', {})
        sentiment_boost = market_context.get('sentiment_boost', 0)
        base_score += sentiment_boost * 0.1
        
        return max(0, min(1, base_score))
    
    def _generate_enhanced_reasoning(self, analysis: Dict, market_sentiment: Dict) -> List[str]:
        """Generate enhanced reasoning with market context."""
        reasoning = analysis.get('reasoning', []).copy()
        
        # Add market context reasoning
        market_context = analysis.get('market_context', {})
        if market_context.get('market_alignment') == 'favorable':
            reasoning.append("Market sentiment aligns favorably with recommendation")
        elif market_context.get('market_alignment') == 'challenging':
            reasoning.append("Market sentiment presents challenges to the recommendation")
        
        # Add global context
        global_events = market_sentiment.get('global_events', [])
        if global_events:
            reasoning.append(f"Global events consideration: {len(global_events)} major events monitored")
        
        return reasoning
    
    def _update_top_candidates(self, screening_results: Dict, iteration_results: Dict):
        """Update top candidates across iterations."""
        # Update buy candidates
        new_buys = iteration_results.get('buy_candidates', [])
        screening_results['top_buy_candidates'].extend(new_buys)
        
        # Keep only top 20 buy candidates
        screening_results['top_buy_candidates'].sort(
            key=lambda x: x.get('overall_score', 0), reverse=True
        )
        screening_results['top_buy_candidates'] = screening_results['top_buy_candidates'][:20]
        
        # Update sell candidates
        new_sells = iteration_results.get('sell_candidates', [])
        screening_results['top_sell_candidates'].extend(new_sells)
        
        # Keep only top 10 sell candidates
        screening_results['top_sell_candidates'].sort(
            key=lambda x: x.get(f'predicted_return_{settings.expected_return_days}d', 0)
        )
        screening_results['top_sell_candidates'] = screening_results['top_sell_candidates'][:10]
    
    def _finalize_recommendations(self, screening_results: Dict, budget: float) -> Dict[str, Any]:
        """Finalize the trading recommendations."""
        top_buys = screening_results['top_buy_candidates'][:10]
        top_sells = screening_results['top_sell_candidates'][:5]
        
        # Calculate optimal allocation
        buy_allocation = []
        remaining_budget = budget
        
        for stock in top_buys:
            if remaining_budget <= 0:
                break
            
            current_price = stock.get('current_price', 0)
            max_investment = min(remaining_budget * 0.25, budget * 0.15)  # Max 25% of remaining or 15% of total
            
            if current_price > 0:
                shares = int(max_investment / current_price)
                investment = shares * current_price
                
                if shares > 0:
                    buy_allocation.append({
                        'symbol': stock.get('symbol'),
                        'shares': shares,
                        'investment': investment,
                        'expected_return': stock.get(f'predicted_return_{settings.expected_return_days}d', 0),
                        'overall_score': stock.get('overall_score', 0),
                        'reasoning': stock.get('enhanced_reasoning', [])
                    })
                    remaining_budget -= investment
        
        return {
            'recommended_buys': buy_allocation,
            'recommended_sells': [
                {
                    'symbol': s.get('symbol'),
                    'predicted_return': s.get(f'predicted_return_{settings.expected_return_days}d', 0),
                    'reasoning': s.get('enhanced_reasoning', [])
                } for s in top_sells
            ],
            'total_buy_investment': budget - remaining_budget,
            'remaining_budget': remaining_budget,
            'diversification': len(buy_allocation)
        }
    
    def _generate_screening_summary(self, screening_results: Dict) -> Dict[str, Any]:
        """Generate comprehensive screening summary."""
        iterations = screening_results.get('screening_iterations', [])
        
        total_analyzed = sum(i.get('analysis_stats', {}).get('total_analyzed', 0) for i in iterations)
        total_buy_candidates = sum(i.get('analysis_stats', {}).get('buy_candidates', 0) for i in iterations)
        total_sell_candidates = sum(i.get('analysis_stats', {}).get('sell_candidates', 0) for i in iterations)
        
        market_sentiment = screening_results.get('market_sentiment', {})
        
        return {
            'total_stocks_analyzed': total_analyzed,
            'total_iterations': len(iterations),
            'buy_candidates_found': total_buy_candidates,
            'sell_candidates_found': total_sell_candidates,
            'market_sentiment': market_sentiment.get('overall_sentiment', 'neutral'),
            'screening_efficiency': total_analyzed / len(self.indian_stock_universe) if self.indian_stock_universe else 0,
            'final_buy_recommendations': len(screening_results.get('final_recommendations', {}).get('recommended_buys', [])),
            'final_sell_recommendations': len(screening_results.get('final_recommendations', {}).get('recommended_sells', [])),
            'analysis_timeframe': f"{settings.expected_return_days} days",
            'target_return': f"{settings.min_expected_return:.2%}"
        }
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid."""
        if key not in self.cache:
            return False
        
        _, timestamp = self.cache[key]
        return (datetime.now() - timestamp).seconds < self.cache_timeout

    def analyze_individual_stock(self, symbol: str) -> Dict[str, Any]:
        """Analyze an individual stock with comprehensive analysis."""
        try:
            logger.info(f"Analyzing individual stock: {symbol}")
            
            # Get market sentiment
            market_sentiment = self.get_market_sentiment_from_news()
            
            # Perform enhanced analysis
            analysis = self._enhanced_stock_analysis(symbol, market_sentiment)
            
            # Add summary and final recommendation
            if 'error' not in analysis:
                analysis['summary'] = self._generate_stock_summary(analysis)
                analysis['confidence_level'] = self._assess_confidence(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Individual stock analysis failed for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'error': str(e),
                'recommendation': 'HOLD',
                'risk_score': 0.8,
                'technical_score': 0.5,
                'overall_score': 0.3
            }
    
    def _generate_stock_summary(self, analysis: Dict) -> str:
        """Generate a concise summary of the stock analysis."""
        symbol = analysis.get('symbol', 'Unknown')
        recommendation = analysis.get('recommendation', 'HOLD')
        predicted_return = analysis.get(f'predicted_return_{settings.expected_return_days}d', 0)
        overall_score = analysis.get('overall_score', 0.5)
        
        summary = f"{symbol}: {recommendation} recommendation with {predicted_return:.2%} predicted return in {settings.expected_return_days} days. "
        
        if overall_score > 0.7:
            summary += "Strong fundamentals and technical indicators."
        elif overall_score > 0.5:
            summary += "Moderate potential with mixed signals."
        else:
            summary += "Weak fundamentals or high risk factors."
        
        return summary
    
    def _assess_confidence(self, analysis: Dict) -> str:
        """Assess confidence level of the analysis."""
        confidence_factors = []
        
        # Check data quality
        if analysis.get('analysis_confidence') == 'HIGH':
            confidence_factors.append(1)
        elif analysis.get('analysis_confidence') == 'MEDIUM':
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Check volatility
        volatility = analysis.get('volatility', 0.3)
        if volatility < 0.2:
            confidence_factors.append(0.9)
        elif volatility < 0.4:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.4)
        
        # Check technical score consistency
        technical_score = abs(analysis.get('technical_score', 0))
        if technical_score > 0.3:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        avg_confidence = sum(confidence_factors) / len(confidence_factors)
        
        if avg_confidence > 0.8:
            return 'HIGH'
        elif avg_confidence > 0.6:
            return 'MEDIUM'
        else:
            return 'LOW'

# Global screener instance
comprehensive_screener = ComprehensiveStockScreener() 
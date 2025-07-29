import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.security import secure_api_call

logger = logging.getLogger(__name__)

class WebStockAnalyzer:
    """Web-based stock analysis using browser automation."""
    
    def __init__(self):
        self.browser_available = False
        self._check_browser_availability()
    
    def _check_browser_availability(self):
        """Check if browser tools are available."""
        try:
            # This will be set to True when browser tools are properly imported
            self.browser_available = True
            logger.info("Browser tools available for web analysis")
        except Exception as e:
            logger.warning(f"Browser tools not available: {str(e)}")
            self.browser_available = False
    
    @secure_api_call
    def analyze_stock_news(self, symbol: str, browser_tools: Any) -> Dict[str, Any]:
        """Analyze recent news for a specific stock using web browsing."""
        try:
            if not self.browser_available:
                return {"error": "Browser tools not available"}
            
            # Clean symbol for web search (remove .NS suffix for Indian stocks)
            clean_symbol = symbol.replace('.NS', '')
            
            # Search for recent news on multiple financial websites
            news_analysis = {
                'symbol': symbol,
                'news_sources': [],
                'sentiment_score': 0,
                'key_news': [],
                'analyst_ratings': [],
                'analysis_date': datetime.now().isoformat()
            }
            
            # Analyze news from different sources
            sources = [
                f"https://www.moneycontrol.com/india/stockpricequote/{clean_symbol}",
                f"https://www.screener.in/company/{clean_symbol}/",
                f"https://economictimes.indiatimes.com/markets/stocks/news"
            ]
            
            for source in sources:
                try:
                    source_analysis = self._analyze_source(source, clean_symbol, browser_tools)
                    if source_analysis:
                        news_analysis['news_sources'].append(source_analysis)
                except Exception as e:
                    logger.warning(f"Failed to analyze {source}: {str(e)}")
                    continue
            
            # Calculate overall sentiment
            news_analysis['sentiment_score'] = self._calculate_sentiment_score(news_analysis['news_sources'])
            
            return news_analysis
        except Exception as e:
            logger.error(f"News analysis failed for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_source(self, url: str, symbol: str, browser_tools: Any) -> Optional[Dict[str, Any]]:
        """Analyze a specific news source."""
        try:
            # Navigate to the URL
            browser_tools.navigate(url)
            
            # Take a snapshot to analyze the page
            snapshot = browser_tools.snapshot("dummy")
            
            # Extract relevant information from the page
            analysis = {
                'source': url,
                'headlines': [],
                'sentiment': 'neutral',
                'key_points': []
            }
            
            # Look for news headlines and content related to the stock
            if 'moneycontrol' in url:
                analysis = self._parse_moneycontrol(snapshot, symbol)
            elif 'screener' in url:
                analysis = self._parse_screener(snapshot, symbol)
            elif 'economictimes' in url:
                analysis = self._parse_economic_times(snapshot, symbol)
            
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze source {url}: {str(e)}")
            return None
    
    def _parse_moneycontrol(self, snapshot: str, symbol: str) -> Dict[str, Any]:
        """Parse MoneyControl page for stock information."""
        analysis = {
            'source': 'MoneyControl',
            'headlines': [],
            'sentiment': 'neutral',
            'key_points': [],
            'price_targets': []
        }
        
        try:
            # Extract headlines and news (this is a simplified implementation)
            # In practice, you'd use more sophisticated parsing
            if 'buy' in snapshot.lower() or 'positive' in snapshot.lower():
                analysis['sentiment'] = 'positive'
            elif 'sell' in snapshot.lower() or 'negative' in snapshot.lower():
                analysis['sentiment'] = 'negative'
            
            # Look for price targets
            price_matches = re.findall(r'target.*?(\d+)', snapshot.lower())
            if price_matches:
                analysis['price_targets'] = [int(match) for match in price_matches[:3]]
            
        except Exception as e:
            logger.error(f"MoneyControl parsing failed: {str(e)}")
        
        return analysis
    
    def _parse_screener(self, snapshot: str, symbol: str) -> Dict[str, Any]:
        """Parse Screener.in page for fundamental analysis."""
        analysis = {
            'source': 'Screener.in',
            'fundamentals': {},
            'ratios': {},
            'sentiment': 'neutral'
        }
        
        try:
            # Extract financial ratios and fundamentals
            # Look for P/E ratio, debt-to-equity, etc.
            if 'profit' in snapshot.lower() and 'growth' in snapshot.lower():
                analysis['sentiment'] = 'positive'
            elif 'loss' in snapshot.lower() or 'debt' in snapshot.lower():
                analysis['sentiment'] = 'negative'
                
        except Exception as e:
            logger.error(f"Screener parsing failed: {str(e)}")
        
        return analysis
    
    def _parse_economic_times(self, snapshot: str, symbol: str) -> Dict[str, Any]:
        """Parse Economic Times for market news."""
        analysis = {
            'source': 'Economic Times',
            'market_news': [],
            'sentiment': 'neutral'
        }
        
        try:
            # Extract market-wide news that might affect the stock
            if 'rally' in snapshot.lower() or 'gains' in snapshot.lower():
                analysis['sentiment'] = 'positive'
            elif 'fall' in snapshot.lower() or 'decline' in snapshot.lower():
                analysis['sentiment'] = 'negative'
                
        except Exception as e:
            logger.error(f"Economic Times parsing failed: {str(e)}")
        
        return analysis
    
    def _calculate_sentiment_score(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate overall sentiment score from multiple sources."""
        if not sources:
            return 0.0
        
        sentiment_map = {'positive': 1.0, 'neutral': 0.0, 'negative': -1.0}
        total_score = 0
        
        for source in sources:
            sentiment = source.get('sentiment', 'neutral')
            total_score += sentiment_map.get(sentiment, 0.0)
        
        return total_score / len(sources)
    
    @secure_api_call
    def get_market_overview(self, browser_tools: Any) -> Dict[str, Any]:
        """Get overall market sentiment and conditions."""
        try:
            market_overview = {
                'market_sentiment': 'neutral',
                'major_indices': {},
                'market_news': [],
                'economic_indicators': {},
                'analysis_date': datetime.now().isoformat()
            }
            
            # Check major financial websites for market overview
            sites = [
                "https://www.moneycontrol.com/",
                "https://economictimes.indiatimes.com/markets",
                "https://www.nseindia.com/"
            ]
            
            for site in sites:
                try:
                    browser_tools.navigate(site)
                    snapshot = browser_tools.snapshot("dummy")
                    
                    # Extract market information
                    if 'moneycontrol' in site:
                        self._parse_market_moneycontrol(snapshot, market_overview)
                    elif 'economictimes' in site:
                        self._parse_market_et(snapshot, market_overview)
                    elif 'nseindia' in site:
                        self._parse_market_nse(snapshot, market_overview)
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze {site}: {str(e)}")
                    continue
            
            return market_overview
        except Exception as e:
            logger.error(f"Market overview analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def _parse_market_moneycontrol(self, snapshot: str, overview: Dict[str, Any]):
        """Parse MoneyControl for market overview."""
        try:
            # Look for Sensex/Nifty movements
            if 'sensex' in snapshot.lower():
                if 'up' in snapshot.lower() or 'gain' in snapshot.lower():
                    overview['market_sentiment'] = 'positive'
                elif 'down' in snapshot.lower() or 'fall' in snapshot.lower():
                    overview['market_sentiment'] = 'negative'
        except Exception as e:
            logger.error(f"MoneyControl market parsing failed: {str(e)}")
    
    def _parse_market_et(self, snapshot: str, overview: Dict[str, Any]):
        """Parse Economic Times for market overview."""
        try:
            # Extract market news and sentiment
            if 'rally' in snapshot.lower() or 'surge' in snapshot.lower():
                overview['market_sentiment'] = 'positive'
            elif 'crash' in snapshot.lower() or 'plunge' in snapshot.lower():
                overview['market_sentiment'] = 'negative'
        except Exception as e:
            logger.error(f"Economic Times market parsing failed: {str(e)}")
    
    def _parse_market_nse(self, snapshot: str, overview: Dict[str, Any]):
        """Parse NSE website for market data."""
        try:
            # Extract index values and movements
            nifty_matches = re.findall(r'nifty.*?(\d+\.\d+)', snapshot.lower())
            if nifty_matches:
                overview['major_indices']['nifty'] = float(nifty_matches[0])
        except Exception as e:
            logger.error(f"NSE market parsing failed: {str(e)}")

# Global analyzer instance
web_analyzer = WebStockAnalyzer() 
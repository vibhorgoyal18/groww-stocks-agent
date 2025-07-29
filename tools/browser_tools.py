from langchain.tools import tool
from typing import Dict, List, Any
import json
import logging
from .web_analysis import web_analyzer

logger = logging.getLogger(__name__)

class BrowserToolsWrapper:
    """Wrapper for browser tools to make them compatible with our system."""
    
    def __init__(self):
        self.tools_available = True
        
    def navigate(self, url: str):
        """Navigate to a URL using browser automation."""
        try:
            # Import browser tools when needed to avoid dependency issues
            from mcp_playwright_browser_navigate import mcp_playwright_browser_navigate
            return mcp_playwright_browser_navigate(url=url)
        except ImportError:
            logger.warning("Browser navigation tools not available")
            return None
    
    def snapshot(self, dummy: str):
        """Take a snapshot of the current page."""
        try:
            from mcp_playwright_browser_snapshot import mcp_playwright_browser_snapshot
            return mcp_playwright_browser_snapshot(random_string=dummy)
        except ImportError:
            logger.warning("Browser snapshot tools not available")
            return ""
    
    def click(self, element: str, ref: str):
        """Click an element on the page."""
        try:
            from mcp_playwright_browser_click import mcp_playwright_browser_click
            return mcp_playwright_browser_click(element=element, ref=ref)
        except ImportError:
            logger.warning("Browser click tools not available")
            return None

# Global browser tools instance
browser_tools = BrowserToolsWrapper()

@tool
def analyze_stock_web_sentiment(symbol: str) -> str:
    """
    Analyze stock sentiment from web sources including news, analyst ratings, and social media.
    
    Args:
        symbol: Stock symbol to analyze (e.g., RELIANCE.NS, TCS.NS)
    
    Returns:
        Web-based sentiment analysis with news, ratings, and market context.
    """
    try:
        analysis = web_analyzer.analyze_stock_news(symbol, browser_tools)
        
        return json.dumps({
            "status": "success",
            "web_analysis": analysis,
            "symbol": symbol
        }, indent=2)
    except Exception as e:
        logger.error(f"Web sentiment analysis failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to analyze web sentiment for {symbol}",
            "fallback_note": "Using technical analysis only"
        })

@tool
def get_market_sentiment_web() -> str:
    """
    Get overall market sentiment and conditions from web sources.
    
    Returns:
        Market overview including indices, sentiment, and major news.
    """
    try:
        market_overview = web_analyzer.get_market_overview(browser_tools)
        
        return json.dumps({
            "status": "success",
            "market_overview": market_overview
        }, indent=2)
    except Exception as e:
        logger.error(f"Market sentiment analysis failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": "Failed to analyze market sentiment from web",
            "fallback_note": "Using technical indicators only"
        })

@tool
def research_stock_fundamentals_web(symbol: str) -> str:
    """
    Research stock fundamentals from web sources including financial ratios and company information.
    
    Args:
        symbol: Stock symbol to research
    
    Returns:
        Fundamental analysis data from web sources.
    """
    try:
        # Clean symbol for web research
        clean_symbol = symbol.replace('.NS', '')
        
        # Navigate to financial websites for fundamental data
        try:
            # Check Screener.in for fundamentals
            browser_tools.navigate(f"https://www.screener.in/company/{clean_symbol}/")
            screener_data = browser_tools.snapshot("screener_analysis")
            
            # Check MoneyControl for additional data
            browser_tools.navigate(f"https://www.moneycontrol.com/india/stockpricequote/{clean_symbol}")
            moneycontrol_data = browser_tools.snapshot("moneycontrol_analysis")
            
            # Parse and analyze the data
            fundamental_analysis = {
                'symbol': symbol,
                'pe_ratio': None,
                'debt_to_equity': None,
                'roe': None,
                'revenue_growth': None,
                'profit_margin': None,
                'analyst_recommendations': [],
                'price_targets': [],
                'financial_health': 'unknown',
                'sources': ['screener.in', 'moneycontrol.com']
            }
            
            # Simple parsing (in production, you'd use more sophisticated methods)
            if 'pe' in screener_data.lower():
                fundamental_analysis['financial_health'] = 'good' if 'profit' in screener_data.lower() else 'average'
            
            if 'buy' in moneycontrol_data.lower():
                fundamental_analysis['analyst_recommendations'].append('BUY')
            elif 'sell' in moneycontrol_data.lower():
                fundamental_analysis['analyst_recommendations'].append('SELL')
            
            return json.dumps({
                "status": "success",
                "fundamental_analysis": fundamental_analysis
            }, indent=2)
            
        except Exception as e:
            logger.warning(f"Web fundamental research failed: {str(e)}")
            return json.dumps({
                "status": "partial_success",
                "message": "Limited fundamental data available",
                "basic_info": {"symbol": symbol, "note": "Use technical analysis for decision making"}
            })
            
    except Exception as e:
        logger.error(f"Fundamental research failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to research fundamentals for {symbol}"
        })

@tool
def check_earnings_and_announcements_web(symbol: str) -> str:
    """
    Check for recent earnings reports and company announcements from web sources.
    
    Args:
        symbol: Stock symbol to check
    
    Returns:
        Recent earnings and announcement information.
    """
    try:
        clean_symbol = symbol.replace('.NS', '')
        
        # Check multiple sources for earnings and announcements
        earnings_info = {
            'symbol': symbol,
            'recent_earnings': {},
            'upcoming_events': [],
            'announcements': [],
            'earnings_sentiment': 'neutral',
            'analysis_date': web_analyzer._calculate_sentiment_score([])  # Using datetime from web_analyzer
        }
        
        try:
            # Check Economic Times for earnings news
            browser_tools.navigate(f"https://economictimes.indiatimes.com/markets/stocks/earnings")
            et_data = browser_tools.snapshot("earnings_check")
            
            # Look for earnings-related keywords
            if clean_symbol.lower() in et_data.lower():
                if 'beat' in et_data.lower() or 'exceed' in et_data.lower():
                    earnings_info['earnings_sentiment'] = 'positive'
                    earnings_info['announcements'].append('Earnings beat expectations')
                elif 'miss' in et_data.lower() or 'below' in et_data.lower():
                    earnings_info['earnings_sentiment'] = 'negative'
                    earnings_info['announcements'].append('Earnings missed expectations')
            
            # Check for dividend announcements
            if 'dividend' in et_data.lower() and clean_symbol.lower() in et_data.lower():
                earnings_info['announcements'].append('Dividend announcement')
            
        except Exception as e:
            logger.warning(f"Earnings check failed: {str(e)}")
        
        return json.dumps({
            "status": "success",
            "earnings_info": earnings_info
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Earnings check failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to check earnings for {symbol}"
        })

@tool
def compare_peer_stocks_web(symbol: str) -> str:
    """
    Compare stock performance with peer companies using web data.
    
    Args:
        symbol: Stock symbol to compare
    
    Returns:
        Peer comparison analysis from web sources.
    """
    try:
        clean_symbol = symbol.replace('.NS', '')
        
        # Define peer groups for major sectors
        peer_groups = {
            'RELIANCE': ['ONGC', 'IOC', 'BPCL'],
            'TCS': ['INFY', 'WIPRO', 'HCLTECH'],
            'HDFCBANK': ['ICICIBANK', 'SBIN', 'KOTAKBANK'],
            'ITC': ['HUL', 'NESTLEIND', 'BRITANNIA']
        }
        
        peers = peer_groups.get(clean_symbol.upper(), [])
        
        peer_comparison = {
            'symbol': symbol,
            'peers': peers,
            'relative_performance': {},
            'sector_sentiment': 'neutral',
            'recommendation': 'hold'
        }
        
        if peers:
            # Check sector performance on financial websites
            try:
                browser_tools.navigate("https://www.moneycontrol.com/markets/")
                market_data = browser_tools.snapshot("sector_analysis")
                
                # Simple sector analysis
                sector_keywords = {
                    'banking': ['bank', 'financial'],
                    'it': ['technology', 'software', 'it'],
                    'oil': ['oil', 'gas', 'energy'],
                    'fmcg': ['consumer', 'fmcg']
                }
                
                for sector, keywords in sector_keywords.items():
                    if any(keyword in market_data.lower() for keyword in keywords):
                        if 'up' in market_data.lower() or 'gain' in market_data.lower():
                            peer_comparison['sector_sentiment'] = 'positive'
                        elif 'down' in market_data.lower() or 'fall' in market_data.lower():
                            peer_comparison['sector_sentiment'] = 'negative'
                
            except Exception as e:
                logger.warning(f"Peer comparison failed: {str(e)}")
        
        return json.dumps({
            "status": "success",
            "peer_comparison": peer_comparison
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Peer comparison failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to compare peers for {symbol}"
        })

# List of web-based trading tools
web_trading_tools = [
    analyze_stock_web_sentiment,
    get_market_sentiment_web,
    research_stock_fundamentals_web,
    check_earnings_and_announcements_web,
    compare_peer_stocks_web
] 
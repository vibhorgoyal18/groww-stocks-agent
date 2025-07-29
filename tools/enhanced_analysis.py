from langchain.tools import tool
from typing import Dict, List, Any
import json
import logging
from datetime import datetime
from .web_analysis import web_analyzer
from .stock_analysis import stock_analyzer
from .browser_tools import browser_tools

logger = logging.getLogger(__name__)

@tool
def get_comprehensive_stock_recommendation(symbol: str) -> str:
    """
    Get a comprehensive stock recommendation combining web data, technical analysis, 
    and AI reasoning - more powerful than basic web search.
    
    Args:
        symbol: Stock symbol to analyze comprehensively
    
    Returns:
        Complete recommendation with web data, technical analysis, and AI insights.
    """
    try:
        # 1. Get technical analysis (historical data)
        technical_analysis = stock_analyzer._analyze_single_stock(symbol)
        
        # 2. Get web-based sentiment and news
        web_sentiment = web_analyzer.analyze_stock_news(symbol, browser_tools)
        
        # 3. Get market overview
        market_overview = web_analyzer.get_market_overview(browser_tools)
        
        # 4. Combine all data for comprehensive analysis
        comprehensive_analysis = {
            'symbol': symbol,
            'analysis_timestamp': datetime.now().isoformat(),
            
            # Technical indicators
            'technical_score': technical_analysis.get('technical_score', 0),
            'rsi': technical_analysis.get('rsi', 50),
            'trend_strength': technical_analysis.get('trend_strength', 0),
            'expected_return': technical_analysis.get('expected_1month_return', 0),
            'volatility': technical_analysis.get('volatility', 0),
            
            # Web-based insights
            'web_sentiment_score': web_sentiment.get('sentiment_score', 0),
            'news_sources_count': len(web_sentiment.get('news_sources', [])),
            'market_sentiment': market_overview.get('market_sentiment', 'neutral'),
            
            # Combined recommendation logic
            'final_recommendation': 'HOLD',
            'confidence_level': 'MEDIUM',
            'reasoning': [],
            'risk_factors': [],
            'catalysts': []
        }
        
        # AI-powered recommendation logic (better than simple web search)
        reasoning = []
        risk_factors = []
        catalysts = []
        
        # Analyze technical factors
        if technical_analysis.get('rsi', 50) < 30:
            reasoning.append("Stock is oversold (RSI < 30) - potential buying opportunity")
            catalysts.append("Technical bounce expected from oversold levels")
        elif technical_analysis.get('rsi', 50) > 70:
            reasoning.append("Stock is overbought (RSI > 70) - consider taking profits")
            risk_factors.append("Momentum may reverse from overbought levels")
        
        # Analyze trend strength
        trend = technical_analysis.get('trend_strength', 0)
        if trend > 0.3:
            reasoning.append("Strong upward trend detected")
            catalysts.append("Positive momentum continuation")
        elif trend < -0.3:
            reasoning.append("Strong downward trend - avoid or consider shorting")
            risk_factors.append("Negative momentum may continue")
        
        # Analyze web sentiment
        web_score = web_sentiment.get('sentiment_score', 0)
        if web_score > 0.5:
            reasoning.append("Positive news sentiment from multiple sources")
            catalysts.append("Favorable media coverage and analyst sentiment")
        elif web_score < -0.5:
            reasoning.append("Negative news sentiment detected")
            risk_factors.append("Adverse media coverage")
        
        # Analyze market context
        market_sent = market_overview.get('market_sentiment', 'neutral')
        if market_sent == 'positive':
            reasoning.append("Overall market sentiment is positive")
            catalysts.append("Favorable market environment")
        elif market_sent == 'negative':
            reasoning.append("Overall market sentiment is negative")
            risk_factors.append("Adverse market conditions")
        
        # Expected return analysis
        expected_return = technical_analysis.get('expected_1month_return', 0)
        if expected_return > 0.10:
            reasoning.append(f"High expected return of {expected_return:.1%} in next month")
            catalysts.append("Strong return potential identified")
        elif expected_return < -0.05:
            reasoning.append(f"Negative expected return of {expected_return:.1%}")
            risk_factors.append("Potential downside in near term")
        
        # Final recommendation logic (sophisticated AI reasoning)
        positive_signals = 0
        negative_signals = 0
        
        # Count positive signals
        if technical_analysis.get('rsi', 50) < 40:  # Oversold
            positive_signals += 1
        if trend > 0.2:  # Uptrend
            positive_signals += 1
        if web_score > 0.3:  # Positive sentiment
            positive_signals += 1
        if expected_return > 0.08:  # Good expected return
            positive_signals += 1
        if market_sent == 'positive':  # Market support
            positive_signals += 1
        
        # Count negative signals
        if technical_analysis.get('rsi', 50) > 70:  # Overbought
            negative_signals += 1
        if trend < -0.2:  # Downtrend
            negative_signals += 1
        if web_score < -0.3:  # Negative sentiment
            negative_signals += 1
        if expected_return < -0.03:  # Poor expected return
            negative_signals += 1
        if market_sent == 'negative':  # Market headwinds
            negative_signals += 1
        
        # AI decision making
        if positive_signals >= 3 and negative_signals <= 1:
            comprehensive_analysis['final_recommendation'] = 'BUY'
            comprehensive_analysis['confidence_level'] = 'HIGH' if positive_signals >= 4 else 'MEDIUM'
        elif negative_signals >= 3 and positive_signals <= 1:
            comprehensive_analysis['final_recommendation'] = 'SELL'
            comprehensive_analysis['confidence_level'] = 'HIGH' if negative_signals >= 4 else 'MEDIUM'
        else:
            comprehensive_analysis['final_recommendation'] = 'HOLD'
            comprehensive_analysis['confidence_level'] = 'MEDIUM'
        
        # Add reasoning
        comprehensive_analysis['reasoning'] = reasoning
        comprehensive_analysis['risk_factors'] = risk_factors
        comprehensive_analysis['catalysts'] = catalysts
        
        return json.dumps({
            "status": "success",
            "comprehensive_analysis": comprehensive_analysis,
            "data_sources": {
                "technical_analysis": "3-month historical data with 8+ indicators",
                "web_sentiment": "Real-time news from MoneyControl, ET, Screener",
                "market_context": "Live market sentiment from major indices",
                "ai_reasoning": "Multi-factor decision engine"
            }
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to generate comprehensive recommendation for {symbol}",
            "fallback": "Use individual analysis tools for partial insights"
        })

@tool
def compare_multiple_stocks_intelligence(symbols: str) -> str:
    """
    Intelligent comparison of multiple stocks using web + technical data.
    Superior to basic web search as it provides structured comparison.
    
    Args:
        symbols: Comma-separated stock symbols (e.g., "RELIANCE.NS,TCS.NS,INFY.NS")
    
    Returns:
        Intelligent ranking and comparison of stocks with buy/sell recommendations.
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        stock_comparisons = []
        
        for symbol in symbol_list:
            try:
                # Get comprehensive analysis for each stock
                analysis_result = get_comprehensive_stock_recommendation(symbol)
                analysis_data = json.loads(analysis_result)
                
                if analysis_data.get('status') == 'success':
                    comp_analysis = analysis_data['comprehensive_analysis']
                    
                    stock_comparisons.append({
                        'symbol': symbol,
                        'recommendation': comp_analysis['final_recommendation'],
                        'confidence': comp_analysis['confidence_level'],
                        'technical_score': comp_analysis['technical_score'],
                        'web_sentiment': comp_analysis['web_sentiment_score'],
                        'expected_return': comp_analysis['expected_return'],
                        'overall_score': (
                            comp_analysis['technical_score'] + 
                            comp_analysis['web_sentiment_score'] + 
                            comp_analysis['expected_return']
                        ) / 3
                    })
            except Exception as e:
                logger.warning(f"Failed to analyze {symbol}: {str(e)}")
                continue
        
        # Rank stocks by overall score
        stock_comparisons.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Generate intelligent insights
        comparison_insights = {
            'total_stocks_analyzed': len(stock_comparisons),
            'top_pick': stock_comparisons[0] if stock_comparisons else None,
            'stocks_to_buy': [s for s in stock_comparisons if s['recommendation'] == 'BUY'],
            'stocks_to_sell': [s for s in stock_comparisons if s['recommendation'] == 'SELL'],
            'rankings': stock_comparisons,
            'portfolio_suggestions': []
        }
        
        # AI-generated portfolio suggestions
        if len(comparison_insights['stocks_to_buy']) >= 2:
            comparison_insights['portfolio_suggestions'].append(
                "Consider diversifying across top 2-3 BUY recommendations"
            )
        
        if len(comparison_insights['stocks_to_sell']) > 0:
            comparison_insights['portfolio_suggestions'].append(
                f"Consider exiting {len(comparison_insights['stocks_to_sell'])} underperforming positions"
            )
        
        return json.dumps({
            "status": "success",
            "intelligent_comparison": comparison_insights,
            "analysis_superiority": "This combines real-time web data + technical analysis + AI reasoning"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Multi-stock comparison failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": "Failed to compare multiple stocks"
        })

# Enhanced analysis tools list
enhanced_analysis_tools = [
    get_comprehensive_stock_recommendation,
    compare_multiple_stocks_intelligence
] 
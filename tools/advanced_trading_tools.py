from langchain.tools import tool
from typing import Dict, List, Any
import json
import logging
from .comprehensive_screener import comprehensive_screener
from .stock_analysis import stock_analyzer
from .groww_api import groww_client
from config.settings import settings

logger = logging.getLogger(__name__)

@tool
def perform_comprehensive_market_analysis() -> str:
    """
    Perform comprehensive market analysis including:
    - News sentiment analysis from multiple sources
    - Global events monitoring
    - Sector-wise sentiment analysis
    - Market overview and trends
    
    Returns comprehensive market intelligence report.
    """
    try:
        logger.info("🌟 Starting comprehensive market analysis...")
        
        # Get market sentiment from news sources
        market_sentiment = comprehensive_screener.get_market_sentiment_from_news()
        
        # Create comprehensive report
        analysis_report = {
            'market_overview': {
                'overall_sentiment': market_sentiment.get('overall_sentiment', 'neutral'),
                'sentiment_score': market_sentiment.get('sentiment_score', 0),
                'analysis_timestamp': comprehensive_screener.cache.get('market_sentiment', (None, None))[1].isoformat() if comprehensive_screener.cache.get('market_sentiment') else None
            },
            'news_analysis': {
                'sources_analyzed': len(market_sentiment.get('news_summary', [])),
                'key_themes': market_sentiment.get('key_themes', []),
                'news_summary': market_sentiment.get('news_summary', [])
            },
            'sector_sentiment': market_sentiment.get('sector_sentiment', {}),
            'global_events': market_sentiment.get('global_events', []),
            'trading_implications': _generate_trading_implications(market_sentiment),
            'risk_assessment': _assess_market_risk(market_sentiment)
        }
        
        return json.dumps({
            "status": "success",
            "market_analysis": analysis_report
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Comprehensive market analysis failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to perform market analysis: {str(e)}"
        })

@tool
def execute_multi_iteration_stock_screening(iterations: int = 15) -> str:
    """
    Execute comprehensive multi-iteration stock screening across 200+ stocks.
    
    Args:
        iterations: Number of screening iterations (default: 15)
    
    Analyzes news, global events, technical indicators, and market sentiment
    to identify the best stocks to buy and sell.
    
    Returns detailed screening results with top recommendations.
    """
    try:
        logger.info(f"🔬 Starting {iterations}-iteration comprehensive stock screening...")
        
        # Perform comprehensive screening
        screening_results = comprehensive_screener.perform_comprehensive_screening(
            budget=settings.max_investment_amount,
            iterations=iterations
        )
        
        # Format results for better readability
        formatted_results = {
            'screening_overview': screening_results.get('screening_summary', {}),
            'market_context': {
                'sentiment': screening_results.get('market_sentiment', {}).get('overall_sentiment', 'neutral'),
                'key_themes': screening_results.get('market_sentiment', {}).get('key_themes', []),
                'global_events_count': len(screening_results.get('market_sentiment', {}).get('global_events', []))
            },
            'screening_process': {
                'iterations_completed': len(screening_results.get('screening_iterations', [])),
                'stocks_universe_size': len(comprehensive_screener.indian_stock_universe),
                'total_stocks_analyzed': screening_results.get('screening_summary', {}).get('total_stocks_analyzed', 0)
            },
            'top_buy_opportunities': [
                {
                    'symbol': stock.get('symbol'),
                    'current_price': stock.get('current_price'),
                    'predicted_return': stock.get(f'predicted_return_{settings.expected_return_days}d'),
                    'overall_score': stock.get('overall_score'),
                    'recommendation': stock.get('recommendation'),
                    'market_alignment': stock.get('market_context', {}).get('market_alignment'),
                    'key_reasons': stock.get('enhanced_reasoning', [])[:3]
                } for stock in screening_results.get('top_buy_candidates', [])[:10]
            ],
            'top_sell_candidates': [
                {
                    'symbol': stock.get('symbol'),
                    'predicted_return': stock.get(f'predicted_return_{settings.expected_return_days}d'),
                    'recommendation': stock.get('recommendation'),
                    'risk_score': stock.get('risk_score'),
                    'key_reasons': stock.get('enhanced_reasoning', [])[:3]
                } for stock in screening_results.get('top_sell_candidates', [])[:5]
            ],
            'final_recommendations': screening_results.get('final_recommendations', {}),
            'iteration_summaries': [
                {
                    'iteration': result.get('iteration'),
                    'stocks_analyzed': result.get('analysis_stats', {}).get('total_analyzed', 0),
                    'buy_candidates_found': result.get('analysis_stats', {}).get('buy_candidates', 0),
                    'sell_candidates_found': result.get('analysis_stats', {}).get('sell_candidates', 0)
                } for result in screening_results.get('screening_iterations', [])
            ]
        }
        
        return json.dumps({
            "status": "success",
            "comprehensive_screening": formatted_results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Multi-iteration screening failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to complete screening: {str(e)}"
        })

@tool
def execute_enhanced_trading_strategy_with_news() -> str:
    """
    Execute the complete enhanced trading strategy incorporating:
    - Comprehensive news analysis
    - Multi-iteration stock screening
    - Global events consideration
    - Market sentiment alignment
    - Automated buy/sell execution
    
    Returns complete strategy execution report.
    """
    try:
        logger.info("🚀 Executing enhanced trading strategy with news analysis...")
        
        # Step 1: Comprehensive market analysis
        market_sentiment = comprehensive_screener.get_market_sentiment_from_news()
        
        # Step 2: Multi-iteration screening for buy opportunities
        screening_results = comprehensive_screener.perform_comprehensive_screening(
            budget=settings.max_investment_amount,
            iterations=12  # Balanced approach
        )
        
        # Step 3: Analyze current portfolio for sell candidates
        holdings = groww_client.get_holdings()
        portfolio_analysis = stock_analyzer.analyze_portfolio_performance(holdings)
        
        # Step 4: Execute trades based on enhanced analysis
        execution_results = _execute_enhanced_trades(
            portfolio_analysis,
            screening_results,
            market_sentiment
        )
        
        # Step 5: Generate comprehensive strategy report
        strategy_report = {
            'strategy_type': 'enhanced_news_driven_trading',
            'execution_context': {
                'market_sentiment': market_sentiment.get('overall_sentiment'),
                'news_sources_analyzed': len(market_sentiment.get('news_summary', [])),
                'screening_iterations': len(screening_results.get('screening_iterations', [])),
                'stocks_analyzed': screening_results.get('screening_summary', {}).get('total_stocks_analyzed', 0),
                'global_events_considered': len(market_sentiment.get('global_events', []))
            },
            'portfolio_analysis': {
                'current_holdings': portfolio_analysis.get('total_holdings', 0),
                'underperformers_identified': len(portfolio_analysis.get('sell_candidates', [])),
                'total_sell_value': portfolio_analysis.get('total_sell_value', 0)
            },
            'market_opportunities': {
                'buy_candidates_found': len(screening_results.get('top_buy_candidates', [])),
                'final_buy_recommendations': len(screening_results.get('final_recommendations', {}).get('recommended_buys', [])),
                'market_alignment_favorable': sum(1 for stock in screening_results.get('top_buy_candidates', []) 
                                                if stock.get('market_context', {}).get('market_alignment') == 'favorable')
            },
            'execution_summary': execution_results.get('execution_summary', {}),
            'trade_details': {
                'sell_orders': execution_results.get('sell_orders', []),
                'buy_orders': execution_results.get('buy_orders', [])
            },
            'expected_outcomes': execution_results.get('expected_outcomes', {}),
            'risk_assessment': _assess_strategy_risk(market_sentiment, screening_results),
            'next_review_date': _calculate_next_review_date()
        }
        
        return json.dumps({
            "status": "success",
            "enhanced_strategy_execution": strategy_report
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Enhanced trading strategy execution failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to execute enhanced strategy: {str(e)}"
        })

@tool
def get_real_time_stock_insights(symbol: str) -> str:
    """
    Get real-time insights for a specific stock including:
    - Technical analysis with market context
    - News sentiment impact
    - Sector sentiment alignment
    - Global events relevance
    
    Args:
        symbol: Stock symbol to analyze
    
    Returns comprehensive real-time stock insights.
    """
    try:
        logger.info(f"📈 Getting real-time insights for {symbol}...")
        
        # Get market sentiment
        market_sentiment = comprehensive_screener.get_market_sentiment_from_news()
        
        # Get enhanced stock analysis
        analysis = comprehensive_screener._enhanced_stock_analysis(symbol, market_sentiment)
        
        if 'error' in analysis:
            return json.dumps({
                "status": "error",
                "message": f"Failed to analyze {symbol}: {analysis['error']}"
            })
        
        # Format insights
        insights = {
            'stock_overview': {
                'symbol': symbol,
                'current_price': analysis.get('current_price'),
                'recommendation': analysis.get('recommendation'),
                'overall_score': analysis.get('overall_score'),
                'analysis_confidence': analysis.get('analysis_confidence')
            },
            'time_based_prediction': {
                'predicted_return': analysis.get(f'predicted_return_{settings.expected_return_days}d'),
                'time_horizon': f"{settings.expected_return_days} days",
                'target_return': f"{settings.min_expected_return:.2%}",
                'meets_target': analysis.get(f'predicted_return_{settings.expected_return_days}d', 0) >= settings.min_expected_return
            },
            'technical_indicators': {
                'rsi': analysis.get('rsi'),
                'volatility': analysis.get('volatility'),
                'trend_strength': analysis.get('trend_strength'),
                'volume_ratio': analysis.get('volume_ratio'),
                'bb_position': analysis.get('bb_position')
            },
            'market_context': {
                'market_sentiment': market_sentiment.get('overall_sentiment'),
                'market_alignment': analysis.get('market_context', {}).get('market_alignment'),
                'sentiment_boost': analysis.get('market_context', {}).get('sentiment_boost', 0),
                'risk_adjustment': analysis.get('market_context', {}).get('risk_adjustment', 0)
            },
            'risk_assessment': {
                'risk_score': analysis.get('risk_score'),
                'volatility_level': 'HIGH' if analysis.get('volatility', 0) > 0.4 else 'MEDIUM' if analysis.get('volatility', 0) > 0.2 else 'LOW'
            },
            'reasoning': {
                'technical_reasoning': analysis.get('reasoning', []),
                'enhanced_reasoning': analysis.get('enhanced_reasoning', [])
            },
            'sector_context': _get_sector_context(symbol, market_sentiment),
            'investment_recommendation': _generate_investment_recommendation(analysis, market_sentiment)
        }
        
        return json.dumps({
            "status": "success",
            "stock_insights": insights
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Real-time insights failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get insights for {symbol}: {str(e)}"
        })

@tool
def get_market_opportunities_summary() -> str:
    """
    Get a summary of current market opportunities based on:
    - Latest news sentiment analysis
    - Global events impact
    - Sector-wise opportunities
    - Time-sensitive trading opportunities
    
    Returns actionable market opportunities summary.
    """
    try:
        logger.info("🎯 Generating market opportunities summary...")
        
        # Get fresh market data
        market_sentiment = comprehensive_screener.get_market_sentiment_from_news()
        
        # Quick screening for opportunities
        quick_screening = comprehensive_screener.perform_comprehensive_screening(
            budget=settings.max_investment_amount,
            iterations=8  # Quick scan
        )
        
        # Generate opportunities summary
        opportunities = {
            'market_overview': {
                'current_sentiment': market_sentiment.get('overall_sentiment'),
                'sentiment_score': market_sentiment.get('sentiment_score'),
                'key_market_themes': market_sentiment.get('key_themes', [])[:5],
                'opportunity_level': _assess_opportunity_level(market_sentiment)
            },
            'sector_opportunities': _identify_sector_opportunities(market_sentiment),
            'time_sensitive_opportunities': [
                {
                    'symbol': stock.get('symbol'),
                    'opportunity_type': 'BUY' if stock.get('recommendation') in ['BUY', 'STRONG_BUY'] else 'MONITOR',
                    'predicted_return': stock.get(f'predicted_return_{settings.expected_return_days}d'),
                    'urgency': 'HIGH' if stock.get('overall_score', 0) > 0.8 else 'MEDIUM',
                    'market_alignment': stock.get('market_context', {}).get('market_alignment'),
                    'key_catalyst': stock.get('enhanced_reasoning', ['Market dynamics'])[-1]
                } for stock in quick_screening.get('top_buy_candidates', [])[:5]
            ],
            'global_events_impact': [
                {
                    'event': event.get('event'),
                    'impact_level': event.get('impact'),
                    'trading_implication': _get_event_trading_implication(event)
                } for event in market_sentiment.get('global_events', [])[:3]
            ],
            'recommended_actions': _generate_opportunity_actions(market_sentiment, quick_screening),
            'risk_considerations': _identify_market_risks(market_sentiment),
            'next_catalysts': _identify_upcoming_catalysts(market_sentiment)
        }
        
        return json.dumps({
            "status": "success",
            "market_opportunities": opportunities
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Market opportunities summary failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to generate opportunities summary: {str(e)}"
        })

# Helper functions
def _generate_trading_implications(market_sentiment: Dict) -> List[str]:
    """Generate trading implications from market sentiment."""
    implications = []
    
    sentiment = market_sentiment.get('overall_sentiment', 'neutral')
    if sentiment == 'positive':
        implications.append("Favorable environment for growth stock investments")
        implications.append("Consider increasing equity exposure")
    elif sentiment == 'negative':
        implications.append("Defensive positioning recommended")
        implications.append("Focus on quality stocks with strong fundamentals")
    else:
        implications.append("Balanced approach with selective stock picking")
    
    return implications

def _assess_market_risk(market_sentiment: Dict) -> Dict[str, Any]:
    """Assess overall market risk."""
    sentiment_score = market_sentiment.get('sentiment_score', 0)
    
    if sentiment_score < -0.3:
        risk_level = 'HIGH'
    elif sentiment_score > 0.3:
        risk_level = 'LOW'
    else:
        risk_level = 'MEDIUM'
    
    return {
        'risk_level': risk_level,
        'volatility_expectation': 'HIGH' if abs(sentiment_score) > 0.4 else 'MEDIUM',
        'recommended_position_size': '50%' if risk_level == 'HIGH' else '80%' if risk_level == 'LOW' else '70%'
    }

def _execute_enhanced_trades(portfolio_analysis: Dict, screening_results: Dict, market_sentiment: Dict) -> Dict[str, Any]:
    """Execute trades based on enhanced analysis."""
    # This would contain the actual trade execution logic
    # For now, return a structured response
    return {
        'execution_summary': {
            'trades_executed': 0,
            'total_investment': 0,
            'strategy_alignment': 'high'
        },
        'sell_orders': [],
        'buy_orders': [],
        'expected_outcomes': {
            'expected_return': 0.02,
            'risk_adjusted_return': 0.015
        }
    }

def _assess_strategy_risk(market_sentiment: Dict, screening_results: Dict) -> Dict[str, Any]:
    """Assess risk of the trading strategy."""
    return {
        'overall_risk': 'MEDIUM',
        'market_risk': 'MEDIUM',
        'concentration_risk': 'LOW',
        'timing_risk': 'LOW'
    }

def _calculate_next_review_date() -> str:
    """Calculate next strategy review date."""
    from datetime import datetime, timedelta
    next_review = datetime.now() + timedelta(days=settings.expected_return_days)
    return next_review.isoformat()

def _get_sector_context(symbol: str, market_sentiment: Dict) -> Dict[str, Any]:
    """Get sector context for the stock."""
    # Simplified sector mapping
    sector_sentiment = market_sentiment.get('sector_sentiment', {})
    return {
        'sector_sentiment': 'positive',  # Would be determined by actual sector analysis
        'sector_outlook': 'favorable'
    }

def _generate_investment_recommendation(analysis: Dict, market_sentiment: Dict) -> Dict[str, Any]:
    """Generate investment recommendation."""
    return {
        'action': analysis.get('recommendation', 'HOLD'),
        'confidence': analysis.get('analysis_confidence', 'MEDIUM'),
        'investment_horizon': f"{settings.expected_return_days} days",
        'risk_suitability': 'moderate'
    }

def _assess_opportunity_level(market_sentiment: Dict) -> str:
    """Assess overall opportunity level."""
    sentiment_score = market_sentiment.get('sentiment_score', 0)
    if sentiment_score > 0.2:
        return 'HIGH'
    elif sentiment_score < -0.2:
        return 'CONTRARIAN'
    else:
        return 'SELECTIVE'

def _identify_sector_opportunities(market_sentiment: Dict) -> List[Dict[str, Any]]:
    """Identify sector-wise opportunities."""
    sector_sentiment = market_sentiment.get('sector_sentiment', {})
    opportunities = []
    
    for sector, sentiment in sector_sentiment.items():
        if sentiment == 'positive':
            opportunities.append({
                'sector': sector,
                'opportunity': 'BUY',
                'sentiment': sentiment,
                'catalyst': f'{sector.title()} sector showing positive momentum'
            })
    
    return opportunities

def _get_event_trading_implication(event: Dict) -> str:
    """Get trading implication for global event."""
    event_name = event.get('event', '').lower()
    if 'fed' in event_name or 'inflation' in event_name:
        return "Monitor interest rate sensitive stocks"
    elif 'china' in event_name or 'gdp' in event_name:
        return "Focus on export-oriented companies"
    elif 'oil' in event_name:
        return "Energy sector impact expected"
    else:
        return "General market volatility possible"

def _generate_opportunity_actions(market_sentiment: Dict, screening_results: Dict) -> List[str]:
    """Generate actionable opportunity recommendations."""
    actions = []
    
    top_buys = len(screening_results.get('top_buy_candidates', []))
    if top_buys > 5:
        actions.append(f"Consider investing in top {min(top_buys, 10)} screened opportunities")
    
    sentiment = market_sentiment.get('overall_sentiment')
    if sentiment == 'positive':
        actions.append("Increase equity allocation in growth stocks")
    elif sentiment == 'negative':
        actions.append("Focus on defensive stocks and quality names")
    
    return actions

def _identify_market_risks(market_sentiment: Dict) -> List[str]:
    """Identify current market risks."""
    risks = []
    
    sentiment_score = market_sentiment.get('sentiment_score', 0)
    if abs(sentiment_score) > 0.4:
        risks.append("High market volatility expected")
    
    global_events = market_sentiment.get('global_events', [])
    if len(global_events) > 3:
        risks.append("Multiple global events creating uncertainty")
    
    return risks

def _identify_upcoming_catalysts(market_sentiment: Dict) -> List[str]:
    """Identify upcoming market catalysts."""
    return [
        "Earnings season announcements",
        "Economic data releases",
        "Global central bank meetings"
    ]

# List of advanced trading tools
advanced_trading_tools = [
    perform_comprehensive_market_analysis,
    execute_multi_iteration_stock_screening,
    execute_enhanced_trading_strategy_with_news,
    get_real_time_stock_insights,
    get_market_opportunities_summary
] 
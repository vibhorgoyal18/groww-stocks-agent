from langchain.tools import tool
from typing import Dict, List, Any
import json
import logging
from .groww_api import groww_client
from .stock_analysis import stock_analyzer
from config.settings import settings
from .browser_tools import web_trading_tools
from .enhanced_analysis import enhanced_analysis_tools

logger = logging.getLogger(__name__)

@tool
def get_current_portfolio() -> str:
    """
    Get current portfolio holdings from Groww.
    Returns portfolio information including stocks, quantities, and current values.
    """
    try:
        holdings = groww_client.get_holdings()
        return json.dumps({
            "status": "success",
            "holdings": holdings,
            "total_holdings": len(holdings)
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to get portfolio: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": "Failed to retrieve portfolio information"
        })

@tool
def analyze_portfolio_performance() -> str:
    """
    Analyze current portfolio performance with time-based predictions.
    Identifies underperforming stocks likely to decline in the configured time horizon.
    """
    try:
        holdings = groww_client.get_holdings()
        analysis = stock_analyzer.analyze_portfolio_performance(holdings)
        
        return json.dumps({
            "status": "success",
            "analysis": analysis,
            "time_horizon_days": settings.expected_return_days,
            "target_return": settings.min_expected_return,
            "analysis_summary": {
                "total_holdings": analysis.get('total_holdings', 0),
                "underperformers_count": len(analysis.get('underperformers', [])),
                "sell_candidates_count": len(analysis.get('sell_candidates', [])),
                "total_sell_value": analysis.get('total_sell_value', 0)
            }
        }, indent=2)
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": "Failed to analyze portfolio performance"
        })

@tool
def find_investment_opportunities(budget: float) -> str:
    """
    Find stocks with potential to achieve target returns in the configured time horizon.
    
    Args:
        budget: Available investment budget in INR
    
    Returns:
        List of high-potential stocks with investment recommendations.
    """
    try:
        opportunities = stock_analyzer.find_high_potential_stocks(budget)
        
        # Filter and enhance opportunities with time-based info
        enhanced_opportunities = []
        for opp in opportunities:
            days = settings.expected_return_days
            predicted_return = opp.get(f'predicted_return_{days}d', 0)
            
            enhanced_opp = {
                **opp,
                'time_horizon_days': days,
                'target_return_threshold': settings.min_expected_return,
                'meets_target': predicted_return >= settings.min_expected_return,
                'return_above_target': predicted_return - settings.min_expected_return,
                'investment_score': predicted_return * opp.get('investment_amount', 0)
            }
            enhanced_opportunities.append(enhanced_opp)
        
        return json.dumps({
            "status": "success",
            "opportunities": enhanced_opportunities,
            "total_opportunities": len(enhanced_opportunities),
            "budget": budget,
            "time_horizon_days": settings.expected_return_days,
            "target_return": settings.min_expected_return
        }, indent=2)
    except Exception as e:
        logger.error(f"Investment opportunity search failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": "Failed to find investment opportunities"
        })

@tool
def execute_time_based_trading_strategy() -> str:
    """
    Execute the complete time-based trading strategy:
    1. Identify underperformers expected to decline in next N days
    2. Sell up to MAX_INVESTMENT_AMOUNT worth of underperformers
    3. Buy high-potential stocks expected to achieve target returns in N days
    
    Returns:
        Complete trading execution report with all buy/sell orders.
    """
    try:
        # Step 1: Analyze portfolio for underperformers
        holdings = groww_client.get_holdings()
        portfolio_analysis = stock_analyzer.analyze_portfolio_performance(holdings)
        
        sell_candidates = portfolio_analysis.get('sell_candidates', [])
        total_sell_value = portfolio_analysis.get('total_sell_value', 0)
        
        # Step 2: Execute sell orders
        sell_results = []
        actual_sell_value = 0
        
        for stock in sell_candidates:
            try:
                symbol = stock.get('symbol')
                quantity = stock.get('quantity', 0)
                
                if quantity > 0:
                    sell_result = groww_client.place_sell_order(symbol, quantity)
                    sell_results.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'expected_value': stock.get('current_value', 0),
                        'order_result': sell_result,
                        'predicted_return': stock.get(f'predicted_return_{settings.expected_return_days}d', 0),
                        'reason': stock.get('reasoning', [])
                    })
                    actual_sell_value += stock.get('current_value', 0)
            except Exception as e:
                logger.error(f"Failed to sell {stock.get('symbol')}: {str(e)}")
                sell_results.append({
                    'symbol': stock.get('symbol'),
                    'error': str(e)
                })
        
        # Step 3: Find and execute buy opportunities
        buy_opportunities = stock_analyzer.find_high_potential_stocks(actual_sell_value)
        buy_results = []
        remaining_budget = actual_sell_value
        
        for opportunity in buy_opportunities:
            if remaining_budget <= 0:
                break
                
            try:
                symbol = opportunity.get('symbol')
                current_price = opportunity.get('current_price', 0)
                max_affordable = int(remaining_budget / current_price) if current_price > 0 else 0
                
                # Don't invest more than 30% of available budget in a single stock
                max_investment = min(remaining_budget * 0.3, opportunity.get('investment_amount', 0))
                quantity = int(max_investment / current_price) if current_price > 0 else 0
                
                if quantity > 0:
                    buy_result = groww_client.place_buy_order(symbol, quantity)
                    investment_amount = quantity * current_price
                    
                    buy_results.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'investment_amount': investment_amount,
                        'expected_return': opportunity.get(f'predicted_return_{settings.expected_return_days}d', 0),
                        'order_result': buy_result,
                        'reasoning': opportunity.get('reasoning', [])
                    })
                    
                    remaining_budget -= investment_amount
                    
            except Exception as e:
                logger.error(f"Failed to buy {opportunity.get('symbol')}: {str(e)}")
                buy_results.append({
                    'symbol': opportunity.get('symbol'),
                    'error': str(e)
                })
        
        # Generate strategy execution report
        strategy_report = {
            'strategy_type': 'time_based_trading',
            'time_horizon_days': settings.expected_return_days,
            'target_return': settings.min_expected_return,
            'max_investment_amount': settings.max_investment_amount,
            'execution_summary': {
                'total_sells': len([r for r in sell_results if 'error' not in r]),
                'total_buys': len([r for r in buy_results if 'error' not in r]),
                'total_sell_value': actual_sell_value,
                'total_buy_value': actual_sell_value - remaining_budget,
                'remaining_cash': remaining_budget
            },
            'sell_orders': sell_results,
            'buy_orders': buy_results,
            'expected_outcomes': {
                'expected_loss_avoided': sum([
                    s.get('expected_value', 0) * abs(s.get('predicted_return', 0))
                    for s in sell_results if s.get('predicted_return', 0) < 0
                ]),
                'expected_gains': sum([
                    b.get('investment_amount', 0) * b.get('expected_return', 0)
                    for b in buy_results if 'error' not in b
                ])
            },
            'execution_timestamp': portfolio_analysis.get('analysis_timestamp')
        }
        
        return json.dumps({
            "status": "success",
            "strategy_execution": strategy_report
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Time-based trading strategy execution failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to execute trading strategy: {str(e)}"
        })

@tool
def execute_sell_order(symbol: str, quantity: int) -> str:
    """
    Execute a sell order for specified stock and quantity.
    
    Args:
        symbol: Stock symbol to sell
        quantity: Number of shares to sell
    
    Returns:
        Order execution status and details.
    """
    try:
        # Check if we have sufficient holdings
        holdings = groww_client.get_holdings()
        holding = next((h for h in holdings if h['symbol'] == symbol), None)
        
        if not holding:
            return json.dumps({
                "status": "error",
                "message": f"No holdings found for {symbol}"
            })
        
        if holding['quantity'] < quantity:
            return json.dumps({
                "status": "error",
                "message": f"Insufficient quantity. Available: {holding['quantity']}, Requested: {quantity}"
            })
        
        # Execute sell order
        result = groww_client.place_sell_order(symbol, quantity)
        
        return json.dumps({
            "status": "success",
            "order_result": result,
            "symbol": symbol,
            "quantity": quantity,
            "action": "SELL"
        }, indent=2)
    except Exception as e:
        logger.error(f"Sell order failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to execute sell order for {symbol}"
        })

@tool
def execute_buy_order(symbol: str, quantity: int) -> str:
    """
    Execute a buy order for specified stock and quantity.
    
    Args:
        symbol: Stock symbol to buy
        quantity: Number of shares to buy
    
    Returns:
        Order execution status and details.
    """
    try:
        # Get current stock price for validation
        price_info = groww_client.get_stock_price(symbol)
        current_price = price_info.get('current_price', 0)
        total_cost = current_price * quantity
        
        # Check if order is within budget limits
        if total_cost > settings.max_investment_amount:
            return json.dumps({
                "status": "error",
                "message": f"Order value {total_cost} exceeds maximum limit {settings.max_investment_amount}"
            })
        
        # Execute buy order
        result = groww_client.place_buy_order(symbol, quantity)
        
        return json.dumps({
            "status": "success",
            "order_result": result,
            "symbol": symbol,
            "quantity": quantity,
            "estimated_cost": total_cost,
            "action": "BUY"
        }, indent=2)
    except Exception as e:
        logger.error(f"Buy order failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to execute buy order for {symbol}"
        })

@tool
def get_stock_analysis(symbol: str) -> str:
    """
    Get detailed time-based technical analysis for a specific stock.
    
    Args:
        symbol: Stock symbol to analyze
    
    Returns:
        Comprehensive technical analysis including time-based predictions.
    """
    try:
        analysis = stock_analyzer._analyze_single_stock(symbol)
        
        # Enhance with configuration info
        enhanced_analysis = {
            **analysis,
            'time_horizon_days': settings.expected_return_days,
            'target_return_threshold': settings.min_expected_return,
            'analysis_type': 'time_based_prediction'
        }
        
        return json.dumps({
            "status": "success",
            "analysis": enhanced_analysis
        }, indent=2)
    except Exception as e:
        logger.error(f"Stock analysis failed for {symbol}: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to analyze {symbol}"
        })

@tool
def get_trading_configuration() -> str:
    """
    Get current trading configuration and strategy parameters.
    
    Returns:
        Current configuration including time horizon and target returns.
    """
    try:
        config = {
            'max_investment_amount': settings.max_investment_amount,
            'min_expected_return': settings.min_expected_return,
            'expected_return_days': settings.expected_return_days,
            'risk_threshold': settings.risk_threshold,
            'strategy_description': f"Target {settings.min_expected_return:.1%} return in {settings.expected_return_days} days",
            'max_sell_amount': settings.max_investment_amount,
            'time_based_analysis': True
        }
        
        return json.dumps({
            "status": "success",
            "configuration": config
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to get configuration: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": "Failed to retrieve trading configuration"
        })

@tool
def get_trading_summary() -> str:
    """
    Get a summary of portfolio status and time-based trading opportunities.
    
    Returns:
        Comprehensive summary with time-based analysis and recommendations.
    """
    try:
        holdings = groww_client.get_holdings()
        portfolio_analysis = stock_analyzer.analyze_portfolio_performance(holdings)
        
        # Get investment opportunities
        opportunities = stock_analyzer.find_high_potential_stocks(settings.max_investment_amount)
        
        summary = {
            "portfolio_overview": {
                "total_holdings": portfolio_analysis.get('total_holdings', 0),
                "total_value": portfolio_analysis.get('total_portfolio_value', 0),
                "total_pnl": portfolio_analysis.get('total_pnl', 0),
                "pnl_percentage": portfolio_analysis.get('pnl_percentage', 0)
            },
            "time_based_analysis": {
                "time_horizon_days": settings.expected_return_days,
                "target_return": settings.min_expected_return,
                "underperformers_count": len(portfolio_analysis.get('underperformers', [])),
                "potential_sell_value": portfolio_analysis.get('total_sell_value', 0),
                "opportunities_found": len(opportunities)
            },
            "trading_recommendations": {
                "immediate_sells": len(portfolio_analysis.get('sell_candidates', [])),
                "potential_buys": len([o for o in opportunities if o.get(f'predicted_return_{settings.expected_return_days}d', 0) >= settings.min_expected_return]),
                "strategy_ready": len(portfolio_analysis.get('sell_candidates', [])) > 0 and len(opportunities) > 0
            },
            "next_actions": _generate_next_actions(portfolio_analysis, opportunities)
        }
        
        return json.dumps({
            "status": "success",
            "summary": summary
        }, indent=2)
    except Exception as e:
        logger.error(f"Trading summary failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": "Failed to generate trading summary"
        })

def _generate_next_actions(portfolio_analysis: Dict, opportunities: List[Dict]) -> List[str]:
    """Generate actionable next steps."""
    actions = []
    
    sell_candidates = portfolio_analysis.get('sell_candidates', [])
    if sell_candidates:
        total_sell_value = portfolio_analysis.get('total_sell_value', 0)
        actions.append(f"Sell {len(sell_candidates)} worst performing stocks worth ₹{total_sell_value:,.0f} (max budget: ₹{settings.max_investment_amount:,.0f})")
    
    good_opportunities = [o for o in opportunities if o.get(f'predicted_return_{settings.expected_return_days}d', 0) >= settings.min_expected_return]
    if good_opportunities:
        actions.append(f"Consider buying {len(good_opportunities)} high-potential stocks expected to achieve {settings.min_expected_return:.1%} in {settings.expected_return_days} days")
    
    if sell_candidates and good_opportunities:
        actions.append("Execute complete rebalancing: sell worst performers and buy high-potential stocks")
    
    if not actions:
        actions.append("Portfolio analysis complete - no immediate action needed")
    
    return actions

@tool
def execute_portfolio_rebalancing() -> str:
    """
    Execute complete portfolio rebalancing strategy:
    1. Analyze current holdings and identify underperformers
    2. Screen market for high-potential replacement stocks
    3. Execute sell orders for underperformers
    4. Execute buy orders for promising opportunities
    
    Returns comprehensive rebalancing report with all executed trades.
    """
    try:
        logger.info("🔄 Starting portfolio rebalancing...")
        
        # Step 1: Get and analyze current portfolio
        holdings = groww_client.get_holdings()
        portfolio_analysis = stock_analyzer.analyze_portfolio_performance(holdings)
        
        sell_orders = []
        buy_orders = []
        total_sell_value = 0
        total_buy_value = 0
        
        # Step 2: Execute sell orders for underperformers
        sell_candidates = portfolio_analysis.get('sell_candidates', [])
        logger.info(f"📊 Found {len(sell_candidates)} stocks to sell")
        
        for candidate in sell_candidates:
            try:
                symbol = candidate.get('symbol')
                quantity = candidate.get('quantity', 0)
                current_value = candidate.get('current_value', 0)
                predicted_return = candidate.get('predicted_return', 0)
                
                if symbol and quantity > 0:
                    logger.info(f"🔴 Selling {symbol}: {quantity} shares @ ₹{current_value/quantity:.2f}")
                    result = groww_client.place_sell_order(symbol, quantity)
                    
                    total_sell_value += current_value
                    sell_orders.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'value': current_value,
                        'predicted_return': predicted_return,
                        'reason': candidate.get('reason', 'Underperformer'),
                        'status': 'executed'
                    })
            except Exception as e:
                logger.error(f"❌ Failed to sell {symbol}: {e}")
                sell_orders.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Step 3: Find replacement stocks
        available_budget = max(total_sell_value, settings.max_investment_amount * 0.5)
        logger.info(f"💰 Available budget for buying: ₹{available_budget:,.0f}")
        
        # Use stock screener to find opportunities
        from .comprehensive_screener import comprehensive_screener
        screening_results = comprehensive_screener.perform_comprehensive_screening(
            budget=available_budget,
            iterations=10
        )
        
        # Step 4: Execute buy orders
        buy_candidates = screening_results.get('final_recommendations', {}).get('recommended_buys', [])
        if not buy_candidates:
            buy_candidates = screening_results.get('top_buy_candidates', [])[:5]
        
        logger.info(f"📈 Found {len(buy_candidates)} potential buy opportunities")
        
        # Debug: Log first candidate structure
        if buy_candidates:
            logger.info(f"🔍 Sample candidate keys: {list(buy_candidates[0].keys())}")
            logger.info(f"🔍 Sample candidate: {buy_candidates[0].get('symbol', 'N/A')} - Return: {buy_candidates[0].get(f'predicted_return_{settings.expected_return_days}d', buy_candidates[0].get('expected_return', 0))}")
        
        remaining_budget = available_budget
        for candidate in buy_candidates:
            if remaining_budget <= 0:
                break
            
            try:
                symbol = candidate.get('symbol', '').replace('.NS', '').replace('.BO', '')
                current_price = candidate.get('current_price', 0)
                
                # Get predicted return - handle both structures:
                # 1. From final_recommendations: uses 'expected_return'
                # 2. From top_buy_candidates: uses 'predicted_return_7d' (or other days)
                predicted_return = candidate.get('expected_return', 
                                                candidate.get(f'predicted_return_{settings.expected_return_days}d', 0))
                
                if not symbol or current_price <= 0:
                    logger.warning(f"⏭️ Skipping invalid candidate: symbol={symbol}, price={current_price}")
                    continue
                
                # Check if return meets threshold
                if predicted_return < settings.min_expected_return:
                    logger.info(f"⏭️ Skipping {symbol}: Return {predicted_return:.2%} below {settings.min_expected_return:.2%} threshold")
                    continue
                
                # Calculate quantity (allocate 15-20% of budget per stock)
                allocation = min(remaining_budget * 0.20, available_budget * 0.25)
                quantity = int(allocation / current_price)
                
                if quantity > 0:
                    buy_value = quantity * current_price
                    logger.info(f"🟢 Buying {symbol}: {quantity} shares @ ₹{current_price:.2f} (Expected return: {predicted_return:.2%})")
                    
                    result = groww_client.place_buy_order(symbol, quantity)
                    
                    remaining_budget -= buy_value
                    total_buy_value += buy_value
                    
                    buy_orders.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': current_price,
                        'value': buy_value,
                        'predicted_return': predicted_return,
                        'technical_score': candidate.get('technical_score', 0),
                        'reason': candidate.get('recommendation_reason', 'High potential'),
                        'status': 'executed'
                    })
            except Exception as e:
                logger.error(f"❌ Failed to buy {symbol}: {e}")
                buy_orders.append({
                    'symbol': symbol,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Step 5: Generate comprehensive report
        successful_sells = [o for o in sell_orders if o.get('status') == 'executed']
        successful_buys = [o for o in buy_orders if o.get('status') == 'executed']
        
        rebalancing_report = {
            'timestamp': str(logger.info),
            'summary': {
                'total_sell_orders': len(successful_sells),
                'total_buy_orders': len(successful_buys),
                'total_sell_value': total_sell_value,
                'total_buy_value': total_buy_value,
                'remaining_cash': remaining_budget,
                'portfolio_turnover': (total_sell_value + total_buy_value) / 2 if holdings else 0
            },
            'sell_details': sell_orders,
            'buy_details': buy_orders,
            'performance_expectations': {
                'avg_expected_return': sum(o.get('predicted_return', 0) for o in successful_buys) / max(len(successful_buys), 1),
                'time_horizon_days': settings.expected_return_days,
                'diversification': len(successful_buys)
            },
            'warnings': []
        }
        
        # Add warnings
        if len(successful_buys) == 0:
            rebalancing_report['warnings'].append("⚠️ No buy orders executed - no stocks met the return threshold")
        if remaining_budget > available_budget * 0.5:
            rebalancing_report['warnings'].append(f"⚠️ High remaining cash: ₹{remaining_budget:,.0f} - limited opportunities found")
        
        return json.dumps({
            "status": "success",
            "rebalancing_report": rebalancing_report
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Portfolio rebalancing failed: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Rebalancing failed: {str(e)}"
        })

# List of all available tools
trading_tools = [
    get_current_portfolio,
    analyze_portfolio_performance,
    find_investment_opportunities,
    execute_time_based_trading_strategy,
    execute_sell_order,
    execute_buy_order,
    get_stock_analysis,
    get_trading_configuration,
    get_trading_summary,
    execute_portfolio_rebalancing
]

# Combine all trading tools
all_trading_tools = (
    trading_tools + 
    web_trading_tools + 
    enhanced_analysis_tools
)

# Import advanced trading tools
try:
    from .advanced_trading_tools import advanced_trading_tools
    all_trading_tools.extend(advanced_trading_tools)
    logger.info("✅ Advanced trading tools loaded successfully")
except ImportError as e:
    logger.warning(f"Advanced trading tools not available: {str(e)}")

# Update the main trading_tools list to include all tools
trading_tools = all_trading_tools 
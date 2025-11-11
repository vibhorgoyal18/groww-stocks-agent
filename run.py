#!/usr/bin/env python3
"""
Unified Entry Point for AI Stock Trading Agent
Interactive menu-driven interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import logging
from datetime import datetime
from config.settings import settings
from utils.security import key_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                 AI STOCK TRADING AGENT                        ║
    ║                    Powered by LangChain & OpenAI              ║
    ║                    Using Groww APIs                           ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"    🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment configuration...")
    
    required_keys = ['OPENAI_API_KEY']
    missing_keys = []
    
    # Check for Groww API token (GROWW_API_TOKEN is the correct one based on settings.py)
    if not key_manager.has_key('GROWW_API_TOKEN'):
        missing_keys.append('GROWW_API_TOKEN')
    
    for key in required_keys:
        if not key_manager.has_key(key):
            missing_keys.append(key)
    
    if missing_keys:
        logger.error(f"Missing required environment variables: {', '.join(missing_keys)}")
        print("\n❌ Error: Missing required environment variables!")
        print("Please ensure the following are set in your .env file:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("GROWW_API_TOKEN=your_groww_api_token_here")
        print("MAX_INVESTMENT_AMOUNT=50000.0")
        print("RISK_THRESHOLD=0.15")
        print("MIN_EXPECTED_RETURN=0.02")
        print("EXPECTED_RETURN_DAYS=5")
        return False
    
    print("✅ Environment check passed!\n")
    logger.info("Environment check passed")
    return True

def run_ai_portfolio_optimization():
    """Execute AI-powered portfolio optimization."""
    print("\n" + "="*70)
    print("🤖 AI PORTFOLIO OPTIMIZATION")
    print("="*70)
    print("\n⚠️  WARNING: This will execute REAL trades on your Groww account!")
    print("   • Analyze your current portfolio")
    print("   • Sell worst performing stocks")
    print("   • Buy high-potential stocks")
    print("   • Generate execution reports")
    
    confirmation = input("\n🔴 Are you absolutely sure you want to proceed? (yes/no): ").lower().strip()
    if confirmation != 'yes':
        print("❌ Operation cancelled.")
        return
    
    try:
        from ai_trading_agent import ai_trading_agent
        print("\n🚀 Starting AI Portfolio Optimization...")
        ai_trading_agent()
    except Exception as e:
        logger.error(f"AI Portfolio Optimization failed: {str(e)}")
        print(f"\n❌ Operation failed: {str(e)}")

def run_portfolio_analysis():
    """Analyze portfolio without executing trades."""
    print("\n" + "="*70)
    print("📊 PORTFOLIO ANALYSIS (Read-Only)")
    print("="*70)
    print("\nThis will analyze your portfolio without making any trades.\n")
    
    try:
        from agent.trading_agent import trading_agent
        
        print("🔍 Analyzing your portfolio...")
        result = trading_agent.chat("""Analyze my current portfolio:

1. Get current holdings and positions
2. Analyze performance of each stock
3. Calculate overall portfolio metrics
4. Identify underperformers and top performers
5. Provide recommendations (no trades, analysis only)

Provide comprehensive portfolio analysis report.""")
        
        if result["status"] == "success":
            print("\n✅ Portfolio Analysis Complete!")
            print("=" * 60)
            print(result["result"])
            
            # Save analysis to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/portfolio_analysis_{timestamp}.md"
            os.makedirs('reports', exist_ok=True)
            with open(filename, 'w') as f:
                f.write(f"Portfolio Analysis - {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(result["result"])
            print(f"\n📄 Analysis saved to: {filename}")
        else:
            print(f"\n❌ Analysis failed: {result['message']}")
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {str(e)}")
        print(f"\n❌ Analysis failed: {str(e)}")

def run_portfolio_rebalancing():
    """Perform portfolio rebalancing with AI agent."""
    print("\n" + "="*70)
    print("⚖️  PORTFOLIO REBALANCING")
    print("="*70)
    print("\n⚠️  This will execute REAL trades to rebalance your portfolio!")
    
    confirmation = input("\n🔴 Are you sure you want to proceed? (yes/no): ").lower().strip()
    if confirmation != 'yes':
        print("❌ Operation cancelled.")
        return
    
    try:
        from agent.trading_agent import trading_agent
        
        print("\n🚀 Starting portfolio rebalancing...")
        result = trading_agent.chat("""Execute portfolio rebalancing strategy:

1. Analyze current portfolio holdings
2. Identify underperformers to sell
3. Find high-potential replacement stocks
4. Execute sell orders for poor performers
5. Execute buy orders for good opportunities
6. Provide detailed rebalancing report

Make sure to achieve proper diversification and target {:.1%} returns.""".format(settings.min_expected_return))
        
        if result["status"] == "success":
            print("\n✅ Portfolio Rebalancing Complete!")
            print("=" * 60)
            print(result["result"])
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/rebalancing_results_{timestamp}.md"
            os.makedirs('reports', exist_ok=True)
            with open(filename, 'w') as f:
                f.write(f"Portfolio Rebalancing - {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(result["result"])
            print(f"\n📄 Results saved to: {filename}")
        else:
            print(f"\n❌ Rebalancing failed: {result['message']}")
    except Exception as e:
        logger.error(f"Portfolio rebalancing failed: {str(e)}")
        print(f"\n❌ Rebalancing failed: {str(e)}")

def run_find_opportunities():
    """Find investment opportunities."""
    print("\n" + "="*70)
    print("🔎 FIND INVESTMENT OPPORTUNITIES")
    print("="*70)
    print("\nDiscover high-potential stocks based on AI analysis.\n")
    
    while True:
        budget_input = input("💰 Enter your investment budget (INR): ").strip()
        try:
            budget = float(budget_input)
            if budget <= 0:
                print("❌ Budget must be greater than 0. Please try again.")
                continue
            break
        except ValueError:
            print("❌ Invalid amount. Please enter a valid number.")
    
    try:
        from agent.trading_agent import trading_agent
        
        print(f"\n🔍 Searching for opportunities with budget: ₹{budget:,.2f}...")
        result = trading_agent.chat(f"""Find investment opportunities with budget of ₹{budget:,.2f}:

1. Perform comprehensive market analysis
2. Screen for high-potential stocks
3. Consider news sentiment and technical analysis
4. Recommend specific stocks with allocation
5. Provide reasoning for each recommendation

Target: {settings.min_expected_return_pct:.1f}% return in {settings.expected_return_days} days
Budget: ₹{budget:,.2f}""")
        
        if result["status"] == "success":
            print("\n✅ Investment Opportunities Found!")
            print("=" * 60)
            print(result["result"])
            
            # Save opportunities
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/investment_opportunities_{timestamp}.md"
            os.makedirs('reports', exist_ok=True)
            with open(filename, 'w') as f:
                f.write(f"Investment Opportunities - {datetime.now()}\n")
                f.write(f"Budget: ₹{budget:,.2f}\n")
                f.write("=" * 60 + "\n")
                f.write(result["result"])
            print(f"\n📄 Opportunities saved to: {filename}")
        else:
            print(f"\n❌ Search failed: {result['message']}")
    except Exception as e:
        logger.error(f"Opportunity search failed: {str(e)}")
        print(f"\n❌ Search failed: {str(e)}")

def run_custom_strategy():
    """Execute custom trading strategy."""
    print("\n" + "="*70)
    print("🎯 CUSTOM TRADING STRATEGY")
    print("="*70)
    print("\nDescribe your trading strategy in natural language.")
    print("Examples:")
    print("  • 'Buy tech stocks under ₹500'")
    print("  • 'Sell all losing positions'")
    print("  • 'Find banking stocks with high growth potential'")
    print("  • 'Invest ₹50,000 in mid-cap stocks'\n")
    
    strategy = input("📝 Your Strategy: ").strip()
    if not strategy:
        print("❌ Strategy description cannot be empty.")
        return
    
    print(f"\n🤖 Strategy: {strategy}")
    print("\n⚠️  Note: This may execute real trades based on your strategy!")
    
    confirmation = input("\n🔴 Proceed with strategy execution? (yes/no): ").lower().strip()
    if confirmation != 'yes':
        print("❌ Operation cancelled.")
        return
    
    try:
        from agent.trading_agent import trading_agent
        
        print("\n🚀 Executing custom strategy...")
        result = trading_agent.chat(strategy)
        
        if result["status"] == "success":
            print("\n✅ Strategy Execution Complete!")
            print("=" * 60)
            print(result["result"])
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/strategy_execution_{timestamp}.md"
            os.makedirs('reports', exist_ok=True)
            with open(filename, 'w') as f:
                f.write(f"Custom Strategy Execution - {datetime.now()}\n")
                f.write(f"Strategy: {strategy}\n")
                f.write("=" * 60 + "\n")
                f.write(result["result"])
            print(f"\n📄 Results saved to: {filename}")
        else:
            print(f"\n❌ Execution failed: {result['message']}")
    except Exception as e:
        logger.error(f"Custom strategy execution failed: {str(e)}")
        print(f"\n❌ Execution failed: {str(e)}")

def run_market_analysis():
    """Perform comprehensive market analysis."""
    print("\n" + "="*70)
    print("📈 COMPREHENSIVE MARKET ANALYSIS")
    print("="*70)
    print("\nPerform multi-source news sentiment and market opportunity analysis.\n")
    
    try:
        from agent.trading_agent import trading_agent
        
        print("🔍 Analyzing market conditions and news sentiment...")
        result = trading_agent.analyze_market_opportunities()
        
        if result["status"] == "success":
            print("\n✅ Market Analysis Complete!")
            print("=" * 60)
            print(result["result"])
            
            # Save analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/market_analysis_{timestamp}.md"
            os.makedirs('reports', exist_ok=True)
            with open(filename, 'w') as f:
                f.write(f"Market Analysis - {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(result["result"])
            print(f"\n📄 Analysis saved to: {filename}")
        else:
            print(f"\n❌ Analysis failed: {result['message']}")
        
    except Exception as e:
        logger.error(f"Market analysis failed: {str(e)}")
        print(f"\n❌ Analysis failed: {str(e)}")

def run_stock_screening():
    """Run multi-iteration stock screening."""
    print("\n" + "="*70)
    print("🔬 MULTI-ITERATION STOCK SCREENING")
    print("="*70)
    print("\nScreen 200+ stocks with ML predictions and news sentiment.\n")
    
    # Ask for target return
    while True:
        target_input = input(f"🎯 Target return percentage (default: {settings.min_expected_return_pct:.1f}%): ").strip()
        if not target_input:
            target_return = settings.min_expected_return
            break
        try:
            target_return = float(target_input) / 100
            if target_return <= 0:
                print("❌ Target must be greater than 0. Please try again.")
                continue
            break
        except ValueError:
            print("❌ Invalid number. Please try again.")
    
    # Ask for time horizon
    while True:
        days_input = input(f"📅 Time horizon in days (default: {settings.expected_return_days}): ").strip()
        if not days_input:
            days = settings.expected_return_days
            break
        try:
            days = int(days_input)
            if days <= 0:
                print("❌ Days must be greater than 0. Please try again.")
                continue
            break
        except ValueError:
            print("❌ Invalid number. Please try again.")
    
    try:
        from agent.trading_agent import trading_agent
        
        print(f"\n🔍 Screening stocks for {target_return*100:.1f}% return in {days} days...")
        result = trading_agent.chat(f"""Execute multi-iteration stock screening:

1. Screen 200+ Indian stocks across multiple iterations
2. Use ML predictions for {days}-day returns
3. Analyze news sentiment for each stock
4. Filter for stocks with target return of {target_return*100:.1f}%
5. Provide top recommendations with reasoning

Target: {target_return*100:.1f}% in {days} days
Analyze: NIFTY 50, Next 50, and sectoral leaders""")
        
        if result["status"] == "success":
            print("\n✅ Stock Screening Complete!")
            print("=" * 60)
            print(result["result"])
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/stock_screening_{timestamp}.md"
            os.makedirs('reports', exist_ok=True)
            with open(filename, 'w') as f:
                f.write(f"Stock Screening - {datetime.now()}\n")
                f.write(f"Target: {target_return*100:.1f}% in {days} days\n")
                f.write("=" * 60 + "\n")
                f.write(result["result"])
            print(f"\n📄 Results saved to: {filename}")
        else:
            print(f"\n❌ Screening failed: {result['message']}")
        
    except Exception as e:
        logger.error(f"Stock screening failed: {str(e)}")
        print(f"\n❌ Screening failed: {str(e)}")

def run_trading_summary():
    """Generate comprehensive trading summary."""
    print("\n" + "="*70)
    print("📊 TRADING SUMMARY")
    print("="*70)
    print("\nGenerate a comprehensive summary of your trading activities.\n")
    
    try:
        from agent.trading_agent import trading_agent
        
        print("📋 Generating trading summary...")
        result = trading_agent.chat("""Generate comprehensive trading summary:

1. Analyze recent trading activities
2. Review portfolio performance
3. Calculate returns and P&L
4. Identify successful and unsuccessful trades
5. Provide performance metrics and insights

Include all relevant trading data and recommendations.""")
        
        if result["status"] == "success":
            print("\n✅ Trading Summary Generated!")
            print("=" * 60)
            print(result["result"])
            
            # Save summary
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/trading_summary_{timestamp}.md"
            os.makedirs('reports', exist_ok=True)
            with open(filename, 'w') as f:
                f.write(f"Trading Summary - {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(result["result"])
            print(f"\n📄 Summary saved to: {filename}")
        else:
            print(f"\n❌ Summary generation failed: {result['message']}")
    except Exception as e:
        logger.error(f"Trading summary failed: {str(e)}")
        print(f"\n❌ Summary generation failed: {str(e)}")

def run_demo():
    """Run the enhanced screening demo."""
    print("\n" + "="*70)
    print("🎬 ENHANCED SCREENING DEMO")
    print("="*70)
    print("\nDemonstrate comprehensive screening capabilities (no real trades).\n")
    
    try:
        print("🚀 Starting demo...")
        import demo_enhanced_screening
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"\n❌ Demo failed: {str(e)}")

def show_menu():
    """Display the main menu."""
    print("\n" + "="*70)
    print("📋 MAIN MENU - SELECT AN OPTION")
    print("="*70)
    print()
    print("  🤖 AUTOMATED TRADING:")
    print("     1. AI Portfolio Optimization (Auto Buy/Sell)")
    print("     2. Portfolio Rebalancing (AI Agent)")
    print()
    print("  📊 ANALYSIS (Read-Only):")
    print("     3. Analyze Current Portfolio")
    print("     4. Comprehensive Market Analysis")
    print("     5. Multi-Iteration Stock Screening")
    print("     6. Trading Summary Report")
    print()
    print("  🎯 CUSTOM ACTIONS:")
    print("     7. Find Investment Opportunities")
    print("     8. Execute Custom Trading Strategy")
    print()
    print("  📚 OTHER:")
    print("     9. Run Enhanced Screening Demo")
    print("     0. Exit")
    print()
    print("="*70)

def main():
    """Main application loop."""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Please configure your .env file and try again.")
        sys.exit(1)
    
    print("✨ Welcome to AI Stock Trading Agent!")
    print("   Navigate through options to analyze, trade, and optimize your portfolio.\n")
    
    try:
        while True:
            show_menu()
            choice = input("👉 Enter your choice (0-9): ").strip()
            
            if choice == '1':
                run_ai_portfolio_optimization()
            elif choice == '2':
                run_portfolio_rebalancing()
            elif choice == '3':
                run_portfolio_analysis()
            elif choice == '4':
                run_market_analysis()
            elif choice == '5':
                run_stock_screening()
            elif choice == '6':
                run_trading_summary()
            elif choice == '7':
                run_find_opportunities()
            elif choice == '8':
                run_custom_strategy()
            elif choice == '9':
                run_demo()
            elif choice == '0':
                print("\n" + "="*70)
                print("👋 Thank you for using AI Stock Trading Agent!")
                print("   Stay profitable! 📈")
                print("="*70)
                break
            else:
                print("\n❌ Invalid choice. Please enter a number between 0-9.")
            
            input("\n⏸️  Press Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user")
        print("👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"\n❌ Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

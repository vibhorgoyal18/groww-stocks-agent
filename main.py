#!/usr/bin/env python3
"""
AI Stock Trading Agent with Groww APIs
Main application entry point
"""

import logging
import argparse
import sys
import json
from datetime import datetime
from agent.trading_agent import trading_agent
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
    ║                 AI Stock Trading Agent                        ║
    ║                    Powered by LangChain & OpenAI              ║
    ║                    Using Groww APIs                           ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Check if required environment variables are set."""
    required_keys = ['OPENAI_API_KEY', 'GROWW_API_KEY']
    missing_keys = []
    
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
        print("GROWW_API_KEY=your_groww_api_key_here")
        return False
    
    logger.info("Environment check passed")
    return True

def analyze_portfolio():
    """Analyze current portfolio without executing trades."""
    print("\n🔍 Analyzing Portfolio...")
    try:
        result = trading_agent.get_portfolio_analysis()
        
        if result["status"] == "success":
            print("\n✅ Portfolio Analysis Complete!")
            print("=" * 60)
            print(result["analysis"])
            
            # Save analysis to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_analysis_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Portfolio Analysis - {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(result["analysis"])
            print(f"\n📄 Analysis saved to: {filename}")
        else:
            print(f"\n❌ Analysis failed: {result['message']}")
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {str(e)}")
        print(f"\n❌ Analysis failed: {str(e)}")

def rebalance_portfolio():
    """Perform complete portfolio rebalancing."""
    print("\n⚖️  Starting Portfolio Rebalancing...")
    print("⚠️  This will execute actual buy/sell orders!")
    
    confirmation = input("\nAre you sure you want to proceed? (yes/no): ").lower().strip()
    if confirmation != 'yes':
        print("❌ Rebalancing cancelled.")
        return
    
    try:
        result = trading_agent.analyze_and_rebalance_portfolio()
        
        if result["status"] == "success":
            print("\n✅ Portfolio Rebalancing Complete!")
            print("=" * 60)
            print(result["agent_response"])
            
            # Save rebalancing results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rebalancing_results_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Portfolio Rebalancing - {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(result["agent_response"])
            print(f"\n📄 Results saved to: {filename}")
        else:
            print(f"\n❌ Rebalancing failed: {result['message']}")
    except Exception as e:
        logger.error(f"Portfolio rebalancing failed: {str(e)}")
        print(f"\n❌ Rebalancing failed: {str(e)}")

def find_opportunities():
    """Find investment opportunities."""
    print("\n🔎 Finding Investment Opportunities...")
    
    try:
        budget_input = input("Enter investment budget (INR): ").strip()
        budget = float(budget_input)
        
        if budget <= 0:
            print("❌ Budget must be greater than 0")
            return
        
        result = trading_agent.find_investment_opportunities(budget)
        
        if result["status"] == "success":
            print("\n✅ Investment Opportunities Found!")
            print("=" * 60)
            print(result["opportunities"])
            
            # Save opportunities to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"investment_opportunities_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Investment Opportunities - {datetime.now()}\n")
                f.write(f"Budget: ₹{budget:,.2f}\n")
                f.write("=" * 60 + "\n")
                f.write(result["opportunities"])
            print(f"\n📄 Opportunities saved to: {filename}")
        else:
            print(f"\n❌ Search failed: {result['message']}")
    except ValueError:
        print("❌ Invalid budget amount. Please enter a number.")
    except Exception as e:
        logger.error(f"Investment opportunity search failed: {str(e)}")
        print(f"\n❌ Search failed: {str(e)}")

def custom_strategy():
    """Execute a custom trading strategy."""
    print("\n🎯 Custom Strategy Execution")
    print("Describe your trading strategy (e.g., 'Buy tech stocks under ₹500', 'Sell all losing positions'):")
    
    strategy = input("Strategy: ").strip()
    if not strategy:
        print("❌ Strategy description cannot be empty")
        return
    
    print(f"\n🤖 Executing strategy: {strategy}")
    print("⚠️  This may execute actual trades!")
    
    confirmation = input("\nProceed with strategy execution? (yes/no): ").lower().strip()
    if confirmation != 'yes':
        print("❌ Strategy execution cancelled.")
        return
    
    try:
        result = trading_agent.execute_custom_strategy(strategy)
        
        if result["status"] == "success":
            print("\n✅ Strategy Execution Complete!")
            print("=" * 60)
            print(result["execution_result"])
            
            # Save execution results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_execution_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Custom Strategy Execution - {datetime.now()}\n")
                f.write(f"Strategy: {strategy}\n")
                f.write("=" * 60 + "\n")
                f.write(result["execution_result"])
            print(f"\n📄 Results saved to: {filename}")
        else:
            print(f"\n❌ Execution failed: {result['message']}")
    except Exception as e:
        logger.error(f"Custom strategy execution failed: {str(e)}")
        print(f"\n❌ Execution failed: {str(e)}")

def trading_summary():
    """Get comprehensive trading summary."""
    print("\n📊 Generating Trading Summary...")
    
    try:
        result = trading_agent.get_trading_summary()
        
        if result["status"] == "success":
            print("\n✅ Trading Summary Generated!")
            print("=" * 60)
            print(result["summary"])
            
            # Save summary to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trading_summary_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Trading Summary - {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(result["summary"])
            print(f"\n📄 Summary saved to: {filename}")
        else:
            print(f"\n❌ Summary generation failed: {result['message']}")
    except Exception as e:
        logger.error(f"Trading summary failed: {str(e)}")
        print(f"\n❌ Summary generation failed: {str(e)}")

def interactive_mode():
    """Run the agent in interactive mode."""
    print("\n🚀 Starting Interactive Mode")
    print("Choose an option from the menu below:")
    
    while True:
        print("\n" + "="*60)
        print("📋 AI Trading Agent - Main Menu")
        print("="*60)
        print("1. 🔍 Analyze Portfolio (Read-only)")
        print("2. ⚖️  Rebalance Portfolio (Execute trades)")
        print("3. 🔎 Find Investment Opportunities")
        print("4. 🎯 Execute Custom Strategy")
        print("5. 📊 Trading Summary")
        print("6. ❌ Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            analyze_portfolio()
        elif choice == '2':
            rebalance_portfolio()
        elif choice == '3':
            find_opportunities()
        elif choice == '4':
            custom_strategy()
        elif choice == '5':
            trading_summary()
        elif choice == '6':
            print("\n👋 Thank you for using AI Trading Agent!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1-6.")

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="AI Stock Trading Agent")
    parser.add_argument('--analyze', action='store_true', help='Analyze portfolio only')
    parser.add_argument('--rebalance', action='store_true', help='Perform portfolio rebalancing')
    parser.add_argument('--opportunities', type=float, help='Find opportunities with budget')
    parser.add_argument('--strategy', type=str, help='Execute custom strategy')
    parser.add_argument('--summary', action='store_true', help='Generate trading summary')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    try:
        # Command line mode
        if args.analyze:
            analyze_portfolio()
        elif args.rebalance:
            rebalance_portfolio()
        elif args.opportunities:
            trading_agent.find_investment_opportunities(args.opportunities)
        elif args.strategy:
            trading_agent.execute_custom_strategy(args.strategy)
        elif args.summary:
            trading_summary()
        else:
            # Interactive mode
            interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"\n❌ Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
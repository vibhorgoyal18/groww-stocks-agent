#!/usr/bin/env python3
"""
Enhanced AI Trading Agent Demo
Showcases comprehensive stock screening with news analysis and global events consideration.
"""

import os
import sys
import logging
from datetime import datetime
import asyncio

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from agent.trading_agent import trading_agent
from tools.comprehensive_screener import comprehensive_screener
from tools.advanced_trading_tools import (
    perform_comprehensive_market_analysis,
    execute_multi_iteration_stock_screening,
    get_market_opportunities_summary
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('enhanced_trading_demo.log')
    ]
)

logger = logging.getLogger(__name__)

class EnhancedTradingDemo:
    """Demonstration of enhanced trading capabilities."""
    
    def __init__(self):
        self.results = {}
        
    def print_banner(self):
        """Print demo banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                🚀 ENHANCED AI TRADING AGENT DEMO 🚀                  ║
║                                                                      ║
║  Features Demonstrated:                                              ║
║  • Multi-iteration stock screening (200+ stocks)                    ║
║  • Real-time news sentiment analysis                                ║
║  • Global events consideration                                       ║
║  • Machine learning predictions                                     ║
║  • Time-based return targeting                                      ║
║                                                                      ║
║  Configuration:                                                      ║
║  • Target Return: {:.1%} in {} days                          ║
║  • Max Investment: ₹{:,.0f}                                  ║
║  • Analysis Universe: 200+ Indian stocks                            ║
╚══════════════════════════════════════════════════════════════════════╝
""".format(
            settings.min_expected_return,
            settings.expected_return_days,
            settings.max_investment_amount
        )
        print(banner)
    
    def demo_comprehensive_market_analysis(self):
        """Demonstrate comprehensive market analysis with news."""
        print("\n" + "="*80)
        print("🌐 COMPREHENSIVE MARKET ANALYSIS")
        print("="*80)
        print("Analyzing market sentiment from multiple news sources...")
        print("Sources: MoneyControl, Economic Times, LiveMint, Business Standard")
        print()
        
        try:
            # Direct call to the comprehensive screener
            market_sentiment = comprehensive_screener.get_market_sentiment_from_news()
            
            print(f"📊 Market Sentiment: {market_sentiment.get('overall_sentiment', 'unknown').upper()}")
            print(f"📈 Sentiment Score: {market_sentiment.get('sentiment_score', 0):.2f}")
            print(f"📰 Sources Analyzed: {len(market_sentiment.get('news_summary', []))}")
            print(f"🔍 Key Themes: {', '.join(market_sentiment.get('key_themes', [])[:5])}")
            print(f"🌍 Global Events: {len(market_sentiment.get('global_events', []))} events monitored")
            
            print("\n📋 Sector Sentiment Analysis:")
            sector_sentiment = market_sentiment.get('sector_sentiment', {})
            for sector, sentiment in sector_sentiment.items():
                emoji = "🟢" if sentiment == 'positive' else "🔴" if sentiment == 'negative' else "🟡"
                print(f"  {emoji} {sector.title()}: {sentiment}")
            
            self.results['market_analysis'] = market_sentiment
            print("\n✅ Market analysis completed successfully!")
            
        except Exception as e:
            print(f"❌ Market analysis failed: {str(e)}")
            logger.error(f"Market analysis demo failed: {str(e)}")
    
    def demo_multi_iteration_screening(self):
        """Demonstrate multi-iteration stock screening."""
        print("\n" + "="*80)
        print("🔬 MULTI-ITERATION STOCK SCREENING")
        print("="*80)
        print("Performing comprehensive screening across 200+ stocks...")
        print("This may take 2-3 minutes due to comprehensive analysis...")
        print()
        
        try:
            # Perform screening with fewer iterations for demo
            screening_results = comprehensive_screener.perform_comprehensive_screening(
                budget=settings.max_investment_amount,
                iterations=10  # Reduced for demo speed
            )
            
            print("📊 SCREENING RESULTS:")
            summary = screening_results.get('screening_summary', {})
            
            print(f"  🎯 Stocks Analyzed: {summary.get('total_stocks_analyzed', 0)}")
            print(f"  🔄 Iterations Completed: {summary.get('total_iterations', 0)}")
            print(f"  📈 Buy Candidates Found: {summary.get('buy_candidates_found', 0)}")
            print(f"  📉 Sell Candidates Found: {summary.get('sell_candidates_found', 0)}")
            print(f"  ⏱️  Time Horizon: {summary.get('analysis_timeframe', 'N/A')}")
            print(f"  🎯 Target Return: {summary.get('target_return', 'N/A')}")
            
            # Show top opportunities
            top_buys = screening_results.get('top_buy_candidates', [])[:5]
            if top_buys:
                print("\n🏆 TOP 5 BUY OPPORTUNITIES:")
                for i, stock in enumerate(top_buys, 1):
                    symbol = stock.get('symbol', 'N/A')
                    pred_return = stock.get(f'predicted_return_{settings.expected_return_days}d', 0)
                    score = stock.get('overall_score', 0)
                    recommendation = stock.get('recommendation', 'N/A')
                    
                    print(f"  {i}. {symbol}")
                    print(f"     Return Prediction: {pred_return:.2%}")
                    print(f"     Overall Score: {score:.2f}")
                    print(f"     Recommendation: {recommendation}")
                    print(f"     Market Alignment: {stock.get('market_context', {}).get('market_alignment', 'N/A')}")
                    print()
            
            self.results['screening'] = screening_results
            print("✅ Multi-iteration screening completed successfully!")
            
        except Exception as e:
            print(f"❌ Screening failed: {str(e)}")
            logger.error(f"Screening demo failed: {str(e)}")
    
    def demo_ai_agent_integration(self):
        """Demonstrate AI agent with enhanced capabilities."""
        print("\n" + "="*80)
        print("🤖 AI AGENT ENHANCED ANALYSIS")
        print("="*80)
        print("Testing AI agent with comprehensive market intelligence...")
        print()
        
        try:
            # Test market opportunities analysis
            result = trading_agent.analyze_market_opportunities()
            
            if result["status"] == "success":
                print("✅ AI Agent successfully analyzed market opportunities!")
                print("\n📋 Agent Response Summary:")
                
                # Extract key information from agent response
                response = result["result"]
                print(f"Response length: {len(response)} characters")
                
                # Show intermediate steps if available
                steps = result.get("intermediate_steps", [])
                if steps:
                    print(f"Analysis steps executed: {len(steps)}")
                    for i, step in enumerate(steps[:3], 1):  # Show first 3 steps
                        if hasattr(step, 'tool') and hasattr(step, 'tool_input'):
                            print(f"  Step {i}: {step.tool}")
                
                self.results['ai_agent'] = result
                print("\n✅ AI Agent integration test completed!")
            else:
                print(f"❌ AI Agent test failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ AI Agent integration failed: {str(e)}")
            logger.error(f"AI Agent demo failed: {str(e)}")
    
    def demo_specific_stock_analysis(self):
        """Demonstrate enhanced stock analysis for a specific stock."""
        print("\n" + "="*80)
        print("📈 ENHANCED STOCK ANALYSIS")
        print("="*80)
        
        # Analyze a popular Indian stock
        symbol = "RELIANCE.NS"
        print(f"Analyzing {symbol} with comprehensive intelligence...")
        print()
        
        try:
            # Get market sentiment first
            market_sentiment = comprehensive_screener.get_market_sentiment_from_news()
            
            # Perform enhanced analysis
            analysis = comprehensive_screener._enhanced_stock_analysis(symbol, market_sentiment)
            
            if 'error' not in analysis:
                print(f"📊 ANALYSIS RESULTS FOR {symbol}:")
                print(f"  💰 Current Price: ₹{analysis.get('current_price', 0):.2f}")
                print(f"  📈 Predicted Return ({settings.expected_return_days}d): {analysis.get(f'predicted_return_{settings.expected_return_days}d', 0):.2%}")
                print(f"  🎯 Recommendation: {analysis.get('recommendation', 'N/A')}")
                print(f"  ⭐ Overall Score: {analysis.get('overall_score', 0):.2f}")
                print(f"  📊 Technical Score: {analysis.get('technical_score', 0):.2f}")
                print(f"  ⚠️  Risk Score: {analysis.get('risk_score', 0):.2f}")
                print(f"  🌡️  Market Alignment: {analysis.get('market_context', {}).get('market_alignment', 'N/A')}")
                
                # Show key indicators
                print(f"\n📊 Technical Indicators:")
                print(f"  RSI: {analysis.get('rsi', 0):.1f}")
                print(f"  Volatility: {analysis.get('volatility', 0):.2%}")
                print(f"  Volume Ratio: {analysis.get('volume_ratio', 0):.2f}")
                
                # Show reasoning
                reasoning = analysis.get('enhanced_reasoning', [])
                if reasoning:
                    print(f"\n🧠 Analysis Reasoning:")
                    for i, reason in enumerate(reasoning[:3], 1):
                        print(f"  {i}. {reason}")
                
                self.results['stock_analysis'] = analysis
                print("\n✅ Enhanced stock analysis completed!")
            else:
                print(f"❌ Stock analysis failed: {analysis['error']}")
                
        except Exception as e:
            print(f"❌ Stock analysis failed: {str(e)}")
            logger.error(f"Stock analysis demo failed: {str(e)}")
    
    def show_summary(self):
        """Show demo summary and results."""
        print("\n" + "="*80)
        print("📋 DEMO SUMMARY")
        print("="*80)
        
        print(f"🕐 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚙️  Configuration used:")
        print(f"   • Target Return: {settings.min_expected_return:.1%} in {settings.expected_return_days} days")
        print(f"   • Max Investment: ₹{settings.max_investment_amount:,.0f}")
        print(f"   • Risk Threshold: {settings.risk_threshold:.1%}")
        
        print(f"\n✅ Successfully demonstrated:")
        completed_demos = []
        
        if 'market_analysis' in self.results:
            completed_demos.append("📰 News sentiment analysis from multiple sources")
            
        if 'screening' in self.results:
            completed_demos.append("🔬 Multi-iteration stock screening across 200+ stocks")
            
        if 'ai_agent' in self.results:
            completed_demos.append("🤖 AI agent integration with enhanced tools")
            
        if 'stock_analysis' in self.results:
            completed_demos.append("📈 Enhanced individual stock analysis")
        
        for demo in completed_demos:
            print(f"   • {demo}")
        
        print(f"\n🎯 Key Capabilities Demonstrated:")
        print("   • Real-time news sentiment from Indian financial media")
        print("   • Machine learning predictions for time-based returns")
        print("   • Global events consideration in trading decisions")
        print("   • Comprehensive technical analysis with 10+ indicators")
        print("   • Risk-adjusted scoring and portfolio optimization")
        print("   • Automated screening across broad stock universe")
        
        print(f"\n💡 Next Steps:")
        print("   1. Add your OpenAI API key to .env file")
        print("   2. Add your Groww API token to .env file")
        print("   3. Run: python main.py to start interactive trading")
        print("   4. Use scheduler.py for automated trading")
        
        print("\n" + "="*80)
        print("🚀 Enhanced AI Trading Agent Demo Completed Successfully! 🚀")
        print("="*80)
    
    def run_complete_demo(self):
        """Run the complete enhanced trading demo."""
        self.print_banner()
        
        print("Starting enhanced trading agent demonstration...")
        print("This demo showcases advanced capabilities including:")
        print("• Multi-source news analysis")
        print("• Global events monitoring")
        print("• ML-based stock predictions")
        print("• Comprehensive risk assessment")
        print()
        
        # Run each demo component
        self.demo_comprehensive_market_analysis()
        self.demo_multi_iteration_screening()
        self.demo_ai_agent_integration()
        self.demo_specific_stock_analysis()
        
        # Show final summary
        self.show_summary()

def main():
    """Main demo function."""
    try:
        demo = EnhancedTradingDemo()
        demo.run_complete_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
        print("Demo can be resumed by running: python demo_enhanced_screening.py")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        logger.error(f"Demo failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
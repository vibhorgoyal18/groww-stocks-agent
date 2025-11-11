#!/usr/bin/env python3
"""
Automated Trading Scheduler
Run the AI trading agent on a schedule
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from agent.trading_agent import trading_agent
from config.settings import settings

logger = logging.getLogger(__name__)

class TradingScheduler:
    """Scheduler for automated trading operations."""
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the scheduler."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scheduler.log'),
                logging.StreamHandler()
            ]
        )
    
    def daily_portfolio_analysis(self):
        """Run daily portfolio analysis."""
        logger.info("Starting scheduled portfolio analysis")
        try:
            result = trading_agent.get_portfolio_analysis()
            
            if result["status"] == "success":
                # Save analysis with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scheduled_analysis_{timestamp}.md"
                
                with open(filename, 'w') as f:
                    f.write(f"Scheduled Portfolio Analysis - {datetime.now()}\n")
                    f.write("=" * 60 + "\n")
                    f.write(result["analysis"])
                
                logger.info(f"Analysis completed and saved to {filename}")
            else:
                logger.error(f"Analysis failed: {result['message']}")
                
        except Exception as e:
            logger.error(f"Scheduled analysis failed: {str(e)}")
    
    def weekly_rebalancing(self):
        """Run weekly portfolio rebalancing."""
        logger.info("Starting scheduled portfolio rebalancing")
        try:
            # Only rebalance if it's a trading day (Monday-Friday)
            if datetime.now().weekday() < 5:  # 0=Monday, 6=Sunday
                result = trading_agent.analyze_and_rebalance_portfolio()
                
                if result["status"] == "success":
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"scheduled_rebalancing_{timestamp}.md"
                    
                    with open(filename, 'w') as f:
                        f.write(f"Scheduled Portfolio Rebalancing - {datetime.now()}\n")
                        f.write("=" * 60 + "\n")
                        f.write(result["agent_response"])
                    
                    logger.info(f"Rebalancing completed and saved to {filename}")
                else:
                    logger.error(f"Rebalancing failed: {result['message']}")
            else:
                logger.info("Skipping rebalancing - not a trading day")
                
        except Exception as e:
            logger.error(f"Scheduled rebalancing failed: {str(e)}")
    
    def hourly_market_check(self):
        """Perform hourly market checks during trading hours."""
        current_hour = datetime.now().hour
        
        # Only run during market hours (9 AM to 4 PM IST, Monday-Friday)
        if (9 <= current_hour <= 16 and 
            datetime.now().weekday() < 5):
            
            logger.info("Running hourly market check")
            try:
                result = trading_agent.get_trading_summary()
                
                if result["status"] == "success":
                    logger.info("Market check completed successfully")
                    # You could add alerts here for significant changes
                else:
                    logger.warning(f"Market check failed: {result['message']}")
                    
            except Exception as e:
                logger.error(f"Hourly market check failed: {str(e)}")
        else:
            logger.info("Market closed - skipping hourly check")
    
    def emergency_stop_loss_check(self):
        """Check for emergency stop-loss conditions."""
        logger.info("Running emergency stop-loss check")
        try:
            # Get portfolio summary
            result = trading_agent.get_trading_summary()
            
            if result["status"] == "success":
                # This is a simplified check - you'd implement more sophisticated logic
                logger.info("Stop-loss check completed")
                # Add logic to check for significant losses and trigger emergency sells
            else:
                logger.error(f"Stop-loss check failed: {result['message']}")
                
        except Exception as e:
            logger.error(f"Emergency stop-loss check failed: {str(e)}")
    
    def setup_schedule(self):
        """Setup the trading schedule."""
        # Daily analysis at 8:30 AM IST (before market opens)
        schedule.every().day.at("08:30").do(self.daily_portfolio_analysis)
        
        # Weekly rebalancing on Mondays at 10:00 AM IST
        schedule.every().monday.at("10:00").do(self.weekly_rebalancing)
        
        # Hourly checks during trading hours
        schedule.every().hour.do(self.hourly_market_check)
        
        # Emergency stop-loss checks every 30 minutes during trading hours
        schedule.every(30).minutes.do(self.emergency_stop_loss_check)
        
        logger.info("Trading schedule configured:")
        logger.info("- Daily analysis: 8:30 AM")
        logger.info("- Weekly rebalancing: Monday 10:00 AM")
        logger.info("- Hourly market checks during trading hours")
        logger.info("- Stop-loss checks every 30 minutes")
    
    def run(self):
        """Run the scheduler."""
        self.setup_schedule()
        logger.info("Starting automated trading scheduler...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            raise

def main():
    """Main entry point for the scheduler."""
    print("🤖 AI Trading Agent - Automated Scheduler")
    print("=" * 50)
    print("This will run the trading agent automatically on schedule.")
    print("Press Ctrl+C to stop the scheduler.")
    print("=" * 50)
    
    scheduler = TradingScheduler()
    scheduler.run()

if __name__ == "__main__":
    main() 
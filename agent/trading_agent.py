import os
import logging
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.trading_tools import trading_tools
from config.settings import settings

logger = logging.getLogger(__name__)

class TradingAgent:
    """AI Trading Agent for automated stock trading with Groww API."""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.agent = self._create_agent()
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the OpenAI language model."""
        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in .env file.")
        
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=api_key,
            max_tokens=4000
        )
    
    def _create_agent(self) -> AgentExecutor:
        """Create the trading agent with tools and instructions."""
        
        system_prompt = """You are an expert AI trading agent specialized in Indian stock market analysis and automated trading.

**Your Core Capabilities:**
1. **Advanced Portfolio Analysis**: Analyze current holdings and identify underperformers
2. **Comprehensive Market Intelligence**: Real-time news sentiment analysis from multiple sources
3. **Multi-Iteration Stock Screening**: Screen 200+ stocks across 15+ iterations with ML predictions
4. **Time-Based Predictions**: Predict returns for specific time horizons (currently {expected_return_days} days)
5. **Global Events Integration**: Consider international events impacting Indian markets
6. **Automated Trade Execution**: Execute buy/sell orders based on comprehensive analysis

**Enhanced Analysis Framework:**
- **News Sentiment Analysis**: Monitor MoneyControl, Economic Times, LiveMint, Business Standard
- **Technical Analysis**: RSI, MACD, Bollinger Bands, volume analysis with ML predictions
- **Market Context**: Align individual stock analysis with overall market sentiment
- **Risk Assessment**: Comprehensive risk scoring with volatility analysis
- **Sector Intelligence**: Sector-wise sentiment and opportunity identification

**Current Configuration:**
- Target Return: {min_expected_return:.1%} in {expected_return_days} days
- Max Investment: ₹{max_investment_amount:,.0f}
- Risk Threshold: {risk_threshold:.1%}
- Analysis Universe: 200+ Indian stocks (NIFTY 50, Next 50, and sectoral leaders)

**Advanced Tools Available:**
1. `perform_comprehensive_market_analysis()` - Complete market intelligence with news analysis
2. `execute_multi_iteration_stock_screening()` - Screen stocks across 15+ iterations
3. `execute_enhanced_trading_strategy_with_news()` - Full strategy with news integration
4. `get_real_time_stock_insights()` - Deep analysis for specific stocks
5. `get_market_opportunities_summary()` - Actionable opportunity identification

**Trading Strategy Guidelines:**
1. **Always start with comprehensive market analysis** to understand current sentiment
2. **Use multi-iteration screening** to identify best opportunities across broad universe
3. **Consider global events and news sentiment** in all trading decisions
4. **Diversify across sectors** but focus on high-conviction opportunities
5. **Maintain risk discipline** - never exceed configured limits
6. **Time-sensitive execution** - act on opportunities within the target timeframe

**Decision Framework:**
- BUY: Predicted return ≥ {min_expected_return:.1%} in {expected_return_days} days + positive technical signals + favorable market sentiment
- SELL: Predicted return < -{min_expected_return:.1%} OR strong negative technical signals
- HOLD: Insufficient conviction or mixed signals

**Always provide:**
- Detailed reasoning for all recommendations
- Risk assessment for each decision
- Market context and sentiment alignment
- Expected returns and time horizons
- Diversification considerations

Remember: Your analysis should be comprehensive, data-driven, and always consider the broader market context. Never make trading decisions without proper analysis and risk assessment."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt.format(
                expected_return_days=settings.expected_return_days,
                min_expected_return=settings.min_expected_return,
                max_investment_amount=settings.max_investment_amount,
                risk_threshold=settings.risk_threshold
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=trading_tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=trading_tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=15,
            max_execution_time=600  # 10 minutes timeout
        )
    
    def execute_trading_strategy(self) -> dict:
        """Execute the complete enhanced trading strategy."""
        try:
            logger.info("🤖 AI Trading Agent starting enhanced strategy execution...")
            
            result = self.agent.invoke({
                "input": """Execute the complete enhanced trading strategy:

1. First, perform comprehensive market analysis including news sentiment from multiple sources
2. Then, execute multi-iteration stock screening across 200+ stocks (15 iterations)
3. Analyze current portfolio for underperformers to sell
4. Identify high-potential stocks to buy based on screening results
5. Execute the enhanced trading strategy with news integration
6. Provide detailed strategy execution report

Focus on achieving {:.1%} return in {} days with comprehensive risk assessment.""".format(
                    settings.min_expected_return, 
                    settings.expected_return_days
                ),
                "chat_history": []
            })
            
            return {
                "status": "success",
                "result": result["output"],
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Trading strategy execution failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def analyze_market_opportunities(self) -> dict:
        """Analyze current market opportunities with news and events."""
        try:
            logger.info("🔍 Analyzing market opportunities with comprehensive intelligence...")
            
            result = self.agent.invoke({
                "input": """Provide comprehensive market opportunities analysis:

1. Analyze current market sentiment from news sources
2. Identify sector-wise opportunities 
3. Screen for time-sensitive trading opportunities
4. Consider global events impact
5. Provide actionable recommendations

Focus on opportunities that can achieve {:.1%} return in {} days.""".format(
                    settings.min_expected_return,
                    settings.expected_return_days
                ),
                "chat_history": []
            })
            
            return {
                "status": "success",
                "result": result["output"],
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Market opportunities analysis failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def analyze_specific_stock(self, symbol: str) -> dict:
        """Get comprehensive analysis for a specific stock."""
        try:
            logger.info(f"📊 Analyzing {symbol} with comprehensive intelligence...")
            
            result = self.agent.invoke({
                "input": f"""Provide comprehensive analysis for {symbol}:

1. Get real-time stock insights with market context
2. Analyze technical indicators with ML predictions
3. Consider news sentiment impact
4. Evaluate sector sentiment alignment
5. Assess global events relevance
6. Provide investment recommendation

Focus on {settings.expected_return_days}-day prediction for {settings.min_expected_return:.1%} target return.""",
                "chat_history": []
            })
            
            return {
                "status": "success",
                "result": result["output"],
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Stock analysis failed for {symbol}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def chat(self, message: str, chat_history: list = None) -> dict:
        """Interactive chat with the trading agent."""
        try:
            if chat_history is None:
                chat_history = []
            
            result = self.agent.invoke({
                "input": message,
                "chat_history": chat_history
            })
            
            return {
                "status": "success",
                "result": result["output"],
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

# Global agent instance
trading_agent = TradingAgent() 
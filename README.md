# 🚀 AI Trading Agent for Groww

An intelligent AI-powered trading agent that automates stock trading using Groww APIs with advanced market analysis, news sentiment monitoring, and machine learning predictions.

---

# 🎯 **QUICK START - ONE COMMAND TO RULE THEM ALL**

## 🌟 Unified Interactive Entry Point (Recommended):

```bash
python run.py
```

### ✨ **What This Single Command Gives You:**

**Interactive menu-driven interface** with 9 powerful options:

#### 🤖 **AUTOMATED TRADING:**
1. **AI Portfolio Optimization** - Automatic buy/sell with full analysis
2. **Portfolio Rebalancing** - AI-powered rebalancing with confirmation

#### 📊 **ANALYSIS (Read-Only):**
3. **Analyze Current Portfolio** - Comprehensive portfolio analysis
4. **Comprehensive Market Analysis** - Real-time market sentiment & news
5. **Multi-Iteration Stock Screening** - Screen 200+ stocks with ML predictions
6. **Trading Summary Report** - Complete trading history and performance

#### 🎯 **CUSTOM ACTIONS:**
7. **Find Investment Opportunities** - Discover stocks based on your budget
8. **Execute Custom Trading Strategy** - Natural language trading commands

#### 📚 **OTHER:**
9. **Run Enhanced Screening Demo** - Safe demo mode (no real trades)

### 💡 **No Parameters Needed!**
- The system will **ask you for inputs** as needed
- Clear prompts for budget, target returns, time horizons, etc.
- Built-in validation and helpful error messages
- All results automatically saved to `reports/` folder

### 🔒 **Safety Features:**
- ⚠️ Confirmation prompts before executing real trades
- 📄 Automatic report generation and saving
- 📋 Comprehensive logging to `trading_agent.log`
- ✅ Environment validation on startup

---

## 🎯 **Alternative Entry Points**

### Execute Complete AI Trading Strategy (Direct):

```bash
python ai_trading_agent.py
```

**What This Does:**
- 📊 Analyzes your entire portfolio automatically
- 📉 Sells worst performing stocks
- 📈 Buys high-potential stocks  
- 🎯 Targets 15% returns in 30 days (configurable in `.env`)
- 📄 Generates comprehensive execution reports
- ⚡ Executes real trades through Groww API

### 📈 Recent Execution Results:
```
✅ Successful Sells: 19/19 positions
✅ Successful Buys: 8/8 high-potential stocks  
💰 Capital Deployed: ₹4,93,945
🎯 Expected Gains: ₹83,948 (17.0% ROI in 30 days)
📊 Perfect Sector Diversification: Banking 37.5% | IT 37.5% | Energy 12.4% | Power 12.6%
```

---

## 🚀 Prerequisites

1. **API Setup**: Configure `.env` with your Groww API token and OpenAI key
2. **Dependencies**: Run `pip install -r requirements.txt`
3. **Execution**: Run from project root directory

---

## ✨ Enhanced Features

### 🧠 Advanced AI Capabilities
- **GPT-4o-mini Powered**: Fast, cost-effective AI with 128K context window
- **Multi-Iteration Stock Screening**: Analyze 200+ Indian stocks across 15+ iterations
- **Real-Time News Sentiment**: Monitor MoneyControl, Economic Times, LiveMint, Business Standard
- **Global Events Integration**: Consider international events impacting Indian markets
- **Machine Learning Predictions**: Time-based return predictions using Random Forest models
- **Market Context Alignment**: Align individual stock analysis with overall market sentiment

### 📊 Comprehensive Analysis Framework
- **Technical Analysis**: RSI, MACD, Bollinger Bands, volume analysis with ML predictions
- **Risk Assessment**: Comprehensive risk scoring with volatility analysis
- **Sector Intelligence**: Sector-wise sentiment and opportunity identification
- **Time-Based Targeting**: Configurable return targets for specific time horizons
- **Portfolio Optimization**: Automated rebalancing based on comprehensive analysis

### 🎯 Default Configuration (Modify in `.env`)
- **AI Model**: GPT-4o-mini (128K context, fast & cost-effective)
- **Target Return**: 15% in 30 days (configurable)
- **Max Investment**: ₹10,000 per strategy execution (configurable)
- **Analysis Universe**: 200+ Indian stocks (NIFTY 50, Next 50, sectoral leaders)
- **Risk Management**: 20% risk threshold with volatility monitoring

---

## 📖 Usage Examples

### Example 1: Portfolio Analysis (Read-Only)
```bash
$ python run.py
# Select option 3: Analyze Current Portfolio
# No parameters needed - AI analyzes your holdings automatically
# Results saved to reports/portfolio_analysis_[timestamp].txt
```

### Example 2: Find Investment Opportunities
```bash
$ python run.py
# Select option 7: Find Investment Opportunities
💰 Enter your investment budget (INR): 25000
# AI recommends stocks based on your budget and target returns
# Results saved to reports/investment_opportunities_[timestamp].txt
```

### Example 3: Custom Strategy (Natural Language)
```bash
$ python run.py
# Select option 8: Execute Custom Trading Strategy
� Your Strategy: "Buy top 3 banking stocks under ₹2000"
🔴 Proceed with strategy execution? (yes/no): yes
# AI executes your custom strategy
# Results saved to reports/strategy_execution_[timestamp].txt
```

### Example 4: Stock Screening with Custom Parameters
```bash
$ python run.py
# Select option 5: Multi-Iteration Stock Screening
🎯 Target return percentage (default: 15.0%): 20
📅 Time horizon in days (default: 30): 45
# AI screens 200+ stocks for 20% return in 45 days
# Results saved to reports/stock_screening_[timestamp].txt
```

### Example 5: Direct AI Portfolio Optimization
```bash
$ python ai_trading_agent.py
# Fully automated:
# - Analyzes portfolio
# - Sells underperformers
# - Buys high-potential stocks
# - Generates execution report
```

---

## �🚀 Quick Start

### 1. Installation
```bash
git clone <repository-url>
cd groww_stocks_agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file with your API credentials (or copy from `.env.example`):
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Groww API Configuration - Choose Your Authentication Method
GROWW_AUTH_METHOD=token  # Use 'token' or 'totp'

# Option 1: OAuth 2.0 Token (Requires daily approval)
GROWW_API_TOKEN=your_groww_api_token_here

# Option 2: TOTP Method (No expiry, recommended)
GROWW_TOTP_TOKEN=your_totp_api_key_here
GROWW_TOTP_SECRET=your_totp_secret_here

# Trading Configuration (Customize as needed)
MAX_INVESTMENT_AMOUNT=10000
RISK_THRESHOLD=0.20
MIN_EXPECTED_RETURN=15.0
EXPECTED_RETURN_DAYS=30
LOG_LEVEL=INFO
```

#### 🔐 Authentication Methods Explained

**Token Method (OAuth 2.0):**
- Generate from: https://groww.in/trade-api/api-keys
- Click "Generate API key" button
- Requires daily approval from Groww app
- Token expires after approval period

**TOTP Method (Recommended):**
- Generate from: https://groww.in/trade-api/api-keys
- Click dropdown next to "Generate API key" → "Generate TOTP token"
- Copy both:
  - **TOTP Token** (API Key) → `GROWW_TOTP_TOKEN`
  - **TOTP Secret** → `GROWW_TOTP_SECRET`
- No expiry, no daily approvals needed
- More secure and convenient
- Can scan QR code with authenticator app

**📝 All settings are documented in the `.env` file!**

### 3. Run the Application (Unified Entry Point)
```bash
# Start the interactive menu - ONE COMMAND FOR EVERYTHING!
python run.py
```

This single command gives you access to ALL features through an interactive menu:
- 🤖 AI Portfolio Optimization
- ⚖️ Portfolio Rebalancing
- 📊 Portfolio Analysis
- 📈 Market Analysis
- 🔬 Stock Screening
- 🎯 Custom Strategies
- 📋 Trading Summaries
- And more!

**Example Usage Flow:**
```bash
$ python run.py

# Menu appears with 9 options
# Select option 7 (Find Investment Opportunities)
👉 Enter your choice (0-9): 7

# System asks for your budget
💰 Enter your investment budget (INR): 50000

# AI analyzes and provides recommendations
# Results automatically saved to reports/
```

### 4. Alternative: Demo the Enhanced Capabilities (Safe Mode)
```bash
# Run the comprehensive demo
python demo_enhanced_screening.py
```

This demo showcases:
- 🌐 Multi-source news sentiment analysis
- 🔬 200+ stock screening with ML predictions
- 🤖 AI agent integration with enhanced tools
- 📈 Individual stock analysis with market context

### 5. Alternative Entry Points (Advanced)
```bash
# Direct AI portfolio optimization (no menu)
python ai_trading_agent.py

# Original interactive CLI
python main.py

# Automated trading schedule
python scheduler.py

# Demo mode only
```bash
# Set up automated trading schedule
python scheduler.py
```

## 🛠️ Advanced Tools

### 📈 Enhanced Trading Tools
- `perform_comprehensive_market_analysis()` - Complete market intelligence
- `execute_multi_iteration_stock_screening()` - Broad universe screening
- `execute_enhanced_trading_strategy_with_news()` - Full strategy with news
- `get_real_time_stock_insights()` - Deep individual stock analysis
- `get_market_opportunities_summary()` - Actionable opportunities

### 🔍 Analysis Components
- **Comprehensive Screener**: 200+ stock universe with parallel processing
- **News Sentiment Engine**: Multi-source Indian financial media analysis
- **ML Prediction Engine**: Random Forest models for time-based returns
- **Risk Assessment Engine**: Volatility and correlation analysis
- **Portfolio Optimizer**: Automated rebalancing with diversification

## 📊 Analysis Framework

### Time-Based Predictions
The system uses machine learning to predict stock returns for specific time horizons:
- **Features**: Technical indicators, volume patterns, momentum signals
- **Model**: Random Forest with confidence scoring
- **Output**: Predicted return percentage for configured days
- **Validation**: Historical backtesting with risk adjustment

### News Sentiment Analysis
Real-time sentiment analysis from major Indian financial sources:
- **Sources**: MoneyControl, Economic Times, LiveMint, Business Standard
- **Analysis**: Headline sentiment, sector themes, market mood
- **Integration**: Sentiment scores influence stock recommendations
- **Caching**: 30-minute cache for efficiency

### Risk Management
Multi-layered risk assessment:
- **Volatility Analysis**: Historical and implied volatility scoring
- **Correlation Risk**: Portfolio concentration monitoring  
- **Market Risk**: Overall market sentiment alignment
- **Position Sizing**: Risk-adjusted position recommendations

## 🔧 Configuration Options

### Environment Variables
```env
# AI Configuration
OPENAI_API_KEY=your_key                    # Required for AI analysis
GROWW_API_TOKEN=your_token                 # Required for trading

# Strategy Parameters
MIN_EXPECTED_RETURN=0.02                   # 2% minimum return target
EXPECTED_RETURN_DAYS=5                     # 5-day time horizon
MAX_INVESTMENT_AMOUNT=50000.0              # ₹50k max per execution
RISK_THRESHOLD=0.15                        # 15% risk tolerance

# System Configuration
LOG_LEVEL=INFO                             # Logging verbosity
```

### Trading Strategy Customization
Modify `config/settings.py` to adjust:
- Return targets and time horizons
- Risk tolerance levels
- Stock universe selection
- Analysis depth and iterations

## 📁 Project Structure

```
groww_stocks_agent/
├── agent/
│   ├── trading_agent.py          # Enhanced AI agent with GPT-4
│   └── __init__.py
├── tools/
│   ├── comprehensive_screener.py # 200+ stock screener with news
│   ├── advanced_trading_tools.py # Enhanced LangChain tools
│   ├── stock_analysis.py         # ML-based technical analysis
│   ├── trading_tools.py          # Core trading operations
│   ├── groww_api.py              # Groww API integration
│   ├── web_analysis.py           # News scraping tools
│   ├── enhanced_analysis.py      # Market intelligence
│   └── browser_tools.py          # Browser automation
├── config/
│   ├── settings.py               # Configuration management
│   └── __init__.py
├── utils/
│   ├── security.py               # Secure API key handling
│   └── __init__.py
├── main.py                       # Interactive CLI application
├── scheduler.py                  # Automated trading scheduler
├── demo_enhanced_screening.py    # Comprehensive demo
├── requirements.txt              # Dependencies
├── .env                         # Configuration file
├── .gitignore                   # Git exclusions
└── README.md                    # This file
```

## 🔒 Security Features

- **Secure API Management**: API keys never exposed to AI models
- **Environment Isolation**: Credentials in `.env` file only
- **Risk Controls**: Multiple safety limits and validations
- **Audit Trail**: Comprehensive logging of all operations
- **OAuth 2.0**: Official Groww SDK with secure authentication

## 📈 Performance Metrics

The system tracks comprehensive performance metrics:
- **Return Accuracy**: ML prediction vs actual returns
- **Risk-Adjusted Returns**: Sharpe ratio and volatility metrics
- **Success Rate**: Percentage of profitable trades
- **Market Correlation**: Beta and alpha calculations
- **News Impact**: Sentiment correlation with price movements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## ⚠️ Risk Disclaimer

This software is for educational and research purposes. Trading involves significant financial risk. The AI agent's predictions are not guaranteed, and past performance doesn't indicate future results. Always:

- Use paper trading first
- Start with small amounts
- Understand the risks involved
- Consult financial advisors
- Monitor AI decisions carefully

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions:
1. Check the demo: `python demo_enhanced_screening.py`
2. Review logs in the generated log files
3. Ensure API keys are correctly configured
4. Check network connectivity for news analysis

## 🌟 What Makes This Special

### Comprehensive Intelligence
Unlike basic trading bots, this agent combines:
- Real-time news sentiment from multiple sources
- Machine learning predictions for specific time horizons
- Global events consideration in trading decisions
- Risk-adjusted scoring across 200+ stocks
- Automated portfolio rebalancing with diversification

### Production-Ready Features
- Parallel processing for fast analysis
- Caching for efficiency
- Error handling and recovery
- Comprehensive logging
- Modular architecture for extensibility

### AI-First Approach
- GPT-4 powered decision making
- LangChain tools for complex workflows
- Natural language interaction
- Adaptive learning from market conditions
- Explainable AI with detailed reasoning

---

**🚀 Ready to revolutionize your trading with AI? Start with the demo and experience the future of algorithmic trading!** 
from growwapi import GrowwAPI
import json
import logging
from typing import Dict, List, Optional, Any
from utils.security import key_manager, secure_api_call
from utils.groww_auth import get_authenticated_groww_client
from config.settings import settings

logger = logging.getLogger(__name__)

class GrowwAPIClient:
    """Secure Groww API client using official SDK with TOTP support."""
    
    def __init__(self):
        self._groww_api = None
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication using the new authentication utility."""
        try:
            # Use the new authentication utility
            self._groww_api = get_authenticated_groww_client()
            logger.info(f"Groww API initialized with {settings.groww_auth_method} authentication")
        except Exception as e:
            logger.error(f"Failed to initialize Groww API: {str(e)}")
            # Fallback to old token method for backward compatibility
            api_token = key_manager.get_key('GROWW_API_TOKEN')
            if api_token:
                self._groww_api = GrowwAPI(api_token)
                logger.info(f"Groww API initialized with legacy token: {key_manager.get_masked_key('GROWW_API_TOKEN')}")
            else:
                logger.warning("No Groww API authentication configured")
    
    @secure_api_call
    def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio positions."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            # Use correct method name
            positions_response = self._groww_api.get_positions_for_user()
            holdings_response = self._groww_api.get_holdings_for_user()
            
            # Handle the response format - data is nested under keys
            positions_data = []
            if isinstance(positions_response, dict) and 'positions' in positions_response:
                positions_data = positions_response['positions']
            elif isinstance(positions_response, list):
                positions_data = positions_response
            
            holdings_data = []
            if isinstance(holdings_response, dict) and 'holdings' in holdings_response:
                holdings_data = holdings_response['holdings']
            elif isinstance(holdings_response, list):
                holdings_data = holdings_response
            
            return {
                "positions": positions_data,
                "holdings": holdings_data,
                "total_positions": len(positions_data),
                "total_holdings": len(holdings_data)
            }
        except Exception as e:
            logger.error(f"Failed to fetch portfolio: {str(e)}")
            raise
    
    @secure_api_call
    def get_holdings(self) -> List[Dict[str, Any]]:
        """Get current stock holdings."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            # Use correct method name
            holdings_response = self._groww_api.get_holdings_for_user()
            
            # Handle the response format - holdings are nested under 'holdings' key
            holdings_data = []
            if isinstance(holdings_response, dict) and 'holdings' in holdings_response:
                holdings_data = holdings_response['holdings']
            elif isinstance(holdings_response, list):
                holdings_data = holdings_response
            
            # Clean and structure holdings data
            cleaned_holdings = []
            if holdings_data:
                for holding in holdings_data:
                    # Extract relevant data from the holding object
                    trading_symbol = holding.get('trading_symbol', '')
                    
                    # Get current stock price using multiple methods
                    current_price = self._get_current_price(trading_symbol)
                    
                    quantity = float(holding.get('quantity', 0))
                    avg_price = float(holding.get('average_price', 0))
                    
                    # If we couldn't get current price, use average price as fallback
                    if current_price <= 0:
                        current_price = avg_price
                        logger.warning(f"Using average price for {trading_symbol}: {current_price}")
                    
                    # Calculate values
                    investment_value = quantity * avg_price
                    current_value = quantity * current_price
                    pnl = current_value - investment_value
                    pnl_percent = (pnl / investment_value * 100) if investment_value > 0 else 0
                    
                    cleaned_holding = {
                        'symbol': trading_symbol,
                        'quantity': quantity,
                        'avg_price': avg_price,
                        'current_price': current_price,
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'investment_value': investment_value,
                        'current_value': current_value,
                        'exchange': 'NSE',  # Default to NSE
                        'instrument_type': 'EQUITY',
                        'isin': holding.get('isin', ''),
                        'demat_free_quantity': float(holding.get('demat_free_quantity', 0))
                    }
                    
                    cleaned_holdings.append(cleaned_holding)
            
            return cleaned_holdings
        except Exception as e:
            logger.error(f"Failed to fetch holdings: {str(e)}")
            raise
    
    def _get_current_price(self, trading_symbol: str) -> float:
        """Get current price using multiple methods."""
        try:
            # Method 1: Try Groww API with proper parameters
            try:
                # Try different combinations of exchange and segment
                ltp_response = self._groww_api.get_ltp(trading_symbol, 'CASH', 'NSE')
                if isinstance(ltp_response, dict) and 'ltp' in ltp_response:
                    return float(ltp_response['ltp'])
            except:
                pass
            
            try:
                # Try with different segment format
                quote_response = self._groww_api.get_quote(trading_symbol, 'NSE', 'CASH')
                if isinstance(quote_response, dict) and 'ltp' in quote_response:
                    return float(quote_response['ltp'])
            except:
                pass
            
            # Try BSE exchange as fallback
            try:
                ltp_response = self._groww_api.get_ltp(trading_symbol, 'CASH', 'BSE')
                if isinstance(ltp_response, dict) and 'ltp' in ltp_response:
                    return float(ltp_response['ltp'])
            except:
                pass
            
            try:
                quote_response = self._groww_api.get_quote(trading_symbol, 'BSE', 'CASH')
                if isinstance(quote_response, dict) and 'ltp' in quote_response:
                    return float(quote_response['ltp'])
            except:
                pass
            
            logger.warning(f"Could not fetch current price for {trading_symbol} from Groww API")
            return 0  # Will be handled by caller
            
        except Exception as e:
            logger.error(f"Failed to get current price for {trading_symbol}: {str(e)}")
            return 0
    
    @secure_api_call
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current trading positions."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            positions = self._groww_api.get_positions_for_user()
            return positions if positions else []
        except Exception as e:
            logger.error(f"Failed to fetch positions: {str(e)}")
            raise
    
    @secure_api_call
    def place_sell_order(self, symbol: str, quantity: int, price: Optional[float] = None) -> Dict[str, Any]:
        """Place a sell order using official SDK."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            # Determine order type based on price
            if price:
                order_type = self._groww_api.ORDER_TYPE_LIMIT
            else:
                order_type = self._groww_api.ORDER_TYPE_MARKET
            
            response = self._groww_api.place_order(
                trading_symbol=symbol,
                quantity=quantity,
                validity=self._groww_api.VALIDITY_DAY,
                exchange=self._groww_api.EXCHANGE_NSE,
                segment=self._groww_api.SEGMENT_CASH,
                product=self._groww_api.PRODUCT_CNC,
                order_type=order_type,
                transaction_type=self._groww_api.TRANSACTION_TYPE_SELL,
                price=price if price else None
            )
            
            logger.info(f"Sell order placed for {symbol}: {quantity} shares")
            return response
        except Exception as e:
            logger.error(f"Failed to place sell order for {symbol}: {str(e)}")
            raise
    
    @secure_api_call
    def place_buy_order(self, symbol: str, quantity: int, price: Optional[float] = None) -> Dict[str, Any]:
        """Place a buy order using official SDK."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            # Determine order type based on price
            if price:
                order_type = self._groww_api.ORDER_TYPE_LIMIT
            else:
                order_type = self._groww_api.ORDER_TYPE_MARKET
            
            response = self._groww_api.place_order(
                trading_symbol=symbol,
                quantity=quantity,
                validity=self._groww_api.VALIDITY_DAY,
                exchange=self._groww_api.EXCHANGE_NSE,
                segment=self._groww_api.SEGMENT_CASH,
                product=self._groww_api.PRODUCT_CNC,
                order_type=order_type,
                transaction_type=self._groww_api.TRANSACTION_TYPE_BUY,
                price=price if price else None
            )
            
            logger.info(f"Buy order placed for {symbol}: {quantity} shares")
            return response
        except Exception as e:
            logger.error(f"Failed to place buy order for {symbol}: {str(e)}")
            raise
    
    @secure_api_call
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current stock price using official SDK."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            # Get market quote using correct method
            quote = self._groww_api.get_quote(symbol)
            ltp = self._groww_api.get_ltp(symbol)
            ohlc = self._groww_api.get_ohlc(symbol)
            
            result = {
                'symbol': symbol,
                'current_price': 0,
                'open_price': 0,
                'high_price': 0,
                'low_price': 0,
                'close_price': 0,
                'volume': 0,
                'change': 0,
                'change_percent': 0
            }
            
            # Extract LTP
            if ltp:
                result['current_price'] = float(ltp.get('ltp', 0))
            
            # Extract OHLC data
            if ohlc:
                result['open_price'] = float(ohlc.get('open', 0))
                result['high_price'] = float(ohlc.get('high', 0))
                result['low_price'] = float(ohlc.get('low', 0))
                result['close_price'] = float(ohlc.get('close', 0))
            
            # Extract quote data
            if quote:
                result['volume'] = float(quote.get('volume', 0))
                result['change'] = float(quote.get('change', 0))
                result['change_percent'] = float(quote.get('changePercentage', 0))
            
            return result
                
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {str(e)}")
            raise
    
    @secure_api_call
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            # Use correct method
            order_status = self._groww_api.get_order_status(order_id)
            order_detail = self._groww_api.get_order_detail(order_id)
            
            if order_status or order_detail:
                data = order_status or order_detail
                return {
                    'order_id': data.get('orderId', order_id),
                    'status': data.get('orderStatus', 'UNKNOWN'),
                    'symbol': data.get('tradingSymbol', ''),
                    'quantity': float(data.get('quantity', 0)),
                    'price': float(data.get('price', 0)),
                    'filled_quantity': float(data.get('filledQuantity', 0)),
                    'transaction_type': data.get('transactionType', ''),
                    'order_type': data.get('orderType', ''),
                    'exchange': data.get('exchange', '')
                }
            else:
                raise ValueError(f"Order {order_id} not found")
                
        except Exception as e:
            logger.error(f"Failed to get order status for {order_id}: {str(e)}")
            raise
    
    @secure_api_call
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get all orders."""
        try:
            if not self._groww_api:
                raise ValueError("Groww API not initialized")
            
            orders = self._groww_api.get_order_list()
            return orders if orders else []
        except Exception as e:
            logger.error(f"Failed to fetch orders: {str(e)}")
            raise

# Global client instance
groww_client = GrowwAPIClient() 
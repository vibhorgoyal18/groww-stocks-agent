"""
Groww API Authentication Utility
Supports both Token and TOTP-based authentication methods
"""

import logging
import pyotp
from growwapi import GrowwAPI
from config.settings import settings
from typing import Optional

logger = logging.getLogger(__name__)


class GrowwAuthenticator:
    """Handle Groww API authentication using multiple methods."""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.auth_method = settings.groww_auth_method
    
    def authenticate(self) -> str:
        """
        Authenticate with Groww API using configured method.
        
        Returns:
            str: Access token for GrowwAPI
            
        Raises:
            ValueError: If authentication fails or credentials are missing
        """
        if self.auth_method == "totp":
            return self._authenticate_with_totp()
        elif self.auth_method == "token":
            return self._authenticate_with_token()
        else:
            raise ValueError(f"Invalid authentication method: {self.auth_method}")
    
    def _authenticate_with_token(self) -> str:
        """
        Authenticate using OAuth 2.0 Token (requires daily approval).
        
        This method uses the GROWW_API_TOKEN from environment variables.
        The token must be generated from: https://groww.in/trade-api/api-keys
        
        Returns:
            str: Access token for GrowwAPI
        """
        logger.info("Authenticating with OAuth 2.0 Token method")
        
        api_token = settings.groww_api_token
        if not api_token:
            raise ValueError(
                "GROWW_API_TOKEN not found in environment variables. "
                "Please set it in your .env file or generate a new token from "
                "https://groww.in/trade-api/api-keys"
            )
        
        # For token method, the token itself is the access token
        self.access_token = api_token
        logger.info("Successfully authenticated with Token method")
        return self.access_token
    
    def _authenticate_with_totp(self) -> str:
        """
        Authenticate using TOTP flow (no expiry, more permanent).
        
        This method uses:
        - GROWW_TOTP_TOKEN: The TOTP API Key
        - GROWW_TOTP_SECRET: The TOTP Secret for generating time-based codes
        
        Both can be generated from: https://groww.in/trade-api/api-keys
        Click 'Generate TOTP token' in the dropdown.
        
        Returns:
            str: Access token for GrowwAPI
        """
        logger.info("Authenticating with TOTP method")
        
        # Validate credentials
        totp_token = settings.groww_totp_token
        totp_secret = settings.groww_totp_secret
        
        if not totp_token:
            raise ValueError(
                "GROWW_TOTP_TOKEN not found in environment variables. "
                "Please generate a TOTP token from https://groww.in/trade-api/api-keys "
                "and set it in your .env file"
            )
        
        if not totp_secret:
            raise ValueError(
                "GROWW_TOTP_SECRET not found in environment variables. "
                "Please copy the TOTP secret from https://groww.in/trade-api/api-keys "
                "and set it in your .env file"
            )
        
        # Generate TOTP code
        try:
            totp_generator = pyotp.TOTP(totp_secret)
            totp_code = totp_generator.now()
            logger.info(f"Generated TOTP code: {totp_code[:3]}***")
            
            # Get access token using TOTP
            access_token = GrowwAPI.get_access_token(
                api_key=totp_token,
                totp=totp_code
            )
            
            if not access_token:
                raise ValueError("Failed to obtain access token from Groww API")
            
            self.access_token = access_token
            logger.info("Successfully authenticated with TOTP method")
            return self.access_token
            
        except Exception as e:
            logger.error(f"TOTP authentication failed: {str(e)}")
            raise ValueError(
                f"TOTP authentication failed: {str(e)}. "
                "Please verify your TOTP token and secret are correct."
            )
    
    def refresh_token(self) -> str:
        """
        Refresh the access token.
        
        For TOTP method, this generates a new TOTP code and gets a fresh token.
        For Token method, this returns the existing token.
        
        Returns:
            str: Refreshed access token
        """
        logger.info("Refreshing access token")
        return self.authenticate()
    
    def get_groww_client(self) -> GrowwAPI:
        """
        Get an authenticated GrowwAPI client instance.
        
        Returns:
            GrowwAPI: Authenticated Groww API client
        """
        if not self.access_token:
            self.authenticate()
        
        return GrowwAPI(self.access_token)
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.access_token is not None


# Global authenticator instance
groww_authenticator = GrowwAuthenticator()


def get_authenticated_groww_client() -> GrowwAPI:
    """
    Convenience function to get an authenticated Groww API client.
    
    Returns:
        GrowwAPI: Authenticated Groww API client
        
    Example:
        ```python
        from utils.groww_auth import get_authenticated_groww_client
        
        groww = get_authenticated_groww_client()
        holdings = groww.get_holdings_for_user()
        ```
    """
    return groww_authenticator.get_groww_client()

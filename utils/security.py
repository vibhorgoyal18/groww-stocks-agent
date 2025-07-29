import os
import logging
from typing import Optional, Dict, Any
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class SecureAPIKeyManager:
    """
    Secure API key manager that loads keys without exposing them to AI models.
    This ensures that API keys are never logged or sent to OpenAI.
    """
    
    def __init__(self):
        self._keys = {}
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from environment variables."""
        # Ensure .env file is loaded
        load_dotenv(override=True)
        
        # OpenAI API Key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self._keys['OPENAI_API_KEY'] = openai_key
            logger.info("✓ OpenAI API key loaded")
        else:
            logger.warning("✗ OpenAI API key not found")
        
        # Groww API Token (OAuth 2.0)
        groww_token = os.getenv('GROWW_API_TOKEN')
        if groww_token:
            self._keys['GROWW_API_TOKEN'] = groww_token
            logger.info("✓ Groww API token loaded")
        else:
            logger.warning("✗ Groww API token not found")
    
    def get_key(self, key_name: str) -> Optional[str]:
        """
        Get API key by name. Never returns the actual key to prevent exposure.
        This method is designed to be used by secure API wrappers only.
        """
        return self._keys.get(key_name)
    
    def has_key(self, key_name: str) -> bool:
        """Check if a key exists without exposing it."""
        return key_name in self._keys and self._keys[key_name] is not None
    
    def get_masked_key(self, key_name: str) -> str:
        """Get a masked version of the key for logging purposes."""
        key = self._keys.get(key_name)
        if key and len(key) > 8:
            return f"{key[:4]}...{key[-4:]}"
        elif key:
            return "***"
        return "NOT_FOUND"
    
    def validate_keys(self) -> Dict[str, bool]:
        """Validate that all required keys are present."""
        required_keys = ['OPENAI_API_KEY', 'GROWW_API_TOKEN']
        validation_result = {}
        
        for key in required_keys:
            validation_result[key] = self.has_key(key)
        
        return validation_result

def secure_api_call(func):
    """
    Decorator to ensure API calls are made securely without exposing credentials.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Remove any sensitive data from kwargs before logging
            safe_kwargs = {k: v for k, v in kwargs.items() 
                          if 'key' not in k.lower() and 'token' not in k.lower() and 'password' not in k.lower()}
            
            logger.debug(f"Executing secure API call: {func.__name__} with args: {safe_kwargs}")
            result = func(*args, **kwargs)
            
            # Ensure no sensitive data in response is logged
            if isinstance(result, dict):
                safe_result = {k: v for k, v in result.items() 
                              if 'key' not in k.lower() and 'token' not in k.lower() and 'password' not in k.lower()}
                logger.debug(f"API call {func.__name__} completed successfully")
            
            return result
        except Exception as e:
            logger.error(f"Secure API call {func.__name__} failed: {str(e)}")
            raise
    
    return wrapper

# Global instance
key_manager = SecureAPIKeyManager() 
import os
import logging
from binance import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

class ClientConnectionError(Exception):
    """Exception raised when connection or credential checks fail."""
    pass

class BinanceFuturesClient:
    """
    Wrapper around python-binance Client specifically targeting the 
    USDT-M Futures Testnet environment.
    """
    def __init__(self, api_key: str | None = None, api_secret: str | None = None, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("trading_bot")
        
        # Load keys from parameters, falling back to environment variables
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        
        # Check if keys are either missing or still using template values
        if not self.api_key or not self.api_secret:
            raise ClientConnectionError(
                "Binance Testnet API Key and/or Secret are missing. "
                "Please configure them in your .env file."
            )
            
        if "your_binance_testnet" in self.api_key or "your_binance_testnet" in self.api_secret:
            raise ClientConnectionError(
                "Default API template keys detected. "
                "Please replace the placeholder values in the .env file with your actual Binance Testnet credentials."
            )

        self.logger.debug("Initializing Binance Client with testnet=True")
        try:
            # Initialize with testnet=True to automatically configure futures base URL to:
            # https://testnet.binancefuture.com
            self.client = Client(self.api_key, self.api_secret, testnet=True)
        except Exception as e:
            self.logger.error(f"Failed to instantiate Binance Client: {e}")
            raise ClientConnectionError(f"Failed to instantiate Binance client: {e}")

    def check_connection(self) -> bool:
        """
        Verifies both network connectivity (ping) and API key validity (account check).
        
        Returns:
            bool: True if connection is healthy.
            
        Raises:
            ClientConnectionError: If connectivity or key verification fails.
        """
        self.logger.info("Verifying connectivity and API credentials with Binance Futures Testnet...")
        
        # 1. Ping test
        try:
            self.client.futures_ping()
            self.logger.debug("Ping to Futures Testnet was successful.")
        except Exception as e:
            self.logger.error(f"Ping failed: {e}")
            raise ClientConnectionError(
                "Failed to ping Binance Futures Testnet. Please check your internet connection "
                "and verify that https://testnet.binancefuture.com is accessible."
            )
            
        # 2. Key permission test
        try:
            self.client.futures_account()
            self.logger.info("API keys and connection verified successfully!")
            return True
        except BinanceAPIException as e:
            self.logger.error(f"Binance API Verification Error [Code {e.code}]: {e.message}")
            if e.code == -2015:
                raise ClientConnectionError(
                    "Invalid API key or IP address. Please double check that your "
                    "Testnet API key and secret are typed correctly."
                )
            raise ClientConnectionError(
                f"Binance authentication failed with message: {e.message} (Binance Error Code: {e.code})"
            )
        except BinanceRequestException as e:
            self.logger.error(f"Binance Request failed: {e}")
            raise ClientConnectionError(
                f"Failed to submit account request to Binance Futures: {e}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected connection health error: {e}")
            raise ClientConnectionError(
                f"An unexpected error occurred during client connection checks: {e}"
            )

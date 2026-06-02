import logging
from binance.exceptions import BinanceAPIException, BinanceRequestException
from .client import BinanceFuturesClient

class OrderPlacementError(Exception):
    """Custom exception raised when a futures order placement fails."""
    pass

def place_futures_order(
    client_wrapper: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    logger: logging.Logger | None = None
) -> dict:
    """
    Executes a MARKET or LIMIT order on Binance Futures Testnet (USDT-M).
    
    Args:
        client_wrapper (BinanceFuturesClient): The verified client instance.
        symbol (str): The contract symbol in uppercase (e.g. 'BTCUSDT').
        side (str): Either 'BUY' or 'SELL'.
        order_type (str): Either 'MARKET' or 'LIMIT'.
        quantity (float): Order quantity size.
        price (float, optional): Order limit price. Required if type is LIMIT.
        logger (Logger, optional): Logging instance.
        
    Returns:
        dict: A structured summary containing keys:
              - 'orderId' (int): The unique ID of the order.
              - 'status' (str): The status (e.g., 'NEW', 'FILLED').
              - 'executedQty' (float): Quantity already filled.
              - 'avgPrice' (float): Average fill price.
              
    Raises:
        OrderPlacementError: If the order is rejected, network fails, or keys are invalid.
    """
    log = logger or logging.getLogger("trading_bot")
    client = client_wrapper.client

    # Build the required parameters payload for the python-binance futures endpoint
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": str(quantity),  # API expects strings to prevent float precision issues
    }

    if order_type == "LIMIT":
        params["price"] = str(price)
        params["timeInForce"] = "GTC"  # Good 'Til Cancelled is standard for limit orders

    log.info(f"Placing Futures {order_type} {side} order for {quantity} {symbol}...")
    log.debug(f"Full API request arguments: {params}")

    try:
        response = client.futures_create_order(**params)
        log.debug(f"Binance API full response: {response}")
        
        # Extract details with safety checks
        order_id = response.get("orderId")
        status = response.get("status", "UNKNOWN")
        
        try:
            executed_qty = float(response.get("executedQty", 0.0))
        except (ValueError, TypeError):
            executed_qty = 0.0
            
        try:
            avg_price = float(response.get("avgPrice", 0.0))
        except (ValueError, TypeError):
            avg_price = 0.0

        summary = {
            "orderId": order_id,
            "status": status,
            "executedQty": executed_qty,
            "avgPrice": avg_price,
        }
        
        log.info(
            f"Successfully created order {order_id}. "
            f"Status: {status}, Executed: {executed_qty}, Avg Price: {avg_price}"
        )
        return summary

    except BinanceAPIException as e:
        log.error(f"Binance API order placement error (Code {e.code}): {e.message}")
        
        # Catch and explain specific trading error codes
        if e.code == -2019:
            error_msg = "Insufficient margin. Your account balance is too low to support this trade."
        elif e.code == -1111:
            error_msg = "Precision error. The quantity or price has too many decimal places for this asset's requirements."
        elif e.code == -1013:
            error_msg = (
                "Order rejected: Invalid quantity or price. It likely violates Binance's filters "
                "(e.g., minimum order value, LOT_SIZE precision, or PRICE_FILTER ranges)."
            )
        elif e.code == -2010:
            error_msg = "Order rejected: Insufficient balance or issue with your account positions."
        elif e.code == -4003:
            error_msg = "Invalid quantity specified. The trade size is either too small or exceeds maximum limits."
        else:
            error_msg = f"Binance API Error: {e.message} (Binance Error Code: {e.code})"
            
        raise OrderPlacementError(error_msg)
        
    except BinanceRequestException as e:
        log.error(f"Network request failure during order execution: {e}")
        raise OrderPlacementError(
            f"Failed to communicate with Binance server. Network error: {e}"
        )
    except Exception as e:
        log.error(f"Unexpected execution failure: {e}")
        raise OrderPlacementError(
            f"An unexpected error occurred during order placement: {e}"
        )

class OrderValidationError(ValueError):
    """Custom exception raised when trading bot input parameters fail validation."""
    pass

def validate_order_inputs(
    symbol: str, 
    side: str, 
    order_type: str, 
    quantity: float | str, 
    price: float | str | None = None
) -> dict:
    """
    Validates and normalizes futures order parameters.
    
    Returns:
        dict: A dictionary containing cleaned and typed values:
              {'symbol': str, 'side': str, 'type': str, 'quantity': float, 'price': float | None}
              
    Raises:
        OrderValidationError: If any of the inputs fail validation logic.
    """
    # 1. Symbol validation
    if not symbol or not isinstance(symbol, str):
        raise OrderValidationError("Symbol must be a non-empty string.")
    
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol.isalnum():
        raise OrderValidationError(
            f"Invalid symbol: '{symbol}'. Symbol must contain only alphanumeric characters."
        )

    # 2. Side validation
    if not side or not isinstance(side, str):
        raise OrderValidationError("Side must be a string ('BUY' or 'SELL').")
    
    normalized_side = side.strip().upper()
    if normalized_side not in ("BUY", "SELL"):
        raise OrderValidationError(
            f"Invalid side: '{side}'. Must be either 'BUY' or 'SELL'."
        )

    # 3. Order type validation
    if not order_type or not isinstance(order_type, str):
        raise OrderValidationError("Order type must be a string ('MARKET' or 'LIMIT').")
    
    normalized_type = order_type.strip().upper()
    if normalized_type not in ("MARKET", "LIMIT"):
        raise OrderValidationError(
            f"Invalid order type: '{order_type}'. Must be either 'MARKET' or 'LIMIT'."
        )

    # 4. Quantity validation
    try:
        qty_float = float(quantity)
    except (ValueError, TypeError):
        raise OrderValidationError(
            f"Quantity must be a numeric value. Got: '{quantity}'."
        )
    
    if qty_float <= 0:
        raise OrderValidationError(
            f"Quantity must be a positive number. Got: {qty_float}."
        )

    # 5. Price validation (Required for LIMIT orders)
    price_float = None
    if normalized_type == "LIMIT":
        if price is None or str(price).strip() == "":
            raise OrderValidationError("Price is required for LIMIT orders.")
        
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            raise OrderValidationError(
                f"Price must be a numeric value. Got: '{price}'."
            )
        
        if price_float <= 0:
            raise OrderValidationError(
                f"Price must be a positive number. Got: {price_float}."
            )
    else:
        # Ignore price for MARKET orders to avoid mistakes
        if price is not None and str(price).strip() != "":
            # We don't fail, but we discard it for MARKET order safety
            price_float = None

    return {
        "symbol": normalized_symbol,
        "side": normalized_side,
        "type": normalized_type,
        "quantity": qty_float,
        "price": price_float,
    }

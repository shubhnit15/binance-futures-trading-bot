import sys
from pathlib import Path
import click
import questionary
from dotenv import load_dotenv

# Ensure the project directory is in the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bot import (
    setup_logging,
    validate_order_inputs,
    OrderValidationError,
    BinanceFuturesClient,
    ClientConnectionError,
    place_futures_order,
    OrderPlacementError,
)

# Load environment variables from .env
load_dotenv()

# Initialize the dual logger (writes DEBUG/INFO to bot.log, INFO to stdout/stderr)
logger = setup_logging()

def run_interactive_wizard() -> dict:
    """
    Runs an interactive Questionary terminal prompt to gather trading inputs
    with immediate validation feedback.
    """
    click.secho("\n=== Interactive Binance Futures Wizard ===", fg="cyan", bold=True)
    
    # 1. Prompt Symbol
    symbol = questionary.text(
        "Enter Trading Symbol (e.g., BTCUSDT):",
        validate=lambda text: len(text.strip()) > 0 or "Symbol cannot be empty."
    ).ask()
    if symbol is None:  # User cancelled via Ctrl+C
        click.secho("\nOperation cancelled.", fg="yellow")
        sys.exit(0)
    symbol = symbol.strip().upper()

    # 2. Prompt Side
    side = questionary.select(
        "Select Side:",
        choices=["BUY", "SELL"]
    ).ask()
    if side is None:
        click.secho("\nOperation cancelled.", fg="yellow")
        sys.exit(0)

    # 3. Prompt Order Type
    order_type = questionary.select(
        "Select Order Type:",
        choices=["MARKET", "LIMIT"]
    ).ask()
    if order_type is None:
        click.secho("\nOperation cancelled.", fg="yellow")
        sys.exit(0)

    # 4. Prompt Quantity
    def validate_quantity(text: str) -> bool | str:
        try:
            val = float(text)
            if val <= 0:
                return "Quantity must be greater than zero."
            return True
        except ValueError:
            return "Please enter a valid positive number."

    quantity = questionary.text(
        f"Enter Quantity ({symbol} contracts):",
        validate=validate_quantity
    ).ask()
    if quantity is None:
        click.secho("\nOperation cancelled.", fg="yellow")
        sys.exit(0)
    quantity = float(quantity)

    # 5. Prompt Price (only if LIMIT)
    price = None
    if order_type == "LIMIT":
        def validate_price(text: str) -> bool | str:
            try:
                val = float(text)
                if val <= 0:
                    return "Price must be greater than zero."
                return True
            except ValueError:
                return "Please enter a valid positive number."

        price_input = questionary.text(
            "Enter Limit Price (USDT):",
            validate=validate_price
        ).ask()
        if price_input is None:
            click.secho("\nOperation cancelled.", fg="yellow")
            sys.exit(0)
        price = float(price_input)

    return {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "price": price,
    }


@click.command(help="Place orders on the Binance Futures Testnet (USDT-M) seamlessly.")
@click.option("--symbol", "-s", type=str, help="Trading pair symbol (e.g., BTCUSDT).")
@click.option("--side", "-d", type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order direction.")
@click.option("--type", "-t", "order_type", type=click.Choice(["MARKET", "LIMIT"], case_sensitive=False), help="Order execution type.")
@click.option("--quantity", "-q", type=float, help="Trade size (contract quantity).")
@click.option("--price", "-p", type=float, help="Execution target price (Required for LIMIT orders).")
def main(symbol: str | None, side: str | None, order_type: str | None, quantity: float | None, price: float | None) -> None:
    """
    Main entry point for the Binance Futures Trading Bot CLI.
    If some or all arguments are omitted, it falls back to an interactive wizard.
    """
    click.clear()
    click.secho("[BOT] Binance Futures Testnet Trading Bot", fg="magenta", bold=True)
    click.secho("-" * 50, fg="magenta")

    # 1. Initialize and test the Binance connection first
    try:
        client_wrapper = BinanceFuturesClient()
        client_wrapper.check_connection()
    except ClientConnectionError as e:
        click.secho(f"\n[ERROR] Connection Failure: {e}", fg="red", err=True, bold=True)
        logger.error(f"Initialization aborted: {e}")
        sys.exit(1)

    # 2. Determine execution mode (CLI inputs vs Interactive fallback)
    # If ANY essential parameters are omitted, we switch to interactive menu mode
    inputs_are_complete = (
        symbol is not None and
        side is not None and
        order_type is not None and
        quantity is not None and
        (order_type.upper() == "MARKET" or price is not None)
    )

    if not inputs_are_complete:
        click.secho("[INFO] Required arguments missing or incomplete.", fg="yellow")
        click.echo("Transitioning to interactive prompt mode...")
        order_params = run_interactive_wizard()
    else:
        # Validate direct CLI command-line options
        try:
            order_params = validate_order_inputs(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
        except OrderValidationError as e:
            click.secho(f"\n[ERROR] Validation Error: {e}", fg="red", err=True, bold=True)
            logger.error(f"Input validation rejected command-line arguments: {e}")
            sys.exit(1)

    # 3. Confirm parameters before submission
    click.secho("\n[ORDER] Order Confirmation Details", fg="cyan", bold=True)
    click.echo(f"  Asset Symbol: {order_params['symbol']}")
    click.echo(f"  Side/Direction: {order_params['side']}")
    click.echo(f"  Order Type:   {order_params['type']}")
    click.echo(f"  Quantity:     {order_params['quantity']}")
    if order_params["type"] == "LIMIT":
        click.echo(f"  Limit Price:  {order_params['price']} USDT")
    click.echo("-" * 35)

    if not inputs_are_complete:
        # Additional step for safety in interactive mode
        confirm = questionary.confirm("Do you want to submit this order to the Testnet?").ask()
        if not confirm:
            click.secho("[CANCEL] Order cancelled by the user.", fg="yellow")
            sys.exit(0)

    # 4. Place the order
    try:
        result = place_futures_order(
            client_wrapper=client_wrapper,
            symbol=order_params["symbol"],
            side=order_params["side"],
            order_type=order_params["type"],
            quantity=order_params["quantity"],
            price=order_params["price"],
            logger=logger
        )
        
        # 5. Output beautiful success summary
        click.secho("\n[SUCCESS] Order Placed Successfully!", fg="green", bold=True)
        click.secho("-" * 40, fg="green")
        click.echo(f"  Order ID:      {result['orderId']}")
        click.echo(f"  Status:        {result['status']}")
        click.echo(f"  Executed Qty:  {result['executedQty']}")
        click.echo(f"  Avg Fill Price: {result['avgPrice']} USDT")
        click.secho("-" * 40, fg="green")
        click.echo(f"Detailed logs saved to {click.style('bot.log', fg='blue')}.\n")

    except OrderPlacementError as e:
        click.secho(f"\n[FAILURE] Trade Execution Failed", fg="red", bold=True)
        click.secho("-" * 40, fg="red")
        click.secho(f"{e}", fg="red")
        click.secho("-" * 40, fg="red")
        click.echo(f"Review {click.style('bot.log', fg='blue')} for full diagnostic stack traces.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

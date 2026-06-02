import logging
import sys
from pathlib import Path

def setup_logging(log_file: str = "bot.log") -> logging.Logger:
    """
    Sets up a dual-handler logger.
    - Detailed logs (DEBUG and above) are written to `bot.log`.
    - User-friendly logs (INFO and above) are printed to the console.
    """
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    # Detailed formatter for the log file
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
    )
    
    # Path logic to ensure logs can be created in the current working directory
    log_path = Path(log_file).resolve()
    
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Simplified, elegant formatter for the console
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Mute chatty third-party packages in logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Python-binance can log a lot of websocket connection details
    logging.getLogger("binance").setLevel(logging.WARNING)

    return logger

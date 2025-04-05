from loguru import logger
import os

# Making logs directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure Loguru logger
logger.add(
    os.path.join(LOG_DIR, "app.log"),  # Log file location
    rotation="00:00",  # Create a new log file every midnight
    compression="zip",  # Compress old logs as ZIP
    level="INFO",  # Minimum log level (can be DEBUG, ERROR, etc.)
    format="{time} | {level} | {message}",  # Log format
    backtrace=True,  # Capture full traceback for errors
    diagnose=True,  # Provide more debugging details
)

logger.info("Logger setup complete. Logging initialized.")


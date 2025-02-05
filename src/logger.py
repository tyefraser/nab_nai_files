import logging
from pathlib import Path
from datetime import datetime

# Define log directory relative to the project root
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)  # Ensure logs directory exists

# Generate log filename with timestamp (e.g., logs/2025-02-05_12-30-00.log)
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
LOG_FILE_PATH = LOG_DIR / log_filename

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8"),  # Log to a timestamped file
        logging.StreamHandler()  # Log to console
    ]
)

# Create a logger instance
logger = logging.getLogger("NAIProcessor")  # Custom logger name

logger.info(f"Logger initialized. Writing to: {LOG_FILE_PATH}")

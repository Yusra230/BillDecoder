import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base project directories
BASE_DIR = Path(__file__).resolve().parent.parent
TRAIN_BILLS_DIR = BASE_DIR / "train" / "bills"
TEST_BILLS_DIR = BASE_DIR / "test" / "bills"
OUTPUT_DIR = BASE_DIR / "output"

# Required challenge AI model - MUST be gemini-3.5-flash-lite
MODEL_NAME = "gemini-3.5-flash-lite"
MODEL_PROVIDER = "google"

# Rate limit pacing: 15 req/min free limit -> sleep 4.2 seconds between requests
REQUEST_DELAY_SECONDS = 4.2
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2.0

import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

# Create directories if they don't exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# File paths
RAW_MSP_DATA_PATH = os.path.join(RAW_DATA_DIR, "msp_data.json")
PROCESSED_MSP_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "processed_msp_data.json")
ANALYSIS_RESULTS_PATH = os.path.join(PROCESSED_DATA_DIR, "analysis_results.json")

# Reddit API settings
SUBREDDIT_NAME = "msp"
MAX_POSTS = 100

# Search terms
QUERIES = [
    "SentinelOne OR S1 OR Sentinel 1 OR Sentinel one OR Sentinel-1 OR Sentinel-one OR Sentinel1",
    "Guardz"
    "CrowdStrike",
    "Sophos",
    "Carbon Black",
    "Cylance",
    "Trend Micro",
]

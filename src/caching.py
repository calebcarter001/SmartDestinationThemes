import time
import logging
import pickle
import os
from datetime import timedelta
from typing import Optional, Dict, Any

# --- Cache Configuration ---
CACHE_DIR = "cache"
PAGE_CONTENT_CACHE_EXPIRY_DAYS = 30
BRAVE_SEARCH_CACHE_EXPIRY_DAYS = 7

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# --- Core Caching Functions ---

def get_cache_path(key: list) -> str:
    """Creates a consistent, file-system-safe path from a cache key."""
    # Simple key-to-filename conversion
    filename = "_".join(str(k) for k in key).replace('/', '_').replace(':', '')
    return os.path.join(CACHE_DIR, f"{filename}.pkl")

def write_to_cache(key: list, data: Any):
    """Writes data to a cache file."""
    try:
        path = get_cache_path(key)
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        logging.debug(f"Successfully wrote to cache with key: {key}")
    except Exception as e:
        logging.error(f"Failed to write to cache for key {key}: {e}", exc_info=True)

def read_from_cache(key: list, expiry_days: int) -> Optional[Any]:
    """Reads data from a cache file if it exists and is not expired."""
    try:
        path = get_cache_path(key)
        if not os.path.exists(path):
            return None
        
        # Check if the file is expired
        file_mod_time = os.path.getmtime(path)
        if (time.time() - file_mod_time) > timedelta(days=expiry_days).total_seconds():
            logging.info(f"Cache expired for key: {key}")
            os.remove(path)
            return None
        
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        logging.error(f"Failed to read from cache for key {key}: {e}", exc_info=True)
        return None

# --- Affinity Cache Class (for pipeline state) ---

class AffinityCache:
    """
    Implements a simple cache for the final affinity results of a destination.
    This uses the generic caching functions.
    """
    def __init__(self, config: dict):
        self.config = config
        self.ttl_days = self.config.get("caching", {}).get("affinity_expiry_days", 1)

    def get(self, destination_name: str) -> Optional[Dict]:
        """Retrieves final affinity data for a destination."""
        cache_key = ["affinity_result", destination_name]
        return read_from_cache(cache_key, self.ttl_days)

    def set(self, destination_name: str, data: dict):
        """Stores final affinity data for a destination."""
        cache_key = ["affinity_result", destination_name]
        write_to_cache(cache_key, data)

# The more advanced cache from your design would look something like this.
# This is for future implementation.
class AdvancedAffinityCache:
    def __init__(self):
        # self.redis_client = Redis(**settings.REDIS_CONFIG)
        # self.vector_db = Pinecone(**settings.PINECONE_CONFIG)
        pass
        
    def smart_cache_strategy(self, destination):
        # Tier destinations by popularity/query frequency
        # tier = self.get_destination_tier(destination)
        
        # cache_ttl = {
        #     'top_100': timedelta(days=7),
        #     'top_1000': timedelta(days=30),
        #     'long_tail': timedelta(days=90),
        #     'seasonal': self.dynamic_ttl()
        # }
        
        # return cache_ttl.get(tier)
        pass 
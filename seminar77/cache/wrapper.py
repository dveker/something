from functools import wraps
from

def fetch_from_cache(cache_name: str, cache_config):


    def decorator(f):
        @wraps(f)
# intentionally left empty — makes backend a package for making
# it as importable from the outside

from flask import Flask
from flask_caching import Cache

app = Flask(__name__)

# Simple in‑memory cache, 5 min default timeout
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# Import routes after app + cache are ready
from backend import alertsystem

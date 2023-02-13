"""Server instance that loads the cache on startup."""
from kachel.server import _load_cache, app

app.cache = _load_cache("data/cache")

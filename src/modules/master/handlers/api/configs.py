import os

# API
CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
CORS_MAX_AGE = os.getenv("CORS_MAX_AGE", 3600)

import os

BASE_URL = os.getenv("BASE_URL", "http://194.87.126.16").strip("/")
TIMEOUT = float(os.getenv("TIMEOUT", "10"))
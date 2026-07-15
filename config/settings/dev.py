from .base import *  # noqa: F401,F403

DEBUG = True

# Convenient defaults for local development; still overridable via .env.
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS + ["localhost", "127.0.0.1"]))

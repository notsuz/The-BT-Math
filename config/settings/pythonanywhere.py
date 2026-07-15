from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# PythonAnywhere terminates TLS at its own front-end proxy. Unlike Render,
# it's not guaranteed to forward X-Forwarded-Proto, so blindly enabling
# SECURE_SSL_REDIRECT here can cause an infinite redirect loop. Leave it off
# by default; flip DJANGO_SECURE_SSL_REDIRECT=True in your .env only after
# confirming https:// loads correctly without it.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

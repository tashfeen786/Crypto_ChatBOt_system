# app/routes/__init__.py
"""
API Routes Package
"""

__all__ = []

# Try to import all route modules
try:
    from . import auth
    __all__.append('auth')
except ImportError:
    pass

try:
    from . import chat
    __all__.append('chat')
except ImportError:
    pass

try:
    from . import coins
    __all__.append('coins')
except ImportError:
    pass

try:
    from . import trading
    __all__.append('trading')
except ImportError:
    pass

try:
    from . import user
    __all__.append('user')
except ImportError:
    pass

try:
    from . import portfolio
    __all__.append('portfolio')
except ImportError:
    pass

try:
    from . import news
    __all__.append('news')
except ImportError:
    pass

# 🆕 Alerts module
try:
    from . import alerts
    __all__.append('alerts')
except ImportError:
    pass
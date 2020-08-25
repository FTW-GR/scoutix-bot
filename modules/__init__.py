"""
Loads all classes ending in 'Module' as direct attributes here
"""

import os
import sys

path = os.path.dirname(os.path.abspath(__file__))

for py in [f[:-3] for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py']:
    mod = __import__('.'.join([__name__, py]), fromlist=[py])
    for x in dir(mod):
        y = getattr(mod, x)
        if isinstance(y, type) and x.endswith('Module'):
            setattr(sys.modules[__name__], y.__name__, y)

import sys as _sys
from user import User
from table import Table
from vclient import Client

_this_module = _sys.modules[__name__]
if not hasattr(_this_module, 'client'):
    client = Client()
    setattr(_this_module, 'client', client)



# This file makes the routers directory a Python package
from . import collectors, citizen, admin

__all__ = ["collectors", "citizen", "admin"]
"""hot2sql 主模块"""
from .database import HotSearchDB
from .config import SUPABASE_URL, SUPABASE_KEY, PLATFORMS

__all__ = ['HotSearchDB', 'SUPABASE_URL', 'SUPABASE_KEY', 'PLATFORMS']

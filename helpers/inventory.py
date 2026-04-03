"""Inventory cache helpers shared by tabs/t09_rack.py and tabs/t10_inventory.py."""
import streamlit as st

try:
    import db as _db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

_INV_CACHE_KEY = "_inv_devices_cache"


def get_inventory_cached():
    if _INV_CACHE_KEY not in st.session_state:
        st.session_state[_INV_CACHE_KEY] = _db.list_inventory_devices() if _DB_AVAILABLE else []
    return st.session_state[_INV_CACHE_KEY]


def inv_cache_invalidate():
    st.session_state.pop(_INV_CACHE_KEY, None)

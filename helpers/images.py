import streamlit as st
from config import DEVICE_IMAGE_MAP

def _get_device_img_b64(device_key):
    """Load device image as base64 for SVG embedding. Returns None if unavailable."""
    import os as _os
    fname = DEVICE_IMAGE_MAP.get(device_key)
    if not fname:
        return None
    img_path = f"/app/images/{fname}"
    if not _os.path.exists(img_path):
        return None
    mtime = _os.path.getmtime(img_path)
    return _get_device_img_b64_cached(img_path, mtime)


@st.cache_data(max_entries=30, show_spinner=False)
def _get_device_img_b64_cached(img_path, mtime):
    import base64 as _b64mod
    try:
        with open(img_path, "rb") as fh:
            return _b64mod.b64encode(fh.read()).decode()
    except Exception:
        return None


@st.cache_data(max_entries=50, show_spinner=False)
def _strip_white_bg(b64_str):
    """Return a base64 PNG with near-white pixels made transparent. Cached across reruns."""
    try:
        import numpy as _np
        from PIL import Image as _PILI
        import io as _pio, base64 as _pb64
        _img = _PILI.open(_pio.BytesIO(_pb64.b64decode(b64_str))).convert("RGBA")
        _arr = _np.array(_img, dtype=_np.uint8)
        _white = (_arr[:, :, 0] > 200) & (_arr[:, :, 1] > 200) & (_arr[:, :, 2] > 200)
        _arr[_white, 3] = 0
        _out = _pio.BytesIO()
        _PILI.fromarray(_arr).save(_out, format="PNG")
        return _pb64.b64encode(_out.getvalue()).decode()
    except Exception:
        return b64_str


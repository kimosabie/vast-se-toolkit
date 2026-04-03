import streamlit as st
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    import db as _db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

from helpers.inventory import get_inventory_cached as _get_inventory_cached
from helpers.inventory import inv_cache_invalidate as _inv_cache_invalidate


def render():
    st.subheader("📦 Device Inventory")
    st.caption("Build your global product library. Devices saved here are available across all projects and can be added to any rack diagram.")
    st.markdown("---")

    _dinv_all = _get_inventory_cached()
    _dinv_cats = ["All"] + (_db.DEVICE_CATEGORIES if _DB_AVAILABLE else [])

    _dinv_left, _dinv_right = st.columns([1, 1])

    with _dinv_left:
        # ── Browse / manage inventory ────────────────────────
        st.markdown("### 📚 Product Library")

        _dinv_s_col, _dinv_c_col = st.columns([3, 2])
        with _dinv_s_col:
            _dinv_search = st.text_input("Search", key="inv_search",
                                          placeholder="Filter by name…",
                                          label_visibility="collapsed")
        with _dinv_c_col:
            _dinv_cat_sel = st.selectbox("Category", _dinv_cats, key="inv_cat_sel",
                                          label_visibility="collapsed")

        _dinv_search = st.session_state.get("inv_search", "")
        _dinv_filtered = [
            d for d in _dinv_all
            if (_dinv_search.lower() in d["product_name"].lower() or not _dinv_search)
            and (_dinv_cat_sel == "All" or d["category"] == _dinv_cat_sel)
        ]

        if _dinv_filtered:
            for _dinv_d in _dinv_filtered:
                _dil, _dir = st.columns([5, 1])
                with _dil:
                    _dinv_v = f" · {_dinv_d['vendor']}" if _dinv_d["vendor"] else ""
                    _dinv_n = f"  *{_dinv_d['notes']}*" if _dinv_d["notes"] else ""
                    st.markdown(
                        f'<p style="font-size:12px;margin:6px 0 0 0">'
                        f'<b>{_dinv_d["product_name"]}</b>{_dinv_v}<br>'
                        f'<span style="color:#888">{_dinv_d["category"]} · '
                        f'{_dinv_d["u_height"]}U · {_dinv_d["weight_lbs"]:.0f} lbs · '
                        f'{_dinv_d["avg_w"]}W avg / {_dinv_d["max_w"]}W max'
                        f'{"  📷" if _dinv_d["img_b64"] else ""}'
                        f'{_dinv_n}</span></p>',
                        unsafe_allow_html=True,
                    )
                with _dir:
                    if st.button("🗑️", key=f"inv_del_{_dinv_d['id']}",
                                 help="Delete from inventory permanently"):
                        _db.delete_inventory_device(_dinv_d["id"])
                        _inv_cache_invalidate()
                        st.rerun()
        elif _dinv_all:
            st.caption("No products match the filter.")
        else:
            st.caption("Inventory is empty — add your first product using the form →")

    with _dinv_right:
        # ── Add / update product ─────────────────────────────
        st.markdown("### ➕ Add Product")
        st.caption("Define the product specs once. Use the Rack Diagram tab to add instances to a rack.")

        _inv_prod    = st.text_input("Product Name *", key="inv_prod",
                                      placeholder="e.g. APC Smart-UPS 3000")
        _inv_vendor  = st.text_input("Vendor / Brand", key="inv_vendor",
                                      placeholder="e.g. APC, Vertiv, Raritan")
        _inv_cat     = st.selectbox("Category", _db.DEVICE_CATEGORIES if _DB_AVAILABLE else ["Other"],
                                     key="inv_cat")
        _inv_notes   = st.text_input("Notes (optional)", key="inv_notes",
                                      placeholder="e.g. 208V input, phase A")

        _inv_phys1, _inv_phys2 = st.columns(2)
        with _inv_phys1:
            _inv_u       = st.number_input("Height (U)", min_value=1, max_value=20, value=2,
                                            key="inv_u")
            _inv_avg_w   = st.number_input("Avg Power (W)", min_value=0, value=500, step=10,
                                            key="inv_avg_w")
        with _inv_phys2:
            _inv_weight  = st.number_input("Weight (lbs)", min_value=0.0, value=50.0, step=1.0,
                                            key="inv_weight_lbs")
            _inv_max_w   = st.number_input("Max Power (W)", min_value=0, value=800, step=10,
                                            key="inv_max_w")

        _inv_img = st.file_uploader("Device Image (PNG, max 2 MB)", type=["png"], key="inv_img",
                                     help="Landscape PNG preferred. Displayed inside the rack slot.")

        _inv_errors = []
        if not _inv_prod.strip():
            _inv_errors.append("Product Name is required.")
        if _inv_img is not None and _inv_img.size > 2 * 1024 * 1024:
            _inv_errors.append("Image exceeds 2 MB limit.")
        for _ie in _inv_errors:
            st.warning(_ie)

        if st.button("Save to Inventory", key="inv_add_btn",
                     disabled=bool(_inv_errors) or not _inv_prod.strip(),
                     use_container_width=True):
            import base64 as _b64mod
            _inv_img_b64 = ""
            if _inv_img is not None:
                _inv_img_b64 = _b64mod.b64encode(_inv_img.read()).decode("utf-8")
            _db.upsert_inventory_device(
                product_name=_inv_prod.strip(),
                vendor=_inv_vendor.strip(),
                category=_inv_cat,
                u_height=int(_inv_u),
                weight_lbs=float(_inv_weight),
                avg_w=int(_inv_avg_w),
                max_w=int(_inv_max_w),
                img_b64=_inv_img_b64,
                notes=_inv_notes.strip(),
            )
            _inv_cache_invalidate()
            st.success(f'✅ "{_inv_prod.strip()}" saved to inventory.')
            st.rerun()




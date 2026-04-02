import streamlit as st
from jinja2 import Environment, FileSystemLoader
from datetime import date
import sys
import os
import requests
sys.path.insert(0, os.path.dirname(__file__))
try:
    import db as _db
    _DB_AVAILABLE = True
except Exception as _db_import_err:
    _DB_AVAILABLE = False

_INV_CACHE_KEY = "_inv_devices_cache"

def _get_inventory_cached():
    """Return cached inventory list. Call _inv_cache_invalidate() after any write."""
    if _INV_CACHE_KEY not in st.session_state:
        st.session_state[_INV_CACHE_KEY] = _db.list_inventory_devices() if _DB_AVAILABLE else []
    return st.session_state[_INV_CACHE_KEY]

def _inv_cache_invalidate():
    st.session_state.pop(_INV_CACHE_KEY, None)

# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(
    page_title="VAST SE Installation Toolkit",
    page_icon="/app/images/vast_logo_icon.png",
    layout="wide"
)
st.logo(
    "/app/images/vast_logo_wide.png",
    icon_image="/app/images/vast_logo_icon.png",
    size="large",
)
st.markdown("""
<style>
[data-testid="stLogo"],
[data-testid="stSidebarHeader"] img,
[data-testid="stSidebarHeader"] [data-testid="stLogo"],
div[class*="logo"] img {
    height: 12rem !important;
    max-height: 12rem !important;
    width: auto !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HARDWARE PROFILES & HELPERS  (extracted to config.py / helpers/)
# ============================================================
from config import (
    HARDWARE_PROFILES, SPEED_RANK, DBOX_PROFILES, CNODE_PERF,
    DEVICE_SPECS, DEVICE_IMAGES, DEVICE_IMAGE_MAP, DR_ESTIMATES,
)
from helpers.images import _get_device_img_b64, _strip_white_bg
from helpers.svg_export import (
    _svg_to_pdf_cached, _svg_to_jpg_cached,
    _build_multipage_pdf, _build_consolidated_pdf,
)
from helpers.port_logic import (
    get_sw_suffix, get_port_mappings, validate_port_counts, render_cable_summary,
)
from helpers.state import (
    _is_saveable, _SAVEABLE_EXACT, _SKIP_EXACT, _SKIP_PREFIXES,
)

# ============================================================
# PENDING LOAD / CLEAR
# Must run before any widgets are instantiated so that
# session_state values are set before widgets read them.
# ============================================================

_just_loaded = False
if "_pending_load" in st.session_state:
    _pending = st.session_state.pop("_pending_load")
    for _k, _v in _pending.items():
        if _is_saveable(_k):
            st.session_state[_k] = _v
    if "_db_project_id" in _pending:
        st.session_state["_db_project_id"] = _pending["_db_project_id"]
    _just_loaded = True

# Purge any button/file_uploader/download_button keys that may have
# leaked into session_state from an old project snapshot saved while a
# widget was active. Streamlit forbids setting these keys programmatically.
# Only run during project loads — running unconditionally would delete button
# click state before widgets get to read it, making those buttons silently fail.
if _just_loaded:
    for _wk in list(st.session_state.keys()):
        if _wk in _SKIP_EXACT or any(_wk.startswith(_sp) for _sp in _SKIP_PREFIXES):
            del st.session_state[_wk]

# Deferred rack-device removal: button sets _pending_rack_rm index, we apply
# it here (before widgets render) then clear the button states so the click
# is not replayed on subsequent reruns triggered by st.rerun().
if "_pending_rack_rm" in st.session_state:
    _rm_idx = st.session_state.pop("_pending_rack_rm")
    _cur_devs = st.session_state.get("rack_custom_devices", [])
    st.session_state["rack_custom_devices"] = [
        d for i, d in enumerate(_cur_devs) if i != _rm_idx
    ]
    for _wk in list(st.session_state.keys()):
        if _wk.startswith("rack_cust_rm_"):
            del st.session_state[_wk]

# Deferred rack-device add: button stages _pending_rack_add dict, we apply
# it here so we can also pre-set the rack placement widget key (rack_rack_*)
# before the widget renders, and clear rack_pick_add to prevent cascading.
if "_pending_rack_add" in st.session_state:
    _pa = st.session_state.pop("_pending_rack_add")
    _pa_devs = list(st.session_state.get("rack_custom_devices", []))
    _pa_name = _pa["name"]
    _pa_base, _pa_idx = _pa_name, 1
    while any(d["name"] == _pa_name for d in _pa_devs):
        _pa_name = f"{_pa_base}-{_pa_idx}"
        _pa_idx += 1
    _pa_devs.append({
        "name":         _pa_name,
        "product_name": _pa["product_name"],
        "u":            _pa["u"],
        "weight_lbs":   _pa["weight_lbs"],
        "avg_w":        _pa["avg_w"],
        "max_w":        _pa["max_w"],
        "img_b64":      _pa["img_b64"],
    })
    st.session_state["rack_custom_devices"] = _pa_devs
    # Pre-set rack assignment so the placement selectbox starts on the right rack
    _pa_rack_key = "rack_rack_" + _pa_name.replace(" ", "_").replace("-", "_")
    st.session_state[_pa_rack_key] = _pa["rack_no"]
    # Clear add-button state to prevent this from firing again on next rerun
    if "rack_pick_add" in st.session_state:
        del st.session_state["rack_pick_add"]

if "_pending_clear" in st.session_state:
    st.session_state.pop("_pending_clear")
    _internal = {k: v for k, v in st.session_state.items()
                 if k.startswith("_") and k != "_db_project_id"}
    st.session_state.clear()
    st.session_state.update(_internal)
    st.session_state["_db_project_id"] = None
    # Explicitly reset all proj_ and tab5_/tab6_ keys to defaults.
    # This runs before any widget renders so Streamlit accepts it.
    _str_defaults = [
        "proj_psnt", "proj_license", "proj_sfdc", "proj_ticket",
        "proj_slack", "proj_lucid", "proj_survey", "proj_peer_rev",
        "proj_install_guide", "proj_vast_release", "proj_os_version",
        "proj_bundle",
        "proj_nb_mtu", "proj_gpu_servers", "proj_site_notes",
        "proj_ip_notes",
        "tab7_sw_a_ip", "tab7_sw_b_ip", "tab7_gw", "tab7_ntp",
        "tab7_isl", "tab7_uplink",
        "tab8_sw_a_ip", "tab8_sw_b_ip", "tab8_gw", "tab8_ntp",
        "tab8_isl", "tab8_uplink",
    ]
    for _k in _str_defaults:
        st.session_state[_k] = ""
    st.session_state["tab7_vlan"] = 100  # number_input — must be int, not ""
    _bool_defaults = [
        "proj_phison", "proj_dual_nic", "proj_dbox_ha",
        "proj_encryption", "proj_ip_conflict",
        "tab7_isl_short", "tab8_enabled", "tab8_isl_short",
    ]
    for _k in _bool_defaults:
        st.session_state[_k] = False
    st.session_state["proj_num_dboxes"] = 1
    st.session_state["proj_num_cnodes"] = 4
    st.session_state["tab7_mgmt_vlan"]  = 1
    st.session_state["tab8_mgmt_vlan"]  = 1
    st.session_state["tab8_vlans"]      = ""
    st.session_state["sizer_drr_override"] = 0.0
    st.session_state["sizer_num_dboxes"]   = 1
    st.session_state["sizer_num_cnodes"]   = 4

# ============================================================
# SIDEBAR — persistent status bar
# ============================================================
with st.sidebar:
    st.markdown("## ⚡ VAST Data")
    st.markdown("**SE Installation Toolkit**")
    st.markdown("---")

    _sb_se       = st.session_state.get("se_name",      "—")
    _sb_customer = st.session_state.get("customer",     "—")
    _sb_cluster  = st.session_state.get("cluster_name", "—")
    _sb_date     = st.session_state.get("install_date", "—")
    _sb_proj_id  = st.session_state.get("_db_project_id")
    _sb_milestone= st.session_state.get("_save_milestone", "—")

    st.markdown(f"👤 **{_sb_se}**")
    st.markdown(f"🏢 {_sb_customer}")
    st.markdown(f"🖥️  {_sb_cluster}")
    st.markdown(f"📅 {_sb_date}")
    st.markdown("---")

    if _sb_proj_id:
        st.markdown(f"💾 Project **#{_sb_proj_id}**")
        st.markdown(f"🏷️  {_sb_milestone}")
        if _DB_AVAILABLE:
            try:
                # Cache version info — only re-query when project or save milestone changes
                _sb_ver_ck = f"_sb_ver_{_sb_proj_id}_{_sb_milestone}"
                if _sb_ver_ck not in st.session_state:
                    # Clear any stale version cache entries
                    for _vk in [k for k in st.session_state if k.startswith("_sb_ver_")]:
                        del st.session_state[_vk]
                    _sb_vs = _db.get_project_versions(_sb_proj_id)
                    st.session_state[_sb_ver_ck] = _sb_vs[0] if _sb_vs else None
                _sb_latest = st.session_state[_sb_ver_ck]
                if _sb_latest:
                    st.caption(f"v{_sb_latest['version_num']} · {_sb_latest['saved_at'][:16].replace('T', ' ')}")
            except Exception:
                pass
    else:
        st.caption("💾 Unsaved project")

    st.markdown("---")

    if "_online_status" not in st.session_state:
        try:
            requests.get("https://www.google.com", timeout=3)
            st.session_state["_online_status"] = True
        except Exception:
            st.session_state["_online_status"] = False

    if st.session_state.get("_online_status"):
        st.markdown("🟢 Online")
    else:
        st.markdown("🔴 Offline")

    st.markdown("---")
    st.caption("⚡ VAST SE Toolkit v1.2.0")
    st.caption(f"📅 {date.today().strftime('%d %B %Y')}")



# ── Always-available derived values ─────────────────────────
# These read from session_state with safe defaults so that
# ============================================================
# DERIVED VALUES  (computed once per render from session state)
# ============================================================
from helpers.context import get_ctx, build_sw_name
_ctx         = get_ctx()
pfx          = _ctx["pfx"]
num_dboxes   = _ctx["num_dboxes"]
num_cnodes   = _ctx["num_cnodes"]
topology     = _ctx["topology"]
include_ru   = _ctx["include_ru"]
dbox_label   = _ctx["dbox_label"]
dnode_label  = _ctx["dnode_label"]
cnode_label  = _ctx["cnode_label"]
dbox_ru_list = _ctx["dbox_ru_list"]
cnode_ru_list= _ctx["cnode_ru_list"]
sw1_ru       = _ctx["sw1_ru"]
sw2_ru       = _ctx["sw2_ru"]
vendor_suffix= _ctx["vendor_suffix"]
se_name      = _ctx["se_name"]
customer     = _ctx["customer"]
cluster_name = _ctx["cluster_name"]
install_date = _ctx["install_date"]
full_sw_a    = _ctx["full_sw_a"]
full_sw_b    = _ctx["full_sw_b"]

def _build_sw_name(sw_num, ru_val, vendor_sfx, gpu=False, spine=False):
    return build_sw_name(sw_num, ru_val, vendor_sfx, pfx, include_ru, gpu, spine)

# ============================================================
# MAIN HEADER
# ============================================================
st.title("⚡ VAST SE Installation Toolkit")
_hdr_se   = st.session_state.get("se_name", "")
_hdr_cust = st.session_state.get("customer", "")
if _hdr_se and _hdr_cust:
    st.caption(f"SE: **{_hdr_se}** · Customer: **{_hdr_cust}**")

# ============================================================
# TABS
# ============================================================
import tabs.t01_session    as _t01
import tabs.t02_sizer      as _t02
import tabs.t03_project    as _t03
import tabs.t04_confluence as _t04
import tabs.t05_preflight  as _t05
import tabs.t07_switch     as _t07
import tabs.t08_data_switch as _t08
import tabs.t09_rack       as _t09
import tabs.t10_inventory  as _t10
import tabs.t11_ai         as _t11
import tabs.t12_network    as _t12
import tabs.t13_kb         as _t13

tab1, tab2, tab3, tab7, tab8, tab9, tab12, tab10, tab11, tab5, tab4, tab13 = st.tabs([
    "🧑‍💻 Session",
    "📏 Capacity & Performance Sizer",
    "📋 Project Details",
    "🔌 Internal Switch — Southbound",
    "🖥️ Data Switch — Northbound",
    "📐 Rack Diagram",
    "🗺️ Network Diagram",
    "📦 Device Inventory",
    "🤖 AI Assistant",
    "✅ Pre-Flight, Validation & Installation",
    "📄 Confluence Install Plan",
    "📖 Knowledge Base",
])

with tab1:  _t01.render()
with tab2:  _t02.render()
with tab3:  _t03.render()
with tab4:  _t04.render()
with tab5:  _t05.render()
with tab7:  _t07.render()
with tab8:  _t08.render()
with tab9:  _t09.render()
with tab10: _t10.render()
with tab11: _t11.render()
with tab12: _t12.render()
with tab13: _t13.render()

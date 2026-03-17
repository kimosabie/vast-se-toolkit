import streamlit as st
from jinja2 import Environment, FileSystemLoader
from datetime import date
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
try:
    import db as _db
    _DB_AVAILABLE = True
except Exception as _db_import_err:
    _DB_AVAILABLE = False

# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(
    page_title="VAST SE Installation Toolkit",
    page_icon="⚡",
    layout="wide"
)

# ============================================================
# HARDWARE PROFILES
# ============================================================
HARDWARE_PROFILES = {
    "NVIDIA SN3700": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       32,
        "native_speed":      "200GbE",
        "connector":         "QSFP56",
        "mtu":               9216,
        "node_cable":        {"spec": "200G AOC",           "supplier": "VAST"},
        "isl_cable_short":   {"spec": "200G DAC (≤1m)",     "supplier": "VAST"},
        "isl_cable_long":    {"spec": "200G AOC (>1m)",     "supplier": "VAST"},
        "spine_cable":       {"spec": "200G AOC",           "supplier": "VAST"},
        "breakout_required": False,
        "customer_cables":   False,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "Mid-to-large cluster leaf switch"
    },
    "NVIDIA SN4600": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       64,
        "native_speed":      "200GbE",
        "connector":         "QSFP28",
        "mtu":               9216,
        "node_cable":        {"spec": "200G AOC",           "supplier": "VAST"},
        "isl_cable_short":   {"spec": "200G DAC (≤1m)",     "supplier": "VAST"},
        "isl_cable_long":    {"spec": "200G AOC (>1m)",     "supplier": "VAST"},
        "spine_cable":       {"spec": "200G AOC",           "supplier": "VAST"},
        "breakout_required": False,
        "customer_cables":   False,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "Large cluster leaf or spine"
    },
    "NVIDIA SN4700": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       32,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "AI/GPU workloads, spine capable"
    },
    "NVIDIA SN5400": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       64,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "NCP AI scale-out, spine"
    },
    "Arista 7050CX4-24D8": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       32,
        "native_speed":      "200GbE",
        "connector":         "QSFP56",
        "mtu":               9216,
        "node_cable":        {"spec": "200G AOC",           "supplier": "VAST"},
        "isl_cable_short":   {"spec": "200G DAC (≤1m)",     "supplier": "VAST"},
        "isl_cable_long":    {"spec": "200G AOC (>1m)",     "supplier": "VAST"},
        "spine_cable":       {"spec": "200G AOC",           "supplier": "VAST"},
        "breakout_required": False,
        "customer_cables":   False,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "Mixed 200G/400G ports, ToR leaf"
    },
    "Arista 7050DX4-32S": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       32,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "High-density 400G leaf"
    },
    "Arista 7060DX5-32S": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       32,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "Latest gen 400G leaf/spine"
    },
    "Arista 7060DX5-64S": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       64,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "High-density 400G leaf/spine"
    },
}

# Speed rank — spine must be >= leaf, same vendor
SPEED_RANK = {
    "200GbE": 1,
    "400GbE": 2,
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_sw_suffix(model_key):
    if "NVIDIA" in model_key or "Mellanox" in model_key:
        return "NVIDIA"
    elif "Arista" in model_key:
        return "ARISTA"
    return "SW"


def get_port_mappings(side, num_dboxes, num_cnodes, dnode_start,
                      cnode_start, pfx="VAST",
                      dbox_label="DBOX", dnode_label="DNODE",
                      cnode_label="CNODE"):
    mappings = []
    port_side = "1" if side == "A" else "2"

    for i in range(1, num_dboxes + 1):
        for dnode_idx in range(1, 3):
            swp_num = dnode_start + (i - 1) * 2 + (dnode_idx - 1)
            mappings.append({
                "port":  swp_num,
                "swp":   f"swp{swp_num}",
                "eth":   f"Ethernet{swp_num}",
                "desc":  (
                    f"{pfx}-{dbox_label}-{i}-"
                    f"{dnode_label}-{dnode_idx}-P{port_side}"
                ),
                "dbox":  i,
                "dnode": dnode_idx,
                "type":  "dnode"
            })

    for i in range(1, num_cnodes + 1):
        swp_num = cnode_start + (i - 1)
        mappings.append({
            "port":  swp_num,
            "swp":   f"swp{swp_num}",
            "eth":   f"Ethernet{swp_num}",
            "desc":  f"{pfx}-{cnode_label}-{i}-P{port_side}",
            "cnode": i,
            "type":  "cnode"
        })

    return mappings


def validate_port_counts(num_dboxes, num_cnodes, dnode_start,
                         cnode_start, profile):
    errors   = []
    warnings = []

    total_dnode_ports = num_dboxes * 2
    total_cnode_ports = num_cnodes
    dnode_end = dnode_start + total_dnode_ports - 1
    cnode_end = cnode_start + total_cnode_ports - 1
    isl_start = min(profile["default_isl"])

    if dnode_end >= cnode_start:
        errors.append(
            f"❌ DNode ports (swp{dnode_start}–swp{dnode_end}) "
            f"overlap with CNode start (swp{cnode_start}). "
            f"Reduce DBox count or adjust port ranges."
        )

    if cnode_end >= isl_start:
        errors.append(
            f"❌ CNode ports (swp{cnode_start}–swp{cnode_end}) "
            f"overflow into ISL/Uplink range (swp{isl_start}+). "
            f"Reduce CNode count or adjust port ranges."
        )

    total_needed = total_dnode_ports + total_cnode_ports
    if total_needed > profile["max_node_ports"]:
        errors.append(
            f"❌ Total ports needed ({total_needed}) exceeds "
            f"available node ports ({profile['max_node_ports']}) "
            f"on this switch model."
        )
    elif total_needed > profile["max_node_ports"] * 0.85:
        warnings.append(
            f"⚠️ Using {total_needed} of {profile['max_node_ports']} "
            f"available ports "
            f"({int(total_needed/profile['max_node_ports']*100)}% capacity). "
            f"Limited room for expansion."
        )

    return errors, warnings


def render_cable_summary(profile, isl_short):
    supplier_ok   = "✅ VAST ships"
    supplier_warn = "⚠️ Customer/Partner must supply"

    if profile["customer_cables"]:
        st.error(
            "⚠️ **400G CUSTOMER-SUPPLIED CABLES REQUIRED** — "
            "This switch has 400GbE native ports. "
            "VAST does not ship 400G MPO cables. "
            "Customer or partner must supply all 400G cables "
            "**before install day.**"
        )

    isl_cable = (
        profile["isl_cable_short"] if isl_short
        else profile["isl_cable_long"]
    )

    st.table([
        {
            "Connection":  "DNode (BF-3) → Switch",
            "Cable":       profile["node_cable"]["spec"],
            "Supplied By": supplier_warn
                           if profile["node_cable"]["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
        {
            "Connection":  "CNode (CX7) → Switch",
            "Cable":       profile["node_cable"]["spec"],
            "Supplied By": supplier_warn
                           if profile["node_cable"]["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
        {
            "Connection":  f"ISL / Peerlink ({'≤1m' if isl_short else '>1m'})",
            "Cable":       isl_cable["spec"],
            "Supplied By": supplier_warn
                           if isl_cable["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
        {
            "Connection":  "Spine / Uplink",
            "Cable":       profile["spine_cable"]["spec"],
            "Supplied By": supplier_warn
                           if profile["spine_cable"]["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
    ])


# ============================================================
# PENDING LOAD / CLEAR
# Must run before any widgets are instantiated so that
# session_state values are set before widgets read them.
# ============================================================
# Keys we save and restore — explicit whitelist.
# Excludes button/download_button keys which Streamlit forbids setting from code.
_SAVEABLE_PREFIXES = (
    "proj_", "tab5_", "tab6_", "spine_", "name_",
)
_SAVEABLE_EXACT = {
    "se_name", "customer", "cluster_name", "install_date",
}
_SKIP_SUFFIXES = ("_dl_A", "_dl_B", "_dl_a", "_dl_b", "_download",
                  "_handoff_dl", "tab5_download", "tab6_download")

def _is_saveable(k):
    if k in _SAVEABLE_EXACT:
        return True
    if any(k.startswith(p) for p in _SAVEABLE_PREFIXES):
        if any(k.endswith(s) or k == s for s in _SKIP_SUFFIXES):
            return False
        return True
    return False

if "_pending_load" in st.session_state:
    _pending = st.session_state.pop("_pending_load")
    for _k, _v in _pending.items():
        if _is_saveable(_k):
            st.session_state[_k] = _v
    if "_db_project_id" in _pending:
        st.session_state["_db_project_id"] = _pending["_db_project_id"]

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
        "proj_bundle", "proj_dbox_type", "proj_cbox_type",
        "proj_nb_mtu", "proj_gpu_servers", "proj_site_notes",
        "proj_ip_notes",
        "tab5_sw_a_ip", "tab5_sw_b_ip", "tab5_gw", "tab5_ntp",
        "tab5_isl", "tab5_uplink", "tab5_vlan",
        "tab6_sw_a_ip", "tab6_sw_b_ip", "tab6_gw", "tab6_ntp",
        "tab6_isl", "tab6_uplink", "tab6_vlan",
    ]
    for _k in _str_defaults:
        st.session_state[_k] = ""
    _bool_defaults = [
        "proj_phison", "proj_dual_nic", "proj_dbox_ha",
        "proj_encryption", "proj_ip_conflict",
        "tab5_isl_short", "tab6_enabled", "tab6_isl_short",
    ]
    for _k in _bool_defaults:
        st.session_state[_k] = False
    st.session_state["proj_num_dboxes"] = 1
    st.session_state["proj_num_cnodes"] = 4

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## ⚡ VAST Data")
    st.markdown("**SE Installation Toolkit**")
    st.markdown("---")

    st.header("📋 Session Details")
    se_name = st.text_input(
        "SE Name",
        value=st.session_state.get("se_name", ""),
        placeholder="Your full name"
    )
    st.session_state["se_name"] = se_name

    customer = st.text_input(
        "Customer Name",
        value=st.session_state.get("customer", ""),
        placeholder="e.g. Acme Corp"
    )
    st.session_state["customer"] = customer

    cluster_name = st.text_input(
        "Cluster Name",
        value=st.session_state.get("cluster_name", ""),
        placeholder="e.g. ACME-VAST-01"
    )
    st.session_state["cluster_name"] = cluster_name

    _saved_date = st.session_state.get("install_date", date.today())
    if isinstance(_saved_date, str):
        try:
            from datetime import datetime
            _saved_date = datetime.strptime(_saved_date, "%Y-%m-%d").date()
        except Exception:
            _saved_date = date.today()
    install_date = st.date_input("Install Date", value=_saved_date)
    st.session_state["install_date"] = str(install_date)


    st.markdown("---")
    st.caption("⚡ VAST SE Toolkit v1.1.0")
    st.caption(f"📅 {date.today().strftime('%d %B %Y')}")



# ── Always-available derived values ─────────────────────────
# These read from session_state with safe defaults so that
# all tabs work correctly even before Tab 1 has been filled in.

pfx          = st.session_state.get("cluster_name", "") or "VAST"
num_dboxes   = int(st.session_state.get("proj_num_dboxes",  1))
num_cnodes   = int(st.session_state.get("proj_num_cnodes",  4))
topology     = st.session_state.get("proj_topology", "Leaf Pair")

# Naming convention values (set in Tabs 5/6, defaulted here)
include_ru   = st.session_state.get("include_ru", False)
dbox_label   = st.session_state.get("name_dbox",  "DBOX")
dnode_label  = st.session_state.get("name_dnode", "DNODE")
cnode_label  = st.session_state.get("name_cnode", "CNODE")

dbox_ru_raw  = st.session_state.get("dbox_ru_raw",  "")
cnode_ru_raw = st.session_state.get("cnode_ru_raw", "")
dbox_ru_list = [l.strip() for l in dbox_ru_raw.split("\n")  if l.strip()]
cnode_ru_list= [l.strip() for l in cnode_ru_raw.split("\n") if l.strip()]

sw1_ru       = st.session_state.get("sw1_ru",      "")
sw2_ru       = st.session_state.get("sw2_ru",      "")

# Switch model for suffix
sw_model_current = st.session_state.get(
    "tab5_sw_model", list(HARDWARE_PROFILES.keys())[0]
)
vendor_suffix = get_sw_suffix(sw_model_current)


def _build_sw_name(sw_num, ru_val, vendor_sfx, gpu=False, spine=False):
    parts = [pfx, vendor_sfx]
    if include_ru and ru_val:
        parts.append(f"U{ru_val}")
    if spine:
        parts.append(f"SPINE-SW{sw_num}")
    else:
        parts.append(f"SW{sw_num}")
    name = "-".join(parts)
    if gpu:
        name += "-GPU"
    return name


full_sw_a = _build_sw_name(1, sw1_ru, vendor_suffix)
full_sw_b = _build_sw_name(2, sw2_ru, vendor_suffix)


# ============================================================
# MAIN HEADER
# ============================================================
st.title("⚡ VAST SE Installation Toolkit")
if se_name and customer:
    st.markdown(
        f"**SE:** {se_name} &nbsp;|&nbsp; "
        f"**Customer:** {customer} &nbsp;|&nbsp; "
        f"**Cluster:** {cluster_name} &nbsp;|&nbsp; "
        f"**Date:** {install_date.strftime('%d %B %Y')}"
    )


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📋 Project Details",
    "📄 Confluence Install Plan",
    "✅ Validation & Pre-Flight",
    "📋 Installation Procedure",
    "🔌 Internal Switch — Southbound",
    "🖥️ Data Switch — Northbound",
    "🚀 Coming Soon"
])
#=============================================================
# ============================================================
# TAB 1 — PROJECT DETAILS (new)
# ============================================================
with tab1:
    st.subheader("📋 Project Details")
    st.caption(
        "Complete all sections before generating configs or the install plan. "
        "Fields marked ⚠️ are required."
    )

    # ── Project Save / Load ──────────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 Project")

    if st.session_state.get("_save_msg"):
        st.success(st.session_state.pop("_save_msg"))

    if not _DB_AVAILABLE:
        st.warning(
            "⚠️ Database unavailable — projects cannot be saved or loaded. "
            "Check that `db.py` is present and `/app/data/` is writable."
        )
    else:
        # Auto-backup on first render each session
        if not st.session_state.get("_auto_backup_done"):
            _db.auto_backup_if_stale()
            st.session_state["_auto_backup_done"] = True

        proj_id = st.session_state.get("_db_project_id")
        proj_id_label = f"Project #{proj_id}" if proj_id else "Unsaved project"

        db_col1, db_col2, db_col3 = st.columns([1, 1, 1])

        with db_col1:
            if st.button("🆕 New Project", use_container_width=True):
                st.session_state["_pending_clear"] = True
                st.rerun()

        with db_col2:
            save_milestone = st.selectbox(
                "Milestone",
                options=[
                    "Initial / Sizing",
                    "Pre-Install",
                    "Post-Install / Config",
                    "Other",
                ],
                key="_save_milestone",
                label_visibility="collapsed"
            )
            if st.button("💾 Save Project", use_container_width=True):
                try:
                    _save_data = {k: v for k, v in st.session_state.items()
                                  if _is_saveable(k)}
                    _save_data["_db_project_id"] = st.session_state.get("_db_project_id")
                    pid = _db.save_project(
                        _save_data,
                        label=save_milestone
                    )
                    st.session_state["_db_project_id"] = pid
                    st.session_state["_save_msg"] = f"✅ Saved — {save_milestone}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Save failed: {e}")

        with db_col3:
            try:
                projects = _db.list_projects()
            except Exception:
                projects = []

            if not projects:
                st.info("No saved projects yet.")
            else:
                proj_options = {
                    f"#{p['id']} — {p['name']} ({p['updated_at'][:10]})": p['id']
                    for p in projects
                }
                selected_label = st.selectbox(
                    "Load project",
                    options=list(proj_options.keys()),
                    key="_load_select",
                    label_visibility="collapsed"
                )
                if st.button("📂 Load", use_container_width=True):
                    try:
                        pid = proj_options[selected_label]
                        state = _db.load_project(pid)
                        st.session_state["_pending_load"] = state
                        st.rerun()
                    except Exception as e:
                        st.error(f"Load failed: {e}")

        # Version history expander
        if proj_id:
            with st.expander(f"🕓 Version history — {proj_id_label}", expanded=False):
                try:
                    versions = _db.get_project_versions(proj_id)
                    if not versions:
                        st.caption("No versions saved yet.")
                    else:
                        for v in versions:
                            v_label = v['label'] or "—"
                            v_col1, v_col2 = st.columns([3, 1])
                            with v_col1:
                                st.caption(
                                    f"v{v['version_num']} · "
                                    f"{v['saved_at'][:16].replace('T', ' ')} · "
                                    f"{v_label}"
                                )
                            with v_col2:
                                if st.button(
                                    "Restore",
                                    key=f"_restore_v{v['id']}",
                                    use_container_width=True
                                ):
                                    try:
                                        state = _db.load_version(v['id'])
                                        st.session_state["_pending_load"] = state
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Restore failed: {e}")
                except Exception as e:
                    st.error(f"Could not load version history: {e}")

        st.caption(f"Current: {proj_id_label}")

    # ── Cluster Inventory ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📦 Cluster Inventory")

    inv_col1, inv_col2 = st.columns(2)
    with inv_col1:
        proj_num_dboxes = st.slider(
            "Number of DBoxes", min_value=1, max_value=14,
            key="proj_num_dboxes"
        )
    with inv_col2:
        proj_num_cnodes = st.slider(
            "Number of CNodes", min_value=1, max_value=28,
            key="proj_num_cnodes"
        )

    # ── Topology ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🌐 Deployment Topology")

    proj_topology = st.radio(
        "Select topology",
        options=["Leaf Pair", "Spine-Leaf"],
        horizontal=True,
        key="proj_topology"
    )
    if proj_topology == "Spine-Leaf":
        st.info(
            "**Spine-Leaf mode** — Leaf switches connect to nodes. "
            "Spine switches provide the uplink fabric. "
            "Both leaf and spine run as MLAG pairs. "
            "Spine must be same vendor and equal or greater speed than leaf."
        )

    # ── Opportunity Links ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔗 Links & Identity")

    link_col1, link_col2 = st.columns(2)
    with link_col1:
        proj_sfdc    = st.text_input("SFDC Opportunity URL",
                         placeholder="https://vastdata.lightning.force.com/…",
                         key="proj_sfdc")
        proj_ticket  = st.text_input("Install Ticket URL",
                         placeholder="https://vastdata.lightning.force.com/…",
                         key="proj_ticket")
        proj_slack   = st.text_input("Slack Internal Channel",
                         placeholder="#cust-acme-corp",
                         key="proj_slack")
        proj_psnt    = st.text_input("System PSNT",
                         placeholder="e.g. VARW255117024",
                         key="proj_psnt")
        proj_license = st.text_input("License Key",
                         placeholder="e.g. LS-003197",
                         key="proj_license")
    with link_col2:
        proj_lucid    = st.text_input("Lucidchart URL",
                          placeholder="https://lucid.app/lucidchart/…",
                          key="proj_lucid")
        proj_survey   = st.text_input("Site Survey URL",
                          placeholder="https://docs.google.com/spreadsheets/…",
                          key="proj_survey")
        proj_peer_rev = st.text_input("PreSales Peer Reviewer",
                          placeholder="e.g. Eric ElMasry",
                          key="proj_peer_rev")
        proj_guide    = st.text_input("VAST Install Guide URL",
                          placeholder="https://kb.vastdata.com/docs/…",
                          key="proj_install_guide")

    # ── Software Versions ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 Software Versions")
    st.caption("Find latest approved releases on the [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/FIELD).")

    ver_col1, ver_col2 = st.columns(2)
    with ver_col1:
        proj_release  = st.text_input("VAST Release",
                          placeholder="e.g. 5.4.1-sp4",
                          key="proj_vast_release")
        proj_os_ver   = st.text_input("VastOS Version",
                          placeholder="e.g. 12.15.15-2123585",
                          key="proj_os_version")
    with ver_col2:
        proj_bundle   = st.text_input("Bundle Version",
                          placeholder="e.g. release-5.4.1-sp4-2248419",
                          key="proj_bundle")
        proj_phison   = st.toggle("PHISON drives present",
                          value=False, key="proj_phison")
        if proj_phison:
            st.warning("⚠️ PHISON drives require FW update check before install.")

    # ── Hardware Details ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🖥️ Hardware Details")

    hw_col1, hw_col2 = st.columns(2)
    with hw_col1:
        proj_dbox_type  = st.text_input("DBox Type",
                            placeholder="e.g. 338TB Ceres (DF-3015)",
                            key="proj_dbox_type")
        proj_cbox_type  = st.text_input("CNode Type",
                            placeholder="e.g. GEN6 Turin Dell Dual NIC CX7",
                            key="proj_cbox_type")
        proj_dual_nic   = st.toggle("CNodes have Dual NIC",
                            value=False, key="proj_dual_nic")
    with hw_col2:
        proj_ipmi       = st.selectbox("IPMI Configuration",
                            options=["Outband (Cat6)", "B2B (Back-to-Back)"],
                            key="proj_ipmi")
        proj_second_nic = st.selectbox("Second NIC Use (Dual NIC only)",
                            options=["N/A",
                                     "Split Ethernet (GPU/Client traffic)",
                                     "Northband mgmt bond"],
                            key="proj_second_nic")
        proj_nb_mtu     = st.text_input("Northbound MTU (if second NIC)",
                            value="9000", key="proj_nb_mtu")
        proj_gpu_svrs   = st.text_input("GPU Servers (count + type)",
                            placeholder="e.g. 8x Dell R760xa (4x L40S each)",
                            key="proj_gpu_servers")

    # ── Cluster Configuration ────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚙️ Cluster Configuration")

    cfg_col1, cfg_col2 = st.columns(2)
    with cfg_col1:
        proj_dbox_ha    = st.toggle("DBox HA enabled",
                            value=False, key="proj_dbox_ha")
        proj_encryption = st.toggle("Encryption at Rest",
                            value=False, key="proj_encryption")
    with cfg_col2:
        proj_similarity = st.selectbox("Similarity",
                            options=["Yes w/ Adaptive Chunking (Default)", "No"],
                            key="proj_similarity")
        proj_ip_conflict= st.toggle("Internal IP range conflict with customer",
                            value=False, key="proj_ip_conflict")
        if proj_ip_conflict:
            proj_ip_notes = st.text_input("Alternative IP range",
                               placeholder="e.g. 10.10.128.0/18",
                               key="proj_ip_notes")

    # ── Site Notes ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📝 Site Notes")

    proj_site_notes = st.text_area(
        "Site Overview / Important Notes",
        placeholder=(
            "e.g. Cluster installed in shipping container DC.\n"
            "GPUaaS POC. 8x GPU servers with 4x L40S each.\n"
            "Network design: NVMe Ethernet for data and client traffic."
        ),
        key="proj_site_notes",
        height=150
    )

    # ── Completeness indicator ───────────────────────────────
    st.markdown("---")
    required = {
        "Customer Name":    st.session_state.get("customer",          ""),
        "Cluster Name":     st.session_state.get("cluster_name",      ""),
        "SE Name":          st.session_state.get("se_name",           ""),
        "System PSNT":      st.session_state.get("proj_psnt",         ""),
        "License Key":      st.session_state.get("proj_license",      ""),
        "VAST Release":     st.session_state.get("proj_vast_release", ""),
        "VastOS Version":   st.session_state.get("proj_os_version",   ""),
        "Bundle Version":   st.session_state.get("proj_bundle",       ""),
        "SFDC URL":         st.session_state.get("proj_sfdc",         ""),
        "DBox Type":        st.session_state.get("proj_dbox_type",    ""),
        "CNode Type":       st.session_state.get("proj_cbox_type",    ""),
        "NTP Server":       st.session_state.get("tab5_ntp",          ""),
        "Site Notes":       st.session_state.get("proj_site_notes",   ""),
    }
    missing = [k for k, v in required.items() if not v]

    if missing:
        st.warning(
            f"⚠️ **{len(missing)} required field(s) not yet completed:**\n\n"
            + "\n".join(f"- {m}" for m in missing)
        )
    else:
        st.success("✅ Project Details complete — ready to generate configs and install plan.")


# TAB 5 — INTERNAL SWITCH — SOUTHBOUND
# ============================================================
with tab5:
    st.subheader("Internal Storage Fabric — Leaf Pair Configuration")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("#### Switch Selection")
        sw_model = st.selectbox(
            "Switch Model",
            options=list(HARDWARE_PROFILES.keys()),
            key="tab5_sw_model"
        )
        profile = HARDWARE_PROFILES[sw_model]

        st.info(
            f"**Vendor:** {profile['vendor'].capitalize()}  \n"
            f"**OS:** {'Cumulus NV' if profile['os'] == 'cumulus' else 'Arista EOS'}  \n"
            f"**Ports:** {profile['total_ports']}  \n"
            f"**Speed:** {profile['native_speed']}  \n"
            f"**Form Factor:** {profile['form_factor']}  \n"
            f"**MTU:** {profile['mtu']}  \n"
            f"**Notes:** {profile['notes']}"
        )

        st.markdown("#### Port Reservation")
        dnode_start = st.number_input(
            "DNode start port", min_value=1,
            max_value=profile["total_ports"], value=1,
            key="tab5_dnode_start"
        )
        cnode_start = st.number_input(
            "CNode start port", min_value=1,
            max_value=profile["total_ports"],
            value=15 if profile["total_ports"] == 32 else 29,
            key="tab5_cnode_start"
        )

        st.markdown("#### Switch Networking")
        vlan_id = st.number_input(
            "Storage VLAN ID", min_value=1, max_value=4094,
            value=100, key="tab5_vlan"
        )
        sw_a_ip = st.text_input(
            "Switch A MGMT IP/mask", value="192.168.1.1/24",
            key="tab5_sw_a_ip"
        )
        sw_b_ip = st.text_input(
            "Switch B MGMT IP/mask", value="192.168.1.2/24",
            key="tab5_sw_b_ip"
        )
        mgmt_gw = st.text_input(
            "MGMT Gateway", value="192.168.1.254", key="tab5_gw"
        )
        ntp_srv = st.text_input(
            "NTP Server", value="",
            placeholder="Enter customer NTP server IP",
            key="tab5_ntp"
        )

        st.markdown("#### ISL / Uplink Ports")
        isl_ports_input = st.text_input(
            "ISL Ports (comma separated)",
            value=",".join([f"swp{p}" for p in profile["default_isl"]]),
            key="tab5_isl"
        )
        uplink_ports_input = st.text_input(
            "Uplink Ports (comma separated)",
            value=",".join([f"swp{p}" for p in profile["default_uplink"]]),
            key="tab5_uplink"
        )
        isl_short = st.toggle(
            "ISL cable run is ≤1m (use DAC)",
            value=False, key="tab5_isl_short"
        )

    with col_right:

        errors, warnings = validate_port_counts(
            num_dboxes, num_cnodes,
            dnode_start, cnode_start, profile
        )

        if errors:
            for e in errors:
                st.error(e)

        for w in warnings:
            st.warning(w)

        if not ntp_srv:
            st.warning(
                "⚠️ NTP Server is empty. "
                "Confirm the customer NTP IP before applying config."
            )

        st.markdown("#### 📦 Cable Requirements")
        render_cable_summary(profile, isl_short)

        st.markdown("#### 🗺️ Port Mapping / Cabling Guide")
        table_map = get_port_mappings(
            "A", num_dboxes, num_cnodes, dnode_start, cnode_start,
            pfx=pfx, dbox_label=dbox_label,
            dnode_label=dnode_label, cnode_label=cnode_label
        )

        isl_list    = [p.strip() for p in isl_ports_input.split(",")]
        uplink_list = [p.strip() for p in uplink_ports_input.split(",") if p.strip()]

        table_rows = []
        for item in table_map:
            table_rows.append({
                "Switch Port (A)": item["swp"] if profile["os"] == "cumulus"
                                   else item["eth"],
                "Switch Port (B)": item["swp"] if profile["os"] == "cumulus"
                                   else item["eth"],
                "Device":          item["desc"].replace("-P1", ""),
                "NIC":             "BF-3 200GbE" if item["type"] == "dnode"
                                   else "CX7 200GbE",
                "Cable":           profile["node_cable"]["spec"],
                "Supplied By":     profile["node_cable"]["supplier"]
            })

        for p in isl_list:
            isl_cable = (
                profile["isl_cable_short"] if isl_short
                else profile["isl_cable_long"]
            )
            table_rows.append({
                "Switch Port (A)": p,
                "Switch Port (B)": p,
                "Device":          "ISL / Peerlink",
                "NIC":             "—",
                "Cable":           isl_cable["spec"],
                "Supplied By":     isl_cable["supplier"]
            })

        for p in uplink_list:
            table_rows.append({
                "Switch Port (A)": p,
                "Switch Port (B)": p,
                "Device":          "Uplink to Customer Core",
                "NIC":             "—",
                "Cable":           profile["spine_cable"]["spec"],
                "Supplied By":     profile["spine_cable"]["supplier"]
            })

        st.dataframe(table_rows, use_container_width=True)

        st.markdown("#### ⚙️ Generated Switch Configurations")

        env       = Environment(loader=FileSystemLoader("templates"))
        tmpl_file = (
            "cumulus_nv.j2" if profile["os"] == "cumulus"
            else "arista_eos.j2"
        )

        try:
            template = env.get_template(tmpl_file)
        except Exception:
            st.error(
                f"Template `{tmpl_file}` not found in /templates. "
                "Please create it to generate configs."
            )
            template = None

        if template:
            cfg_col_a, cfg_col_b = st.columns(2)

            for i, side in enumerate(["A", "B"]):
                port_map = get_port_mappings(
                    side, num_dboxes, num_cnodes,
                    dnode_start, cnode_start,
                    pfx=pfx, dbox_label=dbox_label,
                    dnode_label=dnode_label, cnode_label=cnode_label
                )
                context = {
                    "se_name":       se_name or "—",
                    "customer":      customer or "—",
                    "cluster_name":  cluster_name or "—",
                    "install_date":  str(install_date),
                    "hostname":      full_sw_a if side == "A" else full_sw_b,
                    "mgmt_ip":       sw_a_ip if side == "A" else sw_b_ip,
                    "mgmt_gw":       mgmt_gw,
                    "ntp_server":    ntp_srv or mgmt_gw,
                    "vlan_id":       vlan_id,
                    "mtu":           profile["mtu"],
                    "isl_ports":     isl_list,
                    "uplink_ports":  uplink_list,
                    "clag_id":       100,
                    "peer_ip":       sw_b_ip.split("/")[0] if side == "A"
                                     else sw_a_ip.split("/")[0],
                    "port_map":      port_map,
                    "clag_priority": 1000 if side == "A" else 2000,
                }
                config_text = template.render(context).replace('\r\n', '\n').replace('\r', '\n')

                with (cfg_col_a if side == "A" else cfg_col_b):
                    st.markdown(
                        f"**Switch {side}** "
                        f"({'Primary' if side == 'A' else 'Secondary'})"
                    )
                    st.code(config_text, language="bash")
                    st.download_button(
                        label=f"💾 Download Switch {side} Config",
                        data=config_text,
                        file_name=(
                            f"{pfx}_SW{side}_"
                            f"{profile['vendor'].upper()}_"
                            f"{date.today().isoformat()}.txt"
                        ),
                        mime="text/plain",
                        key=f"tab5_dl_{side}"
                    )

    # ── SPINE-LEAF SECTION ───────────────────────────────────
    if topology == "Spine-Leaf":
        st.markdown("---")
        st.markdown("### 🔺 Spine Switch Configuration")
        st.caption(
            "Spine switches provide the uplink fabric between leaf pairs "
            "and the customer core. Always deployed as a pair. "
            "Must be same vendor as leaf and equal or greater speed."
        )

        spine_col_left, spine_col_right = st.columns([1, 2])

        with spine_col_left:
            st.markdown("#### Spine Switch Selection")

            leaf_speed_rank = SPEED_RANK.get(profile["native_speed"], 1)
            leaf_vendor     = profile["vendor"]

            valid_spine_models = [
                m for m, p in HARDWARE_PROFILES.items()
                if SPEED_RANK.get(p["native_speed"], 1) >= leaf_speed_rank
                and p["vendor"] == leaf_vendor
            ]

            spine_model   = st.selectbox(
                "Spine Switch Model",
                options=valid_spine_models,
                key="spine_sw_model"
            )
            spine_profile = HARDWARE_PROFILES[spine_model]

            st.info(
                f"**Vendor:** {spine_profile['vendor'].capitalize()}  \n"
                f"**OS:** {'Cumulus NV' if spine_profile['os'] == 'cumulus' else 'Arista EOS'}  \n"
                f"**Ports:** {spine_profile['total_ports']}  \n"
                f"**Speed:** {spine_profile['native_speed']}  \n"
                f"**Form Factor:** {spine_profile['form_factor']}  \n"
                f"**MTU:** {spine_profile['mtu']}  \n"
                f"**Notes:** {spine_profile['notes']}"
            )

            st.markdown("#### Spine Port Reservation")
            num_leaf_pairs = st.number_input(
                "Number of Leaf Pairs",
                min_value=1, max_value=16, value=1,
                key="spine_num_leaf_pairs"
            )
            spine_downlink_start = st.number_input(
                "Downlink start port (to leaf switches)",
                min_value=1,
                max_value=spine_profile["total_ports"],
                value=1,
                key="spine_downlink_start"
            )
            spine_isl_ports_input = st.text_input(
                "Spine ISL ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in spine_profile["default_isl"]]
                ),
                key="spine_isl_ports"
            )
            spine_uplink_ports_input = st.text_input(
                "Uplink ports to customer core (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in spine_profile["default_uplink"]]
                ),
                key="spine_uplink_ports"
            )
            spine_isl_short = st.toggle(
                "Spine ISL cable run ≤1m (use DAC)",
                value=False,
                key="spine_isl_short"
            )

            st.markdown("#### Spine Networking")
            spine_a_ip = st.text_input(
                "Spine A MGMT IP/mask",
                value="192.168.3.1/24", key="spine_a_ip"
            )
            spine_b_ip = st.text_input(
                "Spine B MGMT IP/mask",
                value="192.168.3.2/24", key="spine_b_ip"
            )
            spine_mgmt_gw = st.text_input(
                "Spine MGMT Gateway",
                value="192.168.3.254", key="spine_mgmt_gw"
            )
            spine_ntp = st.text_input(
                "Spine NTP Server", value="",
                placeholder="Enter customer NTP server IP",
                key="spine_ntp"
            )

        with spine_col_right:

            if not spine_ntp:
                st.warning(
                    "⚠️ Spine NTP Server is empty. "
                    "Confirm the customer NTP IP before applying config."
                )

            if spine_profile["customer_cables"]:
                st.error(
                    f"⚠️ **{spine_model} requires customer-supplied "
                    f"400G cables.** Confirm all spine cables are "
                    f"on-site before install day."
                )

            spine_isl_cable = (
                spine_profile["isl_cable_short"] if spine_isl_short
                else spine_profile["isl_cable_long"]
            )

            st.markdown("#### 📦 Spine Cable Requirements")
            st.table([
                {
                    "Connection":  "Spine → Leaf downlinks",
                    "Cable":       spine_profile["spine_cable"]["spec"],
                    "Supplied By": spine_profile["spine_cable"]["supplier"]
                },
                {
                    "Connection":  f"Spine ISL ({'≤1m' if spine_isl_short else '>1m'})",
                    "Cable":       spine_isl_cable["spec"],
                    "Supplied By": spine_isl_cable["supplier"]
                },
                {
                    "Connection":  "Spine → Customer core uplink",
                    "Cable":       spine_profile["spine_cable"]["spec"],
                    "Supplied By": spine_profile["spine_cable"]["supplier"]
                },
            ])

            st.markdown("#### 🗺️ Spine Port Mapping")

            spine_isl_list    = [
                p.strip() for p in spine_isl_ports_input.split(",")
                if p.strip()
            ]
            spine_uplink_list = [
                p.strip() for p in spine_uplink_ports_input.split(",")
                if p.strip()
            ]

            spine_vendor_suffix = get_sw_suffix(spine_model)
            spine_sw_a_name     = f"{pfx}-{spine_vendor_suffix}-SPINE-SW1"
            spine_sw_b_name     = f"{pfx}-{spine_vendor_suffix}-SPINE-SW2"

            spine_table_rows = []

            for lp in range(1, num_leaf_pairs + 1):
                port_a = spine_downlink_start + (lp - 1) * 2
                port_b = spine_downlink_start + (lp - 1) * 2 + 1
                p_a = (f"swp{port_a}" if spine_profile["os"] == "cumulus"
                       else f"Ethernet{port_a}")
                p_b = (f"swp{port_b}" if spine_profile["os"] == "cumulus"
                       else f"Ethernet{port_b}")
                spine_table_rows.append({
                    "Spine-A Port": p_a,
                    "Spine-B Port": p_b,
                    "Connects To":  f"{pfx}-Leaf-Pair-{lp} (Leaf-A / Leaf-B)",
                    "Cable":        spine_profile["spine_cable"]["spec"],
                    "Supplied By":  spine_profile["spine_cable"]["supplier"]
                })

            for p in spine_isl_list:
                spine_table_rows.append({
                    "Spine-A Port": p,
                    "Spine-B Port": p,
                    "Connects To":  "Spine ISL / Peerlink",
                    "Cable":        spine_isl_cable["spec"],
                    "Supplied By":  spine_isl_cable["supplier"]
                })

            for p in spine_uplink_list:
                spine_table_rows.append({
                    "Spine-A Port": p,
                    "Spine-B Port": p,
                    "Connects To":  "Customer Core",
                    "Cable":        spine_profile["spine_cable"]["spec"],
                    "Supplied By":  spine_profile["spine_cable"]["supplier"]
                })

            st.dataframe(spine_table_rows, use_container_width=True)

        # Spine configs — full width outside columns
        st.markdown("#### ⚙️ Generated Spine Configurations")

        spine_env       = Environment(loader=FileSystemLoader("templates"))
        spine_tmpl_file = (
            "cumulus_spine.j2" if spine_profile["os"] == "cumulus"
            else "arista_spine.j2"
        )

        try:
            spine_template = spine_env.get_template(spine_tmpl_file)
        except Exception:
            st.error(
                f"Template `{spine_tmpl_file}` not found in /templates. "
                "Please create it and rebuild."
            )
            spine_template = None

        if spine_template:
            spine_cfg_col_a, spine_cfg_col_b = st.columns(2)

            for i, side in enumerate(["A", "B"]):
                spine_port_map = []
                for lp in range(1, num_leaf_pairs + 1):
                    port_num = (
                        spine_downlink_start
                        + (lp - 1) * 2
                        + (0 if side == "A" else 1)
                    )
                    spine_port_map.append({
                        "port": port_num,
                        "swp":  f"swp{port_num}",
                        "eth":  f"Ethernet{port_num}",
                        "desc": (
                            f"Downlink-to-{pfx}-Leaf-Pair-{lp}-"
                            f"{'Leaf-A' if side == 'A' else 'Leaf-B'}"
                        ),
                        "type": "downlink"
                    })

                spine_context = {
                    "se_name":       se_name or "—",
                    "customer":      customer or "—",
                    "cluster_name":  cluster_name or "—",
                    "install_date":  str(install_date),
                    "hostname":      (
                        spine_sw_a_name if side == "A"
                        else spine_sw_b_name
                    ),
                    "mgmt_ip":       (
                        spine_a_ip if side == "A" else spine_b_ip
                    ),
                    "mgmt_gw":       spine_mgmt_gw,
                    "ntp_server":    spine_ntp or spine_mgmt_gw,
                    "vlan_id":       vlan_id,
                    "mtu":           spine_profile["mtu"],
                    "isl_ports":     spine_isl_list,
                    "uplink_ports":  spine_uplink_list,
                    "clag_id":       300,
                    "peer_ip":       (
                        spine_b_ip.split("/")[0] if side == "A"
                        else spine_a_ip.split("/")[0]
                    ),
                    "port_map":      spine_port_map,
                    "clag_priority": 1000 if side == "A" else 2000,
                }

                spine_config_text = spine_template.render(spine_context).replace('\r\n', '\n').replace('\r', '\n')

                with (
                    spine_cfg_col_a if side == "A"
                    else spine_cfg_col_b
                ):
                    st.markdown(
                        f"**Spine {side}** "
                        f"({'Primary' if side == 'A' else 'Secondary'})"
                    )
                    st.code(spine_config_text, language="bash")
                    st.download_button(
                        label=f"💾 Download Spine {side} Config",
                        data=spine_config_text,
                        file_name=(
                            f"{pfx}_SPINE_{side}_"
                            f"{spine_profile['vendor'].upper()}_"
                            f"{date.today().isoformat()}.txt"
                        ),
                        mime="text/plain",
                        key=f"spine_dl_{side}"
                    )


# ============================================================
# TAB 6 — DATA SWITCH — NORTHBOUND
# ============================================================
with tab6:
    st.subheader("GPU / Data Network Switch — Leaf Pair Configuration")

    gpu_enabled = st.toggle(
        "Enable GPU / Data Network Switch Configuration",
        value=False, key="tab6_enabled"
    )

    if not gpu_enabled:
        st.info(
            "Enable the toggle above to configure an additional "
            "leaf pair for CNode to GPU / Data Network connectivity."
        )
    else:
        col_left2, col_right2 = st.columns([1, 2])

        with col_left2:
            st.markdown("#### Switch Selection")
            sw_model2 = st.selectbox(
                "Switch Model",
                options=list(HARDWARE_PROFILES.keys()),
                key="tab6_sw_model"
            )
            profile2 = HARDWARE_PROFILES[sw_model2]

            st.info(
                f"**Vendor:** {profile2['vendor'].capitalize()}  \n"
                f"**OS:** {'Cumulus NV' if profile2['os'] == 'cumulus' else 'Arista EOS'}  \n"
                f"**Ports:** {profile2['total_ports']}  \n"
                f"**Speed:** {profile2['native_speed']}  \n"
                f"**Form Factor:** {profile2['form_factor']}  \n"
                f"**MTU:** {profile2['mtu']}  \n"
                f"**Notes:** {profile2['notes']}"
            )

            st.markdown("#### Port Reservation")
            cnode_start2 = st.number_input(
                "CNode start port", min_value=1,
                max_value=profile2["total_ports"], value=1,
                key="tab6_cnode_start"
            )
            gpu_start2 = st.number_input(
                "GPU Server start port", min_value=1,
                max_value=profile2["total_ports"],
                value=15 if profile2["total_ports"] == 32 else 29,
                key="tab6_gpu_start"
            )
            num_gpu_servers = st.slider(
                "Number of GPU Servers",
                min_value=1, max_value=profile2["max_node_ports"],
                value=4, key="tab6_gpu_count"
            )
            gpu_nic_speed = st.selectbox(
                "GPU Server NIC Speed",
                options=["200GbE", "100GbE", "400GbE"],
                key="tab6_gpu_nic"
            )

            st.markdown("#### Switch Networking")
            vlan_id2  = st.number_input(
                "GPU Network VLAN ID", min_value=1, max_value=4094,
                value=200, key="tab6_vlan"
            )
            sw_a_ip2  = st.text_input(
                "Switch A MGMT IP/mask", value="192.168.2.1/24",
                key="tab6_sw_a_ip"
            )
            sw_b_ip2  = st.text_input(
                "Switch B MGMT IP/mask", value="192.168.2.2/24",
                key="tab6_sw_b_ip"
            )
            mgmt_gw2  = st.text_input(
                "MGMT Gateway", value="192.168.2.254", key="tab6_gw"
            )
            ntp_srv2  = st.text_input(
                "NTP Server", value="",
                placeholder="Enter customer NTP server IP",
                key="tab6_ntp"
            )

            st.markdown("#### ISL / Uplink Ports")
            isl_ports_input2 = st.text_input(
                "ISL Ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in profile2["default_isl"]]
                ),
                key="tab6_isl"
            )
            uplink_ports_input2 = st.text_input(
                "Uplink Ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in profile2["default_uplink"]]
                ),
                key="tab6_uplink"
            )
            isl_short2 = st.toggle(
                "ISL cable run is ≤1m (use DAC)",
                value=False, key="tab6_isl_short"
            )

        with col_right2:

            if gpu_nic_speed == "100GbE" and profile2["native_speed"] in ["200GbE", "400GbE"]:
                st.warning(
                    f"⚠️ GPU Server NIC speed ({gpu_nic_speed}) is lower "
                    f"than switch native speed ({profile2['native_speed']}). "
                    f"Breakout or speed-matching cables will be required."
                )
            if gpu_nic_speed == "200GbE" and profile2["native_speed"] == "400GbE":
                st.error(
                    f"⚠️ GPU Server NIC ({gpu_nic_speed}) requires "
                    f"400G→2x200G AOC breakout cables on this switch. "
                    f"Customer/Partner must supply these cables."
                )
            if gpu_nic_speed == "400GbE" and profile2["native_speed"] == "200GbE":
                st.error(
                    f"❌ GPU Server NIC ({gpu_nic_speed}) exceeds "
                    f"switch native speed ({profile2['native_speed']}). "
                    f"Incompatible — select a higher speed switch."
                )

            # GPU switch validation — ranges can be in either order
            gpu_end2   = gpu_start2 + num_gpu_servers - 1
            cnode_end2 = cnode_start2 + num_cnodes - 1
            isl_start2 = min(profile2["default_isl"])

            errors2   = []
            warnings2 = []

            # Check the two ranges don't overlap each other
            if not (gpu_end2 < cnode_start2 or cnode_end2 < gpu_start2):
                errors2.append(
                    f"❌ GPU Server ports (swp{gpu_start2}–swp{gpu_end2}) "
                    f"overlap with CNode ports (swp{cnode_start2}–swp{cnode_end2}). "
                    f"Adjust port ranges so they don't collide."
                )

            # Check neither range runs into ISL
            if gpu_end2 >= isl_start2:
                errors2.append(
                    f"❌ GPU Server ports (swp{gpu_start2}–swp{gpu_end2}) "
                    f"overflow into ISL range (swp{isl_start2}+). "
                    f"Reduce GPU server count or adjust start port."
                )
            if cnode_end2 >= isl_start2:
                errors2.append(
                    f"❌ CNode ports (swp{cnode_start2}–swp{cnode_end2}) "
                    f"overflow into ISL range (swp{isl_start2}+). "
                    f"Reduce CNode count or adjust start port."
                )

            total_needed2 = num_gpu_servers + num_cnodes
            if total_needed2 > profile2["max_node_ports"] * 0.85:
                warnings2.append(
                    f"⚠️ Using {total_needed2} of "
                    f"{profile2['max_node_ports']} available ports "
                    f"({int(total_needed2/profile2['max_node_ports']*100)}% capacity)."
                )

            if errors2:
                for e in errors2:
                    st.error(e)
                
            for w in warnings2:
                st.warning(w)  

            if not ntp_srv2:
                st.warning(
                    "⚠️ NTP Server is empty. "
                    "Confirm the customer NTP IP before applying config."
                )

            st.markdown("#### 📦 Cable Requirements")
            render_cable_summary(profile2, isl_short2)

            st.markdown("#### 🗺️ Port Mapping / Cabling Guide")

            isl_list2    = [p.strip() for p in isl_ports_input2.split(",")]
            uplink_list2 = [p.strip() for p in uplink_ports_input2.split(",") if p.strip()]

            table_rows2 = []

            for i in range(1, num_cnodes + 1):
                swp_num  = cnode_start2 + (i - 1)
                port_str = (f"swp{swp_num}" if profile2["os"] == "cumulus"
                            else f"Ethernet{swp_num}")
                table_rows2.append({
                    "Switch Port (A)": port_str,
                    "Switch Port (B)": port_str,
                    "Device":          f"{pfx}-{cnode_label}-{i}",
                    "NIC":             "CX7 200GbE",
                    "Cable":           profile2["node_cable"]["spec"],
                    "Supplied By":     profile2["node_cable"]["supplier"]
                })

            for i in range(1, num_gpu_servers + 1):
                swp_num  = gpu_start2 + (i - 1)
                port_str = (f"swp{swp_num}" if profile2["os"] == "cumulus"
                            else f"Ethernet{swp_num}")
                if gpu_nic_speed == "200GbE" and profile2["native_speed"] == "400GbE":
                    gpu_cable = "400G→2x200G AOC breakout ⚠️ Customer"
                elif gpu_nic_speed == "100GbE":
                    gpu_cable = "Breakout AOC ⚠️ Check compatibility"
                else:
                    gpu_cable = profile2["node_cable"]["spec"]

                table_rows2.append({
                    "Switch Port (A)": port_str,
                    "Switch Port (B)": port_str,
                    "Device":          f"{pfx}-GPU-SERVER-{i}",
                    "NIC":             gpu_nic_speed,
                    "Cable":           gpu_cable,
                    "Supplied By":     (
                        "CUSTOMER"
                        if profile2["customer_cables"]
                        or gpu_nic_speed != profile2["native_speed"]
                        else "VAST"
                    )
                })

            for p in isl_list2:
                isl_cable2 = (
                    profile2["isl_cable_short"] if isl_short2
                    else profile2["isl_cable_long"]
                )
                table_rows2.append({
                    "Switch Port (A)": p,
                    "Switch Port (B)": p,
                    "Device":          "ISL / Peerlink",
                    "NIC":             "—",
                    "Cable":           isl_cable2["spec"],
                    "Supplied By":     isl_cable2["supplier"]
                })

            for p in uplink_list2:
                table_rows2.append({
                    "Switch Port (A)": p,
                    "Switch Port (B)": p,
                    "Device":          "Uplink to Customer Core",
                    "NIC":             "—",
                    "Cable":           profile2["spine_cable"]["spec"],
                    "Supplied By":     profile2["spine_cable"]["supplier"]
                })

            st.dataframe(table_rows2, use_container_width=True)

            st.markdown("#### ⚙️ Generated Switch Configurations")

            env2       = Environment(loader=FileSystemLoader("templates"))
            tmpl_file2 = (
                "cumulus_nv.j2" if profile2["os"] == "cumulus"
                else "arista_eos.j2"
            )

            try:
                template2 = env2.get_template(tmpl_file2)
            except Exception:
                st.error(
                    f"Template `{tmpl_file2}` not found. "
                    "Please create it to generate configs."
                )
                template2 = None

            if template2:
                cfg_col_a2, cfg_col_b2 = st.columns(2)

                for i, side in enumerate(["A", "B"]):
                    port_side = "1" if side == "A" else "2"
                    port_map2 = []

                    for c in range(1, num_cnodes + 1):
                        swp_num = cnode_start2 + (c - 1)
                        port_map2.append({
                            "port": swp_num,
                            "swp":  f"swp{swp_num}",
                            "eth":  f"Ethernet{swp_num}",
                            "desc": f"{pfx}-{cnode_label}-{c}-GPU-P{port_side}",
                            "type": "cnode"
                        })

                    for g in range(1, num_gpu_servers + 1):
                        swp_num = gpu_start2 + (g - 1)
                        port_map2.append({
                            "port": swp_num,
                            "swp":  f"swp{swp_num}",
                            "eth":  f"Ethernet{swp_num}",
                            "desc": f"{pfx}-GPU-SERVER-{g}-P{port_side}",
                            "type": "gpu"
                        })

                    context2 = {
                        "se_name":       se_name or "—",
                        "customer":      customer or "—",
                        "cluster_name":  cluster_name or "—",
                        "install_date":  str(install_date),
                        "hostname":      (
                            f"{full_sw_a}-GPU" if side == "A"
                            else f"{full_sw_b}-GPU"
                        ),
                        "mgmt_ip":       sw_a_ip2 if side == "A" else sw_b_ip2,
                        "mgmt_gw":       mgmt_gw2,
                        "ntp_server":    ntp_srv2 or mgmt_gw2,
                        "vlan_id":       vlan_id2,
                        "mtu":           profile2["mtu"],
                        "isl_ports":     isl_list2,
                        "uplink_ports":  uplink_list2,
                        "clag_id":       200,
                        "peer_ip":       (
                            sw_b_ip2.split("/")[0] if side == "A"
                            else sw_a_ip2.split("/")[0]
                        ),
                        "port_map":      port_map2,
                        "clag_priority": 1000 if side == "A" else 2000,
                    }
                    config_text2 = template2.render(context2).replace('\r\n', '\n').replace('\r', '\n')

                    with (cfg_col_a2 if side == "A" else cfg_col_b2):
                        st.markdown(
                            f"**Switch {side}** "
                            f"({'Primary' if side == 'A' else 'Secondary'})"
                        )
                        st.code(config_text2, language="bash")
                        st.download_button(
                            label=f"💾 Download GPU Switch {side} Config",
                            data=config_text2,
                            file_name=(
                                f"{pfx}_GPU_SW{side}_"
                                f"{profile2['vendor'].upper()}_"
                                f"{date.today().isoformat()}.txt"
                            ),
                            mime="text/plain",
                            key=f"tab6_dl_{side}"
                        )

            # Customer Handoff Document
            st.markdown("---")
            st.markdown("#### 📄 Customer Network Handoff Document")
            st.caption(
                "Share this with the customer's network team. "
                "Covers what they need to configure on their side "
                "to accept the VAST uplink."
            )

            handoff_doc = f"""
VAST DATA — CUSTOMER NETWORK HANDOFF REQUIREMENTS
==================================================
Cluster:      {cluster_name or "—"}
Customer:     {customer or "—"}
SE:           {se_name or "—"}
Date:         {install_date}
Generated by: VAST SE Toolkit v1.0.0

YOUR NETWORK TEAM MUST CONFIGURE THE FOLLOWING
===============================================

1. PORT-CHANNEL / MLAG
   - Create Port-Channel 200
   - Mode: LACP Active
   - Member ports: as agreed with SE on-site
   - MTU: {profile2["mtu"]} (MANDATORY — do not use 9000 or 1500)

2. VLAN
   - Allow VLAN {vlan_id2} on the port-channel
   - Configure as Trunk mode

3. UPLINK CONNECTIVITY
   - Connect to VAST Switch A uplink ports: {uplink_ports_input2}
   - Connect to VAST Switch B uplink ports: {uplink_ports_input2}
   - Both connections form an MLAG/LACP bond

4. CABLE REQUIREMENTS
   - Cable type: {profile2["spine_cable"]["spec"]}
   - Supplied by: {profile2["spine_cable"]["supplier"]}
   {"⚠️  NOTE: 400G MPO AOC cables are NOT supplied by VAST." if profile2["customer_cables"] else "✅  Cables are included in VAST shipment."}

5. ACCEPTANCE TEST
   After cabling run the following to confirm connectivity:

   [Mellanox / Cumulus]
   net show lldp
   net show mlag

   [Arista EOS]
   show mlag
   show port-channel summary
   show lldp neighbors

6. VAST REQUIREMENTS SUMMARY
   - MTU:          {profile2["mtu"]}
   - VLAN:         {vlan_id2}
   - LACP Mode:    Active
   - Port-Channel: 200

For questions contact your VAST SE: {se_name or "—"}
==================================================
"""
            st.code(handoff_doc, language="text")
            st.download_button(
                label="📄 Download Customer Handoff Document",
                data=handoff_doc,
                file_name=(
                    f"{pfx}_Customer_Handoff_"
                    f"{date.today().isoformat()}.txt"
                ),
                mime="text/plain",
                key="tab6_handoff_dl"
            )


# ============================================================
# TAB 3 — VALIDATION & PRE-FLIGHT
# ============================================================
with tab3:
    st.subheader("Validation & Pre-Flight Checks")
    st.caption(
        "Run through all checks below before starting the VAST bootstrap. "
        "Every item must be green before you proceed."
    )

    # Grab state from other tabs
    profile_t3     = HARDWARE_PROFILES.get(
        st.session_state.get("tab5_sw_model",
        list(HARDWARE_PROFILES.keys())[0])
    )
    vlan_t3        = st.session_state.get("tab5_vlan",   100)
    sw_a_t3        = st.session_state.get("tab5_sw_a_ip","192.168.1.1/24")
    sw_b_t3        = st.session_state.get("tab5_sw_b_ip","192.168.1.2/24")
    ntp_t3         = st.session_state.get("tab5_ntp",    "")
    isl_t3         = st.session_state.get("tab5_isl",    "")
    dnode_st_t3    = int(st.session_state.get("tab5_dnode_start", 1))
    cnode_st_t3    = int(st.session_state.get("tab5_cnode_start", 15))
    isl_short_t3   = st.session_state.get("tab5_isl_short", False)
    gpu_enabled_t3 = st.session_state.get("tab6_enabled", False)
    sw_model_t3    = st.session_state.get(
        "tab5_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )

    sw_a_ip_only = sw_a_t3.split("/")[0]
    sw_b_ip_only = sw_b_t3.split("/")[0]

    # ── Section 1: Port Count Validation ────────────────────
    st.markdown("---")
    st.markdown("### 1️⃣ Port Count Validation")

    errors_t3, warnings_t3 = validate_port_counts(
        num_dboxes, num_cnodes,
        dnode_st_t3, cnode_st_t3, profile_t3
    )

    if errors_t3:
        for e in errors_t3:
            st.error(e)
    elif warnings_t3:
        for w in warnings_t3:
            st.warning(w)
    else:
        total_ports_used = (num_dboxes * 2) + num_cnodes
        st.success(
            f"✅ Port allocation valid — "
            f"Using {total_ports_used} of "
            f"{profile_t3['max_node_ports']} available node ports "
            f"on {sw_model_t3}."
        )

    dnode_end    = dnode_st_t3 + (num_dboxes * 2) - 1
    cnode_end    = cnode_st_t3 + num_cnodes - 1
    isl_ports_t3 = [p.strip() for p in isl_t3.split(",") if p.strip()]
    isl_range    = (
        f"{isl_ports_t3[0]}–{isl_ports_t3[-1]}"
        if isl_ports_t3 else "—"
    )

    st.table([
        {
            "Range":        f"swp{dnode_st_t3}–swp{dnode_end}",
            "Reserved For": "DNodes (BF-3)",
            "Count":         num_dboxes * 2,
            "Status":        "✅ OK" if not errors_t3 else "❌ Error"
        },
        {
            "Range":        f"swp{cnode_st_t3}–swp{cnode_end}",
            "Reserved For": "CNodes (CX7)",
            "Count":         num_cnodes,
            "Status":        "✅ OK" if not errors_t3 else "❌ Error"
        },
        {
            "Range":        isl_range,
            "Reserved For": "ISL / Peerlink",
            "Count":         len(isl_ports_t3),
            "Status":        "✅ OK"
        },
    ])

    # ── Section 2: Cable Pre-Check ───────────────────────────
    st.markdown("---")
    st.markdown("### 2️⃣ Cable Pre-Check")

    if profile_t3["customer_cables"]:
        st.error(
            f"⚠️ **{sw_model_t3} requires customer-supplied 400G cables.** "
            "Confirm all cables are on-site before proceeding."
        )
    else:
        st.success(
            f"✅ All cables for {sw_model_t3} are included "
            "in the VAST shipment."
        )

    isl_cable_t3 = (
        profile_t3["isl_cable_short"] if isl_short_t3
        else profile_t3["isl_cable_long"]
    )

    st.table([
        {
            "Connection":   "DNode (BF-3) → Switch",
            "Cable":        profile_t3["node_cable"]["spec"],
            "Supplied By":  profile_t3["node_cable"]["supplier"],
            "Confirmed ✓":  "☐"
        },
        {
            "Connection":   "CNode (CX7) → Switch",
            "Cable":        profile_t3["node_cable"]["spec"],
            "Supplied By":  profile_t3["node_cable"]["supplier"],
            "Confirmed ✓":  "☐"
        },
        {
            "Connection":   f"ISL / Peerlink ({'≤1m' if isl_short_t3 else '>1m'})",
            "Cable":        isl_cable_t3["spec"],
            "Supplied By":  isl_cable_t3["supplier"],
            "Confirmed ✓":  "☐"
        },
        {
            "Connection":   "Spine / Uplink",
            "Cable":        profile_t3["spine_cable"]["spec"],
            "Supplied By":  profile_t3["spine_cable"]["supplier"],
            "Confirmed ✓":  "☐"
        },
    ])

    # ── Section 3: MGMT & NTP Check ─────────────────────────
    st.markdown("---")
    st.markdown("### 3️⃣ Management & NTP Pre-Check")

    if not ntp_t3:
        st.error(
            "❌ NTP Server not set in Tab 1. "
            "Set the NTP server before running bootstrap."
        )
    else:
        st.success(f"✅ NTP Server configured: {ntp_t3}")

    st.table([
        {
            "Check":  "Switch A MGMT IP reachable",
            "Value":  sw_a_ip_only,
            "Action": f"ping {sw_a_ip_only}"
        },
        {
            "Check":  "Switch B MGMT IP reachable",
            "Value":  sw_b_ip_only,
            "Action": f"ping {sw_b_ip_only}"
        },
        {
            "Check":  "MGMT Gateway reachable",
            "Value":  st.session_state.get("tab5_gw", "—"),
            "Action": f"ping {st.session_state.get('tab5_gw', '—')}"
        },
        {
            "Check":  "NTP Server reachable",
            "Value":  ntp_t3 or "NOT SET",
            "Action": f"ping {ntp_t3}" if ntp_t3 else "❌ Set NTP first"
        },
    ])

    # ── Section 4: LLDP Validation Script ───────────────────
    st.markdown("---")
    st.markdown("### 4️⃣ Post-Cabling LLDP Validation Script")
    st.caption(
        "Paste this into both switch CLIs after cabling is complete. "
        "Every expected node must appear before starting bootstrap."
    )

    expected_neighbors = []
    for i in range(1, num_dboxes + 1):
        for d in range(1, 3):
            expected_neighbors.append(
                f"{pfx}-{dbox_label}-{i}-{dnode_label}-{d}"
            )
    for i in range(1, num_cnodes + 1):
        expected_neighbors.append(f"{pfx}-{cnode_label}-{i}")

    neighbor_grep = "|".join(expected_neighbors)

    cumulus_lldp = f"""#!/bin/bash
# VAST SE Toolkit — LLDP Validation Script
# Cluster: {cluster_name or "—"}  |  SE: {se_name or "—"}
# Run on BOTH Switch A ({sw_a_ip_only}) and Switch B ({sw_b_ip_only})
# ============================================================

echo "=== LLDP NEIGHBOR CHECK ==="
echo "Expected nodes: {len(expected_neighbors)}"
echo ""
nv show interface lldp

echo ""
echo "=== FILTERING FOR VAST NODES ==="
nv show interface lldp | grep -E "{neighbor_grep}"

echo ""
echo "=== MLAG STATUS ==="
nv show mlag

echo ""
echo "=== PEERLINK STATUS ==="
nv show interface peerlink

echo ""
echo "=== BRIDGE VLAN STATUS ==="
nv show bridge domain br_default vlan

echo ""
echo "=== MTU VERIFICATION (expect {profile_t3['mtu']}) ==="
nv show interface | grep -E "swp[1-9]|mtu"

echo ""
echo "=== QoS PFC STATUS ==="
nv show qos roce

echo ""
echo "Expected {len(expected_neighbors)} VAST nodes:"
echo "{chr(10).join(f'  - {n}' for n in expected_neighbors)}"
"""

    arista_lldp = f"""#!/bin/bash
# VAST SE Toolkit — LLDP Validation Script (Arista EOS)
# Cluster: {cluster_name or "—"}  |  SE: {se_name or "—"}
# Run on BOTH Switch A ({sw_a_ip_only}) and Switch B ({sw_b_ip_only})
# ============================================================

echo "=== LLDP NEIGHBOR CHECK ==="
show lldp neighbors

echo ""
echo "=== FILTERING FOR VAST NODES ==="
show lldp neighbors | grep -E "{neighbor_grep}"

echo ""
echo "=== MLAG STATUS ==="
show mlag

echo ""
echo "=== PORT-CHANNEL SUMMARY ==="
show port-channel summary

echo ""
echo "=== VLAN STATUS ==="
show vlan

echo ""
echo "=== MTU VERIFICATION (expect {profile_t3['mtu']}) ==="
show interfaces | grep -E "Ethernet|MTU"

echo ""
echo "=== QoS PFC STATUS ==="
show priority-flow-control
show qos

echo ""
echo "Expected {len(expected_neighbors)} VAST nodes:"
echo "{chr(10).join(f'  - {n}' for n in expected_neighbors)}"
"""

    lldp_script = (
        cumulus_lldp if profile_t3["os"] == "cumulus"
        else arista_lldp
    )

    st.code(lldp_script, language="bash")
    st.download_button(
        label="💾 Download LLDP Validation Script",
        data=lldp_script,
        file_name=(
            f"{pfx}_LLDP_Validation_"
            f"{date.today().isoformat()}.sh"
        ),
        mime="text/plain",
        key="tab3_lldp_dl"
    )

    # ── Section 5: Pre-Flight Checklist ─────────────────────
    st.markdown("---")
    st.markdown("### 5️⃣ Pre-Flight Checklist")
    st.caption(
        "Work through this checklist top to bottom. "
        "Do not start VAST bootstrap until all items are confirmed."
    )

    checklist = f"""
VAST INSTALLATION PRE-FLIGHT CHECKLIST
=======================================
Cluster:  {pfx}
Customer: {customer or "—"}
SE:       {se_name or "—"}
Date:     {install_date}
Switch:   {sw_model_t3}
Topology: {topology}
Generated by: VAST SE Toolkit v1.0.0

PHYSICAL
--------
☐  All DBoxes racked and powered on
☐  All CNodes racked and powered on
☐  All switches racked and powered on
☐  {"⚠️  400G customer-supplied cables on-site and verified" if profile_t3["customer_cables"] else "VAST-supplied cables verified against packing list"}
☐  DNode (BF-3) cables run: {profile_t3["node_cable"]["spec"]}
☐  CNode (CX7)  cables run: {profile_t3["node_cable"]["spec"]}
☐  ISL cables run:          {isl_cable_t3["spec"]}
☐  Uplink cables run:       {profile_t3["spine_cable"]["spec"]}

NETWORK — SWITCH A ({sw_a_ip_only})
{"─" * 40}
☐  Switch A powered on and booted
☐  Switch A MGMT IP configured: {sw_a_ip_only}
☐  Switch A config applied (downloaded from Tab 1)
☐  Switch A MLAG primary (priority 1000)
☐  Switch A NTP synced to: {ntp_t3 or "NOT SET — SET BEFORE PROCEEDING"}

NETWORK — SWITCH B ({sw_b_ip_only})
{"─" * 40}
☐  Switch B powered on and booted
☐  Switch B MGMT IP configured: {sw_b_ip_only}
☐  Switch B config applied (downloaded from Tab 1)
☐  Switch B MLAG secondary (priority 2000)
☐  Switch B NTP synced to: {ntp_t3 or "NOT SET — SET BEFORE PROCEEDING"}

{"SPINE SWITCHES" if topology == "Spine-Leaf" else ""}
{"─" * 40 if topology == "Spine-Leaf" else ""}
{"☐  Spine A config applied (downloaded from Tab 1)" if topology == "Spine-Leaf" else ""}
{"☐  Spine B config applied (downloaded from Tab 1)" if topology == "Spine-Leaf" else ""}
{"☐  Spine MLAG peerlink UP on both spine switches" if topology == "Spine-Leaf" else ""}
{"☐  Leaf-to-Spine uplinks confirmed UP" if topology == "Spine-Leaf" else ""}

VALIDATION
----------
☐  MLAG peerlink UP on both switches
☐  MLAG state MASTER/BACKUP (not SOLO)
☐  LLDP validation script run — all {len(expected_neighbors)} nodes visible
☐  MTU confirmed {profile_t3["mtu"]} on all node ports
☐  PFC / RoCEv2 QoS confirmed active
☐  Customer uplink LACP bond UP (if applicable)
☐  Ping Switch A MGMT: ping {sw_a_ip_only}
☐  Ping Switch B MGMT: ping {sw_b_ip_only}

{"GPU / DATA NETWORK SWITCH" if gpu_enabled_t3 else ""}
{"─" * 40 if gpu_enabled_t3 else ""}
{"☐  GPU Switch A config applied (downloaded from Tab 2)" if gpu_enabled_t3 else ""}
{"☐  GPU Switch B config applied (downloaded from Tab 2)" if gpu_enabled_t3 else ""}
{"☐  Customer handoff document delivered to network team" if gpu_enabled_t3 else ""}
{"☐  GPU switch uplink LACP bond confirmed UP" if gpu_enabled_t3 else ""}

READY FOR BOOTSTRAP
-------------------
☐  All above items confirmed
☐  VAST bootstrap bundle available on laptop
☐  Customer sign-off on network readiness obtained
☐  SE confirms: GO FOR BOOTSTRAP ✅
================================================
"""

    st.code(checklist, language="text")
    st.download_button(
        label="📋 Download Pre-Flight Checklist",
        data=checklist,
        file_name=(
            f"{pfx}_PreFlight_Checklist_"
            f"{date.today().isoformat()}.txt"
        ),
        mime="text/plain",
        key="tab3_checklist_dl"
    )

    # ── Section 6: Cable Label Generator ────────────────────
    st.markdown("---")
    st.markdown("### 6️⃣ Cable Label Generator")
    st.caption(
        "Format: SOURCE-SWITCH-PORT : TARGET-NODE-PORT  |  "
        "Download CSV for label printers or plain text for printing."
    )

    tab3_map = get_port_mappings(
        "A", num_dboxes, num_cnodes,
        dnode_st_t3, cnode_st_t3,
        pfx=pfx, dbox_label=dbox_label,
        dnode_label=dnode_label, cnode_label=cnode_label
    )

    isl_list_t3   = [p.strip() for p in isl_t3.split(",") if p.strip()]
    label_rows    = []
    csv_rows      = []
    cable_number  = 1

    for item in tab3_map:
        port_num   = item["port"]
        sw_a_port  = f"{full_sw_a}-P{port_num}"
        sw_b_port  = f"{full_sw_b}-P{port_num}"
        node_end_a = item["desc"].replace("-P2", "-P1")
        node_end_b = item["desc"].replace("-P1", "-P2")
        cable_spec = profile_t3["node_cable"]["spec"]
        supplier   = profile_t3["node_cable"]["supplier"]

        label_rows.append({
            "Cable #":    f"CBL-{cable_number:03d}",
            "Switch End": sw_a_port,
            "Node End":   node_end_a,
            "Cable Type": cable_spec,
            "Supplier":   supplier,
        })
        csv_rows.append(
            f"CBL-{cable_number:03d},{sw_a_port},{node_end_a},"
            f"{cable_spec},{supplier}"
        )
        cable_number += 1

        label_rows.append({
            "Cable #":    f"CBL-{cable_number:03d}",
            "Switch End": sw_b_port,
            "Node End":   node_end_b,
            "Cable Type": cable_spec,
            "Supplier":   supplier,
        })
        csv_rows.append(
            f"CBL-{cable_number:03d},{sw_b_port},{node_end_b},"
            f"{cable_spec},{supplier}"
        )
        cable_number += 1

    for p in isl_list_t3:
        port_num     = p.replace("swp", "")
        isl_spec     = (
            profile_t3["isl_cable_short"]["spec"] if isl_short_t3
            else profile_t3["isl_cable_long"]["spec"]
        )
        isl_supplier = (
            profile_t3["isl_cable_short"]["supplier"] if isl_short_t3
            else profile_t3["isl_cable_long"]["supplier"]
        )
        label_rows.append({
            "Cable #":    f"CBL-{cable_number:03d}",
            "Switch End": f"{full_sw_a}-ISL-{p}",
            "Node End":   f"{full_sw_b}-ISL-{p}",
            "Cable Type": isl_spec,
            "Supplier":   isl_supplier,
        })
        csv_rows.append(
            f"CBL-{cable_number:03d},"
            f"{full_sw_a}-ISL-{p},"
            f"{full_sw_b}-ISL-{p},"
            f"{isl_spec},{isl_supplier}"
        )
        cable_number += 1

    st.dataframe(label_rows, use_container_width=True)

    plain_labels = (
        f"VAST CABLE LABELS\n"
        f"Cluster: {pfx}  |  SE: {se_name or '—'}  |  "
        f"Date: {install_date}\n"
        f"{'='*65}\n\n"
    )
    for row in label_rows:
        plain_labels += (
            f"[{row['Cable #']}]\n"
            f"  FROM: {row['Switch End']}\n"
            f"  TO:   {row['Node End']}\n"
            f"  TYPE: {row['Cable Type']}  |  "
            f"SUPPLIER: {row['Supplier']}\n\n"
        )

    csv_header = "Cable #,Switch End,Node End,Cable Type,Supplier"
    csv_output = csv_header + "\n" + "\n".join(csv_rows)

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="💾 Download Cable Labels (CSV)",
            data=csv_output,
            file_name=(
                f"{pfx}_Cable_Labels_{date.today().isoformat()}.csv"
            ),
            mime="text/csv",
            key="tab3_labels_csv"
        )
    with dl_col2:
        st.download_button(
            label="🖨️ Download Cable Labels (Print)",
            data=plain_labels,
            file_name=(
                f"{pfx}_Cable_Labels_{date.today().isoformat()}.txt"
            ),
            mime="text/plain",
            key="tab3_labels_txt"
        )

    # ── Section 7: Equipment Checklist ──────────────────────
    st.markdown("---")
    st.markdown("### 7️⃣ Equipment Checklist")
    st.caption(
        "Quantities generated from session inputs. "
        "Add custom items at the bottom."
    )

    total_node_cables   = (num_dboxes * 2 * 2) + (num_cnodes * 2)
    total_isl_cables    = len(isl_list_t3)
    uplink_t3           = st.session_state.get("tab5_uplink", "")
    uplink_list_t3      = [
        p.strip() for p in uplink_t3.split(",") if p.strip()
    ]
    total_uplink_cables = len(uplink_list_t3) * 2

    node_cable_line = (
        f"☐  ⚠️  {total_node_cables}x "
        f"{profile_t3['node_cable']['spec']} "
        f"(node cables — CUSTOMER SUPPLIED)"
        if profile_t3["customer_cables"]
        else
        f"☐  {total_node_cables}x "
        f"{profile_t3['node_cable']['spec']} "
        f"(node cables — VAST supplied)"
    )
    isl_cable_line = (
        f"☐  ⚠️  {total_isl_cables}x "
        f"{isl_cable_t3['spec']} "
        f"(ISL cables — CUSTOMER SUPPLIED)"
        if profile_t3["customer_cables"]
        else
        f"☐  {total_isl_cables}x "
        f"{isl_cable_t3['spec']} "
        f"(ISL cables — VAST supplied)"
    )
    uplink_cable_line = (
        f"☐  ⚠️  {total_uplink_cables}x "
        f"{profile_t3['spine_cable']['spec']} "
        f"(uplink cables — CUSTOMER SUPPLIED)"
        if profile_t3["customer_cables"]
        else
        f"☐  {total_uplink_cables}x "
        f"{profile_t3['spine_cable']['spec']} "
        f"(uplink cables — VAST supplied)"
    )

    dbox_lines  = "\n".join(
        f"     ☐  {pfx}-{dbox_label}-{i}"
        for i in range(1, num_dboxes + 1)
    )
    cnode_lines = "\n".join(
        f"     ☐  {pfx}-{cnode_label}-{i}"
        for i in range(1, num_cnodes + 1)
    )

    custom_val = st.session_state.get("equip_custom", "")

    equip_checklist = f"""
VAST INSTALLATION — EQUIPMENT CHECKLIST
========================================
Cluster:  {pfx}
Customer: {customer or "—"}
SE:       {se_name or "—"}
Date:     {install_date}
Switch:   {sw_model_t3}
Topology: {topology}
Generated by: VAST SE Toolkit v1.0.0

🔧 TOOLS
========
☐  SE go bag
☐  Laptop with VAST SE Toolkit running
☐  Console cable (RJ45 to USB)

💾 SOFTWARE & BOOTSTRAP FILES
==============================
☐  VAST OS bundle downloaded to laptop (latest version confirmed)
☐  Switch firmware verified ({"Cumulus NV" if profile_t3["os"] == "cumulus" else "Arista EOS"})
☐  SE Toolkit configs downloaded:
     ☐  {full_sw_a} config
     ☐  {full_sw_b} config
{"     ☐  Spine A config" if topology == "Spine-Leaf" else ""}
{"     ☐  Spine B config" if topology == "Spine-Leaf" else ""}
{"     ☐  GPU Switch A config" if gpu_enabled_t3 else ""}
{"     ☐  GPU Switch B config" if gpu_enabled_t3 else ""}
{"     ☐  Customer handoff document sent/printed" if gpu_enabled_t3 else ""}

🔌 SWITCH HARDWARE
==================
☐  2x {sw_model_t3} switches
     ☐  {full_sw_a}
     ☐  {full_sw_b}
{"☐  2x " + spine_model + " spine switches" if topology == "Spine-Leaf" else ""}
{node_cable_line}
{isl_cable_line}
{uplink_cable_line}

📦 COMPUTE NODES
================
☐  {num_dboxes}x DBox enclosure{"s" if num_dboxes > 1 else ""}:
{dbox_lines}
☐  {num_cnodes}x CNode{"s" if num_cnodes > 1 else ""} (with CX7 NICs):
{cnode_lines}

🗄️ RACK EQUIPMENT
==================
☐  Rack rails for all nodes and switches
☐  Cable managers / D-rings
☐  PDU capacity confirmed for node count
☐  1U blanking panels

➕ CUSTOM ITEMS
===============
{custom_val if custom_val else "(none)"}
========================================
"""

    st.code(equip_checklist, language="text")

    st.text_area(
        "Add custom items (one per line)",
        placeholder="e.g. Customer PO number confirmed\nData center escort arranged",
        key="equip_custom",
        height=100
    )

    st.download_button(
        label="📋 Download Equipment Checklist",
        data=equip_checklist,
        file_name=(
            f"{pfx}_Equipment_Checklist_"
            f"{date.today().isoformat()}.txt"
        ),
        mime="text/plain",
        key="tab3_equip_dl"
    )
# ============================================================
# TAB 4 — INSTALLATION PROCEDURE
# ============================================================
with tab4:
    st.subheader("Switch Installation Procedure")
    st.caption(
        "Step-by-step procedure personalised for this session. "
        "Work through each section in order. "
        "Do not start VAST bootstrap until all switches are validated."
    )

    # Pull session state
    proc_sw_model   = st.session_state.get(
        "tab5_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_profile    = HARDWARE_PROFILES[proc_sw_model]
    proc_sw_a_ip    = st.session_state.get("tab5_sw_a_ip", "192.168.1.1/24")
    proc_sw_b_ip    = st.session_state.get("tab5_sw_b_ip", "192.168.1.2/24")
    proc_ntp        = st.session_state.get("tab5_ntp", "")
    proc_gpu        = st.session_state.get("tab6_enabled", False)
    proc_gpu_sw_a   = st.session_state.get("tab6_sw_a_ip", "192.168.2.1/24")
    proc_gpu_sw_b   = st.session_state.get("tab6_sw_b_ip", "192.168.2.2/24")

    # Build filenames matching what the toolkit generates
    today_str       = date.today().isoformat()
    vendor_up       = proc_profile["vendor"].upper()
    fname_sw_a      = f"{pfx}_SWA_{vendor_up}_{today_str}.txt"
    fname_sw_b      = f"{pfx}_SWB_{vendor_up}_{today_str}.txt"

    proc_gpu_model  = st.session_state.get(
        "tab6_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_gpu_profile = HARDWARE_PROFILES[proc_gpu_model]
    gpu_vendor_up   = proc_gpu_profile["vendor"].upper()
    fname_gpu_sw_a  = f"{pfx}_GPU_SWA_{gpu_vendor_up}_{today_str}.txt"
    fname_gpu_sw_b  = f"{pfx}_GPU_SWB_{gpu_vendor_up}_{today_str}.txt"

    spine_enabled   = topology == "Spine-Leaf"
    proc_spine_model = st.session_state.get(
        "spine_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_spine_profile = HARDWARE_PROFILES[proc_spine_model]
    spine_vendor_up = proc_spine_profile["vendor"].upper()
    fname_spine_a   = f"{pfx}_SPINE_A_{spine_vendor_up}_{today_str}.txt"
    fname_spine_b   = f"{pfx}_SPINE_B_{spine_vendor_up}_{today_str}.txt"

    proc_spine_a_ip = st.session_state.get("spine_a_ip", "192.168.3.1/24")
    proc_spine_b_ip = st.session_state.get("spine_b_ip", "192.168.3.2/24")

    TEMP_IP = "192.168.2.101/24"

    # ── Section 1: Prerequisites ─────────────────────────────
    st.markdown("---")
    st.markdown("### 1️⃣ Prerequisites")
    st.markdown(
        "Before touching any switch hardware, confirm the following:"
    )

    switch_list = [
        f"**{full_sw_a}** config file: `{fname_sw_a}`",
        f"**{full_sw_b}** config file: `{fname_sw_b}`",
    ]
    if proc_gpu:
        switch_list += [
            f"**{full_sw_a}-GPU** config file: `{fname_gpu_sw_a}`",
            f"**{full_sw_b}-GPU** config file: `{fname_gpu_sw_b}`",
        ]
    if spine_enabled:
        spine_vsuffix = get_sw_suffix(proc_spine_model)
        switch_list += [
            f"**{pfx}-{spine_vsuffix}-SPINE-A** config file: `{fname_spine_a}`",
            f"**{pfx}-{spine_vsuffix}-SPINE-B** config file: `{fname_spine_b}`",
        ]

    st.markdown("**Config files downloaded from this toolkit:**")
    for s in switch_list:
        st.markdown(f"- {s}")

    st.markdown(
        "\n**Tools required:**\n"
        "- Laptop with VAST SE Toolkit\n"
        "- Console cable (RJ45 to USB)\n"
        "- Ethernet patch cable (for eth0 MGMT)\n"
        "- Serial terminal app (PuTTY on Windows / Serial.app on Mac)\n"
    )

    st.info(
        "💡 **Serial connection settings for Mellanox/Cumulus:** "
        "115200 baud, 8 data bits, no parity, 1 stop bit, no flow control."
    )

    # ── Helper to render per-switch steps ───────────────────
    def render_switch_procedure(
        switch_label, hostname, mgmt_ip, config_filename,
        switch_side, is_primary, peer_ip
    ):
        priority = "1000 (Primary)" if is_primary else "2000 (Secondary)"
        mgmt_ip_only = mgmt_ip.split("/")[0]

        st.markdown(f"#### Connect to {switch_label}")
        st.markdown(
            f"Connect your **serial cable** to the console port "
            f"and your **Ethernet cable** to the `eth0` port on "
            f"**{hostname}**."
        )
        st.info(
            "⚠️ You may need to hand-type serial terminal commands. "
            "Copy/paste can be unreliable over serial connections."
        )

        st.markdown("**Step 1 — Factory reset the switch:**")
        st.code("nv action reset system factory-default", language="bash")
        st.caption(
            "Wait for the switch to fully reboot before continuing. "
            "This ensures no previous config interferes."
        )

        st.markdown("**Step 2 — Set a temporary management IP:**")
        st.code(
            f"nv unset interface eth0 ip address dhcp\n"
            f"nv set interface eth0 ip address {TEMP_IP}\n"
            f"nv config apply",
            language="bash"
        )

        st.markdown(
            f"**Step 3 — SCP the config file from your laptop:**"
        )
        st.caption(
            "Run this from your laptop (not the switch terminal)."
        )
        st.code(
            f"scp {config_filename} cumulus@{TEMP_IP.split('/')[0]}:/tmp/",
            language="bash"
        )
        st.warning(
            "If you see a host key warning run this on your laptop first:  \n"
            f"`ssh-keygen -R {TEMP_IP.split('/')[0]}`"
        )

        st.markdown("**Step 4 — Back on the serial terminal, remove the temp IP:**")
        st.code(
            f"nv unset interface eth0 ip address {TEMP_IP}\n",
            language="bash"
        )

        st.markdown("**Step 5 — Make the config executable and apply it:**")
        st.code(
            f"chmod +x /tmp/{config_filename}\n"
            f"sed -i 's/\\r//' /tmp/{config_filename}\n"
            f"/tmp/{config_filename}",
            language="bash"
        )
        st.caption(
            "The `sed` command removes Windows line endings. "
            "The config will apply, save, and set the permanent MGMT IP."
        )

        st.markdown("**Step 6 — Connect MGMT cable to customer network and validate NTP:**")
        st.code(
            f"# Confirm date is correct\n"
            f"date\n\n"
            f"# Check NTP sync"
            + (
                f"\nntpq -p\n# Look for * or + next to {proc_ntp}"
                if proc_ntp else
                f"\nntpq -p\n# ⚠️ NTP server not set — check Tab 1"
            ),
            language="bash"
        )

        st.success(
            f"✅ **{hostname}** configured. "
            f"Permanent MGMT IP: `{mgmt_ip_only}` — "
            f"MLAG priority: `{priority}`"
        )
        st.markdown("---")

    # ── Section 2: Internal Storage Fabric ──────────────────
    st.markdown("---")
    st.markdown("### 2️⃣ Internal Storage Fabric Switches")
    st.markdown(
        f"Switch model: **{proc_sw_model}**  \n"
        f"OS: **{'Cumulus NV' if proc_profile['os'] == 'cumulus' else 'Arista EOS'}**"
    )

    render_switch_procedure(
        switch_label    = f"Switch A — {full_sw_a}",
        hostname        = full_sw_a,
        mgmt_ip         = proc_sw_a_ip,
        config_filename = fname_sw_a,
        switch_side     = "A",
        is_primary      = True,
        peer_ip         = proc_sw_b_ip.split("/")[0]
    )

    render_switch_procedure(
        switch_label    = f"Switch B — {full_sw_b}",
        hostname        = full_sw_b,
        mgmt_ip         = proc_sw_b_ip,
        config_filename = fname_sw_b,
        switch_side     = "B",
        is_primary      = False,
        peer_ip         = proc_sw_a_ip.split("/")[0]
    )

    # ── Section 3: GPU Switches ──────────────────────────────
    if proc_gpu:
        st.markdown("---")
        st.markdown("### 3️⃣ GPU / Data Network Switches")
        st.markdown(
            f"Switch model: **{proc_gpu_model}**  \n"
            f"OS: **{'Cumulus NV' if proc_gpu_profile['os'] == 'cumulus' else 'Arista EOS'}**"
        )

        render_switch_procedure(
            switch_label    = f"GPU Switch A — {full_sw_a}-GPU",
            hostname        = f"{full_sw_a}-GPU",
            mgmt_ip         = proc_gpu_sw_a,
            config_filename = fname_gpu_sw_a,
            switch_side     = "A",
            is_primary      = True,
            peer_ip         = proc_gpu_sw_b.split("/")[0]
        )

        render_switch_procedure(
            switch_label    = f"GPU Switch B — {full_sw_b}-GPU",
            hostname        = f"{full_sw_b}-GPU",
            mgmt_ip         = proc_gpu_sw_b,
            config_filename = fname_gpu_sw_b,
            switch_side     = "B",
            is_primary      = False,
            peer_ip         = proc_gpu_sw_a.split("/")[0]
        )

    # ── Section 4: Spine Switches ────────────────────────────
    if spine_enabled:
        spine_vsuffix   = get_sw_suffix(proc_spine_model)
        spine_a_name    = f"{pfx}-{spine_vsuffix}-SPINE-A"
        spine_b_name    = f"{pfx}-{spine_vsuffix}-SPINE-B"

        st.markdown("---")
        st.markdown("### 4️⃣ Spine Switches")
        st.markdown(
            f"Switch model: **{proc_spine_model}**  \n"
            f"OS: **{'Cumulus NV' if proc_spine_profile['os'] == 'cumulus' else 'Arista EOS'}**"
        )

        render_switch_procedure(
            switch_label    = f"Spine A — {spine_a_name}",
            hostname        = spine_a_name,
            mgmt_ip         = proc_spine_a_ip,
            config_filename = fname_spine_a,
            switch_side     = "A",
            is_primary      = True,
            peer_ip         = proc_spine_b_ip.split("/")[0]
        )

        render_switch_procedure(
            switch_label    = f"Spine B — {spine_b_name}",
            hostname        = spine_b_name,
            mgmt_ip         = proc_spine_b_ip,
            config_filename = fname_spine_b,
            switch_side     = "B",
            is_primary      = False,
            peer_ip         = proc_spine_a_ip.split("/")[0]
        )

    # ── Section 5: Post-Config Validation ───────────────────
    section_num = (
        3 + (1 if proc_gpu else 0) + (1 if spine_enabled else 0)
    )
    st.markdown("---")
    st.markdown(f"### {section_num}️⃣ Post-Config Validation")
    st.markdown(
        "Run these checks on **every switch** after all configs are applied."
    )

    st.markdown("#### MLAG Validation")
    st.markdown(
        "Run on both switches. One must show `primary`, "
        "the other `secondary`. Both must show `peer-alive: True`."
    )
    st.code("nv show mlag", language="bash")

    sw_a_ip_only = proc_sw_a_ip.split("/")[0]
    sw_b_ip_only = proc_sw_b_ip.split("/")[0]

    st.markdown("**Expected output — Switch A:**")
    st.code(
        f"local-role      primary\n"
        f"peer-role       secondary\n"
        f"peer-alive      True\n"
        f"[backup]        {sw_b_ip_only}",
        language="text"
    )

    st.markdown("**Expected output — Switch B:**")
    st.code(
        f"local-role      secondary\n"
        f"peer-role       primary\n"
        f"peer-alive      True\n"
        f"[backup]        {sw_a_ip_only}",
        language="text"
    )

    st.markdown("#### Peerlink Validation")
    st.code("nv show interface peerlink", language="bash")
    st.caption("Confirm `oper-status: up` and `link.state: up`.")

    st.markdown("#### MTU Validation")
    st.code(
        f"nv show interface | grep mtu\n"
        f"# All node ports should show {proc_profile['mtu']}",
        language="bash"
    )

    st.markdown("#### LLDP Validation")
    st.markdown(
        "Once all nodes are cabled, run the LLDP validation script "
        "from **Tab 3 → Section 4**. "
        f"Confirm all **{(num_dboxes * 2) + num_cnodes}** "
        "expected nodes are visible before starting VAST bootstrap."
    )

    st.success(
        "✅ All switches validated — ready for VAST bootstrap."
    )

# ============================================================
# TAB 2 — CONFLUENCE INSTALL PLAN GENERATOR
# ============================================================
with tab2:
    try:
        st.write("TAB5 ALIVE")  # ← add this as the very first line
        st.subheader("📄 Confluence Install Plan Generator")
        st.caption(
            "Generates a complete install plan in Confluence-ready markdown. "
            "Fill in the **Project Details** sections in the sidebar, then copy "
            "the output below into a new Confluence page using the Markdown macro."
        )

        # ── Pull all sidebar project detail values ─────────────────
        p_sfdc         = st.session_state.get("proj_sfdc",          "")
        p_ticket       = st.session_state.get("proj_ticket",        "")
        p_slack        = st.session_state.get("proj_slack",         "")
        p_lucid        = st.session_state.get("proj_lucid",         "")
        p_survey       = st.session_state.get("proj_survey",        "")
        p_psnt         = st.session_state.get("proj_psnt",          "")
        p_license      = st.session_state.get("proj_license",       "")
        p_peer_rev     = st.session_state.get("proj_peer_rev",      "")
        p_release      = st.session_state.get("proj_vast_release",  "")
        p_os_ver       = st.session_state.get("proj_os_version",    "")
        p_bundle       = st.session_state.get("proj_bundle",        "")
        p_guide        = st.session_state.get("proj_install_guide", "")
        p_phison       = st.session_state.get("proj_phison",        False)
        p_dbox_type    = st.session_state.get("proj_dbox_type",     "")
        p_cbox_type    = st.session_state.get("proj_cbox_type",     "")
        p_dual_nic     = st.session_state.get("proj_dual_nic",      False)
        p_ipmi         = st.session_state.get("proj_ipmi",          "Outband (Cat6)")
        p_second_nic   = st.session_state.get("proj_second_nic",    "N/A")
        p_nb_mtu       = st.session_state.get("proj_nb_mtu",        "9000")
        p_gpu_svrs     = st.session_state.get("proj_gpu_servers",   "")
        p_dbox_ha      = st.session_state.get("proj_dbox_ha",       False)
        p_encryption   = st.session_state.get("proj_encryption",    False)
        p_similarity   = st.session_state.get("proj_similarity",    "Yes w/ Adaptive Chunking (Default)")
        p_ip_conflict  = st.session_state.get("proj_ip_conflict",   False)
        p_ip_notes     = st.session_state.get("proj_ip_notes",      "")
        p_site_notes   = st.session_state.get("proj_site_notes",    "")

        # ── Pull session data from other tabs ───────────────────────
        t1_sw_model    = st.session_state.get("tab5_sw_model",      list(HARDWARE_PROFILES.keys())[0])
        t1_profile     = HARDWARE_PROFILES[t1_sw_model]
        t1_sw_a_ip     = st.session_state.get("tab5_sw_a_ip",       "192.168.1.1/24")
        t1_sw_b_ip     = st.session_state.get("tab5_sw_b_ip",       "192.168.1.2/24")
        t1_mgmt_gw     = st.session_state.get("tab5_gw",            "192.168.1.254")
        t1_ntp         = st.session_state.get("tab5_ntp",           "")
        t1_vlan        = st.session_state.get("tab5_vlan",          100)
        t1_isl         = st.session_state.get("tab5_isl",           "")
        t1_uplink      = st.session_state.get("tab5_uplink",        "")
        t1_dnode_start = int(st.session_state.get("tab5_dnode_start", 1))
        t1_cnode_start = int(st.session_state.get("tab5_cnode_start", 15))

        t2_enabled     = st.session_state.get("tab6_enabled",       False)
        t2_sw_a_ip     = st.session_state.get("tab6_sw_a_ip",       "192.168.2.1/24")
        t2_sw_b_ip     = st.session_state.get("tab6_sw_b_ip",       "192.168.2.2/24")
        t2_sw_model    = st.session_state.get("tab6_sw_model",      list(HARDWARE_PROFILES.keys())[0])

        spine_en       = (topology == "Spine-Leaf")
        sp_a_ip        = st.session_state.get("spine_a_ip",         "192.168.3.1/24")
        sp_b_ip        = st.session_state.get("spine_b_ip",         "192.168.3.2/24")
        sp_model       = st.session_state.get("spine_sw_model",     list(HARDWARE_PROFILES.keys())[0])
        sp_ntp         = st.session_state.get("spine_ntp",          "")

        # ── Derived values ──────────────────────────────────────────
        sw_a_ip_only   = t1_sw_a_ip.split("/")[0]
        sw_b_ip_only   = t1_sw_b_ip.split("/")[0]
        cidr           = t1_sw_a_ip.split("/")[1] if "/" in t1_sw_a_ip else "24"
        t2_a_ip_only   = t2_sw_a_ip.split("/")[0]
        t2_b_ip_only   = t2_sw_b_ip.split("/")[0]
        sp_a_ip_only   = sp_a_ip.split("/")[0]
        sp_b_ip_only   = sp_b_ip.split("/")[0]

        today_str      = date.today().isoformat()
        today_nice     = install_date.strftime("%d %B %Y")
        vendor_up      = t1_profile["vendor"].upper()
        t2_profile     = HARDWARE_PROFILES[t2_sw_model]
        sp_profile     = HARDWARE_PROFILES[sp_model]
        sp_vsuf        = get_sw_suffix(sp_model)

        fname_sw_a     = f"{pfx}_SWA_{vendor_up}_{today_str}.txt"
        fname_sw_b     = f"{pfx}_SWB_{vendor_up}_{today_str}.txt"
        fname_gpu_a    = f"{pfx}_GPU_SWA_{t2_profile['vendor'].upper()}_{today_str}.txt"
        fname_gpu_b    = f"{pfx}_GPU_SWB_{t2_profile['vendor'].upper()}_{today_str}.txt"
        fname_sp_a     = f"{pfx}_SPINE_A_{sp_profile['vendor'].upper()}_{today_str}.txt"
        fname_sp_b     = f"{pfx}_SPINE_B_{sp_profile['vendor'].upper()}_{today_str}.txt"

        isl_ports      = [p.strip() for p in t1_isl.split(",") if p.strip()]
        uplink_ports   = [p.strip() for p in t1_uplink.split(",") if p.strip()]

        # Node port ranges for documentation
        dnode_end      = t1_dnode_start + (num_dboxes * 2) - 1
        cnode_end      = t1_cnode_start + num_cnodes - 1

        # ── Helper functions ────────────────────────────────────────
        def _v(val, fallback="⚠️ *NOT SET*"):
            """Return value or a visible placeholder."""
            return val if val else fallback

        def _link(label, url):
            return f"[{label}]({url})" if url else f"{label} *(link not set)*"

        def _yn(flag, yes_text="Yes", no_text="No [Default]"):
            return yes_text if flag else no_text

        def _sw_config_steps(sw_label, hostname, mgmt_ip, config_file, is_primary,
                             peer_ip, ntp_server, sw_os):
            """Generate the per-switch installation procedure block."""
            mgmt_ip_only = mgmt_ip.split("/")[0]
            priority = "1000 (Primary)" if is_primary else "2000 (Secondary)"
            temp_ip = "192.168.2.101"

            ntp_check = (
                f"ntpq -p\n# Look for * or + next to {ntp_server}"
                if ntp_server else
                "ntpq -p\n# ⚠️ NTP server not configured — set in sidebar before using this plan"
            )

            if sw_os == "cumulus":
                reset_cmd = "nv action reset system factory-default"
                apply_cmds = (
                    f"chmod +x /tmp/{config_file}\n"
                    f"sed -i 's/\\r//' /tmp/{config_file}\n"
                    f"/tmp/{config_file}"
                )
                ntp_cmd = ntp_check
            else:  # arista
                reset_cmd = "write erase\nreload"
                apply_cmds = (
                    f"bash /tmp/{config_file}"
                )
                ntp_cmd = "show ntp status\nshow clock"

            return f"""
    #### {sw_label}

    > ⚠️ You may need to hand-type serial commands. Copy/paste can be unreliable over a serial connection.

    Connect your **serial cable** to the console port and **Ethernet cable** to the `eth0` / `Management1` port on **{hostname}**.

    **Step 1 — Reset to factory defaults:**
    ````bash
    {reset_cmd}
    ````
    *Wait for full reboot before continuing.*

    **Step 2 — Set temporary management IP:**
    ````bash
    nv unset interface eth0 ip address dhcp
    nv set interface eth0 ip address {temp_ip}/24
    nv config apply
    ````

    **Step 3 — SCP config file from your laptop** *(run on laptop, not switch)*:
    ````bash
    scp {config_file} cumulus@{temp_ip}:/tmp/
    ````
    *If you see a host key warning, run this first: `ssh-keygen -R {temp_ip}`*

    **Step 4 — Back on serial terminal, remove the temporary IP:**
    ````bash
    nv unset interface eth0 ip address {temp_ip}/24
    ````

    **Step 5 — Apply the configuration:**
    ````bash
    {apply_cmds}
    ````
    *The `sed` command removes Windows CRLF line endings. The script sets the permanent MGMT IP and saves the config.*

    **Step 6 — Connect Cat6 MGMT cable to customer network and validate NTP:**
    ````bash
    date
    {ntp_cmd}
    ````

    ✅ **{hostname}** configured. Permanent MGMT IP: `{mgmt_ip_only}` | MLAG priority: `{priority}`

    ---
    """

        # ── Build download commands ─────────────────────────────────
        # NOTE: We build these as plain strings using \n and string
        # concatenation to avoid triple-backtick inside triple-quote
        # confusion. The content is markdown shown to the SE in Tab 5.

        CODE = "```"  # reusable fence marker — avoids ``` inside """

        if p_os_ver:
            os_download = (
                f"{CODE}bash\n"
                f"# VastOS ISO\n"
                f"aws s3 cp s3://vast-os-iso/{p_os_ver}/vast-os-{p_os_ver}.iso .\n"
                f"aws s3 cp s3://vast-os-iso/{p_os_ver}/vast-os-{p_os_ver}.bfb-image.bfb .       # Ceres V1 DNodes\n"
                f"aws s3 cp s3://vast-os-iso/{p_os_ver}/vast-os-{p_os_ver}.bfb-image.v3.bfb .    # Ceres V2 DNodes\n"
                f"{CODE}"
            )
        else:
            os_download = (
                "> ⚠️ **VastOS Version not set** — enter it in the sidebar under Software Versions."
            )

        if p_bundle and p_release:
            bundle_download = (
                f"**AWS:**\n"
                f"{CODE}bash\n"
                f"aws s3 cp s3://vastdata-releases/release_bundles/service-packs/"
                f"{p_release}/{p_bundle}.vast.tar.gz .\n"
                f"{CODE}\n\n"
                f"**Azure:**\n"
                f"{CODE}\n"
                f"https://vastdatasupporteuwest.blob.core.windows.net/official-releases/"
                f"<build-id>/release/{p_bundle}.vast.tar.gz\n"
                f"{CODE}\n"
                f"*(Get the full Azure SAS URL from the FIELD dashboard for your release.)*\n\n"
                f"**vast\\_bootstrap.sh (AWS):**\n"
                f"{CODE}bash\n"
                f"aws s3 cp s3://vastdata-releases/release_bundles/service-packs/"
                f"{p_release}/vast_bootstrap.sh .\n"
                f"{CODE}\n\n"
                f"> 🍎 **Mac users:** Use `aws s3 cp` or `wget` — "
                f"browsers will gunzip the file automatically."
            )
        else:
            bundle_download = (
                "> ⚠️ **Bundle Version / VAST Release not set** — "
                "enter them in the sidebar under Software Versions."
            )

        # ── Build bootstrap SCP commands ───────────────────────────
        # These are the commands the SE runs on-site to push the bundle
        # to CNode 1 and kick off the VAST bootstrap process.
        if p_bundle:
            bootstrap_cmds = (
                f"Upload the VAST release bundle and bootstrap script to CNode 1 "
                f"(tech port `192.168.2.2`):\n\n"
                f"{CODE}bash\n"
                f"scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f"    {p_bundle}.vast.tar.gz vastdata@192.168.2.2:/vast/bundles/\n\n"
                f"scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f"    vast_bootstrap.sh vastdata@192.168.2.2:/vast/bundles/\n\n"
                f"ssh -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" "
                f"vastdata@192.168.2.2\n"
                f"cd /vast/bundles\n"
                f"chmod u+x ./vast_bootstrap.sh\n"
                f"./vast_bootstrap.sh\n"
                f"{CODE}\n"
                f"*Bootstrapping takes approximately 15 minutes.*"
            )
        else:
            bootstrap_cmds = (
                "> ⚠️ **Bundle Version not set** — enter it in the sidebar. "
                "Commands will populate automatically.\n>\n"
                f"> Template:\n"
                f"> {CODE}bash\n"
                f"> scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f">     <bundle>.vast.tar.gz vastdata@192.168.2.2:/vast/bundles/\n"
                f"> scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f">     vast_bootstrap.sh vastdata@192.168.2.2:/vast/bundles/\n"
                f"> {CODE}"
            )

        # ── Build switch configuration export commands ──────────────
        

        # ── Build VMS switch add commands ────────────────────────────
        sw_add_cmds = (
            f"switch add --ip {sw_a_ip_only} --username cumulus --password CumulusLinux!\n"
            f"switch add --ip {sw_b_ip_only} --username cumulus --password CumulusLinux!"
        )
        if t2_enabled:
            sw_add_cmds += (
                f"\nswitch add --ip {t2_a_ip_only} --username cumulus --password CumulusLinux!"
                f"\nswitch add --ip {t2_b_ip_only} --username cumulus --password CumulusLinux!"
            )
        if spine_en:
            sw_add_cmds += (
                f"\nswitch add --ip {sp_a_ip_only} --username cumulus --password CumulusLinux!"
                f"\nswitch add --ip {sp_b_ip_only} --username cumulus --password CumulusLinux!"
            )

        # ── Cable quantities ─────────────────────────────────────────
        node_cable_qty  = (num_dboxes * 2 * 2) + (num_cnodes * 2)
        isl_cable_qty   = len(isl_ports) if isl_ports else len(t1_profile["default_isl"])
        node_cable_spec = t1_profile["node_cable"]["spec"]
        isl_spec        = t1_profile["isl_cable_long"]["spec"]
        mgmt_cable_qty  = (num_dboxes * 2) + num_cnodes + 4

        # ── Conditional blocks ───────────────────────────────────────
        phison_block = ""
        if p_phison:
            phison_block = (
                "\n> ⚠️ **PHISON DRIVES DETECTED** — Verify FW level on each DNode:\n"
                "> ```bash\n"
                "> sudo nvme list | grep PASCARI\n"
                "> ```\n"
                "> If FW level is `VF1AT0R4` — **STOP** and update to `VF1AT0R5` before proceeding.\n"
                "> See [DBOX SSD and NVRAM Support Matrix](https://vastdata.atlassian.net/wiki/).\n"
            )

        dual_nic_block = ""
        if p_dual_nic and p_second_nic != "N/A":
            dual_nic_block = (
                f"\n| Second NIC Use | {p_second_nic} |"
                f"\n| Northbound MTU | `{p_nb_mtu}` |"
            )

        gpu_srv_block = f"\n| GPU Servers | {p_gpu_svrs} |" if p_gpu_svrs else ""

        ip_conflict_block = (
            f"\n> ⚠️ **Internal IP conflict** — Alternative range: `{_v(p_ip_notes, 'see SE notes')}`"
            if p_ip_conflict else
            "\n> ✅ No conflict — using default VAST internal IP ranges."
        )

        # ── Per-switch config procedure sections ─────────────────────
        fabric_sw_proc = (
            _sw_config_steps(
                f"Switch A — {full_sw_a} (Primary)",
                full_sw_a, t1_sw_a_ip, fname_sw_a,
                True, sw_b_ip_only, t1_ntp, t1_profile["os"]
            ) +
            _sw_config_steps(
                f"Switch B — {full_sw_b} (Secondary)",
                full_sw_b, t1_sw_b_ip, fname_sw_b,
                False, sw_a_ip_only, t1_ntp, t1_profile["os"]
            )
        )

        gpu_sw_section = ""
        if t2_enabled:
            gpu_ntp = st.session_state.get("tab6_ntp", "")
            gpu_sw_section = (
                "\n---\n\n### GPU / Data Network Switches\n\n"
                f"**Model:** {t2_sw_model} | "
                f"**OS:** {'Cumulus NV' if t2_profile['os'] == 'cumulus' else 'Arista EOS'}\n\n"
                f"Config files: `{fname_gpu_a}` and `{fname_gpu_b}` (downloaded from **Tab 2**)\n"
                + _sw_config_steps(
                    f"GPU Switch A — {full_sw_a}-GPU (Primary)",
                    f"{full_sw_a}-GPU", t2_sw_a_ip, fname_gpu_a,
                    True, t2_b_ip_only, gpu_ntp, t2_profile["os"]
                )
                + _sw_config_steps(
                    f"GPU Switch B — {full_sw_b}-GPU (Secondary)",
                    f"{full_sw_b}-GPU", t2_sw_b_ip, fname_gpu_b,
                    False, t2_a_ip_only, gpu_ntp, t2_profile["os"]
                )
            )

        spine_sw_section = ""
        if spine_en:
            spine_a_name = f"{pfx}-{sp_vsuf}-SPINE-A"
            spine_b_name = f"{pfx}-{sp_vsuf}-SPINE-B"
            spine_ntp    = st.session_state.get("spine_ntp", "")
            spine_sw_section = (
                "\n---\n\n### Spine Switches\n\n"
                f"**Model:** {sp_model} | "
                f"**OS:** {'Cumulus NV' if sp_profile['os'] == 'cumulus' else 'Arista EOS'}\n\n"
                f"Config files: `{fname_sp_a}` and `{fname_sp_b}` (downloaded from **Tab 1 — Spine section**)\n"
                + _sw_config_steps(
                    f"Spine A — {spine_a_name} (Primary)",
                    spine_a_name, sp_a_ip, fname_sp_a,
                    True, sp_b_ip_only, spine_ntp, sp_profile["os"]
                )
                + _sw_config_steps(
                    f"Spine B — {spine_b_name} (Secondary)",
                    spine_b_name, sp_b_ip, fname_sp_b,
                    False, sp_a_ip_only, spine_ntp, sp_profile["os"]
                )
            )

        # ── Config file list for prerequisites ───────────────────────
        config_file_list = f"- `{fname_sw_a}` — {full_sw_a}\n- `{fname_sw_b}` — {full_sw_b}"
        if t2_enabled:
            config_file_list += f"\n- `{fname_gpu_a}` — {full_sw_a}-GPU"
            config_file_list += f"\n- `{fname_gpu_b}` — {full_sw_b}-GPU"
        if spine_en:
            config_file_list += f"\n- `{fname_sp_a}` — {pfx}-{sp_vsuf}-SPINE-A"
            config_file_list += f"\n- `{fname_sp_b}` — {pfx}-{sp_vsuf}-SPINE-B"

        # ── Switch rows for equipment table ──────────────────────────
        switch_table_rows = f"| {t1_sw_model} switches | 2 | ☐ |"
        if t2_enabled:
            switch_table_rows += f"\n| {t2_sw_model} GPU switches | 2 | ☐ |"
        if spine_en:
            switch_table_rows += f"\n| {sp_model} spine switches | 2 | ☐ |"

        total_switch_rail_kits = 2 + (2 if t2_enabled else 0) + (2 if spine_en else 0)

        # ── Dual NIC cabling note ────────────────────────────────────
        dual_nic_cabling = ""
        if p_dual_nic:
            dual_nic_cabling = (
                "\n- ☐ CNode (dual NIC): **RIGHT card LEFT** port → Switch A "
                "| **RIGHT card RIGHT** port → Switch B"
            )
            if p_second_nic != "N/A":
                dual_nic_cabling += (
                    f"\n- ☐ CNode **LEFT NIC** ({p_second_nic}) → customer switch"
                )

        gpu_cabling = ""
        if t2_enabled:
            gpu_cabling = (
                "\n- ☐ Run GPU switch ISL cables (ports: see Tab 2)"
                "\n- ☐ CNode northbound ports → GPU Switch A / GPU Switch B"
            )

        # ── MLAG spine note ──────────────────────────────────────────
        spine_mlag_note = ""
        if spine_en:
            spine_mlag_note = "\nRun the same check on both spine switches."

        # ── IPv6 node count ──────────────────────────────────────────
        total_nodes = num_cnodes + (num_dboxes * 2)

        # ── Assemble the full document ───────────────────────────────
        doc = f"""# {_v(customer, "CUSTOMER")} — {_v(cluster_name, "CLUSTER")} — Install Plan — {today_nice}

---

## ⚠️ Important Site Notes / Site Overview

{_v(p_site_notes, "*(No site notes entered — add them in the sidebar under 📝 Project Details → Site Notes)*")}

---

## Prerequisites

> Prior to filling out this template, you should have a completed and approved Site Survey document.

### Opportunity Document Links

| Document | Link |
|---|---|
| SFDC Opportunity | {_link("SFDC", p_sfdc)} |
| Install Ticket | {_link("Install Ticket", p_ticket)} |
| Slack Internal Channel | {_v(p_slack, "*(not set)*")} |
| Lucidchart Diagrams | {_link("Lucidchart", p_lucid)} |
| Site Survey | {_link("Site Survey", p_survey)} |

### Cluster Name / PSNT / License

| Field | Value |
|---|---|
| Cluster Name | `{_v(cluster_name)}` |
| System PSNT | `{_v(p_psnt)}` |
| License Key | `{_v(p_license)}` |

---

> ⛔ **You must STOP installation attempts if you encounter any issues with VAST Installer where an error presents itself.**
> Engage support before continuing so we do not lose important diagnostic data.
> See: [How to collect logs after installation failure](https://vastdata.atlassian.net/wiki/)

---

### Approvals

| Role | Name | Date | Comments |
|---|---|---|---|
| Sales Engineer (Owner) | {_v(se_name)} | {today_nice} | |
| Customer Success | | | |
| PreSales Peer Review | {_v(p_peer_rev, "*(not set)*")} | | |
| PreSales Mgmt Review | *Only needed for Beta / NPI / etc* | | |
| Engineering | *Only needed for Beta / NPI / DA with approval* | | |

### Known Issues

Verify workarounds relevant to your release: [Known Installation-Expansion-Upgrade Issues](https://vastdata.atlassian.net/wiki/)

### VAST Installer

| Field | Value |
|---|---|
| VAST Install Eligible | ✅ YES |
| VAST Release | `{_v(p_release)}` |
| VAST Install Guide | {_link("Install Guide", p_guide)} |

---

## Administrative Tasks

### Create a Shared_FieldActivities Calendar Invite

- ☐ Calendar invite created with format: `[Case Number] | {_v(customer)} | {_v(cluster_name)} | New Installation`
- ☐ Invite includes: SFDC ticket #, customer name, cluster name, VAST owner, who is doing the work, what the work is

### Open Install Ticket

- ☐ Install ticket created and linked: {_link("Install Ticket", p_ticket)}
- ☐ Customer Slack, SFDC, and Confluence accounts created (new customers)

---

## Installation Planning

### Cluster Information Overview

#### Version Information

> Verify the latest release on the [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/FIELD). The latest GA or Scale service pack must be used for all new installations.

| Component | Version |
|---|---|
| VAST Release | `{_v(p_release)}` |
| VastOS Version | `{_v(p_os_ver)}` |
| Bundle Version | `{_v(p_bundle)}` |

#### Hardware

| Component | Quantity | Type |
|---|---|---|
| DBoxes | {num_dboxes} | {_v(p_dbox_type)} |
| CNodes | {num_cnodes} | {_v(p_cbox_type)} |{gpu_srv_block}
| PHISON Drives | {_yn(p_phison, "⚠️ YES — FW check required", "No")} | |
{phison_block}
#### Networking

| Parameter | Value |
|---|---|
| Management Interface | {p_ipmi} |
| Internal Traffic NIC | {"Mellanox CX7 (Right NIC — Dual NIC config)" if p_dual_nic else "Mellanox CX7"} |
| Dual NIC CNodes | {_yn(p_dual_nic, "Yes", "No")} |{dual_nic_block}
| Switch Model | {t1_sw_model} ({t1_profile["total_ports"]} port, {t1_profile["native_speed"]}) |
| Topology | {topology} |
| Storage VLAN | {t1_vlan} |
| Internal MTU | {t1_profile["mtu"]} |
| Switch A MGMT IP | `{t1_sw_a_ip}` |
| Switch B MGMT IP | `{t1_sw_b_ip}` |
| MGMT Gateway | `{t1_mgmt_gw}` |
| NTP Server | `{_v(t1_ntp)}` |
| Priority Flow Control | ✅ **REQUIRED** — select PFC in VAST Installer → Advanced Network Settings |
{f"| GPU Switch A MGMT IP | `{t2_sw_a_ip}` |" if t2_enabled else ""}
{f"| GPU Switch B MGMT IP | `{t2_sw_b_ip}` |" if t2_enabled else ""}
{f"| Spine A MGMT IP | `{sp_a_ip}` |" if spine_en else ""}
{f"| Spine B MGMT IP | `{sp_b_ip}` |" if spine_en else ""}

**Internal IP Range:** {ip_conflict_block}

#### Cluster Specific Settings

| Setting | Value |
|---|---|
| DBox HA | {_yn(p_dbox_ha, "Yes", "No [Default]")} |
| Similarity | {p_similarity} |
| Encryption at Rest | {_yn(p_encryption, "Yes", "No [Default]")} |

### Create Switch Configurations

> ✅ Switch configurations generated by **VAST SE Toolkit** — download from Tabs 1 and 2.
> All Mellanox switches require Cumulus. Cumulus **requires PFC** to be configured.
> Validate firmware at [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/NET) before applying config.

**Config files:**
{config_file_list}

**Port assignments:**

| Range | Reserved For | Count |
|---|---|---|
| swp{t1_dnode_start}–swp{dnode_end} | DNodes (BF-3 {t1_profile["native_speed"]}) | {num_dboxes * 2} |
| swp{t1_cnode_start}–swp{cnode_end} | CNodes (CX7 {t1_profile["native_speed"]}) | {num_cnodes} |
| {", ".join(isl_ports) if isl_ports else "see Tab 1"} | ISL / Peerlink | {len(isl_ports)} |
| {", ".join(uplink_ports) if uplink_ports else "none configured"} | Uplink to customer | {len(uplink_ports)} |

---

## Preparing To Go On Site

### VAST OS Image Download

{os_download}

### VAST Bundle and vast_bootstrap.sh Download

{bundle_download}

### Assemble Your Kit

- ☐ Laptop with VAST SE Toolkit + all config files downloaded
- ☐ Console cable (RJ45 to USB)
- ☐ Ethernet patch cable (for switch `eth0`)
- ☐ Serial terminal app (PuTTY on Windows / Serial.app on Mac) — **115200, 8N1, no flow control**
- ☐ USB-A/C to USB-C cable (Ceres DBox re-imaging if needed)
- ☐ USB key with VastOS ISO (if re-imaging CNodes or Mavericks DNodes)

### Prepare Cable Labels

> 📥 Download cable labels CSV from **Tab 3 → Section 6** of the VAST SE Toolkit.

---

## On Site Physical Installation

### Confirm New Equipment Shipped Properly

*If possible, arrange for the customer to inventory gear before your arrival.*

| Equipment | Quantity | Confirmed |
|---|---|---|
| DBoxes ({_v(p_dbox_type, "see project details")}) | {num_dboxes} | ☐ |
| DBox rail kits | {num_dboxes} | ☐ |
| DBox bezels | {num_dboxes} | ☐ |
| CNodes ({_v(p_cbox_type, "see project details")}) | {num_cnodes} | ☐ |
| CNode rail kits | {num_cnodes} | ☐ |
{switch_table_rows}
| Switch rail kits | {total_switch_rail_kits} | ☐ |
| Node cables ({node_cable_spec}) | {node_cable_qty} | ☐ |
| ISL / Peerlink cables ({isl_spec}) | {isl_cable_qty} per switch pair | ☐ |
| Cat6 management cables | {mgmt_cable_qty} | ☐ |
| Power cables | As per BOM | ☐ |

*If anything is missing or damaged — notify **#manufacturing** or **{_v(p_slack, "#opp_<dealname>")}** immediately.*

### Rack and Stack

- ☐ Check DBox drives — physically push on every drive on both sides before racking (can come loose in shipping)
- ☐ Check CNode boot drives are not loose
- ☐ Rack per site survey layout: {_link("Site Survey", p_survey)}
- ☐ Attach DBox bezels after racking

### Power Cabling

- ☐ Switch power: 1 cable per PDU — **crossed** so each switch has one cable to each PDU
- ☐ CNode power: 1 cable per PDU
- ☐ DBox power (Ceres): left connections → left PDU, right connections → right PDU
- ☐ Check all PSU LEDs are **Green** after powering on
- ☐ **Do NOT power on CNodes** until switches are configured and high-speed cabling is complete
- ☐ Verify PDU phase/circuit balance — do not overload

### Network Cabling

- ☐ Run Cat6 management cables to switch `mgmt0` — **do not connect to customer network yet**
- ☐ Run ISL cables between Switch A and Switch B (ports: `{", ".join(isl_ports) if isl_ports else "see Tab 1"}`)
- ☐ Run external uplink cables to switches — **do not connect to customer core yet**
- ☐ DNode **LEFT** BF-3 port → Switch A | **RIGHT** BF-3 port → Switch B
- ☐ CNode (single NIC): **LEFT** CX7 port → Switch A | **RIGHT** CX7 port → Switch B{dual_nic_cabling}{gpu_cabling}
- ☐ Confirm sufficient cable slack for DBox to slide out fully

### 📷 Take a Picture

Take a photo of the rear of the rack before powering on. Attach to the SFDC install case.

---

## Commissioning the System

### Laptop Setup

1. Set Ethernet adapter to `192.168.2.254/24`
2. Ensure SCP connections are allowed through your firewall: [How To Allow SCP](https://vastdata.atlassian.net/wiki/)
3. Enable terminal session logging for all serial and SSH sessions

### Switch OS Upgrade

> Validate firmware version: [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/NET)
> Switches must be on LTS/Stable version. Follow: [Cumulus Switch Upgrade Guide](https://vastdata.atlassian.net/wiki/)

### Switch Configuration

> Configs include: MLAG, ISL, port descriptions, MTU {t1_profile["mtu"]}, NTP `{_v(t1_ntp)}`, and PFC settings.
> Generated by VAST SE Toolkit — filenames below match the download buttons in Tabs 1 and 2.

#### Internal Storage Fabric

**Model:** {t1_sw_model} | **OS:** {"Cumulus NV" if t1_profile["os"] == "cumulus" else "Arista EOS"}
{fabric_sw_proc}{gpu_sw_section}{spine_sw_section}

---

## Pre-Install Validations

### MLAG / MCLAG Validation

Run on **both** fabric switches. One must show `local-role: primary`, the other `secondary`. Both must show `peer-alive: True`.

```bash
nv show mlag
```

**Expected — {full_sw_a} (Primary):**
```
local-role      primary
peer-role       secondary
peer-alive      True
[backup]        {sw_b_ip_only}
```

**Expected — {full_sw_b} (Secondary):**
```
local-role      secondary
peer-role       primary
peer-alive      True
[backup]        {sw_a_ip_only}
```
{spine_mlag_note}

### Peerlink Validation

```bash
nv show interface peerlink
```
Confirm `oper-status: up` and `link.state: up`.

### MTU Validation

```bash
nv show interface | grep mtu
# All node ports should show {t1_profile["mtu"]}
```

### LLDP Validation

Run the LLDP validation script (download from **Tab 3 → Section 4**) on both switches.
Confirm all **{(num_dboxes * 2) + num_cnodes}** expected nodes are visible before starting bootstrap.

### (Optional) Re-Image CNodes and DNodes

Applying a fresh OS image before installation increases success rate by ensuring the latest OS fixes are applied. See: [Install vast-os on a CERES dnode](https://vastdata.atlassian.net/wiki/)

---

## Generate IPv6 Addresses for All Nodes

> ⚠️ **This step is mandatory before running VAST Installer.**

Connect laptop to the tech port of **each node** in turn (start from lowest CNode, bottom-right port):

```bash
ping 192.168.2.2
ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile /dev/null" vastdata@192.168.2.2
# Default password: vastdata
sudo python3 /usr/bin/config_ipv6.py && exit
```

- CNodes take ~1–2 minutes to execute
- Dual NIC errors can be safely ignored
- **Do NOT disconnect** the tech port cable until the process completes
- Repeat for every node: **{num_cnodes} CNodes + {num_dboxes * 2} DNodes = {total_nodes} total**

---

## Run VAST Installer

### Validate Drive Formatting

> ⚠️ **Mandatory BEFORE installation starts.** All NVMe drives must use 512-byte blocks — not 4KiB.

Login to each DNode and run:

```bash
sudo /bin/expose_drives.py -c disable
sudo /bin/expose_drives.py -c enable
sudo /bin/expose_drives.py -c perst
sudo nvme list
```

📸 Screenshot `nvme list` output from each DNode and attach to the SFDC install case.

> ❌ If any drive shows 4KiB format — **DO NOT CONTINUE**. Escalate to Amit Levin or Adar Zinger.
{phison_block}
### Bootstrap the Cluster

> ⚠️ Use **Incognito Mode** in Google Chrome — VAST Installer caches fields from previous sessions.
> ⚠️ **CRITICAL** — Select **Priority Flow Control** in VAST Installer → Advanced Network Settings. Default is Global Pause which will cause installation failures on Cumulus switches.

{bootstrap_cmds}

Once bootstrap completes and hardware is discovered, follow the [VAST Install Guide]({_v(p_guide, "https://kb.vastdata.com")}) to complete the installation.

### Run Automated Sanity Checks

Follow [Automated Cluster Inspection](https://vastdata.atlassian.net/wiki/x/AQAXaQE):

```bash
wget "https://vastdatasupport.blob.core.windows.net/support-tools/main/support/upgrade_checks/vast_support_tools.py" \\
    -O /vast/data/vast_support_tools.py
chmod +x /vast/data/vast_support_tools.py
/vast/data/vms.sh /vast/data/vast_support_tools.py inspect
```

> ⚠️ If any critical errors are flagged — **do not hand off the cluster to the customer** until resolved.
> ✅ Success indicator: `INFO:support-checks.log:All NVMe drives are correctly formatted with 512-byte blocks`

### Add Switches to VMS

**GUI:** Infrastructure → Switches → Add New Switch → enter MGMT IP and credentials.

**vcli:**
```bash
{sw_add_cmds}
```

---

## Post Install Validations

### Run vnetmap

```bash
vnetmap
```

### Run vast_support_tools

```bash
/vast/data/vms.sh /vast/data/vast_support_tools.py inspect
```

### Gather VMS Log Bundle

VMS → Support → Download Log Bundle. Attach to the SFDC install case.

### Configure Call Home / Cloud Integration

Follow [Call Home Configuration Guide](https://vastdata.atlassian.net/wiki/).

### Validate and Document Cluster Performance

```bash
vperfsanity
```

Document output and attach to the SFDC install case.

---

## Customer Handoff

- ☐ **Check VMS** — all nodes discovered, healthy green status
- ☐ **Create VIP** — configure management VIP in VMS
- ☐ **Test VIP failover** — confirm VIP moves correctly between CNodes
- ☐ **Confirm VIP movement and ARP updates** work across the customer network
- ☐ **Generate and add cluster license** — License Key: `{_v(p_license)}`
  - VMS → Settings → License → Add License
- ☐ **C/D-Box placement** confirmed in VMS rack view
- ☐ **Password management** — change all default passwords (cumulus, vastdata, IPMI)
- ☐ **Switch monitoring** — confirm switches visible in VMS → Infrastructure → Switches
- ☐ **Run Post-Install Survey** — [Post-Install Survey](https://vastdata.atlassian.net/wiki/)
- ☐ **Customer sign-off** obtained

---

*Generated by VAST SE Toolkit v1.0.0 | SE: {_v(se_name)} | Customer: {_v(customer)} | {today_nice}*
"""

        # ── Completeness check ────────────────────────────────────────
        missing = []
        if not p_psnt:        missing.append("System PSNT")
        if not p_license:     missing.append("License Key")
        if not p_release:     missing.append("VAST Release")
        if not p_os_ver:      missing.append("VastOS Version")
        if not p_bundle:      missing.append("Bundle Version")
        if not p_sfdc:        missing.append("SFDC URL")
        if not p_dbox_type:   missing.append("DBox Type")
        if not p_cbox_type:   missing.append("CNode Type")
        if not p_site_notes:  missing.append("Site Notes")
        if not t1_ntp:        missing.append("NTP Server (Tab 5)")

        st.markdown("---")

        if missing:
            st.warning(
                f"⚠️ **{len(missing)} field(s) not set** — "
                "these sections will show placeholder text:\n\n"
                + "\n".join(f"- {m}" for m in missing)
                + "\n\nFill them in **Tab 1 — Project Details**."
            )
        else:
            st.success("✅ All key fields populated — install plan is ready.")

        st.markdown("### 📄 Generated Install Plan")
        st.caption(
            "Copy the text below and paste into a new Confluence page. "
            "Use Insert → Other Macros → Markdown to render it."
        )

        st.code(doc, language="markdown")

        st.download_button(
            label="📥 Download Install Plan (.md)",
            data=doc,
            file_name=f"{pfx}_Install_Plan_{today_str}.md",
            mime="text/markdown",
            key="tab5_download"
        )

    except Exception as e:
        import traceback
        st.error(f"Tab 2 crashed: {e}")
        st.code(traceback.format_exc())


# ============================================================
# TAB 7 — COMING SOON
# ============================================================
with tab7:
    st.subheader("🚀 Coming Soon")
    st.markdown("---")

    features = [
        ("📐 Rack Diagram",
         "Visual 42U rack schematic with components placed at their RU positions. "
         "Auto-generated from the RU inputs in Tabs 5 and 6."),
        ("💾 Project History",
         "SQLite database storing all previous installs on this machine. "
         "Load a previous project, track changes over time, export to Google Drive."),
        ("📏 Capacity & Performance Sizer",
         "Indicative sizing based on DBox model, CNode count, and use case. "
         "Covers raw capacity, usable capacity, read/write throughput, "
         "data reduction estimates, and GPU checkpoint sizing for AI workloads."),
        ("🔌 Hardware Selector",
         "Product profiles for CNode (GEN5/GEN6, single/dual NIC) and DBox models. "
         "Automatically adjusts switch config based on NIC type — "
         "dual NIC removes uplink from storage fabric config."),
        ("📚 Knowledge Base",
         "Curated links to VAST Confluence, FIELD dashboard, release notes, "
         "known issues, and installation guides. Searchable by topic."),
        ("🤖 AI Assistant",
         "LLM-powered config reviewer, troubleshooting guide, and natural language "
         "query interface for VAST installation questions."),
    ]

    for title, description in features:
        with st.expander(title):
            st.markdown(description)

    st.markdown("---")
    st.caption("Have a feature request? Raise it with your SE lead.")

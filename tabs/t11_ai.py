import streamlit as st
import requests
from datetime import date
from config import (
    HARDWARE_PROFILES, SPEED_RANK, DBOX_PROFILES, CNODE_PERF,
    DEVICE_SPECS, DEVICE_IMAGES, DEVICE_IMAGE_MAP, DR_ESTIMATES,
)
from helpers.context import get_ctx, build_sw_name
from helpers.images import _get_device_img_b64, _strip_white_bg
from helpers.svg_export import (
    _svg_to_pdf_cached, _svg_to_jpg_cached,
    _build_multipage_pdf, _build_consolidated_pdf,
)
from helpers.port_logic import (
    get_sw_suffix, get_port_mappings, validate_port_counts, render_cable_summary,
)


def render():
    st.subheader("🤖 AI Assistant")
    st.caption("Ask questions about your current project in plain English. Runs locally via Ollama — no internet required.")
    st.markdown("---")

    # ── Connection settings ───────────────────────────────────
    _ai_c1, _ai_c2 = st.columns([3, 1])
    with _ai_c1:
        _ollama_host = st.text_input(
            "Ollama URL",
            value="http://host.docker.internal:11434",
            key="llm_ollama_host",
            help="Mac/Windows: host.docker.internal works. Linux: use http://172.17.0.1:11434"
        )
    with _ai_c2:
        st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
        # Cache probe result keyed on host URL — avoids a 3s blocking call on
        # every Streamlit rerun when Ollama is not running.
        _ollama_ck = f"_ollama_ok_{_ollama_host}"
        if _ollama_ck not in st.session_state:
            _ollama_ok = False
            _models    = []
            try:
                _chk = requests.get(f"{_ollama_host}/api/tags", timeout=3)
                if _chk.status_code == 200:
                    _ollama_ok = True
                    _models = [m["name"] for m in _chk.json().get("models", [])]
            except Exception:
                pass
            st.session_state[_ollama_ck]          = _ollama_ok
            st.session_state[f"_ollama_models_{_ollama_host}"] = _models
        else:
            _ollama_ok = st.session_state[_ollama_ck]
            _models    = st.session_state.get(f"_ollama_models_{_ollama_host}", [])
        if _ollama_ok:
            if st.button("🔄", key="llm_refresh", help="Re-check Ollama connection"):
                del st.session_state[_ollama_ck]
                st.rerun()
            st.success("🟢 Connected")
        else:
            if st.button("🔄", key="llm_refresh", help="Re-check Ollama connection"):
                del st.session_state[_ollama_ck]
                st.rerun()
            st.error("🔴 Ollama not found")

    if not _ollama_ok:
        st.info(
            "**Ollama is not running.** To get started:\n\n"
            "1. Download Ollama from **ollama.com** and install it\n"
            "2. Run: `ollama pull llama3.2:3b`\n"
            "3. Ollama starts automatically in the background\n\n"
            "Recommended model: `llama3.2:3b` (~2 GB, fast on CPU)"
        )
    elif not _models:
        st.warning(
            "Ollama is running but no models are installed.\n\n"
            "Run: `ollama pull llama3.2:3b`"
        )
    else:
        _ai_m1, _ai_m2 = st.columns([2, 1])
        with _ai_m1:
            _selected_model = st.selectbox("Model", options=_models, key="llm_model")
        with _ai_m2:
            st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Clear chat", use_container_width=True):
                st.session_state["llm_chat_history"] = []
                st.rerun()

        st.markdown("---")

        # ── Build project context ─────────────────────────────
        def _build_llm_context():
            _pfx        = st.session_state.get("cluster_name",    "UNKNOWN")
            _se         = st.session_state.get("se_name",         "Unknown SE")
            _cust       = st.session_state.get("customer",        "Unknown")
            _idate      = st.session_state.get("install_date",    "Unknown")
            _n_dbox     = int(st.session_state.get("proj_num_dboxes", 1))
            _n_cnode    = int(st.session_state.get("proj_num_cnodes", 4))
            _dbox_type  = st.session_state.get("proj_dbox_type",  "Unknown")
            _cnode_type = st.session_state.get("proj_cbox_type",  "Unknown")
            _topology   = st.session_state.get("proj_topology",   "Leaf Pair")
            _sw_model   = st.session_state.get("tab7_sw_model",   "Unknown")
            _sw_a_ip    = st.session_state.get("tab7_sw_a_ip",    "Not set")
            _sw_b_ip    = st.session_state.get("tab7_sw_b_ip",    "Not set")
            _vlan       = st.session_state.get("tab7_vlan",       "Not set")
            _ntp        = st.session_state.get("tab7_ntp",        "Not set")
            _mgmt_vlan  = st.session_state.get("tab7_mgmt_vlan",  "Not set")
            _gpu_on     = st.session_state.get("tab8_enabled",    False)
            _gpu_model  = st.session_state.get("tab8_sw_model",   "Unknown")
            _spine_on   = _topology == "Spine-Leaf"
            _spine_mdl  = st.session_state.get("spine_sw_model",  "Unknown")
            _vastver    = st.session_state.get("proj_vast_release", "Not set")
            _site_notes = st.session_state.get("proj_site_notes", "None")
            _sfdc       = st.session_state.get("proj_sfdc",       "")
            _ticket     = st.session_state.get("proj_ticket",     "")

            # Capacity from sizer if available
            _sizer_dbox   = st.session_state.get("sizer_dbox_type", _dbox_type)
            _sizer_ndbox  = int(st.session_state.get("sizer_num_dboxes", _n_dbox))

            return f"""You are an AI assistant embedded in the VAST SE Installation Toolkit. \
You help VAST Systems Engineers answer questions about their current cluster installation. \
Be concise and precise. If a question cannot be answered from the project data provided, say so clearly.

=== CURRENT PROJECT ===
Cluster:        {_pfx}
Customer:       {_cust}
SE:             {_se}
Install Date:   {_idate}
VastOS Version: {_vastver}
SFDC:           {_sfdc or "Not set"}
Ticket:         {_ticket or "Not set"}

=== HARDWARE ===
DBoxes:  {_n_dbox}x {_dbox_type}
CNodes:  {_n_cnode}x {_cnode_type}
Topology: {_topology}
Storage Switches: {_sw_model} ({'Spine-Leaf' if _spine_on else 'Leaf Pair'})
Spine Switches:   {'Enabled — ' + _spine_mdl if _spine_on else 'Not used'}
GPU/Data Switches: {'Enabled — ' + _gpu_model if _gpu_on else 'Not enabled'}

=== SWITCH CONFIG ===
Storage Switch A IP:  {_sw_a_ip}
Storage Switch B IP:  {_sw_b_ip}
Internal Storage VLAN: {_vlan}
Management VLAN:       {_mgmt_vlan}
NTP Server:            {_ntp or 'Not configured'}

=== SITE NOTES ===
{_site_notes}

=== VAST PLATFORM CONTEXT ===
- VAST is a shared-everything NFS/S3 flash storage platform
- DBoxes are storage nodes (all-flash), CNodes are stateless compute nodes
- Internal fabric uses RoCEv2 with MLAG leaf switch pairs
- MTU 9216 on all data paths, VLAN 69 for internal storage
- Dual NIC CNodes use separate storage and data network fabrics
"""

        # ── Chat interface ────────────────────────────────────
        if "llm_chat_history" not in st.session_state:
            st.session_state["llm_chat_history"] = []

        for _msg in st.session_state["llm_chat_history"]:
            with st.chat_message(_msg["role"]):
                st.markdown(_msg["content"])

        if _prompt := st.chat_input("Ask about your cluster…"):
            st.session_state["llm_chat_history"].append({"role": "user", "content": _prompt})
            with st.chat_message("user"):
                st.markdown(_prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        _messages = [{"role": "system", "content": _build_llm_context()}]
                        _messages += st.session_state["llm_chat_history"]
                        _resp = requests.post(
                            f"{_ollama_host}/api/chat",
                            json={"model": _selected_model, "messages": _messages, "stream": False},
                            timeout=120
                        )
                        _answer = _resp.json()["message"]["content"]
                        st.markdown(_answer)
                        st.session_state["llm_chat_history"].append({"role": "assistant", "content": _answer})
                    except Exception as _e:
                        st.error(f"LLM error: {_e}")




# ============================================================


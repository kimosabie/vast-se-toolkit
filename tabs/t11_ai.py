import os
import streamlit as st
import requests


# ---------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------

def _build_project_data() -> dict:
    """Pull all relevant session state into a plain dict."""
    return {
        "cluster_name":   st.session_state.get("cluster_name",       "UNKNOWN"),
        "customer":       st.session_state.get("customer",           "Unknown"),
        "se_name":        st.session_state.get("se_name",            "Unknown SE"),
        "install_date":   st.session_state.get("install_date",       "Unknown"),
        "vast_release":   st.session_state.get("proj_vast_release",  "Not set"),
        "sfdc":           st.session_state.get("proj_sfdc",          ""),
        "ticket":         st.session_state.get("proj_ticket",        ""),
        "num_dboxes":     int(st.session_state.get("proj_num_dboxes", 1)),
        "num_cnodes":     int(st.session_state.get("proj_num_cnodes", 4)),
        "dbox_type":      st.session_state.get("proj_dbox_type",     "Unknown"),
        "cnode_type":     st.session_state.get("proj_cbox_type",     "Unknown"),
        "topology":       st.session_state.get("proj_topology",      "Leaf Pair"),
        "sw_model":       st.session_state.get("tab7_sw_model",      "Unknown"),
        "sw_a_ip":        st.session_state.get("tab7_sw_a_ip",       "Not set"),
        "sw_b_ip":        st.session_state.get("tab7_sw_b_ip",       "Not set"),
        "vlan":           st.session_state.get("tab7_vlan",          "Not set"),
        "ntp":            st.session_state.get("tab7_ntp",           "Not set"),
        "mgmt_vlan":      st.session_state.get("tab7_mgmt_vlan",     "Not set"),
        "gpu_enabled":    st.session_state.get("tab8_enabled",       False),
        "gpu_model":      st.session_state.get("tab8_sw_model",      "Unknown"),
        "spine_model":    st.session_state.get("spine_sw_model",     "Unknown"),
        "site_notes":     st.session_state.get("proj_site_notes",    "None"),
        "dual_nic":       st.session_state.get("proj_dual_nic",      False),
    }


def _build_local_context(d: dict) -> str:
    spine_on = d["topology"] == "Spine-Leaf"
    return f"""You are an AI assistant embedded in the VAST SE Installation Toolkit. \
You help VAST Systems Engineers answer questions about their current cluster installation. \
Be concise and precise. If a question cannot be answered from the project data provided, say so clearly.

=== CURRENT PROJECT ===
Cluster:        {d['cluster_name']}
Customer:       {d['customer']}
SE:             {d['se_name']}
Install Date:   {d['install_date']}
VastOS Version: {d['vast_release']}
SFDC:           {d['sfdc'] or 'Not set'}
Ticket:         {d['ticket'] or 'Not set'}

=== HARDWARE ===
DBoxes:   {d['num_dboxes']}x {d['dbox_type']}
CNodes:   {d['num_cnodes']}x {d['cnode_type']}
Dual NIC: {'Yes' if d['dual_nic'] else 'No'}
Topology: {d['topology']}
Storage Switches:  {d['sw_model']} ({'Spine-Leaf' if spine_on else 'Leaf Pair'})
Spine Switches:    {'Enabled — ' + d['spine_model'] if spine_on else 'Not used'}
GPU/Data Switches: {'Enabled — ' + d['gpu_model'] if d['gpu_enabled'] else 'Not enabled'}

=== SWITCH CONFIG ===
Storage Switch A IP:   {d['sw_a_ip']}
Storage Switch B IP:   {d['sw_b_ip']}
Internal Storage VLAN: {d['vlan']}
Management VLAN:       {d['mgmt_vlan']}
NTP Server:            {d['ntp'] or 'Not configured'}

=== SITE NOTES ===
{d['site_notes']}

=== VAST PLATFORM CONTEXT ===
- VAST is a shared-everything NFS/S3 flash storage platform
- DBoxes are storage nodes (all-flash), CNodes are stateless compute nodes
- Internal fabric uses RoCEv2 with MLAG leaf switch pairs
- MTU 9216 on all data paths, VLAN 69 for internal storage
- Dual NIC CNodes use separate storage and data network fabrics
"""


def _build_cloud_context(d: dict) -> tuple[str, list[str]]:
    """Return (context_string, list_of_redacted_fields)."""
    spine_on = d["topology"] == "Spine-Leaf"
    redacted = [
        "Customer name", "Cluster name", "SE name", "Install date",
        "SFDC / ticket", "Switch IP addresses", "NTP server", "Site notes",
    ]
    return f"""You are an AI assistant helping a systems engineer with a storage cluster installation. \
Be concise and precise. If a question cannot be answered from the data provided, say so clearly.
Note: identifying details have been redacted before this context was sent to you.

=== HARDWARE ===
DBoxes:   {d['num_dboxes']}x {d['dbox_type']}
CNodes:   {d['num_cnodes']}x {d['cnode_type']}
Dual NIC: {'Yes' if d['dual_nic'] else 'No'}
Topology: {d['topology']}
Storage Switches:  {d['sw_model']} ({'Spine-Leaf' if spine_on else 'Leaf Pair'})
Spine Switches:    {'Enabled — ' + d['spine_model'] if spine_on else 'Not used'}
GPU/Data Switches: {'Enabled — ' + d['gpu_model'] if d['gpu_enabled'] else 'Not enabled'}
VastOS Version:    {d['vast_release']}

=== SWITCH CONFIG ===
Internal Storage VLAN: {d['vlan']}
Management VLAN:       {d['mgmt_vlan']}
NTP Server:            [REDACTED]
Switch IPs:            [REDACTED]

=== VAST PLATFORM CONTEXT ===
- VAST is a shared-everything NFS/S3 flash storage platform
- DBoxes are storage nodes (all-flash), CNodes are stateless compute nodes
- Internal fabric uses RoCEv2 with MLAG leaf switch pairs
- MTU 9216 on all data paths, VLAN 69 for internal storage
- Dual NIC CNodes use separate storage and data network fabrics
""", redacted


# ---------------------------------------------------------------------------
# LLM calls
# ---------------------------------------------------------------------------

def _call_ollama(host: str, model: str, messages: list) -> str:
    resp = requests.post(
        f"{host}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _call_claude(api_key: str, messages: list) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    # Separate system message from conversation
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    chat_msgs = [m for m in messages if m["role"] != "system"]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_msg,
        messages=chat_msgs,
    )
    return response.content[0].text


# ---------------------------------------------------------------------------
# Tab renderer
# ---------------------------------------------------------------------------

def render():
    st.subheader("🤖 AI Assistant")
    st.caption("Ask questions about your current project in plain English.")
    st.markdown("---")

    _ollama_host = "http://ollama:11434"
    _claude_key  = os.environ.get("CLAUDE_API_KEY", "").strip()

    # ── Connection check (cached per host) ────────────────────
    _ck = f"_ollama_ok_{_ollama_host}"
    if _ck not in st.session_state:
        _ollama_ok, _models = False, []
        try:
            _chk = requests.get(f"{_ollama_host}/api/tags", timeout=3)
            if _chk.status_code == 200:
                _ollama_ok = True
                _models = [m["name"] for m in _chk.json().get("models", [])]
        except Exception:
            pass
        st.session_state[_ck] = _ollama_ok
        st.session_state[f"_ollama_models_{_ollama_host}"] = _models
    else:
        _ollama_ok = st.session_state[_ck]
        _models    = st.session_state.get(f"_ollama_models_{_ollama_host}", [])

    # ── Mode selector ─────────────────────────────────────────
    _mode_options = []
    if _ollama_ok and _models:
        _mode_options.append("Local (Ollama)")
    if _claude_key:
        _mode_options.append("Cloud (Claude)")

    _status_col, _refresh_col = st.columns([5, 1])
    with _status_col:
        if _ollama_ok:
            st.success("🟢 Local AI ready")
        else:
            st.error("🔴 Local AI starting up — please wait or refresh")
    with _refresh_col:
        if st.button("🔄 Refresh", use_container_width=True):
            del st.session_state[_ck]
            st.rerun()

    if not _ollama_ok and not _claude_key:
        st.info(
            "Local AI (Ollama) is still starting up. This can take 1–2 minutes on first launch "
            "while the model downloads (~2 GB). Refresh once it's ready.\n\n"
            "To use cloud AI instead, add your `CLAUDE_API_KEY` to the `.env` file and restart."
        )
        return

    if not _mode_options:
        st.warning("Ollama is running but no models are installed yet. Please wait for the model download to complete.")
        return

    _c1, _c2 = st.columns([3, 1])
    with _c1:
        _mode = st.radio("AI mode", _mode_options, horizontal=True, key="llm_mode")
    with _c2:
        st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state["llm_chat_history"] = []
            st.session_state.pop("llm_cloud_acknowledged", None)
            st.rerun()

    _selected_model = None
    if _mode == "Local (Ollama)":
        _selected_model = st.selectbox("Model", options=_models, key="llm_model")

    # ── Cloud privacy acknowledgement ─────────────────────────
    if _mode == "Cloud (Claude)":
        if not st.session_state.get("llm_cloud_acknowledged"):
            st.warning(
                "**Before using cloud AI, review what is and isn't sent:**\n\n"
                "**Sent to Claude API (technical config only):**\n"
                "- Hardware: DBox/CNode counts and models, switch models, topology\n"
                "- Config: VLAN numbers, VastOS version, NIC mode\n\n"
                "**Redacted — never sent:**\n"
                "- Customer name, cluster name, SE name\n"
                "- SFDC case, ticket number, install date\n"
                "- Switch IP addresses, NTP server\n"
                "- Site notes\n\n"
                "Responses are faster but use Anthropic's API. "
                "Do not include customer names or IPs in your questions."
            )
            if st.button("✅ I understand — enable cloud AI"):
                st.session_state["llm_cloud_acknowledged"] = True
                st.session_state["llm_chat_history"] = []
                st.rerun()
            return

        st.info(
            "🔒 **Cloud mode active** — customer name, IPs, and site notes are redacted before sending. "
            "Do not include customer-identifying details in your questions."
        )

    st.markdown("---")

    # ── Chat ──────────────────────────────────────────────────
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
                    _data = _build_project_data()
                    if _mode == "Cloud (Claude)":
                        _ctx, _ = _build_cloud_context(_data)
                    else:
                        _ctx = _build_local_context(_data)

                    _messages = [{"role": "system", "content": _ctx}]
                    _messages += st.session_state["llm_chat_history"]

                    if _mode == "Cloud (Claude)":
                        _answer = _call_claude(_claude_key, _messages)
                    else:
                        _answer = _call_ollama(_ollama_host, _selected_model, _messages)

                    st.markdown(_answer)
                    st.session_state["llm_chat_history"].append(
                        {"role": "assistant", "content": _answer}
                    )
                except Exception as _e:
                    st.error(f"AI error: {_e}")

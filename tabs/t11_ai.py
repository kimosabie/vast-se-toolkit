import os
import streamlit as st
import requests

try:
    import db as _db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False


# ---------------------------------------------------------------------------
# API key resolution — env → db → None
# ---------------------------------------------------------------------------

def _resolve_key(env_var: str, db_key: str) -> tuple[str, str]:
    """Return (key, source) where source is 'env', 'db', or ''."""
    val = os.environ.get(env_var, "").strip()
    if val:
        return val, "env"
    if _DB_AVAILABLE:
        val = (_db.get_setting(db_key) or "").strip()
        if val:
            return val, "db"
    return "", ""


def _save_key(db_key: str, value: str):
    if _DB_AVAILABLE:
        _db.set_setting(db_key, value.strip())


def _clear_key(db_key: str):
    if _DB_AVAILABLE:
        _db.set_setting(db_key, "")


# ---------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------

def _build_project_data() -> dict:
    return {
        "cluster_name": st.session_state.get("cluster_name",       "UNKNOWN"),
        "customer":     st.session_state.get("customer",           "Unknown"),
        "se_name":      st.session_state.get("se_name",            "Unknown SE"),
        "install_date": st.session_state.get("install_date",       "Unknown"),
        "vast_release": st.session_state.get("proj_vast_release",  "Not set"),
        "sfdc":         st.session_state.get("proj_sfdc",          ""),
        "ticket":       st.session_state.get("proj_ticket",        ""),
        "num_dboxes":   int(st.session_state.get("proj_num_dboxes", 1)),
        "num_cnodes":   int(st.session_state.get("proj_num_cnodes", 4)),
        "dbox_type":    st.session_state.get("proj_dbox_type",     "Unknown"),
        "cnode_type":   st.session_state.get("proj_cbox_type",     "Unknown"),
        "topology":     st.session_state.get("proj_topology",      "Leaf Pair"),
        "sw_model":     st.session_state.get("tab7_sw_model",      "Unknown"),
        "sw_a_ip":      st.session_state.get("tab7_sw_a_ip",       "Not set"),
        "sw_b_ip":      st.session_state.get("tab7_sw_b_ip",       "Not set"),
        "vlan":         st.session_state.get("tab7_vlan",          "Not set"),
        "ntp":          st.session_state.get("tab7_ntp",           "Not set"),
        "mgmt_vlan":    st.session_state.get("tab7_mgmt_vlan",     "Not set"),
        "gpu_enabled":  st.session_state.get("tab8_enabled",       False),
        "gpu_model":    st.session_state.get("tab8_sw_model",      "Unknown"),
        "spine_model":  st.session_state.get("spine_sw_model",     "Unknown"),
        "site_notes":   st.session_state.get("proj_site_notes",    "None"),
        "dual_nic":     st.session_state.get("proj_dual_nic",      False),
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


def _build_cloud_context(d: dict) -> str:
    spine_on = d["topology"] == "Spine-Leaf"
    return f"""You are a VAST storage platform expert helping a systems engineer troubleshoot \
and answer complex technical questions. Be concise and precise.
Note: customer-identifying details have been redacted before this context was sent.

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
Switch IPs / NTP:      [REDACTED]

=== VAST PLATFORM CONTEXT ===
- VAST is a shared-everything NFS/S3 flash storage platform
- DBoxes are storage nodes (all-flash), CNodes are stateless compute nodes
- Internal fabric uses RoCEv2 with MLAG leaf switch pairs
- MTU 9216 on all data paths, VLAN 69 for internal storage
- Dual NIC CNodes use separate storage and data network fabrics
"""


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
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    chat_msgs  = [m for m in messages if m["role"] != "system"]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_msg,
        messages=chat_msgs,
    )
    return response.content[0].text


def _call_openai(api_key: str, messages: list) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def _call_gemini(api_key: str, messages: list) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    chat_msgs  = [m for m in messages if m["role"] != "system"]
    # Gemini uses "model" instead of "assistant" for history roles
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in chat_msgs[:-1]
    ]
    last_msg = chat_msgs[-1]["content"] if chat_msgs else ""
    model = genai.GenerativeModel("gemini-1.5-pro", system_instruction=system_msg)
    chat  = model.start_chat(history=history)
    response = chat.send_message(last_msg)
    return response.text


# ---------------------------------------------------------------------------
# Key management UI (rendered inside an expander)
# ---------------------------------------------------------------------------

def _render_key_manager():
    with st.expander("🔑 API Keys — Technical Expert", expanded=False):
        st.caption(
            "Keys are stored locally in the toolkit database. "
            "They never leave your machine except when making API calls. "
            "You can also set them in your `.env` file instead."
        )

        for label, env_var, db_key in [
            ("Anthropic (Claude)", "CLAUDE_API_KEY",  "claude_api_key"),
            ("OpenAI",             "OPENAI_API_KEY",  "openai_api_key"),
            ("Google Gemini",      "GEMINI_API_KEY",  "gemini_api_key"),
        ]:
            st.markdown(f"**{label}**")
            key_val, key_src = _resolve_key(env_var, db_key)

            if key_src == "env":
                st.success(f"Configured via `.env` — edit that file to change it.")
            else:
                col_input, col_save, col_clear = st.columns([4, 1, 1])
                with col_input:
                    entered = st.text_input(
                        f"{label} key",
                        value=key_val,
                        type="password",
                        label_visibility="collapsed",
                        placeholder=f"Paste {label} API key…",
                        key=f"ui_key_{db_key}",
                    )
                with col_save:
                    if st.button("Save", key=f"save_{db_key}", use_container_width=True):
                        if entered.strip():
                            _save_key(db_key, entered.strip())
                            st.success("Saved")
                            st.rerun()
                        else:
                            st.warning("Empty")
                with col_clear:
                    if key_val and st.button("Clear", key=f"clear_{db_key}", use_container_width=True):
                        _clear_key(db_key)
                        st.rerun()


# ---------------------------------------------------------------------------
# Chat UI (shared between both inner tabs)
# ---------------------------------------------------------------------------

def _render_chat(history_key: str, call_fn, system_context: str, placeholder: str):
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    col_spacer, col_clear = st.columns([6, 1])
    with col_clear:
        if st.button("🗑️ Clear", key=f"clear_chat_{history_key}", use_container_width=True):
            st.session_state[history_key] = []
            st.rerun()

    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(placeholder, key=f"input_{history_key}"):
        st.session_state[history_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    messages = [{"role": "system", "content": system_context}]
                    messages += st.session_state[history_key]
                    answer = call_fn(messages)
                    st.markdown(answer)
                    st.session_state[history_key].append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    st.error(f"AI error: {e}")


# ---------------------------------------------------------------------------
# Tab renderer
# ---------------------------------------------------------------------------

def render():
    st.subheader("🤖 AI Assistant")
    st.markdown("---")

    _ollama_host = "http://ollama:11434"

    # ── Ollama connection check (cached) ──────────────────────
    _ck = f"_ollama_ok_{_ollama_host}"
    if _ck not in st.session_state:
        _ollama_ok, _models = False, []
        try:
            r = requests.get(f"{_ollama_host}/api/tags", timeout=3)
            if r.status_code == 200:
                _ollama_ok = True
                _models = [m["name"] for m in r.json().get("models", [])]
        except Exception:
            pass
        st.session_state[_ck] = _ollama_ok
        st.session_state[f"_ollama_models_{_ollama_host}"] = _models
    else:
        _ollama_ok = st.session_state[_ck]
        _models    = st.session_state.get(f"_ollama_models_{_ollama_host}", [])

    # ── Status bar ────────────────────────────────────────────
    st_col, ref_col = st.columns([5, 1])
    with st_col:
        if _ollama_ok and _models:
            st.success("🟢 Local AI ready")
        elif _ollama_ok:
            st.warning("🟡 Ollama running — model still downloading")
        else:
            st.error("🔴 Local AI starting up")
    with ref_col:
        if st.button("🔄 Refresh", use_container_width=True):
            del st.session_state[_ck]
            st.rerun()

    # ── Key manager expander ──────────────────────────────────
    _render_key_manager()

    st.markdown("---")

    # ── Inner tabs ────────────────────────────────────────────
    ai_tab_local, ai_tab_expert = st.tabs(["📋 Project Assistant", "🔬 Technical Expert"])

    # ── Project Assistant (Ollama / local) ────────────────────
    with ai_tab_local:
        st.caption("Ask questions about your current project. Runs locally — nothing leaves your machine.")

        if not _ollama_ok:
            st.info(
                "Local AI is still starting up. This can take 1–2 minutes on first launch "
                "while the model downloads (~2 GB). Hit **🔄 Refresh** above once ready."
            )
        elif not _models:
            st.info("Ollama is running but the model is still downloading. Please wait and refresh.")
        else:
            _selected_model = st.selectbox("Model", options=_models, key="llm_model")
            _data = _build_project_data()
            _ctx  = _build_local_context(_data)

            def _ollama_call(messages):
                return _call_ollama(_ollama_host, _selected_model, messages)

            _render_chat(
                history_key="llm_project_history",
                call_fn=_ollama_call,
                system_context=_ctx,
                placeholder="Ask about your cluster config, cable counts, install steps…",
            )

    # ── Technical Expert (Claude / OpenAI) ───────────────────
    with ai_tab_expert:
        st.caption(
            "Troubleshooting and complex questions. Uses cloud AI — "
            "customer name, IPs, and site notes are **never sent**."
        )

        _claude_key,  _claude_src  = _resolve_key("CLAUDE_API_KEY",  "claude_api_key")
        _openai_key,  _openai_src  = _resolve_key("OPENAI_API_KEY",  "openai_api_key")
        _gemini_key,  _gemini_src  = _resolve_key("GEMINI_API_KEY",  "gemini_api_key")

        _providers = []
        if _claude_key:
            _providers.append("Claude (Anthropic)")
        if _openai_key:
            _providers.append("GPT-4o (OpenAI)")
        if _gemini_key:
            _providers.append("Gemini (Google)")

        if not _providers:
            st.info(
                "No cloud AI keys configured. "
                "Add your Claude or OpenAI key using the **🔑 API Keys** panel above."
            )
        else:
            _provider = st.radio(
                "Provider", _providers, horizontal=True, key="llm_expert_provider"
            )

            if not st.session_state.get("llm_expert_acknowledged"):
                st.warning(
                    "**Review what is and isn't sent to the cloud:**\n\n"
                    "✅ **Sent:** hardware config (DBox/CNode counts and models, switch models, "
                    "topology, VLANs, VastOS version)\n\n"
                    "🚫 **Redacted:** customer name, cluster name, SE name, SFDC/ticket, "
                    "install date, switch IPs, NTP server, site notes\n\n"
                    "Do not include customer names or IP addresses in your questions."
                )
                if st.button("✅ I understand — enable Technical Expert"):
                    st.session_state["llm_expert_acknowledged"] = True
                    st.rerun()
            else:
                st.info(
                    "🔒 **Redacted mode** — customer name, IPs, and site notes are never sent. "
                    "Keep questions technical."
                )

                _data = _build_project_data()
                _ctx  = _build_cloud_context(_data)

                def _expert_call(messages):
                    if _provider == "Claude (Anthropic)":
                        return _call_claude(_claude_key, messages)
                    if _provider == "Gemini (Google)":
                        return _call_gemini(_gemini_key, messages)
                    return _call_openai(_openai_key, messages)

                _render_chat(
                    history_key="llm_expert_history",
                    call_fn=_expert_call,
                    system_context=_ctx,
                    placeholder="Ask a troubleshooting or architecture question…",
                )

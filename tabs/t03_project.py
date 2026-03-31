import streamlit as st
from datetime import date
from config import HARDWARE_PROFILES, DBOX_PROFILES, CNODE_PERF


def render():
    st.subheader("📋 Project Details")
    st.caption(
        "Complete all sections before generating configs or the install plan. "
        "Fields marked ⚠️ are required."
    )

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
        _dbox_options = list(DBOX_PROFILES.keys())
        _dbox_current = st.session_state.get("proj_dbox_type", _dbox_options[0])
        if _dbox_current not in _dbox_options:
            _dbox_current = _dbox_options[0]
        proj_dbox_type = st.selectbox(
            "DBox Model",
            options=_dbox_options,
            index=_dbox_options.index(_dbox_current)
        )
        st.session_state["proj_dbox_type"] = proj_dbox_type

        _cnode_options = list(CNODE_PERF.keys())
        _cnode_raw = st.session_state.get("proj_cbox_type", _cnode_options[0])
        _cnode_current = _cnode_raw.replace(" CNode", "").strip()
        if _cnode_current not in _cnode_options:
            _cnode_current = _cnode_options[0]
        proj_cbox_type = st.selectbox(
            "CNode Generation",
            options=_cnode_options,
            index=_cnode_options.index(_cnode_current)
        )
        st.session_state["proj_cbox_type"] = proj_cbox_type
        proj_dual_nic   = st.toggle("CNodes have Dual NIC",
                            value=False, key="proj_dual_nic")
        if proj_dual_nic:
            st.caption(
                "Right port (BF-3) → Internal Switch (Tab 7) for storage.  \n"
                "Left port (CX7) → Data Switch (Tab 8) for client traffic.  \n"
                "Uplinks removed from Tab 7 storage switch config."
            )
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
        "NTP Server":       st.session_state.get("tab7_ntp",          ""),
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




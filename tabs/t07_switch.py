import streamlit as st
from datetime import date
from config import HARDWARE_PROFILES, SPEED_RANK
from helpers.context import get_ctx
from helpers.port_logic import (
    get_sw_suffix, get_port_mappings, validate_port_counts, render_cable_summary,
)
from jinja2 import Environment, FileSystemLoader
import os as _os


def render():
    ctx          = get_ctx()
    pfx          = ctx["pfx"]
    num_dboxes   = ctx["num_dboxes"]
    num_cnodes   = ctx["num_cnodes"]
    topology     = ctx["topology"]
    dbox_label   = ctx["dbox_label"]
    dnode_label  = ctx["dnode_label"]
    cnode_label  = ctx["cnode_label"]
    full_sw_a    = ctx["full_sw_a"]
    full_sw_b    = ctx["full_sw_b"]
    se_name      = ctx["se_name"]
    customer     = ctx["customer"]
    cluster_name = ctx["cluster_name"]
    install_date = ctx["install_date"]

    st.subheader("Internal Storage Fabric — Leaf Pair Configuration")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("#### Switch Selection")
        sw_model = st.selectbox(
            "Switch Model",
            options=list(HARDWARE_PROFILES.keys()),
            key="tab7_sw_model"
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
            key="tab7_dnode_start"
        )
        cnode_start = st.number_input(
            "CNode start port", min_value=1,
            max_value=profile["total_ports"],
            value=15 if profile["total_ports"] == 32 else 29,
            key="tab7_cnode_start"
        )

        st.markdown("#### Switch Networking")
        vlan_id = st.number_input(
            "Storage VLAN ID", min_value=1, max_value=4094,
            value=100, key="tab7_vlan"
        )
        sw_a_ip = st.text_input(
            "Switch A MGMT IP/mask", value="192.168.1.1/24",
            key="tab7_sw_a_ip"
        )
        sw_b_ip = st.text_input(
            "Switch B MGMT IP/mask", value="192.168.1.2/24",
            key="tab7_sw_b_ip"
        )
        mgmt_gw = st.text_input(
            "MGMT Gateway", value="192.168.1.254", key="tab7_gw"
        )
        mgmt_vlan = st.number_input(
            "Management VLAN ID", min_value=1, max_value=4094,
            value=int(st.session_state.get("tab7_mgmt_vlan", 1)),
            key="tab7_mgmt_vlan"
        )
        ntp_srv = st.text_input(
            "NTP Server", value="",
            placeholder="Enter customer NTP server IP",
            key="tab7_ntp"
        )

        st.markdown("#### ISL / Uplink Ports")
        isl_ports_input = st.text_input(
            "ISL Ports (comma separated)",
            value=",".join([f"swp{p}" for p in profile["default_isl"]]),
            key="tab7_isl"
        )
        uplink_ports_input = st.text_input(
            "Uplink Ports (comma separated)",
            value=",".join([f"swp{p}" for p in profile["default_uplink"]]),
            key="tab7_uplink"
        )
        isl_short = st.toggle(
            "ISL cable run is ≤1m (use DAC)",
            value=False, key="tab7_isl_short"
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

        # Dual NIC — second NIC handles client traffic via Tab 8 (Data Switch)
        # so the storage fabric switch does NOT need uplink ports to customer core.
        dual_nic = st.session_state.get("proj_dual_nic", False)
        if dual_nic:
            uplink_list = []
            st.info(
                "ℹ️ **Dual NIC mode** — uplink ports removed from storage fabric config. "
                "CNode right port (BF-3) connects to this switch for storage traffic. "
                "CNode left port (CX7) connects to the Data Switch (Tab 8) for client traffic."
            )

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
                    "hostname":      (full_sw_a if side == "A" else full_sw_b).replace(".", "-"),
                    "mgmt_ip":       sw_a_ip if side == "A" else sw_b_ip,
                    "mgmt_gw":       mgmt_gw,
                    "mgmt_vlan":     int(st.session_state.get("tab7_mgmt_vlan", 1)),
                    "ntp_server":    ntp_srv or mgmt_gw,
                    "vlan_id":       vlan_id,
                    "mtu":           profile["mtu"],
                    "isl_ports":     isl_list,
                    "uplink_ports":  uplink_list,
                    "clag_id":       100,
                    "mlag_mac":      "44:38:39:ff:00:01",
                    "uplink_description": "Customer-Core",
                    "is_gpu_switch": False,
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
                            f"{pfx}_VAST_SW{side}_"
                            f"{profile['vendor'].upper()}_"
                            f"{date.today().isoformat()}.txt"
                        ),
                        mime="text/plain",
                        key=f"tab7_dl_{side}"
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


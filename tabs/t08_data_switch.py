import streamlit as st
from datetime import date
from config import HARDWARE_PROFILES
from helpers.context import get_ctx
from helpers.port_logic import render_cable_summary
from jinja2 import Environment, FileSystemLoader
import os as _os


def render():
    ctx          = get_ctx()
    pfx          = ctx["pfx"]
    num_cnodes   = ctx["num_cnodes"]
    cnode_label  = ctx["cnode_label"]
    full_sw_a    = ctx["full_sw_a"]
    full_sw_b    = ctx["full_sw_b"]
    se_name      = ctx["se_name"]
    customer     = ctx["customer"]
    cluster_name = ctx["cluster_name"]
    install_date = ctx["install_date"]

    st.subheader("GPU / Data Network Switch — Leaf Pair Configuration")

    gpu_enabled = st.toggle(
        "Enable GPU / Data Network Switch Configuration",
        value=False, key="tab8_enabled"
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
                key="tab8_sw_model"
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
                key="tab8_cnode_start"
            )
            gpu_start2 = st.number_input(
                "GPU Server start port", min_value=1,
                max_value=profile2["total_ports"],
                value=15 if profile2["total_ports"] == 32 else 29,
                key="tab8_gpu_start"
            )
            num_gpu_servers = st.slider(
                "Number of GPU Servers",
                min_value=1, max_value=profile2["max_node_ports"],
                value=4, key="tab8_gpu_count"
            )
            gpu_nic_speed = st.selectbox(
                "GPU Server NIC Speed",
                options=["200GbE", "100GbE", "400GbE"],
                key="tab8_gpu_nic"
            )

            st.markdown("#### Switch Networking")
            gpu_vlans_input = st.text_input(
                "GPU Network VLAN IDs (comma separated, max 8)",
                value=st.session_state.get("tab8_vlans", ""),
                placeholder="e.g. 101, 102",
                key="tab8_vlans"
            )
            # Parse and validate
            _raw_vlans = [v.strip() for v in gpu_vlans_input.split(",") if v.strip()]
            _valid_vlans = []
            for _v in _raw_vlans[:8]:
                try:
                    _vid = int(_v)
                    if 1 <= _vid <= 4094:
                        _valid_vlans.append(_vid)
                except ValueError:
                    pass
            if len(_raw_vlans) > 8:
                st.warning("⚠️ Maximum 8 VLANs supported — only the first 8 will be used.")
            if gpu_vlans_input and not _valid_vlans:
                st.error("❌ No valid VLAN IDs found. Enter comma-separated integers between 1 and 4094.")
            sw_a_ip2  = st.text_input(
                "Switch A MGMT IP/mask", value="192.168.2.1/24",
                key="tab8_sw_a_ip"
            )
            sw_b_ip2  = st.text_input(
                "Switch B MGMT IP/mask", value="192.168.2.2/24",
                key="tab8_sw_b_ip"
            )
            mgmt_gw2  = st.text_input(
                "MGMT Gateway", value="192.168.2.254", key="tab8_gw"
            )
            mgmt_vlan2 = st.number_input(
                "Management VLAN ID", min_value=1, max_value=4094,
                value=int(st.session_state.get("tab8_mgmt_vlan", 1)),
                key="tab8_mgmt_vlan"
            )
            ntp_srv2  = st.text_input(
                "NTP Server", value="",
                placeholder="Enter customer NTP server IP",
                key="tab8_ntp"
            )

            st.markdown("#### ISL / Uplink Ports")
            isl_ports_input2 = st.text_input(
                "ISL Ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in profile2["default_isl"]]
                ),
                key="tab8_isl"
            )
            uplink_ports_input2 = st.text_input(
                "Uplink Ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in profile2["default_uplink"]]
                ),
                key="tab8_uplink"
            )
            isl_short2 = st.toggle(
                "ISL cable run is ≤1m (use DAC)",
                value=False, key="tab8_isl_short"
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
                    "VLANs":           ", ".join(str(v) for v in _valid_vlans) or "—",
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
                        ).replace(".", "-"),
                        "mgmt_ip":       sw_a_ip2 if side == "A" else sw_b_ip2,
                        "mgmt_gw":       mgmt_gw2,
                        "mgmt_vlan":     int(st.session_state.get("tab8_mgmt_vlan", 1)),
                        "ntp_server":    ntp_srv2 or mgmt_gw2,
                        "gpu_vlans":     _valid_vlans,
                        "vlan_id":       _valid_vlans[0] if _valid_vlans else 200,
                        "mtu":           profile2["mtu"],
                        "isl_ports":     isl_list2,
                        "uplink_ports":  uplink_list2,
                        "clag_id":       200,
                        "mlag_mac":      "44:38:39:ff:00:02",
                        "uplink_description": "Gigabrain-Firewall",
                        "is_gpu_switch": True,
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
                                f"{pfx}_VAST_GPU_SW{side}_"
                                f"{profile2['vendor'].upper()}_"
                                f"{date.today().isoformat()}.txt"
                            ),
                            mime="text/plain",
                            key=f"tab8_dl_{side}"
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
   - Allow VLANs {", ".join(str(v) for v in _valid_vlans) if _valid_vlans else "—"} on the port-channel
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
   - VLANs:        {", ".join(str(v) for v in _valid_vlans) if _valid_vlans else "—"}
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
                key="tab8_handoff_dl"
            )


# ============================================================


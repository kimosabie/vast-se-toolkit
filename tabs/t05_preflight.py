import streamlit as st
from datetime import date
from config import HARDWARE_PROFILES
from helpers.context import get_ctx
from helpers.port_logic import get_sw_suffix, get_port_mappings, validate_port_counts


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

    st.subheader("Pre-Flight, Validation & Installation")
    st.caption(
        "Run through each section in order. Complete all pre-flight checks before starting switch configuration."
    )

    # Grab state from other tabs
    profile_t3     = HARDWARE_PROFILES.get(
        st.session_state.get("tab7_sw_model",
        list(HARDWARE_PROFILES.keys())[0])
    )
    vlan_t3        = st.session_state.get("tab7_vlan",   100)
    sw_a_t3        = st.session_state.get("tab7_sw_a_ip","192.168.1.1/24")
    sw_b_t3        = st.session_state.get("tab7_sw_b_ip","192.168.1.2/24")
    ntp_t3         = st.session_state.get("tab7_ntp",    "")
    isl_t3         = st.session_state.get("tab7_isl",    "")
    dnode_st_t3    = int(st.session_state.get("tab7_dnode_start", 1))
    cnode_st_t3    = int(st.session_state.get("tab7_cnode_start", 15))
    isl_short_t3   = st.session_state.get("tab7_isl_short", False)
    isl_list_t3    = [p.strip() for p in isl_t3.split(",") if p.strip()]
    isl_cable_t3   = (
        profile_t3["isl_cable_short"] if isl_short_t3
        else profile_t3["isl_cable_long"]
    )
    gpu_enabled_t3 = st.session_state.get("tab8_enabled", False)
    sw_model_t3    = st.session_state.get(
        "tab7_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )

    sw_a_ip_only = sw_a_t3.split("/")[0]
    sw_b_ip_only = sw_b_t3.split("/")[0]


    proc_gpu_sw_a   = st.session_state.get("tab8_sw_a_ip", "192.168.2.1/24")
    proc_gpu_sw_b   = st.session_state.get("tab8_sw_b_ip", "192.168.2.2/24")

    # Build filenames matching what the toolkit generates
    today_str       = date.today().isoformat()
    vendor_up       = profile_t3["vendor"].upper()
    fname_sw_a      = f"{pfx}_VAST_SWA_{vendor_up}_{today_str}.txt"
    fname_sw_b      = f"{pfx}_VAST_SWB_{vendor_up}_{today_str}.txt"

    proc_gpu_model  = st.session_state.get(
        "tab8_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_gpu_profile = HARDWARE_PROFILES[proc_gpu_model]
    gpu_vendor_up   = proc_gpu_profile["vendor"].upper()
    fname_gpu_sw_a  = f"{pfx}_VAST_GPU_SWA_{gpu_vendor_up}_{today_str}.txt"
    fname_gpu_sw_b  = f"{pfx}_VAST_GPU_SWB_{gpu_vendor_up}_{today_str}.txt"

    spine_enabled   = topology == "Spine-Leaf"
    proc_spine_model = st.session_state.get(
        "spine_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_spine_profile = HARDWARE_PROFILES[proc_spine_model]
    spine_vendor_up = proc_spine_profile["vendor"].upper()
    fname_spine_a   = f"{pfx}_VAST_SPINE_A_{spine_vendor_up}_{today_str}.txt"
    fname_spine_b   = f"{pfx}_VAST_SPINE_B_{spine_vendor_up}_{today_str}.txt"

    proc_spine_a_ip = st.session_state.get("spine_a_ip", "192.168.3.1/24")
    proc_spine_b_ip = st.session_state.get("spine_b_ip", "192.168.3.2/24")

    TEMP_IP = "192.168.2.101/24"

    # ── Section 1: Equipment Checklist ──────────────────────
    st.markdown("---")
    st.markdown("### 1️⃣ Equipment Checklist")
    st.caption(
        "Quantities generated from session inputs. "
        "Add custom items at the bottom."
    )

    total_node_cables   = (num_dboxes * 2 * 2) + (num_cnodes * 2)
    total_isl_cables    = len(isl_list_t3)
    uplink_t3           = st.session_state.get("tab7_uplink", "")
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
    # ── Section 2: Port Count Validation ────────────────────
    st.markdown("---")
    st.markdown("### 2️⃣ Port Count Validation")

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

    # ── Section 3: Cable Pre-Check ───────────────────────────
    st.markdown("---")
    st.markdown("### 3️⃣ Cable Pre-Check")

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

    # ── Section 4: Cable Label Generator ────────────────────
    st.markdown("---")
    st.markdown("### 4️⃣ Cable Label Generator")
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

    # ── Section 5: Management & NTP Check ─────────────────────────
    st.markdown("---")
    st.markdown("### 5️⃣ Management & NTP Pre-Check")

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
            "Value":  st.session_state.get("tab7_gw", "—"),
            "Action": f"ping {st.session_state.get('tab7_gw', '—')}"
        },
        {
            "Check":  "NTP Server reachable",
            "Value":  ntp_t3 or "NOT SET",
            "Action": f"ping {ntp_t3}" if ntp_t3 else "❌ Set NTP first"
        },
    ])

    # ── Section 6: LLDP Validation Script ───────────────────
    st.markdown("---")
    st.markdown("### 6️⃣ Post-Cabling LLDP Validation")
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

    # ── Section 7: Pre-Flight Checklist ─────────────────────
    st.markdown("---")
    st.markdown("### 7️⃣ Pre-Flight Checklist")
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

    # ── Section 8: Prerequisites ─────────────────────────────
    st.markdown("---")
    st.markdown("### 8️⃣ Prerequisites")
    st.markdown(
        "Before touching any switch hardware, confirm the following:"
    )

    switch_list = [
        f"**{full_sw_a}** config file: `{fname_sw_a}`",
        f"**{full_sw_b}** config file: `{fname_sw_b}`",
    ]
    if gpu_enabled_t3:
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
                f"\nntpq -p\n# Look for * or + next to {ntp_t3}"
                if ntp_t3 else
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

    # ── Section 9: Internal Storage Fabric ──────────────────
    st.markdown("---")
    st.markdown("### 9️⃣ Internal Storage Fabric Switches")
    st.markdown(
        f"Switch model: **{sw_model_t3}**  \n"
        f"OS: **{'Cumulus NV' if profile_t3['os'] == 'cumulus' else 'Arista EOS'}**"
    )

    render_switch_procedure(
        switch_label    = f"Switch A — {full_sw_a}",
        hostname        = full_sw_a,
        mgmt_ip         = sw_a_t3,
        config_filename = fname_sw_a,
        switch_side     = "A",
        is_primary      = True,
        peer_ip         = sw_b_t3.split("/")[0]
    )

    render_switch_procedure(
        switch_label    = f"Switch B — {full_sw_b}",
        hostname        = full_sw_b,
        mgmt_ip         = sw_b_t3,
        config_filename = fname_sw_b,
        switch_side     = "B",
        is_primary      = False,
        peer_ip         = sw_a_t3.split("/")[0]
    )

    # ── Section 10: GPU Switches ──────────────────────────────
    if gpu_enabled_t3:
        st.markdown("---")
        st.markdown("### 🔟 GPU / Data Network Switches")
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

    # ── Section 11: Spine Switches ────────────────────────────
    if spine_enabled:
        spine_vsuffix   = get_sw_suffix(proc_spine_model)
        spine_a_name    = f"{pfx}-{spine_vsuffix}-SPINE-A"
        spine_b_name    = f"{pfx}-{spine_vsuffix}-SPINE-B"

        st.markdown("---")
        st.markdown("### 1️⃣1️⃣ Spine Switches")
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

    # ── Section 12: Post-Config Validation ───────────────────
    st.markdown("---")
    st.markdown("### 1️⃣2️⃣ Post-Config Validation")
    st.markdown(
        "Run these checks on **every switch** after all configs are applied."
    )

    st.markdown("#### MLAG Validation")
    st.markdown(
        "Run on both switches. One must show `primary`, "
        "the other `secondary`. Both must show `peer-alive: True`."
    )
    st.code("nv show mlag", language="bash")

    sw_a_ip_only = sw_a_t3.split("/")[0]
    sw_b_ip_only = sw_b_t3.split("/")[0]

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
        f"# All node ports should show {profile_t3['mtu']}",
        language="bash"
    )

    st.markdown("#### LLDP Validation")
    st.markdown(
        "Once all nodes are cabled, run the LLDP validation script "
        "from **Section 6 above**. "
        f"Confirm all **{(num_dboxes * 2) + num_cnodes}** "
        "expected nodes are visible before starting VAST bootstrap."
    )

    st.success(
        "✅ All switches validated — ready for VAST bootstrap."
    )



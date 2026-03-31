import streamlit as st

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



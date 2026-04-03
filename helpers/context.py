"""Shared derived-value helpers used by tab render() functions."""
from datetime import date, datetime
import streamlit as st
from config import HARDWARE_PROFILES
from helpers.port_logic import get_sw_suffix


def build_sw_name(sw_num, ru_val, vendor_sfx, pfx, include_ru,
                  gpu=False, spine=False):
    """Construct a switch hostname from project naming settings."""
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


def get_ctx():
    """Return a dict of all derived values from session state.
    Call at the top of every tab render() function."""
    ss = st.session_state
    pfx          = ss.get("cluster_name", "") or "VAST"
    num_dboxes   = int(ss.get("proj_num_dboxes", 1))
    num_cnodes   = int(ss.get("proj_num_cnodes", 4))
    topology     = ss.get("proj_topology", "Leaf Pair")
    include_ru   = ss.get("include_ru", False)
    dbox_label   = ss.get("name_dbox",  "DBOX")
    dnode_label  = ss.get("name_dnode", "DNODE")
    cnode_label  = ss.get("name_cnode", "CNODE")
    dbox_ru_raw  = ss.get("dbox_ru_raw",  "")
    cnode_ru_raw = ss.get("cnode_ru_raw", "")
    dbox_ru_list = [l.strip() for l in dbox_ru_raw.split("\n")  if l.strip()]
    cnode_ru_list= [l.strip() for l in cnode_ru_raw.split("\n") if l.strip()]
    sw1_ru       = ss.get("sw1_ru", "")
    sw2_ru       = ss.get("sw2_ru", "")
    sw_model     = ss.get("tab7_sw_model", list(HARDWARE_PROFILES.keys())[0])
    vendor_sfx   = get_sw_suffix(sw_model)
    se_name      = ss.get("se_name",      "")
    customer     = ss.get("customer",     "")
    cluster_name = ss.get("cluster_name", "")
    install_date = ss.get("install_date", str(date.today()))
    full_sw_a    = build_sw_name(1, sw1_ru, vendor_sfx, pfx, include_ru)
    full_sw_b    = build_sw_name(2, sw2_ru, vendor_sfx, pfx, include_ru)
    return dict(
        pfx=pfx, num_dboxes=num_dboxes, num_cnodes=num_cnodes,
        topology=topology, include_ru=include_ru,
        dbox_label=dbox_label, dnode_label=dnode_label, cnode_label=cnode_label,
        dbox_ru_list=dbox_ru_list, cnode_ru_list=cnode_ru_list,
        sw1_ru=sw1_ru, sw2_ru=sw2_ru,
        sw_model=sw_model, vendor_suffix=vendor_sfx,
        se_name=se_name, customer=customer,
        cluster_name=cluster_name, install_date=install_date,
        full_sw_a=full_sw_a, full_sw_b=full_sw_b,
    )


def get_switch_ctx(pfx):
    """Return all switch-related state values and derived filenames.
    Used by t04_confluence and t05_preflight to avoid duplicating ~20
    identical session_state reads in each file.
    pfx should come from get_ctx()["pfx"].
    """
    ss = st.session_state
    hw_keys = list(HARDWARE_PROFILES.keys())

    # ── Leaf switch ────────────────────────────────────────────────
    sw_model   = ss.get("tab7_sw_model",      hw_keys[0])
    profile    = HARDWARE_PROFILES[sw_model]
    sw_a_ip    = ss.get("tab7_sw_a_ip",       "192.168.1.1/24")
    sw_b_ip    = ss.get("tab7_sw_b_ip",       "192.168.1.2/24")
    mgmt_gw    = ss.get("tab7_gw",            "192.168.1.254")
    ntp        = ss.get("tab7_ntp",           "")
    vlan       = ss.get("tab7_vlan",          100)
    isl        = ss.get("tab7_isl",           "")
    uplink     = ss.get("tab7_uplink",        "")
    isl_short  = ss.get("tab7_isl_short",     False)
    dnode_start = int(ss.get("tab7_dnode_start", 1))
    cnode_start = int(ss.get("tab7_cnode_start", 15))
    isl_list   = [p.strip() for p in isl.split(",") if p.strip()]
    uplink_list = [p.strip() for p in uplink.split(",") if p.strip()]
    isl_cable  = profile["isl_cable_short"] if isl_short else profile["isl_cable_long"]
    vendor_up  = profile["vendor"].upper()

    # ── Data / GPU switch ──────────────────────────────────────────
    gpu_enabled  = ss.get("tab8_enabled",    False)
    gpu_model    = ss.get("tab8_sw_model",   hw_keys[0])
    gpu_profile  = HARDWARE_PROFILES[gpu_model]
    gpu_sw_a_ip  = ss.get("tab8_sw_a_ip",   "192.168.2.1/24")
    gpu_sw_b_ip  = ss.get("tab8_sw_b_ip",   "192.168.2.2/24")
    gpu_vendor_up = gpu_profile["vendor"].upper()

    # ── Spine switch ───────────────────────────────────────────────
    spine_model   = ss.get("spine_sw_model", hw_keys[0])
    spine_profile = HARDWARE_PROFILES[spine_model]
    spine_a_ip    = ss.get("spine_a_ip",     "192.168.3.1/24")
    spine_b_ip    = ss.get("spine_b_ip",     "192.168.3.2/24")
    spine_ntp     = ss.get("spine_ntp",      "")
    spine_vendor_up = spine_profile["vendor"].upper()

    # ── Derived IPs ────────────────────────────────────────────────
    sw_a_ip_only     = sw_a_ip.split("/")[0]
    sw_b_ip_only     = sw_b_ip.split("/")[0]
    cidr             = sw_a_ip.split("/")[1] if "/" in sw_a_ip else "24"
    gpu_a_ip_only    = gpu_sw_a_ip.split("/")[0]
    gpu_b_ip_only    = gpu_sw_b_ip.split("/")[0]
    spine_a_ip_only  = spine_a_ip.split("/")[0]
    spine_b_ip_only  = spine_b_ip.split("/")[0]

    # ── Config filenames ───────────────────────────────────────────
    today_str   = date.today().isoformat()
    fname_sw_a  = f"{pfx}_VAST_SWA_{vendor_up}_{today_str}.txt"
    fname_sw_b  = f"{pfx}_VAST_SWB_{vendor_up}_{today_str}.txt"
    fname_gpu_a = f"{pfx}_VAST_GPU_SWA_{gpu_vendor_up}_{today_str}.txt"
    fname_gpu_b = f"{pfx}_VAST_GPU_SWB_{gpu_vendor_up}_{today_str}.txt"
    fname_sp_a  = f"{pfx}_VAST_SPINE_A_{spine_vendor_up}_{today_str}.txt"
    fname_sp_b  = f"{pfx}_VAST_SPINE_B_{spine_vendor_up}_{today_str}.txt"

    return dict(
        # leaf
        sw_model=sw_model, profile=profile, vendor_up=vendor_up,
        sw_a_ip=sw_a_ip, sw_b_ip=sw_b_ip, mgmt_gw=mgmt_gw,
        ntp=ntp, vlan=vlan, isl=isl, uplink=uplink,
        isl_short=isl_short, isl_list=isl_list, uplink_list=uplink_list,
        isl_cable=isl_cable,
        dnode_start=dnode_start, cnode_start=cnode_start,
        sw_a_ip_only=sw_a_ip_only, sw_b_ip_only=sw_b_ip_only, cidr=cidr,
        # gpu
        gpu_enabled=gpu_enabled, gpu_model=gpu_model, gpu_profile=gpu_profile,
        gpu_sw_a_ip=gpu_sw_a_ip, gpu_sw_b_ip=gpu_sw_b_ip,
        gpu_a_ip_only=gpu_a_ip_only, gpu_b_ip_only=gpu_b_ip_only,
        gpu_vendor_up=gpu_vendor_up,
        # spine
        spine_model=spine_model, spine_profile=spine_profile,
        spine_a_ip=spine_a_ip, spine_b_ip=spine_b_ip, spine_ntp=spine_ntp,
        spine_a_ip_only=spine_a_ip_only, spine_b_ip_only=spine_b_ip_only,
        spine_vendor_up=spine_vendor_up,
        # filenames
        today_str=today_str,
        fname_sw_a=fname_sw_a, fname_sw_b=fname_sw_b,
        fname_gpu_a=fname_gpu_a, fname_gpu_b=fname_gpu_b,
        fname_sp_a=fname_sp_a, fname_sp_b=fname_sp_b,
    )

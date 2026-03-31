"""Shared derived-value helpers used by tab render() functions."""
from datetime import date
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

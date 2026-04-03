import streamlit as st
from config import HARDWARE_PROFILES, DBOX_PROFILES, CNODE_PERF
from helpers.context import get_ctx
from helpers.svg_export import _svg_to_jpg_cached
from helpers.network_svg import render_net_diagram_svg
import base64 as _b64m


def render():
    ctx         = get_ctx()
    pfx         = ctx["pfx"]
    num_dboxes  = ctx["num_dboxes"]
    num_cnodes  = ctx["num_cnodes"]
    topology    = ctx["topology"]
    dbox_label  = ctx["dbox_label"]
    cnode_label = ctx["cnode_label"]

    st.subheader("🗺️ Network Diagram")
    st.caption(
        "Layered logical topology built from your project settings. "
        "Add customer servers in the Device Inventory tab to show them here."
    )
    st.markdown("---")

    # ── Read project state ─────────────────────────────────────────
    _nd_sw_model    = st.session_state.get("tab7_sw_model",  list(HARDWARE_PROFILES.keys())[0])
    _nd_spine_model = st.session_state.get("spine_sw_model", list(HARDWARE_PROFILES.keys())[0])
    _nd_gpu_model   = st.session_state.get("tab8_sw_model",  list(HARDWARE_PROFILES.keys())[0])
    _nd_dbox_model  = st.session_state.get("proj_dbox_type", list(DBOX_PROFILES.keys())[0])
    _nd_cnode_model = st.session_state.get("proj_cbox_type", list(CNODE_PERF.keys())[0])
    _nd_dual_nic    = st.session_state.get("proj_dual_nic",  False)
    _nd_gpu_on      = st.session_state.get("tab8_enabled",   False)
    _nd_custom_devs = st.session_state.get("rack_custom_devices", [])

    _nd_svg, _nd_w, _nd_h = render_net_diagram_svg(
        pfx           = pfx,
        num_dboxes    = num_dboxes,
        num_cnodes    = num_cnodes,
        topology      = topology,
        dual_nic      = _nd_dual_nic,
        gpu_enabled   = _nd_gpu_on,
        sw_model      = _nd_sw_model,
        spine_model   = _nd_spine_model,
        gpu_sw_model  = _nd_gpu_model,
        dbox_model    = _nd_dbox_model,
        cnode_model   = _nd_cnode_model,
        dbox_label    = dbox_label,
        cnode_label   = cnode_label,
        custom_devices= _nd_custom_devs,
    )

    # Display — embed as base64 SVG in an <img> tag via st.markdown.
    _nd_b64 = _b64m.b64encode(_nd_svg.encode()).decode()
    st.markdown(
        f'<img src="data:image/svg+xml;base64,{_nd_b64}" '
        f'style="width:100%;height:auto;display:block;border-radius:6px;" />',
        unsafe_allow_html=True,
    )

    # ── Info strip ─────────────────────────────────────────────────
    st.markdown("---")
    _nc1, _nc2, _nc3, _nc4 = st.columns(4)
    _nc1.metric("DNodes", num_dboxes)
    _nc2.metric("CNodes", num_cnodes)
    _nc3.metric("Topology", topology)
    _nc4.metric("Data Switch", "Yes" if _nd_gpu_on else "No")
    if _nd_dual_nic:
        st.info(
            "**Dual NIC** — CNode right port (BF-3) → Storage fabric  ·  "
            "CNode left port (CX7) → Data Switch"
        )
    if not _nd_custom_devs:
        st.caption(
            "No customer devices defined — add servers/hosts in the "
            "**Device Inventory** tab to show them in the Customer Servers layer."
        )

    # ── Export ─────────────────────────────────────────────────────
    st.markdown("---")
    _ne1, _ne2 = st.columns(2)
    with _ne1:
        st.download_button(
            "⬇️ Download SVG",
            data=_nd_svg.encode(),
            file_name=f"{pfx}_network_topology.svg",
            mime="image/svg+xml",
            use_container_width=True,
        )
    with _ne2:
        try:
            _nd_png_dl = _svg_to_jpg_cached(_nd_svg, _nd_w * 2, _nd_h * 2)
            st.download_button(
                "⬇️ Download PNG",
                data=_nd_png_dl,
                file_name=f"{pfx}_network_topology.png",
                mime="image/png",
                use_container_width=True,
            )
        except Exception:
            st.caption("PNG export unavailable (cairosvg not installed)")

import streamlit as st
from datetime import date
from config import (
    HARDWARE_PROFILES, SPEED_RANK, DBOX_PROFILES, CNODE_PERF,
    DEVICE_SPECS, DEVICE_IMAGES, DEVICE_IMAGE_MAP, DR_ESTIMATES,
)
from helpers.context import get_ctx, build_sw_name
from helpers.images import _get_device_img_b64, _strip_white_bg
from helpers.svg_export import (
    _svg_to_pdf_cached, _svg_to_jpg_cached,
    _build_multipage_pdf, _build_consolidated_pdf,
)
from helpers.port_logic import (
    get_sw_suffix, get_port_mappings, validate_port_counts, render_cable_summary,
)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    import db as _db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False

_INV_CACHE_KEY = "_inv_devices_cache"

def _get_inventory_cached():
    if _INV_CACHE_KEY not in st.session_state:
        st.session_state[_INV_CACHE_KEY] = _db.list_inventory_devices() if _DB_AVAILABLE else []
    return st.session_state[_INV_CACHE_KEY]


def render():
    ctx          = get_ctx()
    pfx          = ctx["pfx"]
    num_dboxes   = ctx["num_dboxes"]
    num_cnodes   = ctx["num_cnodes"]
    topology     = ctx["topology"]
    install_date = ctx["install_date"]

    st.subheader("📐 Rack Diagram")
    st.caption("Configure rack constraints and device placement. The diagram auto-splits into multiple racks if limits are exceeded.")

    st.markdown("---")

    rack_col1, rack_col2 = st.columns([1, 2])

    with rack_col1:
        st.markdown("### 🗄️ Rack Constraints")
        rack_u          = st.number_input("Rack Height (U)", min_value=10, max_value=52, value=42, key="rack_u")
        rack_use_kw     = st.toggle("Show power in kW", value=True, key="rack_use_kw")
        _power_unit     = "kW" if rack_use_kw else "W"
        _power_div      = 1000 if rack_use_kw else 1
        rack_max_power_kw = st.number_input(
            f"Max Power per Rack ({_power_unit})",
            min_value=0.0,
            value=10.0 if rack_use_kw else 10000.0,
            step=0.5 if rack_use_kw else 500.0,
            key="rack_max_power_kw"
        )
        rack_max_power  = int(rack_max_power_kw * _power_div)  # always in W internally
        rack_use_lbs    = st.toggle("Show weight in lbs", value=False, key="rack_use_lbs")
        _weight_unit    = "lbs" if rack_use_lbs else "kg"
        _weight_conv    = 1.0 if rack_use_lbs else 0.453592
        rack_max_weight_disp = st.number_input(
            f"Max Weight per Rack ({_weight_unit})",
            min_value=0.0,
            value=1134.0 if rack_use_lbs else 500.0,
            step=50.0 if rack_use_lbs else 25.0,
            key="rack_max_weight_disp"
        )
        rack_max_weight = rack_max_weight_disp / _weight_conv  # always in lbs internally
        rack_top_down   = st.toggle("Top-down orientation (U1 at top)", value=False, key="rack_top_down")

        st.markdown("### 📦 Device Placement")

        _dbox_model  = st.session_state.get("proj_dbox_type",  list(DBOX_PROFILES.keys())[0])
        _cnode_gen   = st.session_state.get("proj_cbox_type",  list(CNODE_PERF.keys())[0])
        _sw_model    = st.session_state.get("tab7_sw_model",   list(HARDWARE_PROFILES.keys())[0])
        _gpu_model   = st.session_state.get("tab8_sw_model",   list(HARDWARE_PROFILES.keys())[0])
        _gpu_enabled = st.session_state.get("tab8_enabled",    False)
        _spine_topo  = topology == "Spine-Leaf"
        _spine_model = st.session_state.get("spine_sw_model",  list(HARDWARE_PROFILES.keys())[0])

        _dbox_spec   = DEVICE_SPECS.get(_dbox_model,  {"u": 1, "weight_lbs": 50,  "avg_w": 750,  "max_w": 850})
        _cnode_spec  = DEVICE_SPECS.get(_cnode_gen,   {"u": 1, "weight_lbs": 44,  "avg_w": 500,  "max_w": 775})
        _sw_spec     = DEVICE_SPECS.get(_sw_model,    {"u": 1, "weight_lbs": 25,  "avg_w": 250,  "max_w": 630})
        _gpu_spec    = DEVICE_SPECS.get(_gpu_model,   {"u": 1, "weight_lbs": 25,  "avg_w": 250,  "max_w": 630})
        _spine_spec  = DEVICE_SPECS.get(_spine_model, {"u": 1, "weight_lbs": 25,  "avg_w": 250,  "max_w": 630})

        rack_multi      = st.toggle("Multiple Racks", value=False, key="rack_multi")
        num_racks       = st.slider("Number of Racks", min_value=1, max_value=4, value=2, key="rack_num_racks") if rack_multi else 1

        # Build per-device template (all devices, no RU yet)
        _tpl = []
        _tpl.append({"Device": "Storage SW-A",  "type": "switch",     "u": _sw_spec["u"],    "color": "#E8821A", "model_key": _sw_model,    "weight": _sw_spec["weight_lbs"],    "avg_w": _sw_spec["avg_w"],    "max_w": _sw_spec["max_w"]})
        _tpl.append({"Device": "Storage SW-B",  "type": "switch",     "u": _sw_spec["u"],    "color": "#E8821A", "model_key": _sw_model,    "weight": _sw_spec["weight_lbs"],    "avg_w": _sw_spec["avg_w"],    "max_w": _sw_spec["max_w"]})
        if _gpu_enabled:
            _tpl.append({"Device": "GPU SW-A",  "type": "gpu_switch", "u": _gpu_spec["u"],   "color": "#8B5CF6", "model_key": _gpu_model,   "weight": _gpu_spec["weight_lbs"],   "avg_w": _gpu_spec["avg_w"],   "max_w": _gpu_spec["max_w"]})
            _tpl.append({"Device": "GPU SW-B",  "type": "gpu_switch", "u": _gpu_spec["u"],   "color": "#8B5CF6", "model_key": _gpu_model,   "weight": _gpu_spec["weight_lbs"],   "avg_w": _gpu_spec["avg_w"],   "max_w": _gpu_spec["max_w"]})
        if _spine_topo:
            _tpl.append({"Device": "Spine SW-A","type": "spine",      "u": _spine_spec["u"], "color": "#EF4444", "model_key": _spine_model, "weight": _spine_spec["weight_lbs"], "avg_w": _spine_spec["avg_w"], "max_w": _spine_spec["max_w"]})
            _tpl.append({"Device": "Spine SW-B","type": "spine",      "u": _spine_spec["u"], "color": "#EF4444", "model_key": _spine_model, "weight": _spine_spec["weight_lbs"], "avg_w": _spine_spec["avg_w"], "max_w": _spine_spec["max_w"]})
        for _i in range(1, num_cnodes + 1):
            _tpl.append({"Device": f"{pfx}-CNODE-{_i}", "type": "cnode", "u": _cnode_spec["u"], "color": "#16A34A", "model_key": _cnode_gen,  "weight": _cnode_spec["weight_lbs"], "avg_w": _cnode_spec["avg_w"], "max_w": _cnode_spec["max_w"]})
        for _i in range(1, num_dboxes + 1):
            _tpl.append({"Device": f"{pfx}-DBOX-{_i}",  "type": "dbox",  "u": _dbox_spec["u"],  "color": "#2563EB", "model_key": _dbox_model, "weight": _dbox_spec["weight_lbs"],  "avg_w": _dbox_spec["avg_w"],  "max_w": _dbox_spec["max_w"]})

        # Append user-uploaded custom devices
        for _cd in st.session_state.get("rack_custom_devices", []):
            _tpl.append({
                "Device":    _cd["name"],
                "type":      "custom",
                "u":         _cd["u"],
                "color":     "#6B7280",
                "model_key": _cd.get("product_name") or _cd.get("vendor", "") or "Custom",
                "img_b64":   _cd.get("img_b64", ""),
                "weight":    _cd["weight_lbs"],
                "avg_w":     _cd["avg_w"],
                "max_w":     _cd["max_w"],
            })

        # ── Add Device from Inventory ─────────────────────────
        st.markdown("### ➕ Add Device")
        _inv_all_rack = _get_inventory_cached()
        if not _inv_all_rack:
            st.caption("Your device inventory is empty — go to the **📦 Device Inventory** tab to add products.")
        else:
            _pick_opts = ["— select a product —"] + [d["product_name"] for d in _inv_all_rack]
            _pick_col1, _pick_col2, _pick_col3, _pick_col4 = st.columns([3, 2, 1, 1])
            with _pick_col1:
                _pick_product = st.selectbox("Product", _pick_opts, key="rack_pick_product")
            with _pick_col2:
                _pick_dname = st.text_input("Device Name", key="rack_pick_dname",
                                             placeholder="defaults to product name")
            with _pick_col3:
                _pick_rack = st.selectbox("Rack No.", options=list(range(1, num_racks + 1)),
                                           key="rack_pick_rack",
                                           disabled=(num_racks == 1))
            with _pick_col4:
                st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
                _pick_disabled = (_pick_product == "— select a product —")
                if st.button("+ Add", key="rack_pick_add", disabled=_pick_disabled,
                             use_container_width=True):
                    _sel_inv = next((d for d in _inv_all_rack if d["product_name"] == _pick_product), None)
                    if _sel_inv:
                        st.session_state["_pending_rack_add"] = {
                            "name":         _pick_dname.strip() or _sel_inv["product_name"],
                            "product_name": _sel_inv["product_name"],
                            "u":            _sel_inv["u_height"],
                            "weight_lbs":   _sel_inv["weight_lbs"],
                            "avg_w":        _sel_inv["avg_w"],
                            "max_w":        _sel_inv["max_w"],
                            "img_b64":      _sel_inv["img_b64"],
                            "rack_no":      int(_pick_rack),
                        }
                        st.rerun()
            # Show selected product specs as a hint
            if _pick_product != "— select a product —":
                _hint = next((d for d in _inv_all_rack if d["product_name"] == _pick_product), None)
                if _hint:
                    _hint_v = f" · {_hint['vendor']}" if _hint["vendor"] else ""
                    st.caption(
                        f"{_hint['category']}{_hint_v} · {_hint['u_height']}U · "
                        f"{_hint['weight_lbs']:.0f} lbs · {_hint['avg_w']}W avg / {_hint['max_w']}W max"
                    )

        # ── Devices added to this rack ───────────────────────
        _existing_custom = st.session_state.get("rack_custom_devices", [])
        if _existing_custom:
            st.markdown("**In this rack:**")
            for _ci, _cd in enumerate(_existing_custom):
                _crl, _crr = st.columns([6, 1])
                with _crl:
                    _prod_lbl = (f' <span style="color:#888">({_cd["product_name"]})</span>'
                                 if _cd.get("product_name") and _cd["product_name"] != _cd["name"]
                                 else "")
                    st.markdown(
                        f'<p style="font-size:12px;margin:4px 0">'
                        f'<b>{_cd["name"]}</b>{_prod_lbl} — '
                        f'{_cd["u"]}U · {_cd["weight_lbs"]:.0f} lbs · '
                        f'{_cd["avg_w"]}W avg / {_cd["max_w"]}W max'
                        f'{"  📷" if _cd.get("img_b64") else ""}</p>',
                        unsafe_allow_html=True,
                    )
                with _crr:
                    if st.button("✕", key=f"rack_cust_rm_{_ci}",
                                 help="Remove from this rack"):
                        st.session_state["_pending_rack_rm"] = _ci
                        st.rerun()

        # Compute sequential defaults
        _def_ru = {}
        _cur_ru = 1
        for _t in _tpl:
            _def_ru[_t["Device"]] = _cur_ru
            _cur_ru += _t["u"]

        # Per-device placement rows — individual widgets, no data_editor
        _hc1, _hc2, _hc3, _hc4 = st.columns([2, 2, 1, 2])
        _hc1.caption("Device Name")
        _hc2.caption("Model / Type")
        _hc3.caption("Rack")
        _hc4.caption("Start RU")

        _device_placement = {}
        for _t in _tpl:
            _k  = _t["Device"].replace(" ", "_").replace("-", "_")
            _dc1, _dc2, _dc3, _dc4 = st.columns([2, 2, 1, 2])
            with _dc1:
                st.markdown(f'<p style="font-size:12px;margin:8px 0 0 0">{_t["Device"]}</p>', unsafe_allow_html=True)
            with _dc2:
                st.markdown(f'<p style="font-size:11px;color:#aaa;margin:8px 0 0 0">{_t["model_key"]}</p>', unsafe_allow_html=True)
            with _dc3:
                _rack_val = st.selectbox("Rack", options=list(range(1, num_racks + 1)),
                                         key=f"rack_rack_{_k}", label_visibility="collapsed")
            with _dc4:
                _ru_val = st.number_input("RU", min_value=1, max_value=int(rack_u), step=1,
                                          key=f"rack_ru_{_k}", label_visibility="collapsed")
            _device_placement[_t["Device"]] = {"rack": _rack_val, "ru": _ru_val}

    with rack_col2:
        st.markdown("### 📊 Power & Weight Analysis")

        # Build device list from per-device placement widgets
        devices = []
        for _t in _tpl:
            _pl = _device_placement.get(_t["Device"], {"rack": 1, "ru": _def_ru.get(_t["Device"], 1)})
            devices.append({
                "name":      _t["Device"],
                "ru":        int(_pl["ru"]),
                "rack":      int(_pl["rack"]),
                "u":         _t["u"],
                "weight":    _t["weight"],
                "avg_w":     _t["avg_w"],
                "max_w":     _t["max_w"],
                "color":     _t["color"],
                "type":      _t["type"],
                "model_key": _t["model_key"],
                "img_b64":   _t.get("img_b64", ""),
            })

        # Group devices by rack, sort each rack by RU
        rack_groups = [[] for _ in range(num_racks)]
        for _d in devices:
            _ri = max(0, min(_d["rack"] - 1, num_racks - 1))
            rack_groups[_ri].append(_d)
        for _grp in rack_groups:
            _grp.sort(key=lambda d: d["ru"])

        # Totals (across all racks)
        devices = [d for grp in rack_groups for d in grp]
        total_weight = sum(d["weight"] for d in devices)
        total_avg_w  = sum(d["avg_w"]  for d in devices)
        total_max_w  = sum(d["max_w"]  for d in devices)
        total_u_used = sum(d["u"]      for d in devices)

        # Metrics
        _disp_weight = lambda w: f"{w * _weight_conv:.0f} {_weight_unit}"
        _disp_power  = lambda p: f"{p / _power_div:.1f} {_power_unit}" if rack_use_kw else f"{p:,}W"

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total U Used", f"{total_u_used}U")
        with m2:
            st.metric(f"Total Weight ({_weight_unit})", _disp_weight(total_weight))
        with m3:
            st.metric(f"Avg Power ({_power_unit})", _disp_power(total_avg_w))
        with m4:
            st.metric("Racks", num_racks)

        # Warnings per rack
        for _ri, _grp in enumerate(rack_groups):
            _rw = sum(d["weight"] for d in _grp)
            _rp = sum(d["avg_w"]  for d in _grp)
            if _rw > rack_max_weight:
                st.warning(f"⚠️ Rack {_ri+1} weight ({_disp_weight(_rw)}) exceeds limit ({_disp_weight(rack_max_weight)}).")
            if _rp > rack_max_power:
                st.warning(f"⚠️ Rack {_ri+1} avg power ({_disp_power(_rp)}) exceeds limit ({_disp_power(rack_max_power)}).")

        # Power & weight table
        # ── SVG Rack Diagram ─────────────────────────────────
        st.markdown("### 🖥️ Rack Diagram")

        def _render_rack(rack_devices, rack_num, rack_u_height, top_down,
                         with_summary=False, use_kw=True, use_lbs=False, display_scale=1.0,
                         light_theme=False):
            """Render a single rack as SVG.
            with_summary=True appends a device list + totals table below the diagram.
            display_scale < 1.0 shrinks the rendered SVG for screen display via viewBox scaling.
            light_theme=True uses a white/print-friendly colour scheme (used for PDF/JPG exports).
            """
            # ── Colour theme ─────────────────────────────────────
            if light_theme:
                T = dict(
                    page_bg    = "white",
                    hdr_fill   = "#ccd3e8",
                    hdr_text   = "#111",
                    body_fill  = "#dde2f0",
                    body_stroke= "#000",
                    umark      = "#555",
                    divider    = "#bbc",
                    slot_fill  = "#eaeff7",
                    slot_stroke= "#99a",
                    name_text  = "#222",
                    sum_title  = "#444",
                    sum_hdr    = "#666",
                    sum_div    = "#bbb",
                    row_even   = "#f0f0f6",
                    row_odd    = "#e8e8f2",
                    row_text   = "#222",
                    tot_fill   = "#dde3f0",
                    tot_text   = "#111",
                )
            else:
                T = dict(
                    page_bg    = "#1a1a2e",
                    hdr_fill   = "#000000",
                    hdr_text   = "white",
                    body_fill  = "#000000",
                    body_stroke= "#000000",
                    umark      = "#555",
                    divider    = "#1a1a1a",
                    slot_fill  = "#000000",
                    slot_stroke= "#1a1a1a",
                    name_text  = "#ddd",
                    sum_title  = "#aaa",
                    sum_hdr    = "#888",
                    sum_div    = "#444",
                    row_even   = "#1e1e2e",
                    row_odd    = "#161626",
                    row_text   = "#ccc",
                    tot_fill   = "#2d2d44",
                    tot_text   = "white",
                )

            U_H      = 40      # pixels per U
            RK_W     = 360     # rack interior width (reduced to make room for name column)
            LABEL_W  = 28      # U label column width (left)
            NAME_W   = 160     # device name column width (right)
            NAME_GAP = 8       # gap between rack edge and name column
            PAD      = 10      # outer padding
            HDR_H    = 36      # rack header height
            BAR_W    = 6       # colour bar width
            SVG_W    = PAD + LABEL_W + RK_W + NAME_GAP + NAME_W + PAD
            RACK_H   = HDR_H + rack_u_height * U_H + PAD * 2

            # Summary table geometry (only relevant when with_summary=True)
            ROW_H    = 16
            SUM_PAD  = 14     # gap between rack and table
            SUM_HDR  = 22     # "Device Summary" title height
            COL_HDR  = 18     # column header row height
            TOT_H    = 20     # totals row height
            n_devs   = len(rack_devices)
            SUM_H    = SUM_PAD + SUM_HDR + COL_HDR + n_devs * ROW_H + 4 + TOT_H + PAD

            SVG_H = RACK_H + (SUM_H if with_summary else 0)

            _out_w = int(SVG_W * display_scale)
            _out_h = int(SVG_H * display_scale)
            lines = [
                f'<svg width="{_out_w}" height="{_out_h}" viewBox="0 0 {SVG_W} {SVG_H}" '
                f'xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'style="font-family: Arial, sans-serif; background: {T["page_bg"]};">',
                # Explicit background rect (cairosvg ignores CSS background property)
                f'<rect x="0" y="0" width="{SVG_W}" height="{SVG_H}" fill="{T["page_bg"]}"/>',
                f'<defs><clipPath id="clip{rack_num}"><rect x="{PAD+LABEL_W+BAR_W+1}" '
                f'y="{PAD+HDR_H}" width="{RK_W-BAR_W-2}" height="{rack_u_height*U_H}"/>'
                f'</clipPath></defs>',
                # Rack header (spans rack body only, not name column)
                f'<rect x="{PAD}" y="{PAD}" width="{LABEL_W + RK_W}" height="{HDR_H}" '
                f'rx="4" fill="{T["hdr_fill"]}"/>',
                f'<text x="{PAD + (LABEL_W + RK_W)//2}" y="{PAD + HDR_H//2 + 5}" '
                f'text-anchor="middle" fill="{T["hdr_text"]}" font-size="12" font-weight="bold">'
                f'Rack {rack_num} — {rack_u_height}U</text>',
                # Rack body background
                f'<rect x="{PAD + LABEL_W}" y="{PAD + HDR_H}" width="{RK_W}" '
                f'height="{rack_u_height * U_H}" fill="{T["body_fill"]}"/>',
                # Outer border encompassing header + body
                f'<rect x="{PAD}" y="{PAD}" width="{LABEL_W + RK_W}" height="{HDR_H + rack_u_height * U_H}" '
                f'rx="4" fill="none" stroke="{T["body_stroke"]}" stroke-width="2"/>',
            ]

            # U position markers and slot dividers
            for u in range(1, rack_u_height + 1):
                if top_down:
                    y = PAD + HDR_H + (u - 1) * U_H
                else:
                    y = PAD + HDR_H + (rack_u_height - u) * U_H
                lines.append(
                    f'<text x="{PAD + LABEL_W - 4}" y="{y + U_H//2 + 4}" '
                    f'text-anchor="end" fill="{T["umark"]}" font-size="9">{u}</text>'
                )
                if u > 1:
                    lines.append(
                        f'<line x1="{PAD + LABEL_W}" y1="{y}" x2="{PAD + LABEL_W + RK_W}" y2="{y}" '
                        f'stroke="{T["divider"]}" stroke-width="0.5"/>'
                    )

            # Draw devices
            for d in rack_devices:
                ru_start = d["ru"]
                height_u = d["u"]
                if top_down:
                    y = PAD + HDR_H + (ru_start - 1) * U_H
                else:
                    y = PAD + HDR_H + (rack_u_height - ru_start - height_u + 1) * U_H

                block_h = height_u * U_H - 2
                color   = d["color"]

                lines.append(
                    f'<rect x="{PAD + LABEL_W + 2}" y="{y + 1}" '
                    f'width="{RK_W - 4}" height="{block_h}" '
                    f'rx="2" fill="{T["slot_fill"]}" stroke="{T["slot_stroke"]}" stroke-width="1"/>'
                )
                lines.append(
                    f'<rect x="{PAD + LABEL_W + 2}" y="{y + 1}" '
                    f'width="{BAR_W}" height="{block_h}" '
                    f'rx="2" fill="{color}"/>'
                )
                # Device image — custom upload takes precedence over built-in
                _b64 = d.get("img_b64") or _get_device_img_b64(d.get("model_key", ""))
                if _b64 and block_h >= 14:
                    # Strip white backgrounds for cleaner rendering on both themes
                    _b64 = _strip_white_bg(_b64)
                    _ih = block_h - 2
                    _iw = RK_W - BAR_W - 2
                    _ix = PAD + LABEL_W + BAR_W + 1
                    _iy = y + 1
                    # Use both href (SVG 2) and xlink:href (SVG 1.1) for cairosvg compat
                    lines.append(
                        f'<image x="{_ix}" y="{_iy}" '
                        f'width="{_iw}" height="{_ih}" '
                        f'href="data:image/png;base64,{_b64}" '
                        f'xlink:href="data:image/png;base64,{_b64}" '
                        f'preserveAspectRatio="xMidYMid meet" '
                        f'clip-path="url(#clip{rack_num})"/>'
                    )
                # Device name in right-hand label column, vertically centred on slot
                _name_x  = PAD + LABEL_W + RK_W + NAME_GAP
                _name_y  = y + max(block_h // 2, 1) + 4
                _fs      = 9 if block_h < 24 else 10
                lines.append(
                    f'<text x="{_name_x}" y="{_name_y}" fill="{T["name_text"]}" font-size="{_fs}" '
                    f'dominant-baseline="auto">{d["name"]}</text>'
                )

            # ── Outer rack frame (drawn last so it sits over device edges) ──
            if light_theme:
                _frame_x = PAD + LABEL_W
                _frame_y = PAD
                _frame_w = RK_W
                _frame_h = HDR_H + rack_u_height * U_H
                # Header/body separator
                lines.append(
                    f'<line x1="{_frame_x}" y1="{PAD + HDR_H}" '
                    f'x2="{_frame_x + _frame_w}" y2="{PAD + HDR_H}" '
                    f'stroke="#000" stroke-width="1.5"/>'
                )
                # Outer frame
                lines.append(
                    f'<rect x="{_frame_x}" y="{_frame_y}" width="{_frame_w}" height="{_frame_h}" '
                    f'fill="none" stroke="#000" stroke-width="3" rx="2"/>'
                )

            # ── Summary table (download only) ──────────────────
            if with_summary and rack_devices:
                _w_conv  = 1.0 if use_lbs else 0.453592
                _w_unit  = "lbs" if use_lbs else "kg"
                _p_div   = 1000.0 if use_kw else 1.0
                _p_unit  = "kW" if use_kw else "W"

                def _fw(lbs):
                    v = lbs * _w_conv
                    return f"{v:.0f} {_w_unit}"

                def _fp(w):
                    if use_kw:
                        return f"{w / _p_div:.2f} {_p_unit}"
                    return f"{int(w)} {_p_unit}"

                ty      = RACK_H + SUM_PAD  # top of summary block
                x0      = PAD               # left margin

                # Column x positions
                cx_name = x0
                cx_u    = x0 + 248
                cx_w    = x0 + 290
                cx_ap   = x0 + 360
                cx_mp   = x0 + 430

                # Section title
                lines.append(
                    f'<text x="{x0}" y="{ty + 14}" fill="{T["sum_title"]}" font-size="11" font-weight="bold">'
                    f'Device Summary — Rack {rack_num}</text>'
                )
                ty += SUM_HDR

                # Column headers
                for cx, label in [(cx_name, "Device"), (cx_u, "U"),
                                   (cx_w, f"Weight ({_w_unit})"),
                                   (cx_ap, f"Avg ({_p_unit})"),
                                   (cx_mp, f"Max ({_p_unit})")]:
                    lines.append(
                        f'<text x="{cx}" y="{ty + 12}" fill="{T["sum_hdr"]}" font-size="9" font-weight="bold">'
                        f'{label}</text>'
                    )
                ty += COL_HDR
                lines.append(
                    f'<line x1="{x0}" y1="{ty}" x2="{x0 + LABEL_W + RK_W}" y2="{ty}" '
                    f'stroke="{T["sum_div"]}" stroke-width="0.5"/>'
                )

                # Device rows
                tot_u = tot_w = tot_ap = tot_mp = 0
                for idx, d in enumerate(rack_devices):
                    row_y    = ty + idx * ROW_H
                    row_fill = T["row_even"] if idx % 2 == 0 else T["row_odd"]
                    lines.append(
                        f'<rect x="{x0}" y="{row_y}" width="{LABEL_W + RK_W}" height="{ROW_H}" '
                        f'fill="{row_fill}"/>'
                    )
                    # colour dot
                    lines.append(
                        f'<rect x="{cx_name}" y="{row_y + 5}" width="6" height="6" '
                        f'rx="1" fill="{d["color"]}"/>'
                    )
                    row_data = [
                        (cx_name + 10, d["name"]),
                        (cx_u,         str(d["u"])),
                        (cx_w,         _fw(d["weight"])),
                        (cx_ap,        _fp(d["avg_w"])),
                        (cx_mp,        _fp(d["max_w"])),
                    ]
                    for rx, rv in row_data:
                        lines.append(
                            f'<text x="{rx}" y="{row_y + ROW_H - 4}" fill="{T["row_text"]}" font-size="9">'
                            f'{rv}</text>'
                        )
                    tot_u  += d["u"]
                    tot_w  += d["weight"]
                    tot_ap += d["avg_w"]
                    tot_mp += d["max_w"]

                ty += n_devs * ROW_H + 4
                lines.append(
                    f'<line x1="{x0}" y1="{ty}" x2="{x0 + LABEL_W + RK_W}" y2="{ty}" '
                    f'stroke="{T["sum_div"]}" stroke-width="1"/>'
                )
                ty += 2

                # Totals row
                lines.append(
                    f'<rect x="{x0}" y="{ty}" width="{LABEL_W + RK_W}" height="{TOT_H}" '
                    f'fill="{T["tot_fill"]}"/>'
                )
                for rx, rv in [
                    (cx_name + 10, "TOTAL"),
                    (cx_u,         str(tot_u)),
                    (cx_w,         _fw(tot_w)),
                    (cx_ap,        _fp(tot_ap)),
                    (cx_mp,        _fp(tot_mp)),
                ]:
                    lines.append(
                        f'<text x="{rx}" y="{ty + TOT_H - 5}" fill="{T["tot_text"]}" font-size="9" font-weight="bold">'
                        f'{rv}</text>'
                    )

            lines.append('</svg>')
            return "\n".join(lines)

        # ── Display SVGs (scaled down for on-screen view) ────
        _DISP_SCALE = 0.62
        # ROW_H=16, SUM overhead ≈ SUM_PAD+SUM_HDR+COL_HDR+TOT_H+PAD = 14+22+18+20+14 = 88
        _disp_summary_h = lambda n_devs: int((88 + n_devs * 16) * _DISP_SCALE)
        _disp_rack_h = int((36 + rack_u * 40 + 20) * _DISP_SCALE)  # HDR_H + rack body + PAD*2
        svg_cols = st.columns(min(num_racks, 3))
        for _ri, _rack_devs in enumerate(rack_groups):
            _disp_svg = _render_rack(_rack_devs, _ri + 1, rack_u, rack_top_down,
                                     with_summary=True, display_scale=_DISP_SCALE,
                                     light_theme=True)
            _disp_h = _disp_rack_h + _disp_summary_h(len(_rack_devs)) + 20
            with svg_cols[_ri % len(svg_cols)]:
                st.components.v1.html(_disp_svg, height=_disp_h, scrolling=False)

        # ── Downloads ─────────────────────────────────────────
        # PDF/JPG are generated on demand (button click) to avoid
        # blocking cairosvg conversions on every render.
        try:
            import cairosvg as _cairosvg_probe  # noqa: F401
            _cairosvg_ok = True
        except ImportError:
            _cairosvg_ok = False

        # Paper size dimensions at 150 dpi (landscape only)
        _PAPER_SIZES = {
            "A4 Landscape": (1754, 1240),
            "A3 Landscape": (2480, 1754),
        }

        st.markdown("#### ⬇️ Downloads")

        if _cairosvg_ok:
            _pdf_size = st.radio(
                "PDF paper size",
                options=list(_PAPER_SIZES.keys()),
                horizontal=True,
                key="rack_pdf_size",
            )
            _pdf_w, _pdf_h = _PAPER_SIZES[_pdf_size]

        for _ri, _rack_devs in enumerate(rack_groups):
            _base_fname = f"{pfx or 'rack'}_rack{_ri + 1}_{install_date}"
            if num_racks > 1:
                st.caption(f"Rack {_ri + 1}")

            # Download SVG computed here — fast string ops, no cairosvg
            _dl_svg = _render_rack(_rack_devs, _ri + 1, rack_u, rack_top_down,
                                   with_summary=True, use_kw=rack_use_kw, use_lbs=rack_use_lbs,
                                   display_scale=1.0, light_theme=True)

            _dl_c1, _dl_c2, _dl_c3 = st.columns(3)

            with _dl_c1:
                st.download_button(
                    "⬇️ SVG",
                    data=_dl_svg,
                    file_name=f"{_base_fname}.svg",
                    mime="image/svg+xml",
                    key=f"rack_dl_svg_{_ri}",
                    use_container_width=True,
                )

            if _cairosvg_ok:
                _pdf_ss = f"_rack_pdf_{_ri}"
                _jpg_ss = f"_rack_jpg_{_ri}"
                _pdf_size_ss = f"_rack_pdf_size_{_ri}"

                # Invalidate cached PDF if paper size changed
                if st.session_state.get(_pdf_size_ss) != _pdf_size and _pdf_ss in st.session_state:
                    del st.session_state[_pdf_ss]

                with _dl_c2:
                    if _pdf_ss in st.session_state:
                        st.download_button(
                            "⬇️ PDF",
                            data=st.session_state[_pdf_ss],
                            file_name=f"{_base_fname}.pdf",
                            mime="application/pdf",
                            key=f"rack_dl_pdf_{_ri}",
                            use_container_width=True,
                        )
                    else:
                        if st.button("🔄 Generate PDF", key=f"rack_gen_pdf_{_ri}",
                                     use_container_width=True):
                            st.session_state[_pdf_ss] = _svg_to_pdf_cached(_dl_svg, _pdf_w, _pdf_h)
                            st.session_state[_pdf_size_ss] = _pdf_size
                            st.rerun()

                with _dl_c3:
                    if _jpg_ss in st.session_state:
                        st.download_button(
                            "⬇️ JPG",
                            data=st.session_state[_jpg_ss],
                            file_name=f"{_base_fname}.jpg",
                            mime="image/jpeg",
                            key=f"rack_dl_jpg_{_ri}",
                            use_container_width=True,
                        )
                    else:
                        if st.button("🔄 Generate JPG", key=f"rack_gen_jpg_{_ri}",
                                     use_container_width=True):
                            st.session_state[_jpg_ss] = _svg_to_jpg_cached(_dl_svg, _pdf_w, _pdf_h)
                            st.rerun()

        # ── Multi-rack PDF exports ────────────────────────────
        if _cairosvg_ok and num_racks > 1:
            st.markdown("---")
            st.markdown("##### 📑 Multi-Rack PDF Exports")
            _all_svgs = tuple(
                _render_rack(grp, i + 1, rack_u, rack_top_down,
                             with_summary=True, use_kw=rack_use_kw, use_lbs=rack_use_lbs,
                             display_scale=1.0, light_theme=True)
                for i, grp in enumerate(rack_groups)
            )
            _all_fname = f"{pfx or 'rack'}_all_racks_{install_date}"
            _mp_ss  = "_rack_pdf_multipage"
            _co_ss  = "_rack_pdf_consolidated"
            _mp_sz  = "_rack_pdf_multipage_size"
            _co_sz  = "_rack_pdf_consolidated_size"

            # Invalidate if paper size changed
            if st.session_state.get(_mp_sz) != _pdf_size and _mp_ss in st.session_state:
                del st.session_state[_mp_ss]
            if st.session_state.get(_co_sz) != _pdf_size and _co_ss in st.session_state:
                del st.session_state[_co_ss]

            _exp_c1, _exp_c2 = st.columns(2)

            with _exp_c1:
                if _mp_ss in st.session_state:
                    st.download_button(
                        "⬇️ All Racks PDF (1 per page)",
                        data=st.session_state[_mp_ss],
                        file_name=f"{_all_fname}_multipage.pdf",
                        mime="application/pdf",
                        key="rack_dl_pdf_multipage",
                        use_container_width=True,
                    )
                else:
                    if st.button("🔄 Generate All Racks PDF (1 per page)",
                                 key="rack_gen_pdf_multipage", use_container_width=True):
                        st.session_state[_mp_ss] = _build_multipage_pdf(_all_svgs, _pdf_w, _pdf_h)
                        st.session_state[_mp_sz] = _pdf_size
                        st.rerun()

            with _exp_c2:
                if _co_ss in st.session_state:
                    st.download_button(
                        "⬇️ Consolidated PDF (all racks on 1 page)",
                        data=st.session_state[_co_ss],
                        file_name=f"{_all_fname}_consolidated.pdf",
                        mime="application/pdf",
                        key="rack_dl_pdf_consolidated",
                        use_container_width=True,
                    )
                else:
                    if st.button("🔄 Generate Consolidated PDF (all racks on 1 page)",
                                 key="rack_gen_pdf_consolidated", use_container_width=True):
                        st.session_state[_co_ss] = _build_consolidated_pdf(_all_svgs, _pdf_w, _pdf_h)
                        st.session_state[_co_sz] = _pdf_size
                        st.rerun()

        # Legend
        st.markdown("---")
        _has_custom = bool(st.session_state.get("rack_custom_devices"))
        legend = [
            ("#2563EB", "DBox"),
            ("#16A34A", "CNode"),
            ("#E8821A", "Storage Switch"),
            ("#8B5CF6", "GPU Switch"),
            ("#EF4444", "Spine Switch"),
        ]
        if _has_custom:
            legend.append(("#6B7280", "Custom"))
        legend_cols = st.columns(len(legend))
        for i, (color, label) in enumerate(legend):
            with legend_cols[i]:
                st.markdown(
                    f'<span style="background:{color};padding:2px 8px;border-radius:3px;'
                    f'color:white;font-size:12px">■ {label}</span>',
                    unsafe_allow_html=True
                )

        # ── Device Power & Weight Table ──────────────────────
        st.markdown("---")
        st.markdown("### 📋 Device Power & Weight Details")
        _wlabel  = f"Weight ({_weight_unit})"
        _aplabel = f"Avg Power ({_power_unit})"
        _mplabel = f"Max Power ({_power_unit})"
        _detail_rows = []
        for d in devices:
            _detail_rows.append({
                "Device":  d["name"],
                "Rack":    d.get("rack", 1),
                "RU":      f"U{d['ru']}",
                "Height":  f"{d['u']}U",
                _wlabel:   round(d["weight"] * _weight_conv, 1),
                _aplabel:  round(d["avg_w"] / _power_div, 2) if rack_use_kw else d["avg_w"],
                _mplabel:  round(d["max_w"] / _power_div, 2) if rack_use_kw else d["max_w"],
            })
        _detail_rows.append({
            "Device": "TOTAL", "Rack": "—", "RU": "—", "Height": f"{total_u_used}U",
            _wlabel:  round(total_weight * _weight_conv, 1),
            _aplabel: round(total_avg_w / _power_div, 2) if rack_use_kw else total_avg_w,
            _mplabel: round(total_max_w / _power_div, 2) if rack_use_kw else total_max_w,
        })
        import pandas as _pd2
        _detail_df = _pd2.DataFrame(_detail_rows)
        st.dataframe(_detail_df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download as CSV",
            data=_detail_df.to_csv(index=False),
            file_name=f"{pfx or 'rack'}_power_weight.csv",
            mime="text/csv",
        )

        # Hardware Photo Gallery
        st.markdown("---")
        with st.expander("📷 Hardware Reference Gallery", expanded=False):
            _gallery_devices = []
            # Add devices in use
            if _sw_model in DEVICE_IMAGES:
                _gallery_devices.append((_sw_model, "Storage Switch"))
            if _gpu_enabled and _gpu_model in DEVICE_IMAGES:
                _gallery_devices.append((_gpu_model, "GPU Switch"))
            if _spine_topo and _spine_model in DEVICE_IMAGES:
                _gallery_devices.append((_spine_model, "Spine Switch"))
            if _cnode_gen in DEVICE_IMAGES:
                _gallery_devices.append((_cnode_gen, "CNode"))
            if _dbox_model in DEVICE_IMAGES:
                _gallery_devices.append((_dbox_model, "DBox"))

            if _gallery_devices:
                _gcols = st.columns(min(len(_gallery_devices), 3))
                for _gi, (_gname, _glabel) in enumerate(_gallery_devices):
                    with _gcols[_gi % len(_gcols)]:
                        import base64 as _b64
                        _img_data = DEVICE_IMAGES[_gname]
                        st.markdown(f"**{_glabel}**  \n{_gname}")
                        st.markdown(
                            f'<img src="data:image/png;base64,{_img_data}" style="width:100%;border-radius:4px;border:1px solid #444">',
                            unsafe_allow_html=True
                        )
            else:
                st.caption("No device images available for current selection.")



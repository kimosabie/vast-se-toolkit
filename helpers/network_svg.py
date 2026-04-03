"""Network topology SVG builder — extracted from tabs/t12_network.py."""
from helpers.images import _get_device_img_b64, _strip_white_bg


def render_net_diagram_svg(
    pfx, num_dboxes, num_cnodes, topology, dual_nic, gpu_enabled,
    sw_model, spine_model, gpu_sw_model, dbox_model, cnode_model,
    dbox_label, cnode_label, custom_devices,
):
    """
    Returns (svg_string, width, height).
    Layered top-to-bottom:
      1. Customer Network (cloud)
      2. Customer Servers  (rack_custom_devices if any, else generic)
      3. Data Switches     (if gpu_enabled)
      4. VAST CNodes
      5a. Spine Switches   (if Spine-Leaf)
      5b. Leaf Switches
      6. VAST DNodes
    Dotted separator lines between each layer.
    """
    # ── Constants ──────────────────────────────────────────────────
    MAX_SHOW     = 6
    DW, DH       = 148, 72
    HGAP         = 22
    VGAP         = 90
    MARGIN       = 24
    W            = 1200
    CX           = W // 2
    CLOUD_W, CLOUD_H = 240, 64

    # ── Colours ────────────────────────────────────────────────────
    C = dict(
        bg           = "#f4f5fa",
        leaf_fill    = "#1a4fa0",
        spine_fill   = "#2e6b3e",
        data_fill    = "#7a3b8c",
        dbox_fill    = "#c45200",
        cnode_fill   = "#0d6e8a",
        server_fill  = "#3a3a5c",
        cloud_fill   = "#dce8f9",
        cloud_stroke = "#5580b8",
        cloud_text   = "#1a4fa0",
        isl          = "#e03030",
        uplink       = "#5580b8",
        fabric       = "#6688aa",
        data_line    = "#9b59b6",
        sep          = "#c0c4d4",
        text_light   = "#ffffff",
        text_dark    = "#1a1a2e",
    )

    # ── Load device images ─────────────────────────────────────────
    def _load(key):
        _b = _get_device_img_b64(key)
        return _strip_white_bg(_b) if _b else None

    _sw_img    = _load(sw_model)
    _spine_img = _load(spine_model)
    _gpu_img   = _load(gpu_sw_model)
    _dbox_img  = _load(dbox_model)
    _cnode_img = _load(cnode_model)

    # ── SVG primitives ─────────────────────────────────────────────
    def _rect(x, y, w, h, fill, stroke=None, rx=6, lw=1.5):
        s = stroke or fill
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                f'fill="{fill}" stroke="{s}" stroke-width="{lw}"/>')

    def _txt(x, y, t, size=11, fill="#fff", anchor="middle", bold=False):
        fw = "bold" if bold else "normal"
        return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
                f'dominant-baseline="middle" fill="{fill}" '
                f'font-size="{size}" font-family="sans-serif" '
                f'font-weight="{fw}">{t}</text>')

    def _img_elem(x, y, w, h, b64):
        if not b64:
            return ""
        return (f'<image x="{x}" y="{y}" width="{w}" height="{h}" '
                f'href="data:image/png;base64,{b64}" '
                f'xlink:href="data:image/png;base64,{b64}" '
                f'preserveAspectRatio="xMidYMid meet"/>')

    def _line(x1, y1, x2, y2, stroke, lw=1.5, dash=""):
        d = f'stroke-dasharray="{dash}"' if dash else ""
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{stroke}" stroke-width="{lw}" {d}/>')

    # ── Device box: image + label ───────────────────────────────────
    def _device_box(cx, y, label, sublabel, fill, b64, dw=DW, dh=DH):
        x     = int(cx - dw / 2)
        img_h = dh - 20
        parts = [_rect(x, y, dw, dh, fill, rx=6)]
        if b64:
            parts.append(_img_elem(x + 2, y + 2, dw - 4, img_h - 2, b64))
        parts.append(_txt(int(cx), y + dh - 10, label,
                           size=8, fill=C["text_light"]))
        if sublabel:
            parts.append(_txt(int(cx), y + dh - 1, sublabel,
                               size=7, fill="#ccddee"))
        return "".join(parts)

    # ── Generic server box (fallback when no image) ─────────────────
    def _server_box(cx, y, label, sublabel="", dw=DW, dh=DH):
        x     = int(cx - dw / 2)
        parts = [_rect(x, y, dw, dh, C["server_fill"], rx=6)]
        for bi in range(3):
            by = y + 5 + bi * 17
            parts.append(
                f'<rect x="{x+8}" y="{by}" width="{dw-16}" height="13" '
                f'rx="2" fill="#4a4a72" stroke="#6a6a92" stroke-width="0.5"/>'
            )
            parts.append(
                f'<circle cx="{x+dw-14}" cy="{by+6}" r="3.5" fill="#22ee55"/>'
            )
        parts.append(_txt(int(cx), y + dh - 10, label,
                           size=8, fill=C["text_light"]))
        if sublabel:
            parts.append(_txt(int(cx), y + dh - 1, sublabel,
                               size=7, fill="#aabbcc"))
        return "".join(parts)

    # ── Row centring ────────────────────────────────────────────────
    def _row_cx(n, dw=DW):
        row_w = n * dw + (n - 1) * HGAP
        x0    = CX - row_w // 2
        return [x0 + i * (dw + HGAP) + dw // 2 for i in range(n)]

    def _device_row(names, model_short, num_total, b64, fill, y):
        shown = names[:MAX_SHOW]
        ctrs  = _row_cx(len(shown))
        parts = []
        for cx, nm in zip(ctrs, shown):
            parts.append(_device_box(cx, y, nm, model_short, fill, b64))
        extra = num_total - len(shown)
        if extra > 0:
            bx = int(ctrs[-1] + DW // 2 + HGAP)
            bw, bh = 56, DH
            parts.append(_rect(bx, y, bw, bh, "#dde2f0",
                                stroke="#aab4cc", rx=6))
            parts.append(_txt(bx + bw // 2, y + bh // 2,
                               f"+{extra}", size=12,
                               fill=C["text_dark"], bold=True))
        return "".join(parts), ctrs

    # ── Bus connections between layers ──────────────────────────────
    def _bus(from_cx, from_y, to_cx, to_y, stroke, lw=1.5, dash=""):
        mid_y    = (from_y + to_y) // 2
        all_xs   = list(from_cx) + list(to_cx)
        rx1, rx2 = min(all_xs), max(all_xs)
        parts    = []
        for x in from_cx:
            parts.append(_line(x, from_y, x, mid_y, stroke, lw * 0.7, dash))
        if rx1 < rx2:
            parts.append(_line(rx1, mid_y, rx2, mid_y, stroke, lw, dash))
        for x in to_cx:
            parts.append(_line(x, mid_y, x, to_y, stroke, lw * 0.7, dash))
        return "".join(parts)

    # ── Dotted layer separator ──────────────────────────────────────
    def _sep(y):
        return _line(MARGIN, y, W - MARGIN, y, C["sep"], lw=1, dash="10,7")

    # ── Build layers ────────────────────────────────────────────────
    shapes = []
    conn   = []
    layer  = {}
    y = 44

    # ── 1. Customer Network ─────────────────────────────────────────
    cx_l = CX - CLOUD_W // 2
    shapes.append(
        f'<rect x="{cx_l}" y="{y}" width="{CLOUD_W}" height="{CLOUD_H}" '
        f'rx="{CLOUD_H//2}" fill="{C["cloud_fill"]}" '
        f'stroke="{C["cloud_stroke"]}" stroke-width="2"/>'
        f'<ellipse cx="{cx_l+56}" cy="{y+3}" rx="30" ry="18" '
        f'fill="{C["cloud_fill"]}" stroke="{C["cloud_stroke"]}" stroke-width="1"/>'
        f'<ellipse cx="{cx_l+CLOUD_W-56}" cy="{y+7}" rx="24" ry="14" '
        f'fill="{C["cloud_fill"]}" stroke="{C["cloud_stroke"]}" stroke-width="1"/>'
    )
    shapes.append(_txt(CX, y + CLOUD_H // 2 + 3,
                        "Customer Network", size=15,
                        fill=C["cloud_text"], bold=True))
    layer["cloud"] = {"bot_y": y + CLOUD_H, "centers": [CX]}
    sep_y = y + CLOUD_H + VGAP // 2
    y += CLOUD_H + VGAP

    # ── 2. Customer Servers ─────────────────────────────────────────
    conn.append(_sep(sep_y))
    if custom_devices:
        shown_devs = custom_devices[:MAX_SHOW]
        n = len(shown_devs)
        srv_ctrs = _row_cx(n)
        for cx, dev in zip(srv_ctrs, shown_devs):
            dev_b64 = dev.get("img_b64")
            if dev_b64:
                dev_b64 = _strip_white_bg(dev_b64)
            nm  = dev.get("name", "Server")
            pnm = dev.get("product_name", "")
            sub = pnm if pnm and pnm != nm else ""
            if dev_b64:
                shapes.append(_device_box(cx, y, nm, sub, C["server_fill"], dev_b64))
            else:
                shapes.append(_server_box(cx, y, nm, sub))
        extra_srv = len(custom_devices) - n
        if extra_srv > 0:
            bx = int(srv_ctrs[-1] + DW // 2 + HGAP)
            bw, bh = 56, DH
            shapes.append(_rect(bx, y, bw, bh, "#dde2f0", stroke="#aab4cc", rx=6))
            shapes.append(_txt(bx + bw // 2, y + bh // 2,
                                f"+{extra_srv}", size=12, fill=C["text_dark"], bold=True))
    else:
        srv_ctrs = _row_cx(2)
        for cx, lbl in zip(srv_ctrs, ["Client Server A", "Client Server B"]):
            shapes.append(_server_box(cx, y, lbl))

    layer["servers"] = {"bot_y": y + DH, "centers": srv_ctrs}
    sep_y = y + DH + VGAP // 2
    y += DH + VGAP

    # ── 3. Data Switches ────────────────────────────────────────────
    conn.append(_sep(sep_y))
    if gpu_enabled:
        dsw_names = [f"{pfx}-DATA-SW-A", f"{pfx}-DATA-SW-B"]
        dsw_ms    = gpu_sw_model.replace("NVIDIA ", "").replace("Arista ", "")
        dsw_svg, dsw_ctrs = _device_row(dsw_names, dsw_ms, 2, _gpu_img, C["data_fill"], y)
        shapes.append(dsw_svg)
        layer["data_sw"] = {"bot_y": y + DH, "centers": dsw_ctrs}
        sep_y = y + DH + VGAP // 2
        y += DH + VGAP

    # ── 4. VAST CNodes ──────────────────────────────────────────────
    conn.append(_sep(sep_y))
    cn_names = [f"{pfx}-{cnode_label}-{i}" for i in range(1, num_cnodes + 1)]
    cn_ms    = cnode_model.replace(" CNode", "")
    cn_svg, cn_ctrs = _device_row(cn_names, cn_ms, num_cnodes, _cnode_img, C["cnode_fill"], y)
    shapes.append(cn_svg)
    layer["cnodes"] = {"bot_y": y + DH, "centers": cn_ctrs}
    sep_y = y + DH + VGAP // 2
    y += DH + VGAP

    # ── 5a. Spine Switches ──────────────────────────────────────────
    conn.append(_sep(sep_y))
    if topology == "Spine-Leaf":
        sp_names = [f"{pfx}-SPINE-A", f"{pfx}-SPINE-B"]
        sp_ms    = spine_model.replace("NVIDIA ", "").replace("Arista ", "")
        sp_svg, sp_ctrs = _device_row(sp_names, sp_ms, 2, _spine_img, C["spine_fill"], y)
        shapes.append(sp_svg)
        layer["spines"] = {"bot_y": y + DH, "centers": sp_ctrs}
        sep_y = y + DH + VGAP // 2
        y += DH + VGAP
        conn.append(_sep(sep_y))

    # ── 5b. Leaf Switches ───────────────────────────────────────────
    lf_names = [f"{pfx}-SW-A", f"{pfx}-SW-B"]
    lf_ms    = sw_model.replace("NVIDIA ", "").replace("Arista ", "")
    lf_svg, lf_ctrs = _device_row(lf_names, lf_ms, 2, _sw_img, C["leaf_fill"], y)
    shapes.append(lf_svg)
    isl_y  = y + DH // 2
    isl_x1 = int(lf_ctrs[0] + DW // 2)
    isl_x2 = int(lf_ctrs[1] - DW // 2)
    shapes.append(_line(isl_x1, isl_y, isl_x2, isl_y, C["isl"], lw=2.5, dash="8,4"))
    shapes.append(_txt((isl_x1 + isl_x2) // 2, isl_y - 8,
                        "ISL / Peerlink", size=9, fill=C["isl"], bold=True))
    layer["leaves"] = {"bot_y": y + DH, "centers": lf_ctrs}
    sep_y = y + DH + VGAP // 2
    y += DH + VGAP

    # ── 6. VAST DNodes ──────────────────────────────────────────────
    conn.append(_sep(sep_y))
    db_names = [f"{pfx}-{dbox_label}-{i}" for i in range(1, num_dboxes + 1)]
    db_ms    = dbox_model.split("(")[0].strip()
    db_svg, db_ctrs = _device_row(db_names, db_ms, num_dboxes, _dbox_img, C["dbox_fill"], y)
    shapes.append(db_svg)
    layer["dboxes"] = {"bot_y": y + DH, "centers": db_ctrs}
    y += DH + 30
    CANVAS_H = y

    # ── Connections ─────────────────────────────────────────────────
    conn.append(_bus(
        layer["cloud"]["centers"],   layer["cloud"]["bot_y"],
        layer["servers"]["centers"], layer["servers"]["bot_y"] - DH,
        C["uplink"], lw=2, dash="6,3",
    ))
    if gpu_enabled:
        conn.append(_bus(
            layer["servers"]["centers"], layer["servers"]["bot_y"],
            layer["data_sw"]["centers"], layer["data_sw"]["bot_y"] - DH,
            C["data_line"], lw=2,
        ))
        conn.append(_bus(
            layer["data_sw"]["centers"], layer["data_sw"]["bot_y"],
            layer["cnodes"]["centers"],  layer["cnodes"]["bot_y"] - DH,
            C["data_line"], lw=1.5,
        ))
    else:
        conn.append(_bus(
            layer["servers"]["centers"], layer["servers"]["bot_y"],
            layer["cnodes"]["centers"],  layer["cnodes"]["bot_y"] - DH,
            C["uplink"], lw=1.5, dash="5,3",
        ))
    if topology == "Spine-Leaf" and "spines" in layer:
        conn.append(_bus(
            layer["cnodes"]["centers"], layer["cnodes"]["bot_y"],
            layer["spines"]["centers"], layer["spines"]["bot_y"] - DH,
            C["fabric"], lw=1.5,
        ))
        conn.append(_bus(
            layer["spines"]["centers"], layer["spines"]["bot_y"],
            layer["leaves"]["centers"], layer["leaves"]["bot_y"] - DH,
            C["fabric"], lw=2,
        ))
    else:
        conn.append(_bus(
            layer["cnodes"]["centers"], layer["cnodes"]["bot_y"],
            layer["leaves"]["centers"], layer["leaves"]["bot_y"] - DH,
            C["fabric"], lw=1.5,
        ))
    conn.append(_bus(
        layer["leaves"]["centers"], layer["leaves"]["bot_y"],
        layer["dboxes"]["centers"], layer["dboxes"]["bot_y"] - DH,
        C["fabric"], lw=1.5,
    ))

    # ── Legend ─────────────────────────────────────────────────────
    leg_items = [
        (C["uplink"],    "2",   "6,3", "Uplink / Client Traffic"),
        (C["fabric"],    "1.5", "",    "Storage Fabric"),
        (C["isl"],       "2.5", "8,4", "ISL / Peerlink"),
    ]
    if gpu_enabled:
        leg_items.insert(1, (C["data_line"], "2", "", "Data / GPU Traffic"))

    LX, LY = W - 254, 30
    leg_h  = 22 + len(leg_items) * 18 + 8
    shapes.append(_rect(LX, LY, 242, leg_h, C["cloud_fill"], stroke=C["cloud_stroke"], rx=6))
    shapes.append(_txt(LX + 121, LY + 12, "Legend", size=10, fill=C["text_dark"], bold=True))
    for li, (clr, lw, dsh, lbl) in enumerate(leg_items):
        ly2 = LY + 26 + li * 18
        d   = f'stroke-dasharray="{dsh}"' if dsh else ""
        shapes.append(
            f'<line x1="{LX+8}" y1="{ly2}" x2="{LX+38}" y2="{ly2}" '
            f'stroke="{clr}" stroke-width="{lw}" {d}/>'
        )
        shapes.append(_txt(LX + 44, ly2 + 1, lbl, size=10, fill=C["text_dark"], anchor="start"))

    # ── Title ──────────────────────────────────────────────────────
    title_elem = _txt(CX, 22,
                       f"{pfx} — Logical Network Topology  ({topology})",
                       size=15, fill=C["text_dark"], bold=True)

    # ── Assemble ───────────────────────────────────────────────────
    bg = f'<rect width="{W}" height="{CANVAS_H}" fill="{C["bg"]}"/>'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {W} {CANVAS_H}">'
        + bg
        + title_elem
        + "".join(conn)
        + "".join(shapes)
        + "</svg>"
    )
    return svg, W, CANVAS_H

import streamlit as st


@st.cache_data(max_entries=20, show_spinner=False)
def _svg_to_pdf_cached(svg_str, out_w, out_h):
    """Convert SVG string to PDF bytes via cairosvg. Cached — only reruns when SVG changes."""
    import cairosvg as _cairosvg
    import io as _io
    buf = _io.BytesIO()
    _cairosvg.svg2pdf(bytestring=svg_str.encode(), write_to=buf,
                      output_width=out_w, output_height=out_h)
    return buf.getvalue()


@st.cache_data(max_entries=20, show_spinner=False)
def _svg_to_jpg_cached(svg_str, out_w, out_h):
    """Convert SVG string to JPEG bytes via cairosvg. Cached — only reruns when SVG changes."""
    import cairosvg as _cairosvg
    from PIL import Image as _PILImage
    import io as _io
    png_buf = _io.BytesIO()
    _cairosvg.svg2png(bytestring=svg_str.encode(), write_to=png_buf,
                      output_width=out_w, output_height=out_h)
    png_buf.seek(0)
    img = _PILImage.open(png_buf).convert("RGBA")
    white_bg = _PILImage.new("RGBA", img.size, (255, 255, 255, 255))
    white_bg.paste(img, mask=img.split()[3])
    jpg_buf = _io.BytesIO()
    white_bg.convert("RGB").save(jpg_buf, format="JPEG", quality=92)
    return jpg_buf.getvalue()


@st.cache_data(max_entries=5, show_spinner=False)
def _build_multipage_pdf(svg_strs, paper_w, paper_h):
    """One rack per PDF page. svg_strs must be a tuple (hashable for Streamlit cache)."""
    import cairosvg as _cairosvg
    from PIL import Image as _PILImage
    import io as _io
    page_imgs = []
    for svg in svg_strs:
        buf = _io.BytesIO()
        _cairosvg.svg2png(bytestring=svg.encode(), write_to=buf,
                          output_width=int(paper_w), output_height=int(paper_h))
        buf.seek(0)
        page_imgs.append(_PILImage.open(buf).copy().convert("RGB"))
    if not page_imgs:
        return b""
    pdf_buf = _io.BytesIO()
    page_imgs[0].save(pdf_buf, format="PDF", resolution=150,
                      save_all=True, append_images=page_imgs[1:])
    return pdf_buf.getvalue()


@st.cache_data(max_entries=5, show_spinner=False)
def _build_consolidated_pdf(svg_strs, paper_w, paper_h):
    """All racks side-by-side on a single landscape page, top-aligned so rack
    bodies sit at a uniform level and summaries hang below each rack."""
    import cairosvg as _cairosvg
    from PIL import Image as _PILImage
    import io as _io
    HGAP = 30
    V_MARGIN = 24   # top and bottom margin in output pixels
    rack_imgs = []
    for svg in svg_strs:
        buf = _io.BytesIO()
        _cairosvg.svg2png(bytestring=svg.encode(), write_to=buf)
        buf.seek(0)
        rack_imgs.append(_PILImage.open(buf).copy())
    if not rack_imgs:
        return b""
    max_h   = max(img.height for img in rack_imgs)
    total_w = sum(img.width  for img in rack_imgs) + HGAP * (len(rack_imgs) - 1)
    # Scale to fit within page, reserving vertical margins
    scale = min(paper_w / total_w, (paper_h - 2 * V_MARGIN) / max_h)
    # Centre the rack group horizontally
    scaled_total_w = sum(int(img.width * scale) for img in rack_imgs) + int(HGAP * scale) * (len(rack_imgs) - 1)
    x = int((paper_w - scaled_total_w) / 2)
    canvas = _PILImage.new("RGB", (int(paper_w), int(paper_h)), (255, 255, 255))
    for img in rack_imgs:
        nw, nh = int(img.width * scale), int(img.height * scale)
        rgba = img.convert("RGBA").resize((nw, nh), _PILImage.Resampling.LANCZOS)
        bg = _PILImage.new("RGBA", (nw, nh), (255, 255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[3])
        # Top-align all racks at the same y so rack bodies are level;
        # summaries of different lengths extend naturally downward.
        canvas.paste(bg.convert("RGB"), (x, V_MARGIN))
        x += nw + int(HGAP * scale)
    pdf_buf = _io.BytesIO()
    canvas.save(pdf_buf, format="PDF", resolution=150)
    return pdf_buf.getvalue()


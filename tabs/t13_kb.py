import streamlit as st

# ── Curated link library ─────────────────────────────────────
KB_LINKS = [
    {
        "category": "Knowledge Base",
        "icon": "📚",
        "links": [
            {
                "title": "VAST Knowledge Base",
                "url": "https://kb.vastdata.com",
                "desc": "Official VAST KB — installation guides, release notes, hardware docs, troubleshooting"
            },
        ],
    },
    {
        "category": "Video Library",
        "icon": "🎬",
        "links": [
            {
                "title": "VAST Data YouTube Channel",
                "url": "https://www.youtube.com/@VASTData",
                "desc": "Product demos, tech deep-dives, customer stories and webinar recordings"
            },
        ],
    },
    {
        "category": "Field Resources",
        "icon": "🛠️",
        "links": [
            {
                "title": "FIELD Dashboard (Confluence)",
                "url": "https://vastdata.atlassian.net/wiki/spaces/FIELD",
                "desc": "Approved software releases, SE resources, field guides"
            },
            {
                "title": "VAST Data Website",
                "url": "https://www.vastdata.com",
                "desc": "Product overview, datasheets, whitepapers and case studies"
            },
            {
                "title": "NVIDIA Ethernet Networking",
                "url": "https://www.nvidia.com/en-us/networking/products/ethernet/",
                "desc": "Spectrum switches, ConnectX NICs, BlueField DPUs — full NVIDIA ethernet product portfolio"
            },
        ],
    },
    {
        "category": "Support & Community",
        "icon": "🤝",
        "links": [
            {
                "title": "VAST Support Portal",
                "url": "https://vastdata.com/support",
                "desc": "Open and track support cases, escalations and RMAs"
            },
        ],
    },
]


def render():
    st.subheader("📖 Resources")
    st.caption("Curated VAST resources for Systems Engineers.")

    st.markdown("---")

    # ── Search ───────────────────────────────────────────────
    search = st.text_input(
        "🔍 Search",
        placeholder="e.g. installation, release notes, GPU...",
        label_visibility="collapsed"
    )
    query = search.strip().lower()

    # ── Render categories ────────────────────────────────────
    any_results = False

    for section in KB_LINKS:
        matches = [
            l for l in section["links"]
            if not query
            or query in l["title"].lower()
            or query in l["desc"].lower()
            or query in section["category"].lower()
        ]
        if not matches:
            continue

        any_results = True
        st.markdown(f"### {section['icon']} {section['category']}")

        for link in matches:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**[{link['title']}]({link['url']})**")
                st.caption(link["desc"])
            with col2:
                st.link_button("Open →", link["url"], use_container_width=True)
        st.markdown("---")

    if query and not any_results:
        st.info(f"No results for **{search}**.")

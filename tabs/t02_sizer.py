import streamlit as st
from datetime import date
from config import DBOX_PROFILES, CNODE_PERF, DR_ESTIMATES


def render():
    st.subheader("📏 Capacity & Performance Sizer")
    st.caption("Indicative sizing only — based on published VAST performance data. Not a formal quote.")

    st.markdown("---")

    sizer_col1, sizer_col2 = st.columns([1, 1])

    with sizer_col1:
        st.markdown("### 🖥️ Hardware Selection")

        sizer_cnode_gen = st.selectbox(
            "CNode Generation",
            options=list(CNODE_PERF.keys()),
            key="sizer_cnode_gen"
        )
        if "sizer_num_cnodes" not in st.session_state:
            st.session_state["sizer_num_cnodes"] = 4
        sizer_num_cnodes = st.slider(
            "Number of CNodes",
            min_value=1, max_value=28,
            key="sizer_num_cnodes"
        )
        sizer_dbox_model = st.selectbox(
            "DBox Model",
            options=list(DBOX_PROFILES.keys()),
            key="sizer_dbox_model"
        )
        if "sizer_num_dboxes" not in st.session_state:
            st.session_state["sizer_num_dboxes"] = 1
        sizer_num_dboxes = st.slider(
            "Number of DBoxes",
            min_value=1, max_value=14,
            key="sizer_num_dboxes"
        )

        st.markdown("### 🎯 Workload")
        sizer_use_case = st.selectbox(
            "Use Case",
            options=list(DR_ESTIMATES.keys()),
            key="sizer_use_case"
        )

        _dr_min, _dr_typ, _dr_max = DR_ESTIMATES[st.session_state.get("sizer_use_case", list(DR_ESTIMATES.keys())[0])]
        st.caption(f"Typical DRR range for this use case: {_dr_min}x — {_dr_max}x (typical: {_dr_typ}x)")
        sizer_drr_override = st.number_input(
            "SE DRR Override (leave at 0 to use use-case typical)",
            min_value=0.0, max_value=10.0, value=0.0, step=0.1,
            key="sizer_drr_override"
        )

        sizer_ratio = st.selectbox(
            "Workload Read/Write Ratio",
            options=list(CNODE_PERF["GEN6 Turin"].keys()),
            key="sizer_ratio"
        )

        st.markdown("### 🎯 Capacity Requirement")
        sizer_cap_required = st.number_input(
            "Capacity Required",
            min_value=0.0, value=0.0, step=10.0,
            key="sizer_cap_required"
        )
        sizer_cap_unit = st.radio(
            "Unit",
            options=["TB", "PB"],
            horizontal=True,
            key="sizer_cap_unit"
        )

        st.markdown("### 📈 Growth")
        sizer_growth_years = st.slider(
            "Growth projection (years)", min_value=1, max_value=5, value=3,
            key="sizer_growth_years"
        )
        sizer_growth_pct = st.slider(
            "Annual data growth (%)", min_value=0, max_value=100, value=20,
            key="sizer_growth_pct"
        )

    with sizer_col2:
        st.markdown("### 📊 Results")

        dbox  = DBOX_PROFILES[sizer_dbox_model]
        cperf = CNODE_PERF[sizer_cnode_gen]

        # Capacity
        raw_tb      = dbox["raw_tb"]    * sizer_num_dboxes
        usable_tb   = dbox["usable_tb"] * sizer_num_dboxes
        dr_min, dr_typ, dr_max = DR_ESTIMATES[sizer_use_case]
        # Use SE override if set, otherwise use typical
        sizer_drr_override = st.session_state.get("sizer_drr_override", 0.0)
        dr_effective = sizer_drr_override if sizer_drr_override > 0 else dr_typ
        eff_min_tb  = usable_tb * dr_min
        eff_typ_tb  = usable_tb * dr_effective
        eff_max_tb  = usable_tb * dr_max

        # Performance
        perf_per_cnode = cperf.get(sizer_ratio, 0)
        total_perf_gbs = perf_per_cnode * sizer_num_cnodes

        # Growth
        growth_factor = (1 + sizer_growth_pct / 100) ** sizer_growth_years
        future_tb = usable_tb * growth_factor

        # ── Capacity block ───────────────────────────────────
        st.markdown("#### 💾 Capacity")
        cap_data = {
            "Metric": [
                "Raw Capacity",
                "Usable Capacity",
                f"Effective (min @ {dr_min}x DR)",
                f"Effective ({'SE override' if sizer_drr_override > 0 else 'typical'} @ {dr_effective}x DR)",
                f"Effective (max @ {dr_max}x DR)",
                f"Projected Usable in {sizer_growth_years}yr ({sizer_growth_pct}%/yr)",
            ],
            "Value": [
                f"{raw_tb:,.1f} TB",
                f"{usable_tb:,.1f} TB",
                f"{eff_min_tb:,.1f} TB",
                f"{eff_typ_tb:,.1f} TB",
                f"{eff_max_tb:,.1f} TB",
                f"{future_tb:,.1f} TB",
            ]
        }
        st.table(cap_data)

        # ── Capacity requirement check ───────────────────────
        sizer_cap_required = st.session_state.get("sizer_cap_required", 0.0)
        sizer_cap_unit = st.session_state.get("sizer_cap_unit", "TB")
        if sizer_cap_required > 0:
            req_tb = sizer_cap_required * 1000 if sizer_cap_unit == "PB" else sizer_cap_required
            req_display = f"{sizer_cap_required:,.1f} {sizer_cap_unit}"
            if req_tb <= eff_typ_tb:
                st.success(
                    f"✅ **Hit** — {req_display} required, "
                    f"{eff_typ_tb:,.1f} TB available at typical DR ({dr_effective}x)"
                )
            elif req_tb <= eff_max_tb:
                st.warning(
                    f"⚠️ **Borderline** — {req_display} required exceeds typical DR "
                    f"({eff_typ_tb:,.1f} TB at {dr_effective}x) but fits max DR "
                    f"({eff_max_tb:,.1f} TB at {dr_max}x). Verify customer DRR."
                )
            else:
                st.error(
                    f"❌ **Miss** — {req_display} required exceeds max effective capacity "
                    f"({eff_max_tb:,.1f} TB at {dr_max}x DR). Add more DBoxes."
                )

        # ── Performance block ────────────────────────────────
        st.markdown("#### ⚡ Performance")
        st.metric(
            label=f"{sizer_cnode_gen} × {sizer_num_cnodes} CNodes — {sizer_ratio}",
            value=f"{total_perf_gbs:.1f} GB/s"
        )

        perf_rows = []
        for ratio, per_node in cperf.items():
            total = per_node * sizer_num_cnodes
            perf_rows.append({
                "Workload Mix":     ratio,
                "Per CNode (GB/s)": f"{per_node:.1f}",
                f"× {sizer_num_cnodes} CNodes (GB/s)": f"{total:.1f}",
            })
        st.dataframe(perf_rows, use_container_width=True)

        # ── Hardware summary ─────────────────────────────────
        st.markdown("#### 📦 Configuration Summary")
        st.info(
            f"**{sizer_num_dboxes}× {sizer_dbox_model}** "
            f"({dbox['form_factor']}, {dbox['usable_tb']:.2f} TB usable each)  \n"
            f"**{sizer_num_cnodes}× {sizer_cnode_gen} CNode**  \n"
            f"**Use case:** {sizer_use_case}  \n"
            f"**Switch fabric:** VAST internal storage fabric (200GbE)"
        )

        # ── AI / GPU note ─────────────────────────────────────
        if "AI" in sizer_use_case:
            st.warning(
                "⚠️ **AI workloads** — NFS over RDMA / GDS required for full throughput. "
                "Confirm GPU servers support RoCEv2 and GDS before sizing."
            )

        # ── Erasure coding note ───────────────────────────────
        st.caption(
            "VAST uses a unique Wide Stripe Erasure Code which benefits customers with typically larger environments. "
            "Usable figures shown are per-DBox actuals — overhead is cluster-size dependent (~2.7% at scale). "
            "Data reduction estimates are indicative ranges based on use case — actual results vary. "
            "SE DRR override allows you to apply a customer-specific reduction ratio to the typical effective capacity."
        )

    st.markdown("---")

    apply_col1, apply_col2 = st.columns([1, 2])
    with apply_col1:
        if st.button("📋 Apply to Project →", use_container_width=True):
            _apply = dict(st.session_state)
            _apply["proj_num_dboxes"] = sizer_num_dboxes
            _apply["proj_num_cnodes"] = sizer_num_cnodes
            _apply["proj_dbox_type"]  = sizer_dbox_model
            _apply["proj_cbox_type"]  = sizer_cnode_gen
            st.session_state["_pending_load"] = _apply
            st.session_state["_save_msg"] = (
                f"✅ Sizer applied — "
                f"{sizer_num_dboxes}× {sizer_dbox_model}, "
                f"{sizer_num_cnodes}× {sizer_cnode_gen}. "
                f"Review and complete Tab 3."
            )
            st.rerun()
    with apply_col2:
        st.caption("Optional — applies hardware selection to Project Details. You can also fill Tab 3 manually.")

    st.caption("Performance data: VAST GEN5 Genoa and GEN6 Turin, 1MB Random I/O. Source: VAST internal benchmarks.")




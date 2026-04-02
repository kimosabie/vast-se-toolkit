import streamlit as st
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    import db as _db
    _DB_AVAILABLE = True
except Exception:
    _DB_AVAILABLE = False
from helpers.state import _is_saveable


def render():
    st.subheader("🧑‍💻 Session")
    st.caption("Set your identity and manage project saves. All fields feed the sidebar status bar and the install plan.")

    st.markdown("---")
    st.markdown("### 👤 SE & Customer Identity")

    id_col1, id_col2 = st.columns(2)
    with id_col1:
        se_name = st.text_input(
            "SE Name",
            value=st.session_state.get("se_name", ""),
            placeholder="Your full name"
        )
        st.session_state["se_name"] = se_name

        customer = st.text_input(
            "Customer Name",
            value=st.session_state.get("customer", ""),
            placeholder="e.g. Acme Corp"
        )
        st.session_state["customer"] = customer

    with id_col2:
        _saved_date = st.session_state.get("install_date", date.today())
        if isinstance(_saved_date, str):
            try:
                from datetime import datetime as _dt
                _saved_date = _dt.strptime(_saved_date, "%Y-%m-%d").date()
            except Exception:
                _saved_date = date.today()
        install_date = st.date_input("Install Date", value=_saved_date)
        st.session_state["install_date"] = str(install_date)

        cluster_name = st.text_input(
            "Project Name",
            value=st.session_state.get("cluster_name", ""),
            placeholder="e.g. ACME-VAST-01"
        )
        st.session_state["cluster_name"] = cluster_name

    # ── Project Save / Load ──────────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 Project")

    if st.session_state.get("_save_msg"):
        st.success(st.session_state.pop("_save_msg"))

    if not _DB_AVAILABLE:
        st.warning(
            "⚠️ Database unavailable — projects cannot be saved or loaded. "
            "Check that `db.py` is present and `/app/data/` is writable."
        )
    else:
        # Auto-backup on first render each session
        if not st.session_state.get("_auto_backup_done"):
            _db.auto_backup_if_stale()
            st.session_state["_auto_backup_done"] = True

        proj_id = st.session_state.get("_db_project_id")
        proj_id_label = f"Project #{proj_id}" if proj_id else "Unsaved project"

        db_col1, db_col2, db_col3 = st.columns([1, 1, 1])

        with db_col1:
            if st.button("🆕 New Project", use_container_width=True):
                st.session_state["_pending_clear"] = True
                st.rerun()

        with db_col2:
            save_milestone = st.selectbox(
                "Milestone",
                options=[
                    "Initial / Sizing",
                    "Pre-Install",
                    "Post-Install / Config",
                    "Other",
                ],
                key="_save_milestone",
                label_visibility="collapsed"
            )
            if save_milestone == "Other":
                save_other_notes = st.text_input(
                    "Describe this save",
                    placeholder="e.g. post spine-leaf config",
                    key="_save_other_notes"
                )
                _final_label = f"Other: {save_other_notes}" if save_other_notes else "Other"
            else:
                _final_label = save_milestone
            if st.button("💾 Save Project", use_container_width=True):
                try:
                    _save_data = {k: v for k, v in st.session_state.items()
                                  if _is_saveable(k)}
                    _save_data["_db_project_id"] = st.session_state.get("_db_project_id")
                    _proj_name = st.session_state.get("cluster_name", "").strip()
                    _prefixed_label = f"{_proj_name} — {_final_label}" if _proj_name else _final_label
                    pid = _db.save_project(
                        _save_data,
                        label=_prefixed_label
                    )
                    st.session_state["_db_project_id"] = pid
                    st.session_state["_save_msg"] = f"✅ Saved — {_prefixed_label}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Save failed: {e}")

        with db_col3:
            try:
                projects = _db.list_projects()
            except Exception:
                projects = []

            if not projects:
                st.info("No saved projects yet.")
            else:
                proj_options = {
                    f"#{p['id']} — {p['name']} ({p['updated_at'][:10]})": p['id']
                    for p in projects
                }
                selected_label = st.selectbox(
                    "Load project",
                    options=list(proj_options.keys()),
                    key="_load_select",
                    label_visibility="collapsed"
                )
                _load_col, _del_col = st.columns([1, 1])
                with _load_col:
                    if st.button("📂 Load", use_container_width=True):
                        try:
                            pid = proj_options[selected_label]
                            state = _db.load_project(pid)
                            st.session_state["_pending_load"] = state
                            st.rerun()
                        except Exception as e:
                            st.error(f"Load failed: {e}")
                with _del_col:
                    _del_pid = proj_options[selected_label]
                    if st.session_state.get("_confirm_del_proj") == _del_pid:
                        if st.button("⚠️ Confirm", use_container_width=True, type="primary"):
                            try:
                                _db.delete_project(_del_pid)
                                if st.session_state.get("_db_project_id") == _del_pid:
                                    st.session_state["_pending_clear"] = True
                                st.session_state.pop("_confirm_del_proj", None)
                                st.session_state["_save_msg"] = "🗑️ Project deleted."
                                st.rerun()
                            except Exception as e:
                                st.error(f"Delete failed: {e}")
                    else:
                        if st.button("🗑️ Delete", use_container_width=True):
                            st.session_state["_confirm_del_proj"] = _del_pid
                            st.rerun()

        # Version history expander
        if proj_id:
            with st.expander(f"🕓 Version history — {proj_id_label}", expanded=False):
                try:
                    versions = _db.get_project_versions(proj_id)
                    if not versions:
                        st.caption("No versions saved yet.")
                    else:
                        for v in versions:
                            v_label = v['label'] or "—"
                            v_col1, v_col2, v_col3 = st.columns([4, 1, 1])
                            with v_col1:
                                st.caption(
                                    f"v{v['version_num']} · "
                                    f"{v['saved_at'][:16].replace('T', ' ')} · "
                                    f"{v_label}"
                                )
                            with v_col2:
                                if st.button("Restore", key=f"_restore_v{v['id']}", use_container_width=True):
                                    try:
                                        state = _db.load_version(v['id'])
                                        st.session_state["_pending_load"] = state
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Restore failed: {e}")
                            with v_col3:
                                if st.session_state.get("_confirm_del_ver") == v['id']:
                                    if st.button("⚠️", key=f"_confirm_del_v{v['id']}", use_container_width=True, help="Click to confirm delete"):
                                        try:
                                            _db.delete_version(v['id'])
                                            st.session_state.pop("_confirm_del_ver", None)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Delete failed: {e}")
                                else:
                                    if st.button("🗑️", key=f"_del_v{v['id']}", use_container_width=True, help="Delete this version"):
                                        st.session_state["_confirm_del_ver"] = v['id']
                                        st.rerun()
                except Exception as e:
                    st.error(f"Could not load version history: {e}")

        st.caption(f"Current: {proj_id_label}")

    # ── Cloud Backup ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ☁️ Cloud Backup")

    if not _DB_AVAILABLE:
        st.warning("Database unavailable — cloud backup requires database access.")
    else:
        configured = _db.is_cloud_backup_configured()

        if configured:
            import os
            sync_dir = os.environ.get("CLOUD_SYNC_DIR", "")
            st.success(f"✅ Cloud sync folder configured: `{sync_dir}`")

            last = _db.get_last_cloud_backup_at()
            if last:
                st.caption(f"Last cloud backup: {last[:16].replace('T', ' ')}")
            else:
                st.caption("No cloud backup taken yet this session.")

            if st.button("☁️ Backup to Cloud Now", use_container_width=False):
                try:
                    path = _db.cloud_backup()
                    st.success(f"✅ Backed up to cloud: `{path}`")
                except Exception as e:
                    st.error(f"Cloud backup failed: {e}")
        else:
            st.info(
                "Cloud backup is not configured. "
                "Set `CLOUD_SYNC_DIR` in your `.env` file to point to your "
                "Google Drive or OneDrive folder, then restart the app.\n\n"
                "**Examples:**\n\n"
                "| Platform | Example path |\n"
                "|----------|--------------|\n"
                "| Windows (WSL2) — Google Drive | `/mnt/c/Users/yourname/Google Drive/My Drive/VAST Backups` |\n"
                "| Windows (WSL2) — OneDrive | `/mnt/c/Users/yourname/OneDrive/VAST Backups` |\n"
                "| macOS — Google Drive | `/Users/yourname/Library/CloudStorage/GoogleDrive-you@email.com/My Drive/VAST Backups` |\n"
                "| macOS — OneDrive | `/Users/yourname/Library/CloudStorage/OneDrive-Personal/VAST Backups` |\n"
            )





# Shared session-state key filtering logic used by app.py and tab modules.

_SAVEABLE_PREFIXES = (
    "proj_", "tab7_", "tab8_", "spine_", "name_", "sizer_", "rack_",
)
_SAVEABLE_EXACT = {
    "se_name", "customer", "cluster_name", "install_date",
}
_SKIP_SUFFIXES = ("_dl_A", "_dl_B", "_dl_a", "_dl_b", "_download",
                  "_handoff_dl", "tab7_download", "tab8_download")
_SKIP_EXACT = {
    "rack_cust_add", "rack_cust_img",
    "rack_cust_rm",
    "rack_cust_name",
    "rack_pick_add",
    "rack_pdf_size",
}
_SKIP_PREFIXES = (
    "rack_inv_add_", "rack_inv_del_",
    "rack_cust_rm_",
    "rack_dl_", "rack_gen_",
)


def _is_saveable(k):
    if k in _SAVEABLE_EXACT:
        return True
    if k in _SKIP_EXACT:
        return False
    if any(k.startswith(sp) for sp in _SKIP_PREFIXES):
        return False
    if any(k.startswith(p) for p in _SAVEABLE_PREFIXES):
        if any(k.endswith(s) or k == s for s in _SKIP_SUFFIXES):
            return False
        return True
    return False

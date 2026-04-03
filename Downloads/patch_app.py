# =============================================================
# app.py — patch instructions
# Three str_replace changes — apply in order
# =============================================================
# Run this script from your toolkit root to apply all patches:
#   python3 patch_app.py
# =============================================================
#
# PATCH 1 — Storage switch context: mlag_mac + uplink_description
# PATCH 2 — GPU switch context: mlag_mac + uplink_description
# PATCH 3 — Hostname sanitiser: replace dots with hyphens
#            FIELD BUG A: Cumulus NVUE rejects hostnames containing "."
#            RFC 952 only allows hyphens, letters, digits in hostnames
# =============================================================

import re

with open("app.py", "r") as f:
    content = f.read()

# ── PATCH 1 — Storage switch context (clag_id 100) ────────────
# Adds mlag_mac and uplink_description to the storage pair context dict

OLD_1 = '''                    "clag_id":       100,
                    "peer_ip":       sw_b_ip.split("/")[0] if side == "A"
                                     else sw_a_ip.split("/")[0],'''

NEW_1 = '''                    "clag_id":       100,
                    "mlag_mac":      "44:38:39:ff:00:01",
                    "uplink_description": "Customer-Core",
                    "peer_ip":       sw_b_ip.split("/")[0] if side == "A"
                                     else sw_a_ip.split("/")[0],'''

assert OLD_1 in content, "PATCH 1 target not found — check indentation"
content = content.replace(OLD_1, NEW_1, 1)
print("PATCH 1 applied — storage switch context")

# ── PATCH 2 — GPU switch context (clag_id 200) ────────────────
# Adds mlag_mac and uplink_description to the GPU pair context dict

OLD_2 = '''                        "clag_id":       200,
                        "peer_ip":       (
                            sw_b_ip2.split("/")[0] if side == "A"
                            else sw_a_ip2.split("/")[0]
                        ),'''

NEW_2 = '''                        "clag_id":       200,
                        "mlag_mac":      "44:38:39:ff:00:02",
                        "uplink_description": "Gigabrain-Firewall",
                        "peer_ip":       (
                            sw_b_ip2.split("/")[0] if side == "A"
                            else sw_a_ip2.split("/")[0]
                        ),'''

assert OLD_2 in content, "PATCH 2 target not found — check indentation"
content = content.replace(OLD_2, NEW_2, 1)
print("PATCH 2 applied — GPU switch context")

# ── PATCH 3 — Hostname sanitiser ──────────────────────────────
# FIELD BUG A: NVUE rejects hostnames with dots. Replace the two
# places where hostname is built (full_sw_a / full_sw_b) so dots
# in cluster_name are converted to hyphens before being used.
# The _build_sw_name helper is the single source of both names.

OLD_3 = '''    name = "-".join(parts)
    if gpu:
        name += "-GPU"
    return name'''

NEW_3 = '''    name = "-".join(parts)
    if gpu:
        name += "-GPU"
    # FIELD BUG A FIX — dots are invalid in Cumulus NVUE hostnames
    # RFC 952: only hyphens, letters, and digits are permitted
    name = name.replace(".", "-")
    return name'''

assert OLD_3 in content, "PATCH 3 target not found — check _build_sw_name function"
content = content.replace(OLD_3, NEW_3, 1)
print("PATCH 3 applied — hostname sanitiser")

with open("app.py", "w") as f:
    f.write(content)

print("Done — all patches written to app.py")
print("Verify with:")
print('  grep -n "mlag_mac\\|uplink_description\\|replace.*\\." app.py')

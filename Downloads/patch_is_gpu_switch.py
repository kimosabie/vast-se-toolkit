# =============================================================
# app.py — is_gpu_switch patch
# Adds is_gpu_switch boolean to storage, spine, and GPU contexts
# Run from toolkit root: python3 patch_is_gpu_switch.py
# =============================================================

with open("app.py", "r") as f:
    content = f.read()

# ── PATCH 1 — Storage switch context (clag_id 100) ────────────
OLD_1 = '''                    "mlag_mac":      "44:38:39:ff:00:01",
                    "uplink_description": "Customer-Core",'''

NEW_1 = '''                    "mlag_mac":      "44:38:39:ff:00:01",
                    "uplink_description": "Customer-Core",
                    "is_gpu_switch":  False,'''

assert OLD_1 in content, "PATCH 1 not found — check storage context block"
content = content.replace(OLD_1, NEW_1, 1)
print("PATCH 1 applied — storage switch is_gpu_switch=False")

# ── PATCH 2 — Spine switch context (clag_id 300) ──────────────
OLD_2 = '''                    "clag_id":       300,'''

NEW_2 = '''                    "clag_id":       300,
                    "is_gpu_switch":  False,'''

assert OLD_2 in content, "PATCH 2 not found — check spine context block"
content = content.replace(OLD_2, NEW_2, 1)
print("PATCH 2 applied — spine switch is_gpu_switch=False")

# ── PATCH 3 — GPU switch context (clag_id 200) ────────────────
OLD_3 = '''                        "mlag_mac":      "44:38:39:ff:00:02",
                        "uplink_description": "Gigabrain-Firewall",'''

NEW_3 = '''                        "mlag_mac":      "44:38:39:ff:00:02",
                        "uplink_description": "Gigabrain-Firewall",
                        "is_gpu_switch":  True,'''

assert OLD_3 in content, "PATCH 3 not found — check GPU context block"
content = content.replace(OLD_3, NEW_3, 1)
print("PATCH 3 applied — GPU switch is_gpu_switch=True")

with open("app.py", "w") as f:
    f.write(content)

print("\nDone — all patches written to app.py")
print("Verify with:")
print('  grep -n "is_gpu_switch" app.py')

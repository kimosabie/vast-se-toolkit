# =============================================================
# app.py — hostname sanitiser patch
# Fixes dots → hyphens in hostname for all three switch contexts
# FIELD BUG A: Cumulus NVUE rejects hostnames containing "."
# Run from toolkit root: python3 patch_hostname.py
# =============================================================

with open("app.py", "r") as f:
    content = f.read()

# ── PATCH 1 — Storage switch (line ~1123) ─────────────────────
OLD_1 = '                    "hostname":      full_sw_a if side == "A" else full_sw_b,'
NEW_1 = '                    "hostname":      (full_sw_a if side == "A" else full_sw_b).replace(".", "-"),'

assert OLD_1 in content, "PATCH 1 not found — check line ~1123"
content = content.replace(OLD_1, NEW_1, 1)
print("PATCH 1 applied — storage switch hostname")

# ── PATCH 2 — Spine switch (line ~1389) ───────────────────────
OLD_2 = '''                    "hostname":      (
                        spine_sw_a_name if side == "A"
                        else spine_sw_b_name
                    ),'''
NEW_2 = '''                    "hostname":      (
                        spine_sw_a_name if side == "A"
                        else spine_sw_b_name
                    ).replace(".", "-"),'''

assert OLD_2 in content, "PATCH 2 not found — check line ~1389"
content = content.replace(OLD_2, NEW_2, 1)
print("PATCH 2 applied — spine switch hostname")

# ── PATCH 3 — GPU switch (line ~1755) ─────────────────────────
OLD_3 = '''                        "hostname":      (
                            f"{full_sw_a}-GPU" if side == "A"
                            else f"{full_sw_b}-GPU"
                        ),'''
NEW_3 = '''                        "hostname":      (
                            f"{full_sw_a}-GPU" if side == "A"
                            else f"{full_sw_b}-GPU"
                        ).replace(".", "-"),'''

assert OLD_3 in content, "PATCH 3 not found — check line ~1755"
content = content.replace(OLD_3, NEW_3, 1)
print("PATCH 3 applied — GPU switch hostname")

with open("app.py", "w") as f:
    f.write(content)

print("\nDone — all three hostname patches applied")
print("Verify with:")
print('  grep -n "hostname.*replace" app.py')

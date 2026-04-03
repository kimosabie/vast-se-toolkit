# VAST SE Toolkit — Code Health TODO

Items from the 2026-04-03 health check. Review each before implementing.

---

## 1. app.py — Dead imports (holdovers from monolithic era)

**File:** `app.py` lines 2, 54–68

`app.py` still imports everything that used to live inside it, but since the
refactor all of this is handled inside the tab/helper modules. None of these
are used in app.py's own body:

```python
from jinja2 import Environment, FileSystemLoader          # jinja2 used in t07/t08
from config import SPEED_RANK, DBOX_PROFILES, CNODE_PERF, # all used in tabs/config
                   DEVICE_SPECS, DEVICE_IMAGES,
                   DEVICE_IMAGE_MAP, DR_ESTIMATES
from helpers.images import _get_device_img_b64, _strip_white_bg
from helpers.svg_export import (...)
from helpers.port_logic import (...)
```

**Proposed fix:** Strip these from app.py. Only keep:
- `from config import HARDWARE_PROFILES` (still used in pending-clear block)
- `from helpers.state import (...)` (used in pending-load block)
- `from helpers.context import get_ctx, build_sw_name`

---

## 2. app.py — Dead module-level derived values

**File:** `app.py` lines 244–264

After calling `get_ctx()`, app.py unpacks all the returned values into
module-level variables (`pfx`, `num_dboxes`, `full_sw_a`, etc.). None of these
are used anywhere in app.py's body — each tab calls `get_ctx()` itself.

**Proposed fix:** Remove lines 244–264. Keep only `_build_sw_name()` wrapper
(line 266–267) since it captures `pfx` and `include_ru` from the module scope.
Or refactor that wrapper away too and let tabs call `build_sw_name()` directly.

---

## 3. app.py — Dead inventory cache functions

**File:** `app.py` lines 14–23

`_get_inventory_cached()` and `_inv_cache_invalidate()` are defined in app.py
but never called from app.py — only from t09 and t10 which define their own
copies anyway.

**Proposed fix:** Remove from app.py. See item 4 for the right fix.

---

## 4. Triplicate inventory cache — move to db.py

**Files:** `app.py:14–23`, `tabs/t09_rack.py:18–23`, `tabs/t10_inventory.py:13–19`

`_get_inventory_cached()` and `_INV_CACHE_KEY` are copy-pasted identically
in three files. If logic ever changes it must be updated in three places.

**Proposed fix:** Move to `db.py` (already the source of truth for inventory
reads) as a module-level function, and import from there in t09 and t10.

---

## 5. sys.path.insert in tab files

**Files:** `tabs/t01_session.py:4`, `tabs/t09_rack.py:11`, `tabs/t10_inventory.py:4`

Each does:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```
This was a workaround to find `db.py` when tabs were first extracted. Now that
Docker runs `app.py` from the project root, `db` should already be importable
without path manipulation.

**Proposed fix:** Remove the `sys.path.insert` lines and test that `import db`
still works. If it doesn't, fix via `PYTHONPATH` in the Dockerfile instead.

---

## 6. t12_network.py — SVG builder nested inside render()

**File:** `tabs/t12_network.py`

`_render_net_diagram_svg()` is ~400 lines nested inside `render()`. This makes
t12 the second-largest tab at 494 lines, and the SVG function is hard to read
or edit in isolation.

**Proposed fix:** Extract `_render_net_diagram_svg()` to
`helpers/network_svg.py`. t12 would shrink to ~100 lines, and the SVG builder
becomes independently readable and testable.

---

## 7. t04 / t05 — Shared switch state reading

**Files:** `tabs/t04_confluence.py:58–109`, `tabs/t05_preflight.py:30–83`

Both tabs independently re-read ~15 identical session state keys at the top of
`render()` (tab7_sw_model, tab7_sw_a_ip, tab7_sw_b_ip, tab7_ntp, tab7_isl,
tab7_uplink, spine_*, tab8_*) and compute the same config filename patterns
(`{pfx}_VAST_SWA_{vendor}_{date}.txt` etc.).

**Proposed fix:** Add a `get_switch_ctx()` helper to `helpers/context.py` that
returns all switch-related state values and derived filenames. Both tabs import
and call it instead of duplicating the reads.

---

## 8. Version string inconsistency

Three separate version strings that are out of sync:

| Location | Value |
|----------|-------|
| `app.py:234` (sidebar) | `v1.2.0` |
| `db.py:18` (`APP_VERSION`) | `1.0.0` |
| `tabs/t05_preflight.py:154,613` (checklist text) | `v1.0.0` |

**Proposed fix:** Define one `APP_VERSION = "1.2.0"` in `config.py`, import
it everywhere. `db.py` already uses `APP_VERSION` for its DB records — just
change the source.

---

## Already fixed in this session

- **Bug:** `tabs/t05_preflight.py:180` — `spine_model` NameError in Spine-Leaf
  topology (was undefined; fixed to `proc_spine_model`). Committed `da947fd`.

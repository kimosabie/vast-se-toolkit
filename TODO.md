# VAST SE Toolkit — Code Health TODO

All items from the 2026-04-03 health check are complete.

---

## ✅ Completed 2026-04-03

| # | Item | Commit |
|---|------|--------|
| Bug | `t05_preflight.py:180` NameError `spine_model` in Spine-Leaf topology | `da947fd` |
| 1 | `app.py` dead imports (jinja2, bulk config, helpers) removed | `refactor` |
| 2 | `app.py` dead module-level derived values removed | `refactor` |
| 3 | `app.py` dead inventory cache functions removed | `refactor` |
| 4 | Triplicate `_get_inventory_cached` consolidated into `helpers/inventory.py` | `refactor` |
| 5 | `sys.path.insert` removed from `t09_rack.py` (no longer imports db directly) | `refactor` |
| 6 | `_render_net_diagram_svg` (~400 lines) extracted to `helpers/network_svg.py` | `refactor` |
| 7 | `get_switch_ctx()` added to `helpers/context.py`; used by `t04` and `t05` | `refactor` |
| 8 | `APP_VERSION` centralised in `config.py`; used by `app.py`, `db.py`, `t05` | `refactor` |

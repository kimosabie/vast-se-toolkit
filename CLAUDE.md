# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

VAST SE Toolkit is a Dockerized Streamlit web application for VAST Systems Engineers to automate cluster installation workflows — generating switch configs, cable guides, pre-flight checklists, and Confluence install plans. It runs locally (Windows WSL2/macOS), requires no cloud login, and targets NVIDIA Cumulus NV and Arista EOS switches.

**Stack:** Python 3.11 · Streamlit 1.32 · Jinja2 · SQLite · Docker Compose
**Repo:** https://github.com/kimosabie/vast-se-toolkit (public)
**Dev server:** vast-dev (Tailscale) — project at `~/projects/vast-se-toolkit/`
**Access:** http://\<tailscale-ip\>:8501

## Running the App

```bash
# Start (builds on first run — always required after app.py changes)
docker compose up --build -d
# App available at http://localhost:8501

# Restart without rebuild (template/image changes only)
docker compose restart

# View logs
docker compose logs --tail=50

# Stop
docker compose down

# Syntax check app.py without rebuilding
docker compose exec vast-se-toolkit python3 -c "import ast; ast.parse(open('app.py').read())"
```

**Important:** `app.py` is COPIED into the image at build time — `--build` is always required after any Python change. Templates in `templates/` and images in `images/` are volume-mounted — changes take effect after a simple `docker compose restart`.

For local development without Docker:
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Useful one-liners

```bash
# Syntax check with line numbers
python3 -c "
import ast
with open('app.py') as f: source = f.read()
try:
    ast.parse(source)
    print('Syntax OK')
except SyntaxError as e:
    print(f'SyntaxError at line {e.lineno}: {e.msg}')
"

# Fix mixed tabs/spaces
python3 -c "
with open('app.py', 'r') as f: content = f.read()
content = content.expandtabs(4)
with open('app.py', 'w') as f: f.write(content)
print('Done')
"
```

## Architecture

**`app.py`** (~320 lines) is a thin orchestrator — page config, session state handlers, sidebar, derived values block, tab creation, and calls to each tab's `render()` function. Business logic lives in `helpers/` and `tabs/`.

**`config.py`** — all static hardware data: `HARDWARE_PROFILES`, `DBOX_PROFILES`, `CNODE_PERF`, `DEVICE_SPECS`, `DEVICE_IMAGES`. Edit here to add/change switch models, DBox specs, or performance numbers.

**`db.py`** manages a SQLite database (`data/toolkit.db`) with three tables:
- `projects` — project metadata with soft deletes (`is_deleted=1`)
- `project_versions` — full JSON snapshots of Streamlit session state per save
- `settings` — key/value store (backup location, last backup timestamp)

**`helpers/`** — shared utilities:
- `context.py` — `get_ctx()` returns a dict of all derived session-state values; `build_sw_name()`
- `images.py` — `_get_device_img_b64()`, `_strip_white_bg()`
- `port_logic.py` — `get_port_mappings()`, `validate_port_counts()`, `render_cable_summary()`
- `state.py` — `_is_saveable()` key filter for save/load
- `svg_export.py` — PDF/JPG export helpers

**`tabs/`** — one file per tab, each exports `render()`:
- `t01_session.py` — Session (SE identity, save/load/new project)
- `t02_sizer.py` — Capacity & Performance Sizer
- `t03_project.py` — Project Details
- `t04_confluence.py` — Confluence Install Plan
- `t05_preflight.py` — Pre-Flight, Validation & Installation
- `t07_switch.py` — Internal Switch — Southbound
- `t08_data_switch.py` — Data Switch — Northbound
- `t09_rack.py` — Rack Diagram
- `t10_inventory.py` — Device Inventory
- `t11_ai.py` — AI Assistant (Ollama + cloud Expert)
- `t12_network.py` — Network Diagram
- `t13_kb.py` — Resources

**`templates/`** — Jinja2 templates rendered by app.py:
- `cumulus_nv.j2` / `cumulus_spine.j2` — NVIDIA Cumulus NV leaf/spine configs
- `arista_eos.j2` / `arista_spine.j2` — Arista EOS data/GPU switch configs

**`outputs/`** — Generated config files written here, host-mounted for persistence.

### File structure

```
~/projects/vast-se-toolkit/
├── app.py                    ← orchestrator (~320 lines)
├── config.py                 ← all hardware profiles and static data
├── db.py                     ← SQLite project database module
├── Dockerfile
├── docker-compose.yml        ← mounts outputs/, data/, templates/, images/
├── requirements.txt
├── setup.sh                  ← one-time setup script
├── .env                      ← empty, required by docker-compose
├── .gitignore
├── INSTALL.md
├── README.md
├── helpers/
│   ├── context.py            ← get_ctx(), build_sw_name()
│   ├── images.py             ← device image loading
│   ├── port_logic.py         ← port mapping and cable logic
│   ├── state.py              ← _is_saveable() key filter
│   └── svg_export.py         ← PDF/JPG export
├── tabs/                     ← one file per tab, each exports render()
│   ├── t01_session.py
│   ├── t02_sizer.py
│   ├── t03_project.py
│   ├── t04_confluence.py
│   ├── t05_preflight.py
│   ├── t07_switch.py
│   ├── t08_data_switch.py
│   ├── t09_rack.py
│   ├── t10_inventory.py
│   ├── t11_ai.py
│   ├── t12_network.py
│   └── t13_kb.py
├── templates/
│   ├── cumulus_nv.j2         ← internal fabric leaf switch config (Cumulus)
│   ├── arista_eos.j2         ← internal fabric leaf switch config (Arista EOS)
│   ├── cumulus_spine.j2      ← spine switch config (Cumulus)
│   └── arista_spine.j2       ← spine switch config (Arista EOS)
├── images/                   ← device hardware photos (PNG, mounted read-only)
│   ├── NVIDIA_SN3700.png
│   ├── NVIDIA_SN4600.png
│   ├── NVIDIA_SN4700.png
│   ├── NVIDIA_SN5400.png
│   ├── NVIDIA_SN5600.png
│   ├── NVIDIA_SN5610.png
│   ├── Arista_7050CX4-24D8.png
│   ├── Arista_7050DX4-32S.png
│   ├── Arista_7060DX5-32S.png
│   ├── Arista_7060DX5-64S.png
│   ├── Ceres_338TB_1U.png
│   ├── Ceres_1350TB_1U.png
│   ├── Ceres_2700TB_1U.png
│   ├── MLK_1350TB_2U.png
│   ├── MLK_2700TB_2U.png
│   ├── MLK_5400TB_2U.png
│   ├── GEN5_Genoa_CNode.png
│   └── GEN6_Turin_CNode.png
├── outputs/                  ← generated switch config files
└── data/
    └── toolkit.db            ← SQLite project database
```

## UI Structure (12 Tabs in app.py)

| Position | Variable | Name | Content |
|----------|----------|------|---------|
| 1 | tab1 | Session | SE identity, SFDC/ticket/Slack links, Save/Load/New Project |
| 2 | tab2 | Capacity & Performance Sizer | DBox/CNode hardware selector, performance curves, DRR override, Apply to Project |
| 3 | tab3 | Project Details | Cluster inventory, topology, links, hardware dropdowns, versions, site notes, completeness indicator |
| 4 | tab7 | Internal Switch — Southbound | Cumulus NV + Arista EOS config generation, port mapping, cable guide |
| 5 | tab8 | Data Switch — Northbound | GPU/data network switch config (optional, toggle-enabled) |
| 6 | tab9 | Rack Diagram | Visual rack diagram, power/weight analysis, PDF/JPG export (A4/A3 landscape) |
| 7 | tab12 | Network Diagram | High-level layered topology SVG — CNodes, DBoxes, switches, uplinks |
| 8 | tab10 | Device Inventory | Custom device library for rack diagram |
| 9 | tab5 | Pre-Flight, Validation & Installation | Equipment checklist, port count, cable labels, LLDP script, pre-flight checklist, per-switch installation procedure (§1–§12) |
| 10 | tab4 | Confluence Install Plan | Auto-generated full install plan in markdown |
| 11 | tab11 | AI Assistant | Project Assistant (local Ollama) + Technical Expert (Claude / GPT-4o / Gemini via API key) |
| 12 | tab13 | Resources | Curated VAST links — Knowledge Base, Field Resources, searchable |

**Important — variable names vs positions:** Tab variable names do **not** match their UI position numbers. The `st.tabs()` unpacking at line ~294 in app.py assigns positions. When adding code to a tab, use `with tabX:` where X is the variable from the table above, not the position number.

## Key Functions (by module)

**`helpers/port_logic.py`**
- `get_port_mappings()` — calculates port allocations for DBoxes/CNodes given topology
- `validate_port_counts()` — checks feasibility of the config (ports available vs. required)
- `render_cable_summary()` — generates the cable requirements table

**`helpers/context.py`**
- `get_ctx()` — returns dict of all derived session-state values; called at top of each tab's `render()`
- `build_sw_name()` — constructs switch hostnames incorporating RU position

**`helpers/images.py`**
- `_get_device_img_b64()` — loads device PNGs from `images/` as base64

## Streamlit 1.32 Session State — Critical Patterns

This is the most important thing to understand about this codebase.

**The problem:** Streamlit 1.32 maintains a widget registry separate from session_state. Once a widget with `key="foo"` has rendered, you cannot set `st.session_state["foo"]` directly from code — it throws `StreamlitAPIException`.

**The solution — `_pending_load` / `_pending_clear` pattern:**

At the very top of app.py (before any widgets render), there is a handler:
```python
if "_pending_load" in st.session_state:
    _pending = st.session_state.pop("_pending_load")
    for _k, _v in _pending.items():
        if _is_saveable(_k):
            st.session_state[_k] = _v

if "_pending_clear" in st.session_state:
    st.session_state.pop("_pending_clear")
    # clears all non-internal keys and resets defaults
```

When you need to SET session_state values programmatically (Load, New Project, Apply from Sizer):
```python
# WRONG — will throw if widget already rendered
st.session_state["proj_num_dboxes"] = 4

# CORRECT — stage it, then rerun
_data = dict(st.session_state)
_data["proj_num_dboxes"] = 4
st.session_state["_pending_load"] = _data
st.rerun()
```

### Widgets that must NOT have key= params

Sidebar identity fields and any field the SE needs to set programmatically must use `value=session_state.get(...)` with no `key=` param, and manually sync back:
```python
se_name = st.text_input("SE Name", value=st.session_state.get("se_name", ""))
st.session_state["se_name"] = se_name
```

### Saveable key whitelist

Only keys with these prefixes are saved/loaded/restored:
```python
_SAVEABLE_PREFIXES = ("proj_", "tab7_", "tab8_", "spine_", "name_", "sizer_")
_SAVEABLE_EXACT = {"se_name", "customer", "cluster_name", "install_date"}
```
Download button keys (`tab7_dl_A`, `tab7_dl_B` etc) are explicitly excluded — Streamlit forbids setting these from code.

### Derived values block

Runs on every render between the sidebar and tab definitions. Always available regardless of which tab the SE is on:
```python
pfx        = st.session_state.get("cluster_name", "") or "VAST"
num_dboxes = int(st.session_state.get("proj_num_dboxes", 1))
num_cnodes = int(st.session_state.get("proj_num_cnodes", 4))
topology   = st.session_state.get("proj_topology", "Leaf Pair")
se_name    = st.session_state.get("se_name", "")
customer   = st.session_state.get("customer", "")
cluster_name = st.session_state.get("cluster_name", "")
install_date = st.session_state.get("install_date", str(date.today()))
```

### Session state key reference

| Prefix | Tab | Description |
|--------|-----|-------------|
| `se_name`, `customer`, `cluster_name`, `install_date` | Tab 1 | SE identity (no key=, manual sync) |
| `proj_*` | Tab 3 | Project details fields |
| `proj_num_dboxes`, `proj_num_cnodes` | Tab 3 | Cluster inventory sliders |
| `proj_dbox_type`, `proj_cbox_type` | Tab 3 | Hardware selectboxes (no key=, manual sync) |
| `proj_dual_nic` | Tab 3 | Dual NIC toggle — drives Tab 7 uplink logic |
| `proj_topology` | Tab 3 | "Leaf Pair" or "Spine-Leaf" |
| `sizer_*` | Tab 2 | Sizer inputs |
| `tab7_*` | tab7 (position 4) | Internal switch config inputs |
| `tab8_*` | tab8 (position 5) | GPU/data switch config inputs |
| `spine_*` | tab7 (position 4) | Spine switch inputs |
| `rack_*` | tab9 (position 6) | Rack diagram inputs |
| `_db_project_id` | internal | Current project ID in SQLite |
| `_save_milestone` | Tab 1 | Selected milestone label |
| `_pending_load` | internal | Staged state for next render |
| `_pending_clear` | internal | Flag to clear all state on next render |
| `_online_status` | internal | Cached online/offline check |
| `_save_msg` | internal | Success message to show after rerun |

## Hardware Profiles

Hardware specs (port counts, connector types, cable vendors, ISL/uplink ranges) are defined in `config.py`.

### Switch models (HARDWARE_PROFILES dict)

| Model | Vendor | OS | Ports | Speed | Form |
|-------|--------|-----|-------|-------|------|
| NVIDIA SN3700 | nvidia | cumulus | 32 | 200GbE | 1U |
| NVIDIA SN4600 | nvidia | cumulus | 64 | 200GbE | 2U |
| NVIDIA SN4700 | nvidia | cumulus | 32 | 400GbE | 1U |
| NVIDIA SN5400 | nvidia | cumulus | 64 | 400GbE | 2U |
| NVIDIA SN5600 | nvidia | cumulus | 64 | 800GbE | 2U |
| NVIDIA SN5610 | nvidia | cumulus | 64 | 800GbE | 2U |
| Arista 7050CX4-24D8 | arista | eos | 32 | 200GbE | 1U |
| Arista 7050DX4-32S | arista | eos | 32 | 400GbE | 1U |
| Arista 7060DX5-32S | arista | eos | 32 | 400GbE | 1U |
| Arista 7060DX5-64S | arista | eos | 64 | 400GbE | 2U |

### DBox models (DBOX_PROFILES dict)

| Model | Raw TB | Usable TB | Form |
|-------|--------|-----------|------|
| Ceres 338TB (1U) | 338 | 245.66 | 1U |
| Ceres 1350TB (1U) | 1350 | 982.62 | 1U |
| Ceres 2700TB (1U) | 2700 | 1965.25 | 1U |
| MLK 1350TB (2U) | 1350 | 1105.45 | 2U |
| MLK 2700TB (2U) | 2700 | 2210.90 | 2U |
| MLK 5400TB (2U) | 5400 | 4421.80 | 2U |

### CNode performance (CNODE_PERF dict — per CNode, 1MB Random)

| Ratio | GEN6 Turin | GEN5 Genoa |
|-------|-----------|-----------|
| 100% Read | 37.0 GB/s | 29.0 GB/s |
| 80/20 | 25.1 GB/s | 17.6 GB/s |
| 60/40 | 17.1 GB/s | 11.0 GB/s |
| 40/60 | 13.3 GB/s | 8.1 GB/s |
| 20/80 | 9.7 GB/s | 6.7 GB/s |
| 100% Write | 7.6 GB/s | 3.5 GB/s |
| 100% Write Burst | 23.0 GB/s | 10.0 GB/s |

### Device physical specs (DEVICE_SPECS dict — for rack diagram)

| Device | U | Weight (lbs) | Avg W | Max W |
|--------|---|-------------|-------|-------|
| NVIDIA SN3700 | 1 | 24.5 | 250 | 250 |
| NVIDIA SN4600 | 2 | 32.3 | 250 | 250 |
| NVIDIA SN4700 | 1 | 25.6 | 630 | 630 |
| NVIDIA SN5400 | 2 | 51.8 | 670 | 1735 |
| NVIDIA SN5600 | 2 | 51.8 | 940 | 2167 |
| NVIDIA SN5610 | 2 | 51.8 | 940 | 2167 |
| Arista 7050CX4-24D8 | 1 | 23.0 | 226 | 465 |
| Arista 7050DX4-32S | 1 | 21.0 | 388 | 989 |
| Arista 7060DX5-32S | 1 | 24.4 | 353 | 880 |
| Arista 7060DX5-64S | 2 | 48.4 | 353 | 1716 |
| Ceres 338TB (1U) | 1 | 50.0 | 750 | 850 |
| Ceres 1350TB (1U) | 1 | 50.0 | 750 | 850 |
| Ceres 2700TB (1U) | 1 | 50.0 | 750 | 850 |
| MLK 1350TB (2U) | 2 | 135.0 | 1270 | 1600 |
| MLK 2700TB (2U) | 2 | 135.0 | 1270 | 1600 |
| MLK 5400TB (2U) | 2 | 135.0 | 1270 | 1600 |
| GEN5 Genoa | 1 | 32.0 | 500 | 700 |
| GEN6 Turin | 1 | 44.0 | 500 | 775 |

## Template Conventions

- MTU 9216 on all data paths
- VLAN 69 for internal storage, VLAN 4094 for MLAG peer
- RoCEv2 QoS with PFC watchdog on Cumulus
- MLAG mac-address is unique per switch pair (derived from session state)
- Breakout cables handled conditionally in templates

### Cable rules

- Node → Switch: **AOC only** (never DAC)
- ISL between switches: DAC if ≤1m, AOC if >1m
- Spine/Uplink: **AOC only**
- MTU: **9216** everywhere (never 9000 or 1500)

### Cumulus NV config rules

- `nv set bridge domain br_default vlan 69` — mandatory
- `nv set bridge domain br_default untagged 10` — always 10, never 1
- `nv set interface vlan69 vlan 69` — mandatory
- NTP: unset all 4 Cumulus defaults before setting customer NTP
- ISL ports must be explicitly typed as `swp`
- MTU 9216 on every port explicitly
- No MLAG priority
- MLAG MAC: `44:38:39:ff:00:69`
- Management VLAN: `nv set interface eth0 vlan {{ mgmt_vlan }}`

### Arista EOS config rules

- VLAN 69 (`VAST-Internal`) mandatory
- VLAN 4094 for MLAG peer link
- `interface Vlan4094` with peer IP
- `interface Management1` with IP, encapsulation dot1q, default route
- No MLAG priority
- MTU 9216 on all ports

### Dual NIC logic

- When `proj_dual_nic = True`: uplink_list forced to empty in Tab 7 storage switch config
- Tab 8 (Data Switch) remains optional regardless of NIC type

## Data Persistence

- SQLite DB and generated outputs are in host-mounted Docker volumes (`./data`, `./outputs`)
- Auto-backup runs daily to `~/vast-toolkit-backups/` (configurable in Session tab)
- State serialization strips Streamlit internals before storing as JSON

**Database locations:**
- In container: `/app/data/toolkit.db`
- On host: `~/projects/vast-se-toolkit/data/toolkit.db`

**Key db.py methods:**
- `save_project(session_state, label)` → project_id
- `load_project(project_id)` → dict
- `load_version(version_id)` → dict
- `list_projects()` → list
- `delete_project(project_id)`
- `get_project_versions(project_id)` → list
- `backup(destination_path)` → filepath
- `auto_backup_if_stale(max_age_hours=24)`

## Naming Conventions

- Storage Switch 1: `{CLUSTER}-NVIDIA-SW1`
- Storage Switch 2: `{CLUSTER}-NVIDIA-SW2`
- Spine Switch 1: `{CLUSTER}-NVIDIA-SPINE-SW1`
- GPU Switch 1: `{CLUSTER}-NVIDIA-SW1-GPU`
- CNode 1: `{CLUSTER}-CNODE-1`
- DBox 1: `{CLUSTER}-DBOX-1`

Generated config filenames:
- `{CLUSTER}_VAST_SWA_NVIDIA_2026-03-18.txt`
- `{CLUSTER}_VAST_SWB_NVIDIA_2026-03-18.txt`
- `{CLUSTER}_VAST_GPU_SWA_NVIDIA_2026-03-18.txt`
- `{CLUSTER}_VAST_SPINE_A_NVIDIA_2026-03-18.txt`

## Known Bugs / Deferred Items

1. **Rack diagram — device name labels** — removed because overlaid text and external column both had layout issues. Options to revisit: hover tooltips (JS in iframe), separate legend panel, or clickable blocks.

## Roadmap

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-rack redesign | ✅ Done | Max 3 racks, manual placement, weight/power pre-check |
| Multi-leaf-pair switch config | ✅ Done | Balanced with multi-rack implementation |
| High-level topology diagram | ✅ Done | Network Diagram tab (t12_network.py) |
| Desktop launcher (.ps1 / .command) | ✅ Done | Tested on Windows and macOS |
| KB / Resources tab | ✅ Done | Curated VAST links, searchable (t13_kb.py) |
| AI Assistant | ✅ Done | Local Ollama (Project Assistant) + cloud Expert (Claude / GPT-4o / Gemini) |
| Google Drive backup | 🔲 Next | Copy toolkit.db to sync folder |
| Rack diagram name labels | 🔲 Backlog | Deferred — hover tooltips or legend panel |

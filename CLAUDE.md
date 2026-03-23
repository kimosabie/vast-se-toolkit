# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

VAST SE Toolkit is a Dockerized Streamlit web application for VAST Systems Engineers to automate cluster installation workflows — generating switch configs, cable guides, pre-flight checklists, and Confluence install plans. It runs locally (Windows WSL2/macOS), requires no cloud login, and targets NVIDIA Cumulus NV and Arista EOS switches.

## Running the App

```bash
# Start (builds on first run)
docker compose up --build -d
# App available at http://localhost:8501

# View logs
docker compose logs --tail=50

# Stop
docker compose down

# Syntax check app.py without rebuilding
docker compose exec vast-se-toolkit python3 -c "import ast; ast.parse(open('app.py').read())"
```

For local development without Docker:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

**`app.py`** (~4500 lines) is the monolithic entry point containing all UI, business logic, hardware profiles, and template rendering. There is no separate routes/controllers layer.

**`db.py`** manages a SQLite database (`data/toolkit.db`) with three tables:
- `projects` — project metadata with soft deletes (`is_deleted=1`)
- `project_versions` — full JSON snapshots of Streamlit session state per save
- `settings` — key/value store (backup location, last backup timestamp)

**`templates/`** — Jinja2 templates rendered by app.py:
- `cumulus_nv.j2` / `cumulus_spine.j2` — NVIDIA Cumulus NV leaf/spine configs
- `arista_eos.j2` / `arista_spine.j2` — Arista EOS data/GPU switch configs

**`outputs/`** — Generated config files written here, host-mounted for persistence.

## UI Structure (10 Tabs in app.py)

| Tab | Purpose |
|-----|---------|
| Session | Project save/load/delete, session management |
| Capacity & Performance Sizer | Cluster capacity calculations with DRR override |
| Project Details | Cluster inventory, topology, hardware, versions, site notes |
| Confluence Install Plan | Auto-generated copy-paste installation guide |
| Validation & Pre-Flight | Port count validation, LLDP scripts, cable labels |
| Installation Procedure | Per-switch steps with real hostnames/IPs |
| Internal Switch — Southbound | Cumulus NV + Arista EOS config gen, port mapping, cable guides |
| Data Switch — Northbound | GPU/data network switch configuration |
| Rack Diagram | Visual rack layout with device images, kW/kg toggles |
| Coming Soon | Placeholder |

## Key Functions in app.py

- `get_port_mappings()` — calculates port allocations for DBoxes/CNodes given topology
- `validate_port_counts()` — checks feasibility of the config (ports available vs. required)
- `render_cable_summary()` — generates the cable requirements table
- `_build_sw_name()` — constructs switch hostnames incorporating RU position
- `_get_device_img_b64()` — loads device PNGs from `images/` as base64

## Hardware Profiles

Hardware specs (port counts, connector types, cable vendors, ISL/uplink ranges) are defined as dicts embedded directly in `app.py`. Supported switches:

- **NVIDIA Cumulus NV**: SN3700, SN4600, SN4700, SN5400, SN5600, SN5610
- **Arista EOS**: 7050CX4-24D8, 7050DX4-32S, 7060DX5-32S, 7060DX5-64S

## Template Conventions

- MTU 9216 on all data paths
- VLAN 69 for internal storage, VLAN 4094 for MLAG peer
- RoCEv2 QoS with PFC watchdog on Cumulus
- MLAG mac-address is unique per switch pair (derived from session state)
- Breakout cables handled conditionally in templates

## Data Persistence

- SQLite DB and generated outputs are in host-mounted Docker volumes (`./data`, `./outputs`)
- Auto-backup runs daily to `~/vast-toolkit-backups/` (configurable in Session tab)
- State serialization strips Streamlit internals before storing as JSON

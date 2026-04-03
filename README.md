# VAST SE Toolkit

A Dockerised Streamlit web app for VAST Systems Engineers.
Automates switch config generation, port mapping, cable labelling, pre-flight validation, rack diagrams, and Confluence install plan generation for VAST cluster installations.

**Runs locally on your laptop. No cloud. No login.**

---

## Quick start

```bash
git clone git@github.com:kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
mkdir -p data outputs
docker compose up --build -d
```

Open **http://localhost:8501**

See [INSTALL.md](INSTALL.md) for full setup instructions including desktop launchers.

---

## What it does

| Tab | Feature |
|-----|---------|
| 🧑‍💻 Session | SE identity, install date, project name, save/load/new project |
| 📏 Capacity & Performance Sizer | DBox/CNode hardware selector, capacity requirement checker, performance curves, DRR override |
| 📋 Project Details | SFDC/ticket/Slack links, software versions, cluster inventory, topology, hardware, site notes |
| 🔌 Internal Switch — Southbound | Cumulus NV + Arista EOS config generation, port mapping, cable guide |
| 🖥️ Data Switch — Northbound | GPU/data network switch config (optional, toggle-enabled) |
| 📐 Rack Diagram | Visual rack layout, power/weight analysis, PDF/JPG export (A4/A3 landscape) |
| 📦 Device Inventory | Custom device library for rack diagram |
| 🤖 AI Assistant | Local LLM (Ollama) config reviewer and troubleshooting assistant |
| ✅ Pre-Flight, Validation & Installation | Equipment checklist, port count validation, cable labels, LLDP script, pre-flight checklist, per-switch step-by-step installation procedure |
| 📄 Confluence Install Plan | Auto-generated full install plan — copy-paste to Confluence |

---

## Supported hardware

### NVIDIA Cumulus NV switches
| Model | Ports | Speed | Form |
|-------|-------|-------|------|
| NVIDIA SN3700 | 32 | 200GbE | 1U |
| NVIDIA SN4600 | 64 | 200GbE | 2U |
| NVIDIA SN4700 | 32 | 400GbE | 1U |
| NVIDIA SN5400 | 64 | 400GbE | 2U |
| NVIDIA SN5600 | 64 | 800GbE | 2U |
| NVIDIA SN5610 | 64 | 800GbE | 2U |

### Arista EOS switches
| Model | Ports | Speed | Form |
|-------|-------|-------|------|
| Arista 7050CX4-24D8 | 32 | 200GbE | 1U |
| Arista 7050DX4-32S | 32 | 400GbE | 1U |
| Arista 7060DX5-32S | 32 | 400GbE | 1U |
| Arista 7060DX5-64S | 64 | 400GbE | 2U |

### Storage (DBox)
| Model | Raw TB | Form |
|-------|--------|------|
| Ceres 338TB | 338 | 1U |
| Ceres 1350TB | 1350 | 1U |
| Ceres 2700TB | 2700 | 1U |
| MLK 1350TB | 1350 | 2U |
| MLK 2700TB | 2700 | 2U |
| MLK 5400TB | 5400 | 2U |

### Compute (CNode)
| Model | Form |
|-------|------|
| GEN5 Genoa | 1U |
| GEN6 Turin | 1U |

---

## Stack

- Python 3.11 · Streamlit 1.32 · Jinja2 · SQLite
- cairosvg · Pillow (PDF/image export)
- Docker Compose
- Runs on Windows (WSL2), macOS, and Linux

---

## File structure

```
vast-se-toolkit/
├── app.py                  ← orchestrator (page config, sidebar, tab layout)
├── config.py               ← hardware profiles and static data
├── db.py                   ← SQLite project database
├── helpers/                ← shared utilities
│   ├── context.py          ← derived session state values
│   ├── images.py           ← device image loading
│   ├── port_logic.py       ← port mapping and cable logic
│   ├── state.py            ← session state key filtering
│   └── svg_export.py       ← PDF/JPG export
├── tabs/                   ← one file per tab
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup.sh                ← one-time setup script
├── templates/              ← Jinja2 switch config templates (volume-mounted)
├── images/                 ← device hardware photos (volume-mounted)
├── outputs/                ← generated config files (host-mounted)
└── data/
    └── toolkit.db          ← SQLite project database (host-mounted)
```

---

## Cable rules

- Node → Switch: **AOC only** (no DAC)
- ISL between switches: DAC ≤1m, AOC >1m
- Spine / Uplink: **AOC only**
- MTU: **9216** everywhere

---

## Updates

```bash
cd ~/projects/vast-se-toolkit
git pull
docker compose pull
docker compose up -d
```

Your saved projects and generated configs are never affected by updates.

---

## Roadmap

- [ ] Multi-rack redesign (manual placement, max 3 racks, weight/power pre-check)
- [ ] Multi-leaf-pair switch config (1–3 leaf pairs per install)
- [ ] High-level topology diagram (CNodes, DBoxes, switches, uplinks)
- [ ] Google Drive auto-backup
- [ ] KB tab (curated VAST links, searchable)

---

*Internal tool — VAST Systems Engineering*

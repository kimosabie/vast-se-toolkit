# VAST SE Toolkit

A Dockerised Streamlit web app for VAST Systems Engineers.
Automates switch config generation, port mapping, cable labelling, pre-flight validation, and Confluence install plan generation for VAST cluster installations.

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
|---|---|
| 📋 Project Details | Inventory, topology, hardware, cluster config, PSNT, versions, site notes |
| 📄 Confluence Install Plan | Auto-generated full install plan — copy-paste to Confluence |
| ✅ Validation & Pre-Flight | Port count validation, LLDP script, pre-flight checklist, cable labels |
| 📋 Installation Procedure | Per-switch steps with real hostnames, IPs, and filenames |
| 🔌 Internal Switch — Southbound | Cumulus NV + Arista EOS config generation, port mapping, cable guide |
| 🖥️ Data Switch — Northbound | GPU/data network switch config (optional) |

---

## Supported hardware

### NVIDIA (Cumulus NV)
| Model | Ports | Speed |
|---|---|---|
| NVIDIA SN3700 | 32 | 200GbE |
| NVIDIA SN4600 | 64 | 200GbE |
| NVIDIA SN4700 | 32 | 400GbE |
| NVIDIA SN5400 | 64 | 400GbE |

### Arista (EOS)
| Model | Ports | Speed |
|---|---|---|
| Arista 7050CX4-24D8 | 32 | 200GbE |
| Arista 7050DX4-32S | 32 | 400GbE |
| Arista 7060DX5-32S | 32 | 400GbE |
| Arista 7060DX5-64S | 64 | 400GbE |

---

## Stack

- Python 3 · Streamlit · Jinja2 · SQLite
- Docker Compose
- Runs on Windows (WSL2) and macOS

---

## File structure

```
vast-se-toolkit/
├── app.py                  ← main application
├── db.py                   ← SQLite project database
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── templates/              ← Jinja2 switch config templates
├── outputs/                ← generated config files (host-mounted)
└── data/                   ← SQLite database (host-mounted)
    └── toolkit.db
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
git pull
docker compose up --build -d
```

Your database and generated configs are preserved.

---

## Roadmap

- [ ] Hardware selectors (CNode/DBox product profiles)
- [ ] Capacity/performance sizer
- [ ] Rack diagram
- [ ] KB tab
- [ ] LLM integration

---

*Internal tool — VAST Systems Engineering*

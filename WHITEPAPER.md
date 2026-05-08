# VAST SE Toolkit — White Paper

**Prepared by:** Kimo  
**Date:** April 2026  
**Audience:** VAST Systems Engineering, Field Leadership

---

## Executive Summary

The VAST SE Toolkit is a locally-run web application purpose-built for VAST Systems Engineers. It eliminates the manual, error-prone work that today consumes hours of every cluster installation engagement — switch configuration generation, cable planning, pre-flight validation, rack design, and install documentation. What previously required an SE to context-switch across spreadsheets, Confluence templates, vendor CLI references, and tribal knowledge now happens in a single guided workflow that produces consistent, correct, ready-to-deploy outputs.

The toolkit runs entirely on the SE's laptop. It requires no cloud login, no VPN, no Salesforce access, and no internet connectivity during an install. Every output — switch configs, cable labels, LLDP scripts, rack diagrams, and Confluence install plans — is generated from the project inputs the SE has already entered, with no duplication of effort.

---

## The Problem

### Cluster installations are complex, and complexity creates risk

A VAST cluster installation involves tens to hundreds of physical devices, multiple switch vendors, precise port assignments, specific VLAN and QoS configurations, and a tightly sequenced installation procedure. Getting any of it wrong — a wrong IP address, a missing MTU setting, a miswired uplink — can cost hours of troubleshooting on-site, delay customer go-live, and damage VAST's reputation for operational excellence.

### The current SE workflow is manual and fragmented

Before this toolkit, a typical SE preparing for a new install would:

- Manually calculate port assignments for DBoxes and CNodes across leaf switch pairs
- Hand-write or copy-paste switch configurations from previous engagements, then adapt them
- Maintain cable labels and port mapping in a separate spreadsheet
- Build a rack diagram in a generic drawing tool, manually tracking power and weight
- Write the Confluence install plan from scratch or adapt an old one
- Verify equipment quantities from memory or another spreadsheet

Each of these steps introduces opportunities for error. Each one also takes time — time that SEs spend before they even arrive on site, and time that compounds when something doesn't match reality on install day.

### Tribal knowledge doesn't scale

Much of what makes a VAST install go smoothly lives in the heads of experienced SEs: which cable types go where, what the MTU must be set to on every port, the correct MLAG MAC address convention, the order in which switches should be configured, what to check before touching the first DBox. This knowledge is hard to transfer, inconsistently applied, and entirely lost when an SE turns over.

### The cost of inconsistency

When two SEs produce configs for similar clusters using different methods, the configs differ in ways that aren't always intentional — different NTP handling, different bridge VLAN settings, different ISL cable assumptions. This variation makes peer review harder, makes support cases harder to diagnose, and makes it harder to build playbooks for common failure modes.

---

## The Solution: VAST SE Toolkit

The VAST SE Toolkit is a structured, guided workflow that takes a set of project inputs — cluster size, hardware model, topology, switch model, IP addressing — and produces every output an SE needs for a successful installation. It encodes VAST's best practices so that every SE, regardless of experience level, produces the same quality of output as the most experienced engineer on the team.

### Core design principles

- **One source of truth.** The SE enters project details once. Every output — configs, cable guide, checklist, rack diagram, Confluence plan — is generated from those same inputs. No re-entering data, no copy-paste errors.
- **Runs locally, works offline.** The app runs in Docker on the SE's own laptop. It works on a plane, in a data center with no guest WiFi, and in any network environment. No cloud dependency for the core workflow.
- **Encodes best practices as defaults.** MTU 9216, VLAN 69, RoCEv2 QoS, correct cable type rules, MLAG MAC convention — these are baked in. The SE configures what changes per install; the toolkit handles what should never change.
- **Saves and restores project state.** The SE can save a project at any milestone, reload it on any machine, and pick up exactly where they left off. Full version history is maintained.

---

## Feature Walkthrough

### 1. Capacity & Performance Sizer

The SE selects a DBox model and CNode generation and enters the customer's required usable capacity and performance targets. The toolkit calculates:

- Total usable capacity (TB) for any combination of DBox count and model
- Aggregate read/write performance at standard read/write ratios (100% read through 100% write)
- Whether the proposed cluster meets the customer's requirements
- Suggested configurations that hit targets with margin

This gives the SE a defensible, model-driven answer to "how many nodes do I need?" before committing to a BOM. Outputs can be applied directly to the project with one click.

**Supported hardware:** Ceres 338TB, 1350TB, 2700TB (1U); MLK 1350TB, 2700TB, 5400TB (2U); GEN5 Genoa and GEN6 Turin CNodes.

### 2. Project Details

The central project record. The SE enters:

- SE identity, customer name, cluster name, and install date
- SFDC opportunity, JIRA/PS ticket, and Slack channel links (active clickable links in the UI)
- VAST software release, OS version, install bundle version, install guide version
- Hardware inventory: DBox count and model, CNode count and generation
- Network topology (Leaf Pair or Spine-Leaf), dual NIC flag
- Site notes and any custom observations

A completeness indicator shows the SE which fields are still missing before the install, reducing the chance of arriving on site without critical information.

### 3. Internal Switch — Southbound (Leaf/Fabric Configs)

This is the primary config generation engine. The SE selects a switch model and enters IP addresses, VLAN, NTP server, ISL port range, and uplink ports. The toolkit:

- Calculates exact port assignments for every DBox and CNode, accounting for dual-port NICs, breakout cables, and topology
- Validates that the selected switch has enough ports for the cluster
- Generates complete, deploy-ready switch configuration files for both switches (Switch A and Switch B) using Jinja2 templates

**NVIDIA Cumulus NV configs include:**
- Full MLAG setup with correct peer link, SVI, and MLAG MAC
- Bridge domain with VLAN 69 (VAST internal storage) and untagged VLAN 10
- RoCEv2 QoS configuration with PFC watchdog
- NTP with Cumulus defaults unset before customer server is applied
- MTU 9216 on every interface, explicitly
- ISL, uplink, and management interface config
- Breakout cable handling where applicable

**Arista EOS configs include:**
- MLAG with VLAN 4094 peer link
- VLAN 69 (VAST-Internal) and peer-link VLANs
- Management interface with dot1q encapsulation and default route
- MTU 9216 on all ports

**Spine-Leaf topology:** When Spine-Leaf is selected, the toolkit also generates spine switch configs (Cumulus or Arista) for the additional spine layer, with correct uplink assignments from each leaf pair.

The SE downloads the generated configs directly from the browser. Config filenames include the cluster name and date for unambiguous identification.

### 4. Data Switch — Northbound (GPU/Data Network)

Optionally enabled for GPU server deployments. The SE configures a separate data network switch (same vendor options) for GPU northbound traffic. When dual NIC is enabled on the project, the toolkit automatically excludes northbound uplinks from the storage switch config, ensuring the two planes don't collide.

### 5. Cable Guide

Generated automatically from the port mapping. Provides:

- A complete cable requirements summary (AOC count by length, DAC count)
- Per-port cable labels for every node-to-switch connection, formatted for labelling guns
- ISL cable specification
- Uplink cable specification

**Cable rules enforced automatically:**
- Node → Switch connections: AOC only (never DAC)
- ISL between switch pairs: DAC if ≤1m, AOC if longer
- Spine/uplink connections: AOC only
- MTU 9216 everywhere

### 6. Rack Diagram

A visual rack layout tool. The SE places devices into up to three racks, with manual positioning. The toolkit renders a pixel-accurate SVG rack diagram showing device images, RU positions, and rack boundaries.

For each rack, it calculates:
- Total rack units consumed
- Aggregate power draw (average and maximum watts)
- Total weight (pounds)

This gives the SE and the data center team a clear pre-check: will this rack exceed the floor load limit? Does the PDU have enough capacity? The diagram exports to PDF or JPG in A4 or A3 landscape for inclusion in documentation.

### 7. Network Diagram

A high-level topology diagram rendered as SVG, showing the full logical network: CNodes, DBoxes, leaf switches, spine switches (when applicable), and uplinks. Automatically updated from project inputs. Exportable for Confluence or customer-facing documents.

### 8. Device Inventory

A custom device library the SE can populate with non-standard equipment for the rack diagram. Supports any device not in the built-in hardware profiles.

### 9. Pre-Flight, Validation & Installation

The most operationally significant tab. Structured as a sequential checklist the SE works through on install day.

**Section 1 — Equipment Checklist:** Auto-generated from the project inputs. Lists every cable (with quantity and type), every switch, every DBox and CNode, and every accessory required for the install. The SE can add custom items. Designed to be printed or opened on a mobile device at the rack.

**Section 2 — Port Count Validation:** Verifies that the selected switch model has enough physical ports to serve the configured cluster. Catches mismatches before the SE reaches the data center.

**Section 3 — Cable Labels:** Formatted per-port cable labels for every connection in the install. Follows VAST naming conventions (cluster name prefix, device and port identifiers).

**Section 4 — LLDP Verification Script:** Auto-generated shell script the SE runs on each switch after cabling to verify every node is connected to the correct port. Eliminates manual LLDP lookups.

**Sections 5–12 — Installation Procedure:** A complete, per-switch step-by-step installation procedure covering:
- Initial switch access and hostname assignment
- NTP and management interface configuration  
- MLAG setup and peer verification
- Node port configuration
- ISL and uplink configuration
- VAST-internal VLAN and SVI setup
- QoS and PFC watchdog configuration
- Verification steps

The procedure is generated from the actual project values — actual hostnames, actual IP addresses, actual port lists — so the SE follows their specific install, not a generic template.

### 10. Confluence Install Plan Generator

Produces a complete, copy-paste-ready Confluence page in markdown format. The plan includes:

- Project metadata (SE, customer, cluster, SFDC, ticket, Slack)
- Hardware inventory and software versions
- Network topology summary
- Switch configuration parameters
- Site notes
- Links to generated config files

The SE copies the output into a new Confluence page using the Markdown macro. What previously took 30–60 minutes to write from scratch takes seconds.

### 11. AI Assistant

Two modes in one tab:

**Project Assistant (local, offline):** Powered by a locally-running Ollama LLM. The assistant has full context of the current project — cluster name, hardware, topology, switch config, install date. The SE can ask questions in natural language: "What cables do I need for this install?" or "What's the MLAG peer IP for Switch B?" without leaving the tool or re-reading their own notes.

**Technical Expert (cloud):** An optional cloud-connected assistant for deeper VAST-specific technical questions. Supports Claude, GPT-4o, and Gemini via the SE's own API key. Useful for troubleshooting edge cases, answering questions about VAST software behavior, or drafting customer communications.

### 12. Resources

A curated, searchable library of VAST links — Knowledge Base articles, Field Resources, install guides, and reference documentation. Eliminates time spent hunting through Confluence or the VAST portal during an install.

---

## Technical Architecture

The toolkit is designed to be easy to deploy, easy to maintain, and easy to update.

- **Containerized:** The entire application runs in Docker. One command (`docker compose up --build -d`) is all it takes to install from scratch. The SE never needs to manage a Python environment or install dependencies manually.
- **Cross-platform:** Runs on Windows (WSL2), macOS, and Linux. The same Docker image runs identically on every machine.
- **Volume-mounted outputs:** Generated configs, the SQLite project database, and Jinja2 templates are stored on the host filesystem, not inside the container. The SE's data survives container rebuilds and updates.
- **Update mechanism:** `git pull && docker compose pull && docker compose up -d`. The SE pulls the latest image (pre-built and hosted on GitHub Container Registry) and restarts. No rebuild required.
- **Public repository:** The source code is at https://github.com/kimosabie/vast-se-toolkit — open for the team to inspect, fork, and contribute.

### Data persistence

Project state is stored in a local SQLite database (`data/toolkit.db`). Each save creates a versioned JSON snapshot of the full session. The SE can:

- Save at any milestone (e.g., "Pre-flight complete", "Switch A done")
- Load any prior version of any project
- Back up the database to Google Drive automatically (daily, when configured)

No project data ever leaves the SE's machine unless the SE explicitly exports it.

---

## Impact and Value

### Time savings, per install

| Task | Manual (before) | With toolkit |
|------|----------------|--------------|
| Switch config generation (both switches) | 45–90 min | 5 min |
| Cable label generation | 20–30 min | Instant |
| Equipment checklist | 15–20 min | Instant |
| Rack diagram | 30–60 min | 5–10 min |
| Confluence install plan | 30–60 min | 2 min |
| Pre-flight validation | Manual, inconsistent | Structured, systematic |
| **Total per install** | **~3–4 hours** | **~15–20 min** |

For a team running 20+ installs per quarter, this is 60–80 hours of SE time returned to customer-facing work per quarter.

### Quality and consistency

- Every config generated by the toolkit follows the same best-practice template. No SE produces a config that forgets to set MTU 9216, uses the wrong VLAN, or misses a QoS setting.
- New SEs ramp faster. The toolkit encodes what experienced SEs know, so a new hire can produce the same quality config on day one.
- Peer review is faster. When all configs follow the same structure, reviewers can scan for deviations rather than reading every line.

### Reduced on-site risk

- Port count validation catches mismatches before the SE travels.
- The equipment checklist ensures nothing is left at the office.
- The LLDP verification script catches cabling errors before configuration begins.
- The structured installation procedure reduces dependency on memory under pressure.

### Institutional knowledge capture

The toolkit encodes VAST's switch configuration standards, cable type rules, naming conventions, and installation sequence into a version-controlled, maintained artifact. When an SE leaves, this knowledge stays.

---

## Roadmap

| Feature | Status |
|---------|--------|
| Multi-rack redesign (manual placement, max 3 racks, power/weight pre-check) | Complete |
| Multi-leaf-pair switch config | Complete |
| High-level topology diagram | Complete |
| Desktop launcher (Windows + macOS) | Complete |
| Resources / Knowledge Base tab | Complete |
| AI Assistant (local + cloud) | Complete |
| Google Drive auto-backup | In progress |
| Rack diagram device name labels | Backlog |

---

## Getting Started

The toolkit is a public repository and can be installed in under 10 minutes on any laptop with Docker Desktop and Git:

```bash
git clone https://github.com/kimosabie/vast-se-toolkit.git
cd vast-se-toolkit
docker compose up --build -d
```

Open **http://localhost:8501** in any browser.

Full install guides for Windows (WSL2), macOS, and Linux are included in the repository.

---

## Conclusion

The VAST SE Toolkit transforms the cluster installation workflow from a manual, fragmented, knowledge-dependent process into a consistent, guided, automated one. It saves hours per install, reduces on-site risk, accelerates new SE onboarding, and captures institutional knowledge in a maintainable, version-controlled form. It is already in use across the SE team and continues to evolve based on field feedback.

---

*VAST SE Toolkit — https://github.com/kimosabie/vast-se-toolkit*  
*Internal tool — VAST Systems Engineering*

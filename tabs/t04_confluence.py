import streamlit as st
from datetime import date
from config import (
    HARDWARE_PROFILES, SPEED_RANK, DBOX_PROFILES, CNODE_PERF,
    DEVICE_SPECS, DEVICE_IMAGES, DEVICE_IMAGE_MAP, DR_ESTIMATES,
)
from helpers.context import get_ctx, build_sw_name
from helpers.images import _get_device_img_b64, _strip_white_bg
from helpers.svg_export import (
    _svg_to_pdf_cached, _svg_to_jpg_cached,
    _build_multipage_pdf, _build_consolidated_pdf,
)
from helpers.port_logic import (
    get_sw_suffix, get_port_mappings, validate_port_counts, render_cable_summary,
)


def render():
    ctx          = get_ctx()
    pfx          = ctx["pfx"]
    num_dboxes   = ctx["num_dboxes"]
    num_cnodes   = ctx["num_cnodes"]
    topology     = ctx["topology"]
    full_sw_a    = ctx["full_sw_a"]
    full_sw_b    = ctx["full_sw_b"]
    se_name      = ctx["se_name"]
    customer     = ctx["customer"]
    cluster_name = ctx["cluster_name"]
    install_date = ctx["install_date"]

    try:
        st.subheader("📄 Confluence Install Plan Generator")
        st.caption(
            "Generates a complete install plan in Confluence-ready markdown. "
            "Fill in the **Project Details** sections in the sidebar, then copy "
            "the output below into a new Confluence page using the Markdown macro."
        )

        # ── Pull all sidebar project detail values ─────────────────
        p_sfdc         = st.session_state.get("proj_sfdc",          "")
        p_ticket       = st.session_state.get("proj_ticket",        "")
        p_slack        = st.session_state.get("proj_slack",         "")
        p_lucid        = st.session_state.get("proj_lucid",         "")
        p_survey       = st.session_state.get("proj_survey",        "")
        p_psnt         = st.session_state.get("proj_psnt",          "")
        p_license      = st.session_state.get("proj_license",       "")
        p_peer_rev     = st.session_state.get("proj_peer_rev",      "")
        p_release      = st.session_state.get("proj_vast_release",  "")
        p_os_ver       = st.session_state.get("proj_os_version",    "")
        p_bundle       = st.session_state.get("proj_bundle",        "")
        p_guide        = st.session_state.get("proj_install_guide", "")
        p_phison       = st.session_state.get("proj_phison",        False)
        p_dbox_type    = st.session_state.get("proj_dbox_type",     "")
        p_cbox_type    = st.session_state.get("proj_cbox_type",     "")
        p_dual_nic     = st.session_state.get("proj_dual_nic",      False)
        p_ipmi         = st.session_state.get("proj_ipmi",          "Outband (Cat6)")
        p_second_nic   = st.session_state.get("proj_second_nic",    "N/A")
        p_nb_mtu       = st.session_state.get("proj_nb_mtu",        "9000")
        p_gpu_svrs     = st.session_state.get("proj_gpu_servers",   "")
        p_dbox_ha      = st.session_state.get("proj_dbox_ha",       False)
        p_encryption   = st.session_state.get("proj_encryption",    False)
        p_similarity   = st.session_state.get("proj_similarity",    "Yes w/ Adaptive Chunking (Default)")
        p_ip_conflict  = st.session_state.get("proj_ip_conflict",   False)
        p_ip_notes     = st.session_state.get("proj_ip_notes",      "")
        p_site_notes   = st.session_state.get("proj_site_notes",    "")

        # ── Pull session data from other tabs ───────────────────────
        t1_sw_model    = st.session_state.get("tab7_sw_model",      list(HARDWARE_PROFILES.keys())[0])
        t1_profile     = HARDWARE_PROFILES[t1_sw_model]
        t1_sw_a_ip     = st.session_state.get("tab7_sw_a_ip",       "192.168.1.1/24")
        t1_sw_b_ip     = st.session_state.get("tab7_sw_b_ip",       "192.168.1.2/24")
        t1_mgmt_gw     = st.session_state.get("tab7_gw",            "192.168.1.254")
        t1_ntp         = st.session_state.get("tab7_ntp",           "")
        t1_vlan        = st.session_state.get("tab7_vlan",          100)
        t1_isl         = st.session_state.get("tab7_isl",           "")
        t1_uplink      = st.session_state.get("tab7_uplink",        "")
        t1_dnode_start = int(st.session_state.get("tab7_dnode_start", 1))
        t1_cnode_start = int(st.session_state.get("tab7_cnode_start", 15))

        t2_enabled     = st.session_state.get("tab8_enabled",       False)
        t2_sw_a_ip     = st.session_state.get("tab8_sw_a_ip",       "192.168.2.1/24")
        t2_sw_b_ip     = st.session_state.get("tab8_sw_b_ip",       "192.168.2.2/24")
        t2_sw_model    = st.session_state.get("tab8_sw_model",      list(HARDWARE_PROFILES.keys())[0])

        spine_en       = (topology == "Spine-Leaf")
        sp_a_ip        = st.session_state.get("spine_a_ip",         "192.168.3.1/24")
        sp_b_ip        = st.session_state.get("spine_b_ip",         "192.168.3.2/24")
        sp_model       = st.session_state.get("spine_sw_model",     list(HARDWARE_PROFILES.keys())[0])
        sp_ntp         = st.session_state.get("spine_ntp",          "")

        # ── Derived values ──────────────────────────────────────────
        sw_a_ip_only   = t1_sw_a_ip.split("/")[0]
        sw_b_ip_only   = t1_sw_b_ip.split("/")[0]
        cidr           = t1_sw_a_ip.split("/")[1] if "/" in t1_sw_a_ip else "24"
        t2_a_ip_only   = t2_sw_a_ip.split("/")[0]
        t2_b_ip_only   = t2_sw_b_ip.split("/")[0]
        sp_a_ip_only   = sp_a_ip.split("/")[0]
        sp_b_ip_only   = sp_b_ip.split("/")[0]

        today_str      = date.today().isoformat()
        _id = install_date
        if isinstance(_id, str):
            try:
                from datetime import datetime as _dt2
                _id = _dt2.strptime(_id, "%Y-%m-%d").date()
            except Exception:
                _id = date.today()
        today_nice     = _id.strftime("%d %B %Y")
        vendor_up      = t1_profile["vendor"].upper()
        t2_profile     = HARDWARE_PROFILES[t2_sw_model]
        sp_profile     = HARDWARE_PROFILES[sp_model]
        sp_vsuf        = get_sw_suffix(sp_model)

        fname_sw_a     = f"{pfx}_VAST_SWA_{vendor_up}_{today_str}.txt"
        fname_sw_b     = f"{pfx}_VAST_SWB_{vendor_up}_{today_str}.txt"
        fname_gpu_a    = f"{pfx}_VAST_GPU_SWA_{t2_profile['vendor'].upper()}_{today_str}.txt"
        fname_gpu_b    = f"{pfx}_VAST_GPU_SWB_{t2_profile['vendor'].upper()}_{today_str}.txt"
        fname_sp_a     = f"{pfx}_VAST_SPINE_A_{sp_profile['vendor'].upper()}_{today_str}.txt"
        fname_sp_b     = f"{pfx}_VAST_SPINE_B_{sp_profile['vendor'].upper()}_{today_str}.txt"

        isl_ports      = [p.strip() for p in t1_isl.split(",") if p.strip()]
        uplink_ports   = [p.strip() for p in t1_uplink.split(",") if p.strip()]

        # Node port ranges for documentation
        dnode_end      = t1_dnode_start + (num_dboxes * 2) - 1
        cnode_end      = t1_cnode_start + num_cnodes - 1

        # ── Helper functions ────────────────────────────────────────
        def _v(val, fallback="⚠️ *NOT SET*"):
            """Return value or a visible placeholder."""
            return val if val else fallback

        def _link(label, url):
            return f"[{label}]({url})" if url else f"{label} *(link not set)*"

        def _yn(flag, yes_text="Yes", no_text="No [Default]"):
            return yes_text if flag else no_text

        def _sw_config_steps(sw_label, hostname, mgmt_ip, config_file, is_primary,
                             peer_ip, ntp_server, sw_os):
            """Generate the per-switch installation procedure block."""
            mgmt_ip_only = mgmt_ip.split("/")[0]
            priority = "1000 (Primary)" if is_primary else "2000 (Secondary)"
            temp_ip = "192.168.2.101"

            ntp_check = (
                f"ntpq -p\n# Look for * or + next to {ntp_server}"
                if ntp_server else
                "ntpq -p\n# ⚠️ NTP server not configured — set in sidebar before using this plan"
            )

            if sw_os == "cumulus":
                reset_cmd = "nv action reset system factory-default"
                apply_cmds = (
                    f"chmod +x /tmp/{config_file}\n"
                    f"sed -i 's/\\r//' /tmp/{config_file}\n"
                    f"/tmp/{config_file}"
                )
                ntp_cmd = ntp_check
            else:  # arista
                reset_cmd = "write erase\nreload"
                apply_cmds = (
                    f"bash /tmp/{config_file}"
                )
                ntp_cmd = "show ntp status\nshow clock"

            return f"""
    #### {sw_label}

    > ⚠️ You may need to hand-type serial commands. Copy/paste can be unreliable over a serial connection.

    Connect your **serial cable** to the console port and **Ethernet cable** to the `eth0` / `Management1` port on **{hostname}**.

    **Step 1 — Reset to factory defaults:**
    ````bash
    {reset_cmd}
    ````
    *Wait for full reboot before continuing.*

    **Step 2 — Set temporary management IP:**
    ````bash
    nv unset interface eth0 ip address dhcp
    nv set interface eth0 ip address {temp_ip}/24
    nv config apply
    ````

    **Step 3 — SCP config file from your laptop** *(run on laptop, not switch)*:
    ````bash
    scp {config_file} cumulus@{temp_ip}:/tmp/
    ````
    *If you see a host key warning, run this first: `ssh-keygen -R {temp_ip}`*

    **Step 4 — Back on serial terminal, remove the temporary IP:**
    ````bash
    nv unset interface eth0 ip address {temp_ip}/24
    ````

    **Step 5 — Apply the configuration:**
    ````bash
    {apply_cmds}
    ````
    *The `sed` command removes Windows CRLF line endings. The script sets the permanent MGMT IP and saves the config.*

    **Step 6 — Connect Cat6 MGMT cable to customer network and validate NTP:**
    ````bash
    date
    {ntp_cmd}
    ````

    ✅ **{hostname}** configured. Permanent MGMT IP: `{mgmt_ip_only}` | MLAG priority: `{priority}`

    ---
    """

        # ── Build download commands ─────────────────────────────────
        # NOTE: We build these as plain strings using \n and string
        # concatenation to avoid triple-backtick inside triple-quote
        # confusion. The content is markdown shown to the SE in Tab 5.

        CODE = "```"  # reusable fence marker — avoids ``` inside """

        if p_os_ver:
            os_download = (
                f"{CODE}bash\n"
                f"# VastOS ISO\n"
                f"aws s3 cp s3://vast-os-iso/{p_os_ver}/vast-os-{p_os_ver}.iso .\n"
                f"aws s3 cp s3://vast-os-iso/{p_os_ver}/vast-os-{p_os_ver}.bfb-image.bfb .       # Ceres V1 DNodes\n"
                f"aws s3 cp s3://vast-os-iso/{p_os_ver}/vast-os-{p_os_ver}.bfb-image.v3.bfb .    # Ceres V2 DNodes\n"
                f"{CODE}"
            )
        else:
            os_download = (
                "> ⚠️ **VastOS Version not set** — enter it in the sidebar under Software Versions."
            )

        if p_bundle and p_release:
            bundle_download = (
                f"**AWS:**\n"
                f"{CODE}bash\n"
                f"aws s3 cp s3://vastdata-releases/release_bundles/service-packs/"
                f"{p_release}/{p_bundle}.vast.tar.gz .\n"
                f"{CODE}\n\n"
                f"**Azure:**\n"
                f"{CODE}\n"
                f"https://vastdatasupporteuwest.blob.core.windows.net/official-releases/"
                f"<build-id>/release/{p_bundle}.vast.tar.gz\n"
                f"{CODE}\n"
                f"*(Get the full Azure SAS URL from the FIELD dashboard for your release.)*\n\n"
                f"**vast\\_bootstrap.sh (AWS):**\n"
                f"{CODE}bash\n"
                f"aws s3 cp s3://vastdata-releases/release_bundles/service-packs/"
                f"{p_release}/vast_bootstrap.sh .\n"
                f"{CODE}\n\n"
                f"> 🍎 **Mac users:** Use `aws s3 cp` or `wget` — "
                f"browsers will gunzip the file automatically."
            )
        else:
            bundle_download = (
                "> ⚠️ **Bundle Version / VAST Release not set** — "
                "enter them in the sidebar under Software Versions."
            )

        # ── Build bootstrap SCP commands ───────────────────────────
        # These are the commands the SE runs on-site to push the bundle
        # to CNode 1 and kick off the VAST bootstrap process.
        if p_bundle:
            bootstrap_cmds = (
                f"Upload the VAST release bundle and bootstrap script to CNode 1 "
                f"(tech port `192.168.2.2`):\n\n"
                f"{CODE}bash\n"
                f"scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f"    {p_bundle}.vast.tar.gz vastdata@192.168.2.2:/vast/bundles/\n\n"
                f"scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f"    vast_bootstrap.sh vastdata@192.168.2.2:/vast/bundles/\n\n"
                f"ssh -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" "
                f"vastdata@192.168.2.2\n"
                f"cd /vast/bundles\n"
                f"chmod u+x ./vast_bootstrap.sh\n"
                f"./vast_bootstrap.sh\n"
                f"{CODE}\n"
                f"*Bootstrapping takes approximately 15 minutes.*"
            )
        else:
            bootstrap_cmds = (
                "> ⚠️ **Bundle Version not set** — enter it in the sidebar. "
                "Commands will populate automatically.\n>\n"
                f"> Template:\n"
                f"> {CODE}bash\n"
                f"> scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f">     <bundle>.vast.tar.gz vastdata@192.168.2.2:/vast/bundles/\n"
                f"> scp -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile /dev/null\" \\\\\n"
                f">     vast_bootstrap.sh vastdata@192.168.2.2:/vast/bundles/\n"
                f"> {CODE}"
            )

        # ── Build switch configuration export commands ──────────────
        

        # ── Build VMS switch add commands ────────────────────────────
        sw_add_cmds = (
            f"switch add --ip {sw_a_ip_only} --username cumulus --password CumulusLinux!\n"
            f"switch add --ip {sw_b_ip_only} --username cumulus --password CumulusLinux!"
        )
        if t2_enabled:
            sw_add_cmds += (
                f"\nswitch add --ip {t2_a_ip_only} --username cumulus --password CumulusLinux!"
                f"\nswitch add --ip {t2_b_ip_only} --username cumulus --password CumulusLinux!"
            )
        if spine_en:
            sw_add_cmds += (
                f"\nswitch add --ip {sp_a_ip_only} --username cumulus --password CumulusLinux!"
                f"\nswitch add --ip {sp_b_ip_only} --username cumulus --password CumulusLinux!"
            )

        # ── Cable quantities ─────────────────────────────────────────
        node_cable_qty  = (num_dboxes * 2 * 2) + (num_cnodes * 2)
        isl_cable_qty   = len(isl_ports) if isl_ports else len(t1_profile["default_isl"])
        node_cable_spec = t1_profile["node_cable"]["spec"]
        isl_spec        = t1_profile["isl_cable_long"]["spec"]
        mgmt_cable_qty  = (num_dboxes * 2) + num_cnodes + 4

        # ── Conditional blocks ───────────────────────────────────────
        phison_block = ""
        if p_phison:
            phison_block = (
                "\n> ⚠️ **PHISON DRIVES DETECTED** — Verify FW level on each DNode:\n"
                "> ```bash\n"
                "> sudo nvme list | grep PASCARI\n"
                "> ```\n"
                "> If FW level is `VF1AT0R4` — **STOP** and update to `VF1AT0R5` before proceeding.\n"
                "> See [DBOX SSD and NVRAM Support Matrix](https://vastdata.atlassian.net/wiki/).\n"
            )

        dual_nic_block = ""
        if p_dual_nic and p_second_nic != "N/A":
            dual_nic_block = (
                f"\n| Second NIC Use | {p_second_nic} |"
                f"\n| Northbound MTU | `{p_nb_mtu}` |"
            )

        gpu_srv_block = f"\n| GPU Servers | {p_gpu_svrs} |" if p_gpu_svrs else ""

        ip_conflict_block = (
            f"\n> ⚠️ **Internal IP conflict** — Alternative range: `{_v(p_ip_notes, 'see SE notes')}`"
            if p_ip_conflict else
            "\n> ✅ No conflict — using default VAST internal IP ranges."
        )

        # ── Per-switch config procedure sections ─────────────────────
        fabric_sw_proc = (
            _sw_config_steps(
                f"Switch A — {full_sw_a} (Primary)",
                full_sw_a, t1_sw_a_ip, fname_sw_a,
                True, sw_b_ip_only, t1_ntp, t1_profile["os"]
            ) +
            _sw_config_steps(
                f"Switch B — {full_sw_b} (Secondary)",
                full_sw_b, t1_sw_b_ip, fname_sw_b,
                False, sw_a_ip_only, t1_ntp, t1_profile["os"]
            )
        )

        gpu_sw_section = ""
        if t2_enabled:
            gpu_ntp = st.session_state.get("tab8_ntp", "")
            gpu_sw_section = (
                "\n---\n\n### GPU / Data Network Switches\n\n"
                f"**Model:** {t2_sw_model} | "
                f"**OS:** {'Cumulus NV' if t2_profile['os'] == 'cumulus' else 'Arista EOS'}\n\n"
                f"Config files: `{fname_gpu_a}` and `{fname_gpu_b}` (downloaded from **Tab 2**)\n"
                + _sw_config_steps(
                    f"GPU Switch A — {full_sw_a}-GPU (Primary)",
                    f"{full_sw_a}-GPU", t2_sw_a_ip, fname_gpu_a,
                    True, t2_b_ip_only, gpu_ntp, t2_profile["os"]
                )
                + _sw_config_steps(
                    f"GPU Switch B — {full_sw_b}-GPU (Secondary)",
                    f"{full_sw_b}-GPU", t2_sw_b_ip, fname_gpu_b,
                    False, t2_a_ip_only, gpu_ntp, t2_profile["os"]
                )
            )

        spine_sw_section = ""
        if spine_en:
            spine_a_name = f"{pfx}-{sp_vsuf}-SPINE-A"
            spine_b_name = f"{pfx}-{sp_vsuf}-SPINE-B"
            spine_ntp    = st.session_state.get("spine_ntp", "")
            spine_sw_section = (
                "\n---\n\n### Spine Switches\n\n"
                f"**Model:** {sp_model} | "
                f"**OS:** {'Cumulus NV' if sp_profile['os'] == 'cumulus' else 'Arista EOS'}\n\n"
                f"Config files: `{fname_sp_a}` and `{fname_sp_b}` (downloaded from **Tab 1 — Spine section**)\n"
                + _sw_config_steps(
                    f"Spine A — {spine_a_name} (Primary)",
                    spine_a_name, sp_a_ip, fname_sp_a,
                    True, sp_b_ip_only, spine_ntp, sp_profile["os"]
                )
                + _sw_config_steps(
                    f"Spine B — {spine_b_name} (Secondary)",
                    spine_b_name, sp_b_ip, fname_sp_b,
                    False, sp_a_ip_only, spine_ntp, sp_profile["os"]
                )
            )

        # ── Config file list for prerequisites ───────────────────────
        config_file_list = f"- `{fname_sw_a}` — {full_sw_a}\n- `{fname_sw_b}` — {full_sw_b}"
        if t2_enabled:
            config_file_list += f"\n- `{fname_gpu_a}` — {full_sw_a}-GPU"
            config_file_list += f"\n- `{fname_gpu_b}` — {full_sw_b}-GPU"
        if spine_en:
            config_file_list += f"\n- `{fname_sp_a}` — {pfx}-{sp_vsuf}-SPINE-A"
            config_file_list += f"\n- `{fname_sp_b}` — {pfx}-{sp_vsuf}-SPINE-B"

        # ── Switch rows for equipment table ──────────────────────────
        switch_table_rows = f"| {t1_sw_model} switches | 2 | ☐ |"
        if t2_enabled:
            switch_table_rows += f"\n| {t2_sw_model} GPU switches | 2 | ☐ |"
        if spine_en:
            switch_table_rows += f"\n| {sp_model} spine switches | 2 | ☐ |"

        total_switch_rail_kits = 2 + (2 if t2_enabled else 0) + (2 if spine_en else 0)

        # ── Dual NIC cabling note ────────────────────────────────────
        dual_nic_cabling = ""
        if p_dual_nic:
            dual_nic_cabling = (
                "\n- ☐ CNode (dual NIC): **RIGHT card LEFT** port → Switch A "
                "| **RIGHT card RIGHT** port → Switch B"
            )
            if p_second_nic != "N/A":
                dual_nic_cabling += (
                    f"\n- ☐ CNode **LEFT NIC** ({p_second_nic}) → customer switch"
                )

        gpu_cabling = ""
        if t2_enabled:
            gpu_cabling = (
                "\n- ☐ Run GPU switch ISL cables (ports: see Tab 2)"
                "\n- ☐ CNode northbound ports → GPU Switch A / GPU Switch B"
            )

        # ── MLAG spine note ──────────────────────────────────────────
        spine_mlag_note = ""
        if spine_en:
            spine_mlag_note = "\nRun the same check on both spine switches."

        # ── IPv6 node count ──────────────────────────────────────────
        total_nodes = num_cnodes + (num_dboxes * 2)

        # ── Assemble the full document ───────────────────────────────
        doc = f"""# {_v(customer, "CUSTOMER")} — {_v(cluster_name, "CLUSTER")} — Install Plan — {today_nice}

---

## ⚠️ Important Site Notes / Site Overview

{_v(p_site_notes, "*(No site notes entered — add them in the sidebar under 📝 Project Details → Site Notes)*")}

---

## Prerequisites

> Prior to filling out this template, you should have a completed and approved Site Survey document.

### Opportunity Document Links

| Document | Link |
|---|---|
| SFDC Opportunity | {_link("SFDC", p_sfdc)} |
| Install Ticket | {_link("Install Ticket", p_ticket)} |
| Slack Internal Channel | {_v(p_slack, "*(not set)*")} |
| Lucidchart Diagrams | {_link("Lucidchart", p_lucid)} |
| Site Survey | {_link("Site Survey", p_survey)} |

### Cluster Name / PSNT / License

| Field | Value |
|---|---|
| Cluster Name | `{_v(cluster_name)}` |
| System PSNT | `{_v(p_psnt)}` |
| License Key | `{_v(p_license)}` |

---

> ⛔ **You must STOP installation attempts if you encounter any issues with VAST Installer where an error presents itself.**
> Engage support before continuing so we do not lose important diagnostic data.
> See: [How to collect logs after installation failure](https://vastdata.atlassian.net/wiki/)

---

### Approvals

| Role | Name | Date | Comments |
|---|---|---|---|
| Sales Engineer (Owner) | {_v(se_name)} | {today_nice} | |
| Customer Success | | | |
| PreSales Peer Review | {_v(p_peer_rev, "*(not set)*")} | | |
| PreSales Mgmt Review | *Only needed for Beta / NPI / etc* | | |
| Engineering | *Only needed for Beta / NPI / DA with approval* | | |

### Known Issues

Verify workarounds relevant to your release: [Known Installation-Expansion-Upgrade Issues](https://vastdata.atlassian.net/wiki/)

### VAST Installer

| Field | Value |
|---|---|
| VAST Install Eligible | ✅ YES |
| VAST Release | `{_v(p_release)}` |
| VAST Install Guide | {_link("Install Guide", p_guide)} |

---

## Administrative Tasks

### Create a Shared_FieldActivities Calendar Invite

- ☐ Calendar invite created with format: `[Case Number] | {_v(customer)} | {_v(cluster_name)} | New Installation`
- ☐ Invite includes: SFDC ticket #, customer name, cluster name, VAST owner, who is doing the work, what the work is

### Open Install Ticket

- ☐ Install ticket created and linked: {_link("Install Ticket", p_ticket)}
- ☐ Customer Slack, SFDC, and Confluence accounts created (new customers)

---

## Installation Planning

### Cluster Information Overview

#### Version Information

> Verify the latest release on the [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/FIELD). The latest GA or Scale service pack must be used for all new installations.

| Component | Version |
|---|---|
| VAST Release | `{_v(p_release)}` |
| VastOS Version | `{_v(p_os_ver)}` |
| Bundle Version | `{_v(p_bundle)}` |

#### Hardware

| Component | Quantity | Type |
|---|---|---|
| DBoxes | {num_dboxes} | {_v(p_dbox_type)} |
| CNodes | {num_cnodes} | {_v(p_cbox_type)} |{gpu_srv_block}
| PHISON Drives | {_yn(p_phison, "⚠️ YES — FW check required", "No")} | |
{phison_block}
#### Networking

| Parameter | Value |
|---|---|
| Management Interface | {p_ipmi} |
| Internal Traffic NIC | {"Mellanox CX7 (Right NIC — Dual NIC config)" if p_dual_nic else "Mellanox CX7"} |
| Dual NIC CNodes | {_yn(p_dual_nic, "Yes", "No")} |{dual_nic_block}
| Switch Model | {t1_sw_model} ({t1_profile["total_ports"]} port, {t1_profile["native_speed"]}) |
| Topology | {topology} |
| Storage VLAN | {t1_vlan} |
| Internal MTU | {t1_profile["mtu"]} |
| Switch A MGMT IP | `{t1_sw_a_ip}` |
| Switch B MGMT IP | `{t1_sw_b_ip}` |
| MGMT Gateway | `{t1_mgmt_gw}` |
| NTP Server | `{_v(t1_ntp)}` |
| Priority Flow Control | ✅ **REQUIRED** — select PFC in VAST Installer → Advanced Network Settings |
{f"| GPU Switch A MGMT IP | `{t2_sw_a_ip}` |" if t2_enabled else ""}
{f"| GPU Switch B MGMT IP | `{t2_sw_b_ip}` |" if t2_enabled else ""}
{f"| Spine A MGMT IP | `{sp_a_ip}` |" if spine_en else ""}
{f"| Spine B MGMT IP | `{sp_b_ip}` |" if spine_en else ""}

**Internal IP Range:** {ip_conflict_block}

#### Cluster Specific Settings

| Setting | Value |
|---|---|
| DBox HA | {_yn(p_dbox_ha, "Yes", "No [Default]")} |
| Similarity | {p_similarity} |
| Encryption at Rest | {_yn(p_encryption, "Yes", "No [Default]")} |

### Create Switch Configurations

> ✅ Switch configurations generated by **VAST SE Toolkit** — download from Tabs 1 and 2.
> All Mellanox switches require Cumulus. Cumulus **requires PFC** to be configured.
> Validate firmware at [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/NET) before applying config.

**Config files:**
{config_file_list}

**Port assignments:**

| Range | Reserved For | Count |
|---|---|---|
| swp{t1_dnode_start}–swp{dnode_end} | DNodes (BF-3 {t1_profile["native_speed"]}) | {num_dboxes * 2} |
| swp{t1_cnode_start}–swp{cnode_end} | CNodes (CX7 {t1_profile["native_speed"]}) | {num_cnodes} |
| {", ".join(isl_ports) if isl_ports else "see Tab 1"} | ISL / Peerlink | {len(isl_ports)} |
| {", ".join(uplink_ports) if uplink_ports else "none configured"} | Uplink to customer | {len(uplink_ports)} |

---

## Preparing To Go On Site

### VAST OS Image Download

{os_download}

### VAST Bundle and vast_bootstrap.sh Download

{bundle_download}

### Assemble Your Kit

- ☐ Laptop with VAST SE Toolkit + all config files downloaded
- ☐ Console cable (RJ45 to USB)
- ☐ Ethernet patch cable (for switch `eth0`)
- ☐ Serial terminal app (PuTTY on Windows / Serial.app on Mac) — **115200, 8N1, no flow control**
- ☐ USB-A/C to USB-C cable (Ceres DBox re-imaging if needed)
- ☐ USB key with VastOS ISO (if re-imaging CNodes or Mavericks DNodes)

### Prepare Cable Labels

> 📥 Download cable labels CSV from **Tab 3 → Section 6** of the VAST SE Toolkit.

---

## On Site Physical Installation

### Confirm New Equipment Shipped Properly

*If possible, arrange for the customer to inventory gear before your arrival.*

| Equipment | Quantity | Confirmed |
|---|---|---|
| DBoxes ({_v(p_dbox_type, "see project details")}) | {num_dboxes} | ☐ |
| DBox rail kits | {num_dboxes} | ☐ |
| DBox bezels | {num_dboxes} | ☐ |
| CNodes ({_v(p_cbox_type, "see project details")}) | {num_cnodes} | ☐ |
| CNode rail kits | {num_cnodes} | ☐ |
{switch_table_rows}
| Switch rail kits | {total_switch_rail_kits} | ☐ |
| Node cables ({node_cable_spec}) | {node_cable_qty} | ☐ |
| ISL / Peerlink cables ({isl_spec}) | {isl_cable_qty} per switch pair | ☐ |
| Cat6 management cables | {mgmt_cable_qty} | ☐ |
| Power cables | As per BOM | ☐ |

*If anything is missing or damaged — notify **#manufacturing** or **{_v(p_slack, "#opp_<dealname>")}** immediately.*

### Rack and Stack

- ☐ Check DBox drives — physically push on every drive on both sides before racking (can come loose in shipping)
- ☐ Check CNode boot drives are not loose
- ☐ Rack per site survey layout: {_link("Site Survey", p_survey)}
- ☐ Attach DBox bezels after racking

### Power Cabling

- ☐ Switch power: 1 cable per PDU — **crossed** so each switch has one cable to each PDU
- ☐ CNode power: 1 cable per PDU
- ☐ DBox power (Ceres): left connections → left PDU, right connections → right PDU
- ☐ Check all PSU LEDs are **Green** after powering on
- ☐ **Do NOT power on CNodes** until switches are configured and high-speed cabling is complete
- ☐ Verify PDU phase/circuit balance — do not overload

### Network Cabling

- ☐ Run Cat6 management cables to switch `mgmt0` — **do not connect to customer network yet**
- ☐ Run ISL cables between Switch A and Switch B (ports: `{", ".join(isl_ports) if isl_ports else "see Tab 1"}`)
- ☐ Run external uplink cables to switches — **do not connect to customer core yet**
- ☐ DNode **LEFT** BF-3 port → Switch A | **RIGHT** BF-3 port → Switch B
- ☐ CNode (single NIC): **LEFT** CX7 port → Switch A | **RIGHT** CX7 port → Switch B{dual_nic_cabling}{gpu_cabling}
- ☐ Confirm sufficient cable slack for DBox to slide out fully

### 📷 Take a Picture

Take a photo of the rear of the rack before powering on. Attach to the SFDC install case.

---

## Commissioning the System

### Laptop Setup

1. Set Ethernet adapter to `192.168.2.254/24`
2. Ensure SCP connections are allowed through your firewall: [How To Allow SCP](https://vastdata.atlassian.net/wiki/)
3. Enable terminal session logging for all serial and SSH sessions

### Switch OS Upgrade

> Validate firmware version: [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/NET)
> Switches must be on LTS/Stable version. Follow: [Cumulus Switch Upgrade Guide](https://vastdata.atlassian.net/wiki/)

### Switch Configuration

> Configs include: MLAG, ISL, port descriptions, MTU {t1_profile["mtu"]}, NTP `{_v(t1_ntp)}`, and PFC settings.
> Generated by VAST SE Toolkit — filenames below match the download buttons in Tabs 1 and 2.

#### Internal Storage Fabric

**Model:** {t1_sw_model} | **OS:** {"Cumulus NV" if t1_profile["os"] == "cumulus" else "Arista EOS"}
{fabric_sw_proc}{gpu_sw_section}{spine_sw_section}

---

## Pre-Install Validations

### MLAG / MCLAG Validation

Run on **both** fabric switches. One must show `local-role: primary`, the other `secondary`. Both must show `peer-alive: True`.

```bash
nv show mlag
```

**Expected — {full_sw_a} (Primary):**
```
local-role      primary
peer-role       secondary
peer-alive      True
[backup]        {sw_b_ip_only}
```

**Expected — {full_sw_b} (Secondary):**
```
local-role      secondary
peer-role       primary
peer-alive      True
[backup]        {sw_a_ip_only}
```
{spine_mlag_note}

### Peerlink Validation

```bash
nv show interface peerlink
```
Confirm `oper-status: up` and `link.state: up`.

### MTU Validation

```bash
nv show interface | grep mtu
# All node ports should show {t1_profile["mtu"]}
```

### LLDP Validation

Run the LLDP validation script (download from **Tab 3 → Section 4**) on both switches.
Confirm all **{(num_dboxes * 2) + num_cnodes}** expected nodes are visible before starting bootstrap.

### (Optional) Re-Image CNodes and DNodes

Applying a fresh OS image before installation increases success rate by ensuring the latest OS fixes are applied. See: [Install vast-os on a CERES dnode](https://vastdata.atlassian.net/wiki/)

---

## Generate IPv6 Addresses for All Nodes

> ⚠️ **This step is mandatory before running VAST Installer.**

Connect laptop to the tech port of **each node** in turn (start from lowest CNode, bottom-right port):

```bash
ping 192.168.2.2
ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile /dev/null" vastdata@192.168.2.2
# Default password: vastdata
sudo python3 /usr/bin/config_ipv6.py && exit
```

- CNodes take ~1–2 minutes to execute
- Dual NIC errors can be safely ignored
- **Do NOT disconnect** the tech port cable until the process completes
- Repeat for every node: **{num_cnodes} CNodes + {num_dboxes * 2} DNodes = {total_nodes} total**

---

## Run VAST Installer

### Validate Drive Formatting

> ⚠️ **Mandatory BEFORE installation starts.** All NVMe drives must use 512-byte blocks — not 4KiB.

Login to each DNode and run:

```bash
sudo /bin/expose_drives.py -c disable
sudo /bin/expose_drives.py -c enable
sudo /bin/expose_drives.py -c perst
sudo nvme list
```

📸 Screenshot `nvme list` output from each DNode and attach to the SFDC install case.

> ❌ If any drive shows 4KiB format — **DO NOT CONTINUE**. Escalate to Amit Levin or Adar Zinger.
{phison_block}
### Bootstrap the Cluster

> ⚠️ Use **Incognito Mode** in Google Chrome — VAST Installer caches fields from previous sessions.
> ⚠️ **CRITICAL** — Select **Priority Flow Control** in VAST Installer → Advanced Network Settings. Default is Global Pause which will cause installation failures on Cumulus switches.

{bootstrap_cmds}

Once bootstrap completes and hardware is discovered, follow the [VAST Install Guide]({_v(p_guide, "https://kb.vastdata.com")}) to complete the installation.

### Run Automated Sanity Checks

Follow [Automated Cluster Inspection](https://vastdata.atlassian.net/wiki/x/AQAXaQE):

```bash
wget "https://vastdatasupport.blob.core.windows.net/support-tools/main/support/upgrade_checks/vast_support_tools.py" \\
    -O /vast/data/vast_support_tools.py
chmod +x /vast/data/vast_support_tools.py
/vast/data/vms.sh /vast/data/vast_support_tools.py inspect
```

> ⚠️ If any critical errors are flagged — **do not hand off the cluster to the customer** until resolved.
> ✅ Success indicator: `INFO:support-checks.log:All NVMe drives are correctly formatted with 512-byte blocks`

### Add Switches to VMS

**GUI:** Infrastructure → Switches → Add New Switch → enter MGMT IP and credentials.

**vcli:**
```bash
{sw_add_cmds}
```

---

## Post Install Validations

### Run vnetmap

```bash
vnetmap
```

### Run vast_support_tools

```bash
/vast/data/vms.sh /vast/data/vast_support_tools.py inspect
```

### Gather VMS Log Bundle

VMS → Support → Download Log Bundle. Attach to the SFDC install case.

### Configure Call Home / Cloud Integration

Follow [Call Home Configuration Guide](https://vastdata.atlassian.net/wiki/).

### Validate and Document Cluster Performance

```bash
vperfsanity
```

Document output and attach to the SFDC install case.

---

## Customer Handoff

- ☐ **Check VMS** — all nodes discovered, healthy green status
- ☐ **Create VIP** — configure management VIP in VMS
- ☐ **Test VIP failover** — confirm VIP moves correctly between CNodes
- ☐ **Confirm VIP movement and ARP updates** work across the customer network
- ☐ **Generate and add cluster license** — License Key: `{_v(p_license)}`
  - VMS → Settings → License → Add License
- ☐ **C/D-Box placement** confirmed in VMS rack view
- ☐ **Password management** — change all default passwords (cumulus, vastdata, IPMI)
- ☐ **Switch monitoring** — confirm switches visible in VMS → Infrastructure → Switches
- ☐ **Run Post-Install Survey** — [Post-Install Survey](https://vastdata.atlassian.net/wiki/)
- ☐ **Customer sign-off** obtained

---

*Generated by VAST SE Toolkit v1.0.0 | SE: {_v(se_name)} | Customer: {_v(customer)} | {today_nice}*
"""

        # ── Completeness check ────────────────────────────────────────
        missing = []
        if not p_psnt:        missing.append("System PSNT")
        if not p_license:     missing.append("License Key")
        if not p_release:     missing.append("VAST Release")
        if not p_os_ver:      missing.append("VastOS Version")
        if not p_bundle:      missing.append("Bundle Version")
        if not p_sfdc:        missing.append("SFDC URL")
        if not p_dbox_type:   missing.append("DBox Type")
        if not p_cbox_type:   missing.append("CNode Type")
        if not p_site_notes:  missing.append("Site Notes")
        if not t1_ntp:        missing.append("NTP Server (Tab 5)")

        st.markdown("---")

        if missing:
            st.warning(
                f"⚠️ **{len(missing)} field(s) not set** — "
                "these sections will show placeholder text:\n\n"
                + "\n".join(f"- {m}" for m in missing)
                + "\n\nFill them in **Tab 1 — Project Details**."
            )
        else:
            st.success("✅ All key fields populated — install plan is ready.")

        st.markdown("### 📄 Generated Install Plan")
        st.caption(
            "Copy the text below and paste into a new Confluence page. "
            "Use Insert → Other Macros → Markdown to render it."
        )

        st.code(doc, language="markdown")

        st.download_button(
            label="📥 Download Install Plan (.md)",
            data=doc,
            file_name=f"{pfx}_Install_Plan_{today_str}.md",
            mime="text/markdown",
            key="tab7_download"
        )

    except Exception as e:
        import traceback
        st.error(f"Tab 2 crashed: {e}")
        st.code(traceback.format_exc())




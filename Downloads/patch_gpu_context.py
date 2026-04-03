# =============================================================
# app.py — GPU context2 complete fix
# Replaces the entire context2 dict in one shot
# Fixes: hostname dots, mlag_mac, uplink_description, is_gpu_switch
# Run from toolkit root: python3 patch_gpu_context.py
# =============================================================

with open("app.py", "r") as f:
    content = f.read()

OLD = '''                    context2 = {
                        "se_name":       se_name or "—",
                        "customer":      customer or "—",
                        "cluster_name":  cluster_name or "—",
                        "install_date":  str(install_date),
                        "hostname":      (
                            f"{full_sw_a}-GPU" if side == "A"
                            else f"{full_sw_b}-GPU"
                        ),
                        "mgmt_ip":       sw_a_ip2 if side == "A" else sw_b_ip2,
                        "mgmt_gw":       mgmt_gw2,
                        "mgmt_vlan":     int(st.session_state.get("tab8_mgmt_vlan", 1)),
                        "ntp_server":    ntp_srv2 or mgmt_gw2,
                        "gpu_vlans":     _valid_vlans,
                        "vlan_id":       _valid_vlans[0] if _valid_vlans else 200,
                        "mtu":           profile2["mtu"],
                        "isl_ports":     isl_list2,
                        "uplink_ports":  uplink_list2,
                        "clag_id":       200,
                        "peer_ip":       (
                            sw_b_ip2.split("/")[0] if side == "A"
                            else sw_a_ip2.split("/")[0]
                        ),
                        "port_map":      port_map2,
                        "clag_priority": 1000 if side == "A" else 2000,
                    }'''

NEW = '''                    context2 = {
                        "se_name":       se_name or "—",
                        "customer":      customer or "—",
                        "cluster_name":  cluster_name or "—",
                        "install_date":  str(install_date),
                        "hostname":      (
                            f"{full_sw_a}-GPU" if side == "A"
                            else f"{full_sw_b}-GPU"
                        ).replace(".", "-"),
                        "mgmt_ip":       sw_a_ip2 if side == "A" else sw_b_ip2,
                        "mgmt_gw":       mgmt_gw2,
                        "mgmt_vlan":     int(st.session_state.get("tab8_mgmt_vlan", 1)),
                        "ntp_server":    ntp_srv2 or mgmt_gw2,
                        "gpu_vlans":     _valid_vlans,
                        "vlan_id":       _valid_vlans[0] if _valid_vlans else 200,
                        "mtu":           profile2["mtu"],
                        "isl_ports":     isl_list2,
                        "uplink_ports":  uplink_list2,
                        "clag_id":       200,
                        "mlag_mac":      "44:38:39:ff:00:02",
                        "uplink_description": "Gigabrain-Firewall",
                        "is_gpu_switch": True,
                        "peer_ip":       (
                            sw_b_ip2.split("/")[0] if side == "A"
                            else sw_a_ip2.split("/")[0]
                        ),
                        "port_map":      port_map2,
                        "clag_priority": 1000 if side == "A" else 2000,
                    }'''

assert OLD in content, "Target not found — paste the error and we'll check indentation"
content = content.replace(OLD, NEW, 1)
print("GPU context2 patch applied")

with open("app.py", "w") as f:
    f.write(content)

print("Done")
print("Verify with:")
print('  grep -n "mlag_mac\\|uplink_description\\|is_gpu_switch\\|replace.*\\." app.py')

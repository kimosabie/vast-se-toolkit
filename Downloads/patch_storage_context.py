# =============================================================
# app.py — storage context complete fix
# Replaces the entire storage context dict in one shot
# Fixes: hostname dots, mlag_mac, uplink_description, is_gpu_switch
# Run from toolkit root: python3 patch_storage_context.py
# =============================================================

with open("app.py", "r") as f:
    content = f.read()

OLD = '''                context = {
                    "se_name":       se_name or "—",
                    "customer":      customer or "—",
                    "cluster_name":  cluster_name or "—",
                    "install_date":  str(install_date),
                    "hostname":      full_sw_a if side == "A" else full_sw_b,
                    "mgmt_ip":       sw_a_ip if side == "A" else sw_b_ip,
                    "mgmt_gw":       mgmt_gw,
                    "mgmt_vlan":     int(st.session_state.get("tab7_mgmt_vlan", 1)),
                    "ntp_server":    ntp_srv or mgmt_gw,
                    "vlan_id":       vlan_id,
                    "mtu":           profile["mtu"],
                    "isl_ports":     isl_list,
                    "uplink_ports":  uplink_list,
                    "clag_id":       100,
                    "peer_ip":       sw_b_ip.split("/")[0] if side == "A"
                                     else sw_a_ip.split("/")[0],
                    "port_map":      port_map,
                    "clag_priority": 1000 if side == "A" else 2000,
                }'''

NEW = '''                context = {
                    "se_name":       se_name or "—",
                    "customer":      customer or "—",
                    "cluster_name":  cluster_name or "—",
                    "install_date":  str(install_date),
                    "hostname":      (full_sw_a if side == "A" else full_sw_b).replace(".", "-"),
                    "mgmt_ip":       sw_a_ip if side == "A" else sw_b_ip,
                    "mgmt_gw":       mgmt_gw,
                    "mgmt_vlan":     int(st.session_state.get("tab7_mgmt_vlan", 1)),
                    "ntp_server":    ntp_srv or mgmt_gw,
                    "vlan_id":       vlan_id,
                    "mtu":           profile["mtu"],
                    "isl_ports":     isl_list,
                    "uplink_ports":  uplink_list,
                    "clag_id":       100,
                    "mlag_mac":      "44:38:39:ff:00:01",
                    "uplink_description": "Customer-Core",
                    "is_gpu_switch": False,
                    "peer_ip":       sw_b_ip.split("/")[0] if side == "A"
                                     else sw_a_ip.split("/")[0],
                    "port_map":      port_map,
                    "clag_priority": 1000 if side == "A" else 2000,
                }'''

assert OLD in content, "Target not found — paste the error and we'll check indentation"
content = content.replace(OLD, NEW, 1)
print("Storage context patch applied")

with open("app.py", "w") as f:
    f.write(content)

print("Done")
print("Verify with:")
print('  grep -n "mlag_mac\\|uplink_description\\|is_gpu_switch\\|replace.*\\." app.py')

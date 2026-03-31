import streamlit as st
from jinja2 import Environment, FileSystemLoader
from datetime import date
import sys
import os
import requests
sys.path.insert(0, os.path.dirname(__file__))
try:
    import db as _db
    _DB_AVAILABLE = True
except Exception as _db_import_err:
    _DB_AVAILABLE = False

_INV_CACHE_KEY = "_inv_devices_cache"

def _get_inventory_cached():
    """Return cached inventory list. Call _inv_cache_invalidate() after any write."""
    if _INV_CACHE_KEY not in st.session_state:
        st.session_state[_INV_CACHE_KEY] = _db.list_inventory_devices() if _DB_AVAILABLE else []
    return st.session_state[_INV_CACHE_KEY]

def _inv_cache_invalidate():
    st.session_state.pop(_INV_CACHE_KEY, None)

# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(
    page_title="VAST SE Installation Toolkit",
    page_icon="⚡",
    layout="wide"
)

# ============================================================
# HARDWARE PROFILES
# ============================================================
HARDWARE_PROFILES = {
    "NVIDIA SN3700": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       32,
        "native_speed":      "200GbE",
        "connector":         "QSFP56",
        "mtu":               9216,
        "node_cable":        {"spec": "200G AOC",           "supplier": "VAST"},
        "isl_cable_short":   {"spec": "200G DAC (≤1m)",     "supplier": "VAST"},
        "isl_cable_long":    {"spec": "200G AOC (>1m)",     "supplier": "VAST"},
        "spine_cable":       {"spec": "200G AOC",           "supplier": "VAST"},
        "breakout_required": False,
        "customer_cables":   False,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "Mid-to-large cluster leaf switch"
    },
    "NVIDIA SN4600": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       64,
        "native_speed":      "200GbE",
        "connector":         "QSFP28",
        "mtu":               9216,
        "node_cable":        {"spec": "200G AOC",           "supplier": "VAST"},
        "isl_cable_short":   {"spec": "200G DAC (≤1m)",     "supplier": "VAST"},
        "isl_cable_long":    {"spec": "200G AOC (>1m)",     "supplier": "VAST"},
        "spine_cable":       {"spec": "200G AOC",           "supplier": "VAST"},
        "breakout_required": False,
        "customer_cables":   False,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "Large cluster leaf or spine"
    },
    "NVIDIA SN4700": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       32,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "AI/GPU workloads, spine capable"
    },
    "NVIDIA SN5400": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       64,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "NCP AI scale-out, spine"
    },
    "NVIDIA SN5600": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       64,
        "native_speed":      "800GbE",
        "connector":         "OSFP",
        "mtu":               9216,
        "node_cable":        {"spec": "800G→4x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "800G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "800G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "800G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "800G→4x200G",
        "customer_cables":   True,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "Next-gen 800G AI/spine"
    },
    "NVIDIA SN5610": {
        "vendor":            "nvidia",
        "os":                "cumulus",
        "total_ports":       64,
        "native_speed":      "800GbE",
        "connector":         "OSFP",
        "mtu":               9216,
        "node_cable":        {"spec": "800G→4x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "800G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "800G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "800G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "800G→4x200G",
        "customer_cables":   True,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "Next-gen 800G AI/spine enhanced"
    },
    "Arista 7050CX4-24D8": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       32,
        "native_speed":      "200GbE",
        "connector":         "QSFP56",
        "mtu":               9216,
        "node_cable":        {"spec": "200G AOC",           "supplier": "VAST"},
        "isl_cable_short":   {"spec": "200G DAC (≤1m)",     "supplier": "VAST"},
        "isl_cable_long":    {"spec": "200G AOC (>1m)",     "supplier": "VAST"},
        "spine_cable":       {"spec": "200G AOC",           "supplier": "VAST"},
        "breakout_required": False,
        "customer_cables":   False,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "Mixed 200G/400G ports, ToR leaf"
    },
    "Arista 7050DX4-32S": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       32,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "High-density 400G leaf"
    },
    "Arista 7060DX5-32S": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       32,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [29, 30, 31, 32],
        "default_uplink":    [27, 28],
        "max_node_ports":    26,
        "form_factor":       "1U",
        "notes":             "Latest gen 400G leaf/spine"
    },
    "Arista 7060DX5-64S": {
        "vendor":            "arista",
        "os":                "eos",
        "total_ports":       64,
        "native_speed":      "400GbE",
        "connector":         "QSFP-DD",
        "mtu":               9216,
        "node_cable":        {"spec": "400G→2x200G AOC breakout", "supplier": "CUSTOMER"},
        "isl_cable_short":   {"spec": "400G DAC (≤1m)",           "supplier": "CUSTOMER"},
        "isl_cable_long":    {"spec": "400G AOC (>1m)",           "supplier": "CUSTOMER"},
        "spine_cable":       {"spec": "400G AOC",                 "supplier": "CUSTOMER"},
        "breakout_required": True,
        "breakout_spec":     "400G→2x200G",
        "customer_cables":   True,
        "default_isl":       [61, 62, 63, 64],
        "default_uplink":    [59, 60],
        "max_node_ports":    58,
        "form_factor":       "2U",
        "notes":             "High-density 400G leaf/spine"
    },
}

# Speed rank — spine must be >= leaf, same vendor
SPEED_RANK = {
    "200GbE": 1,
    "400GbE": 2,
}

# ============================================================
# DBOX PRODUCT PROFILES
# ============================================================
DBOX_PROFILES = {
    "Ceres 338TB (1U)":   {"raw_tb": 338,   "usable_tb": 245.66,  "form_factor": "1U", "model": "DF-3015"},
    "Ceres 1350TB (1U)":  {"raw_tb": 1350,  "usable_tb": 982.62,  "form_factor": "1U", "model": "DF-3060"},
    "Ceres 2700TB (1U)":  {"raw_tb": 2700,  "usable_tb": 1965.25, "form_factor": "1U", "model": "DF-3120"},
    "MLK 1350TB (2U)":    {"raw_tb": 1350,  "usable_tb": 1105.45, "form_factor": "2U", "model": "MLK-1350"},
    "MLK 2700TB (2U)":    {"raw_tb": 2700,  "usable_tb": 2210.90, "form_factor": "2U", "model": "MLK-2700"},
    "MLK 5400TB (2U)":    {"raw_tb": 5400,  "usable_tb": 4421.80, "form_factor": "2U", "model": "MLK-5400"},
}

# ============================================================
# CNODE PERFORMANCE PROFILES (per CNode, 1MB Random)
# ============================================================
CNODE_PERF = {
    "GEN6 Turin": {
        "100% Read":            37.0,
        "80/20 Read/Write":     25.1,
        "60/40 Read/Write":     17.1,
        "40/60 Read/Write":     13.3,
        "20/80 Read/Write":      9.7,
        "100% Write":            7.6,
        "100% Write Burst":     23.0,
    },
    "GEN5 Genoa": {
        "100% Read":            29.0,
        "80/20 Read/Write":     17.6,
        "60/40 Read/Write":     11.0,
        "40/60 Read/Write":      8.1,
        "20/80 Read/Write":      6.7,
        "100% Write":            3.5,
        "100% Write Burst":     10.0,
    },
}

# ============================================================
# DEVICE PHYSICAL SPECS (weight in lbs, power in watts)
# Source: VAST Hardware Details spreadsheet
# ============================================================
DEVICE_SPECS = {
    # Switches
    "NVIDIA SN3700":       {"u": 1, "weight_lbs": 24.5, "avg_w": 250,  "max_w": 250},
    "NVIDIA SN4600":       {"u": 2, "weight_lbs": 32.3, "avg_w": 250,  "max_w": 250},
    "NVIDIA SN4700":       {"u": 1, "weight_lbs": 25.6, "avg_w": 630,  "max_w": 630},
    "NVIDIA SN5400":       {"u": 2, "weight_lbs": 51.8, "avg_w": 670,  "max_w": 1735},
    "NVIDIA SN5600":       {"u": 2, "weight_lbs": 51.8, "avg_w": 940,  "max_w": 2167},
    "NVIDIA SN5610":       {"u": 2, "weight_lbs": 51.8, "avg_w": 940,  "max_w": 2167},
    "Arista 7050CX4-24D8": {"u": 1, "weight_lbs": 23.0, "avg_w": 226,  "max_w": 465},
    "Arista 7050DX4-32S":  {"u": 1, "weight_lbs": 21.0, "avg_w": 388,  "max_w": 989},
    "Arista 7060DX5-32S":  {"u": 1, "weight_lbs": 24.4, "avg_w": 353,  "max_w": 880},
    "Arista 7060DX5-64S":  {"u": 2, "weight_lbs": 48.4, "avg_w": 353,  "max_w": 1716},
    # DBoxes
    "Ceres 338TB (1U)":    {"u": 1, "weight_lbs": 50.0, "avg_w": 750,  "max_w": 850},
    "Ceres 1350TB (1U)":   {"u": 1, "weight_lbs": 50.0, "avg_w": 750,  "max_w": 850},
    "Ceres 2700TB (1U)":   {"u": 1, "weight_lbs": 50.0, "avg_w": 750,  "max_w": 850},
    "MLK 1350TB (2U)":     {"u": 2, "weight_lbs": 135.0,"avg_w": 1270, "max_w": 1600},
    "MLK 2700TB (2U)":     {"u": 2, "weight_lbs": 135.0,"avg_w": 1270, "max_w": 1600},
    "MLK 5400TB (2U)":     {"u": 2, "weight_lbs": 135.0,"avg_w": 1270, "max_w": 1600},
    # CNodes
    "GEN5 Genoa":          {"u": 1, "weight_lbs": 32.0, "avg_w": 500,  "max_w": 700},
    "GEN6 Turin":          {"u": 1, "weight_lbs": 44.0, "avg_w": 500,  "max_w": 775},
}

# ============================================================
# DEVICE FRONT PANEL IMAGES (base64 thumbnails)
# ============================================================
DEVICE_IMAGES = {
    "NVIDIA SN3700": "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",
    "NVIDIA SN4600": "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",
    "NVIDIA SN4700": "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",
    "NVIDIA SN5400": "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",
    "NVIDIA SN5600": "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",
    "NVIDIA SN5610": "iVBORw0KGgoAAAANSUhEUgAAARgAAAA4CAYAAAAmVecOAACLaklEQVR42nT9d7it2V3fCX7WWm/eOZyc7rmxslSlKkmgQByHMbbb5ulxe9xtz9g97mcad4/t6W53G5pgsAGDDcaADMiAJIJIFlEggUBIAuVcqly3bqibT9zxTWut+WOtvW/J3XOf5zz33nPO3vtN67d+4RvEtad/w949PEZJiVLS/S0UQggAjAAlACwGSaAE1hosCilAYBFCYo1FSIsUAdaCkBasAIH7sgIpJAiNNSClwqL9D6V7dyEwSAQGIXD/tu44QCOkwCCQxr2vNRYhwHL/ozAWIQQWCxaEEBj/c6kt2hqEAmFxn20FxhqkkBhrwBqEFGgrUEJircFY/zlGg5UIKbDG4q6KxRqLlAJtrH+NxR2VwFqLESCMxViDEWCtXV5fay0Cf7z+/9b6a4fAutPAGOMupRAYq8GCte5eCNw5INz5WxbvbdzvG/+euGu2ODr894y/Vv6E3NU2GqxFSemumf/1xb8xYIV1b2EESHeMGANSYiwIYbDWfWtxF5fH4W+aFeb+cfjrbLTAYtxVsQIhAGvQBoSQX/0+xgAC4/+PsGhjkFa46yYswrh77f7tjtndPuMvmb+O1qL9NQd/zQTL+2kBo/3JWDD+2gtr3edb4c5VGH8fxfIaLO6VXV5z/0xa9/4a647ZCrQFazXW31OxuCdW+PPFrR3/WotYPmvu6/7xu5+747VYxOJ75v7PDNJdF8Bglue2vM7+tVjQ/jlcPPcuFvhHzy0ff6xu3QRf/MpL/P4HPsKFs3uc2dsgCBRhuAgwFqUkRru/EZK61kShRGsQAqQU1LUlUNIFIQNBGKDrCikVQii0rgkC9z4Ii5ASXRv3PWsw2hIE/ubIAKzBGI0KAozRLgRJ99lSugUDIJVE1xqlJBaBMQYl5fLiCL8wVRCg3V1DCNAYAuFeU+vFOWr3sAiojUYptbwJQgq01kjhHlpr3XkbbV+z4AVKSmprED6waWOQUvib5N6n1hqJAP/zQEmMNhj/mLhA7a4FwgUfswia/uFQUlBrs1xsxi964xeb8A/ba1/jAo1BSL84FsHIWhfLFgHZBzuLRSLdwhFieS0WC04Kt6jdv5X7bOEWl1sDdhmvBP5a+cBs8cdmFu/HMrpZFg/p4trfD9jWX3x3Xtw/HrfSlovste+1vGHCBxW/Ghbv5Zfd8t9msfGAu9/GYhZ7pLXLQLk4ObN8DxdQ8M+QWwv2fqBCLDe118Zy8ZpjsYtz9GvP3U+LsMIHRYuQ9xc9/l65Tdi/q7E+MC/2drs8xsU5+MfP/Y0PYOo152ctgQ/aZvk9Fyjl/buE9cfujscQBAIlBb1WxsZajyRLCepKE0cxw5Uhg0Gf7Z1V5vMagSXNQo6PxwwGXebzgrKsGPQ73Ds8pt9sgpKcjCasDfscH58ShiFpFnN4eMzKSo/5rKKqa3rdFodHJzRbDQSC6XROv9fhaDQhDhVpEnJ6OqHb7TCb5RitaXcaHB9NabVTjK6ZzSu63TanoxFxGBBFIePJjHarwXxeYKwla6SMRhOajYyqrimLknanwXg0I44ipJJMJzM6nRbT6QwhBUkUcjKe0Wpl1GVFWWsajYzJaEyapgDMZjNarSbT6RwZCIIgYDrLaTUaFHlBbTVZkjIeT0nSBGstZV6QNlKm0zlxGCKlYDbPaTQy8rwALEEYMJ3kNLOYotYYbUiTiMlsThSFgKAsSrIsZpYXSOk+ez4viKOIqtJYawlDxXw+J45DjIGqNiRxRJEXBIFy71NWxElIXhRIoZBSkOcFaZJQ1RVaa+IoIl++BspKE0YhZVWjpMRi0doQBgFlVbkHUSnKqiaMFLV2m0UYKIqyREmBRaBrTRiGlGWNFAIpBUVVE4WSunbLVypJWVZEYUCt3bUIQkVV1kglMf6zo0BRV7VfGYKy1oSBpK7dolPKb0TKBWs0iACKqkb5gFwZQyilD9JuEda1QSmJ1sYHF4XVNVJKCu0WWijBarfIjb2fQVdau812sakItwG491lkSxZrwBjrMilrfRboF7ZxWYwLdy5wGG2WGYqw+GxvEXx90DE+KxIWazTWuvttlpmG24AWcdcag4vf0gdagwuhFqx072v854j7AcdtvgIVSIzVWAtVrZfZjVIKJQWNLGZru8dTjz8AQqG+9a++/buPj0/5xGee4cd+6n1cuLDHv/+Z93Pz7hRbW771v/kOVoYd3vEzv8EP/tv38OAD5/lLf/OfMJtXfO4Lz/P3v+1f8cRjD/CP/7cf4zNffJ4gjPhv/9H3s7u1znt+5Q/41ff9EVvrA/7R//xDyCDi8196mX/9Iz/P2XM7/MAP/zxXr99hOs/59u9+B7s7m/zir/wBf/jHH6fb6/DPv+fHSdKUj3/yaX7iZ36Vc+f2+Jff/05u3zvidDTj+3/4XWzvbPCz7/pNPvrxL9Nqt/jn3/1jdFpNPvqxL/ELv/z7bO1s8N3f+w4mk4Ibt474gR/5Wfb39/ipd/4GX/7KZYIo4H//vv/A2uoKf/CHn+A3f/vDbKyv8p3f+06ElDz74hV+7Cd/hQsX9vh3P/krvHLlDpNJyT/7zp9g/8w2v/zrf8iHPvxp1laGfPcP/DTNRsZnP/cc7/ql3+HSuT1+8EfezdHpmOPRhH/3E7/M2TPbvOu97+eLT79Eq5HxfT/0cwyHPf7s41/g9z7w52xsrPJDP/puBIor127zs7/4O5zZ3eRn3/3b3Lx1iKkt/+Ynfond7XV+/4N/xic/82V63Q4/+hPvpddp84Uvv8xv/M6fsLezzjvf9ZvM85KDw2N+7j2/y97uNr/2vg/x0pWbREHIO37uP7G2NuTDH/0cH/34l1hbXeEn/+OvEcUpL7x4k1953x9zZmeDn/qPv8HJ6ZS6qnnvr/0+2xvr/Nb7P8aLl6/RaTT56Z//LYaDHp/74nN8/M+/yPr6Gu/+5d8jUAG37hzwO+//GDs7a7zvd/+Uk9MxdaX5lV//QzY2VvjTj32Wly7foNVs8N5ffT/9XpevPPsKf/6pp9lYHfArv/lHBIHi4M4xH/jgJ9nZXuP3PvBRRidzKm34vd/9CFvr63zyE09z+cpNmo2U3/6tD9PtdHj2hVf4zOefY23Y53d+72OEKuTevRM+9tEvsrk55EMf+gzjUUFZVLzv9/6M7fVVPvGpZ7h+/R6tZsLvfODjtLotXnj+Cl9++mVWVwa8/4MfJ4zc+/zZp77M1sYaH/rIp8lnFWVl+MM/+Syra30+/ulnuH33mCiM+O33f4xur88Xn36RV28c8NBDe7SbDZIkIU1DsiQmSVLiLCFNYrI4Jk5iktR9pUlMmibEUUySpsRxShxHRHFMGIWkaUwcxyRxRprGJHHkfj9x/06SiCSJ3VcUkcSLfwckcUQYRcRxSBzGqCAkTSOEVKRJRBiEBEFIo9lgPC14/x99Aikks7zi9t0Zq6t9bt2bczqZMZ/nfPzTz/HA+W2efPxBTsYzgkWudHZvizBJ2Frvs73RoNsO6HVS3v41j3LuzCanb3iYbrfN1nqfb/q6J3j0oXOEgeKb3v4GNjdWePKJS2xtrLC9MeRNb3iE7c1VLp3fp9/rsLoy4LFHLrG9uYrRmkcevsDqoM8DF/fY211ndWXIAw+eZThsc2Z/nfG4Tb/f48L5PVZX+gRhwMVLe3R7CXtnt9hYX6Hba7O1u0av12R7Zx2DotdrcnZ/l8GgR6UNh6cbdLotzpzbYbjWodfJ2D+zQ6fTYGt7lXarSafTZHdng163wepal7o2dFsZu7ur9IctqtqwubVKu5WytjZkOOjS7zbY3lyh3cpYWx/QnKS0Wgnr60O6nQxTa1ZX+mRpwnDYodPOaGURK8M+jSxhOOgQBSHNLGNra0in06DVbtLrtsnSkH6vS7ORgjJ0WglZHNFrNWlmGUkS0m81SP2DhTAkSUCr1SCOI9I4pJ3GRKEkiiVpHBD7302jgEYakyYBYaRI45BISeIoIEkCgsCSRAFRKMhDSxhKAiUJpCQMBFJAWdcIaQgjRaAChAIVWAIpkVKCAiXdzi6ExFrtfke67EFIv3NKX+5aEFZjhaY0NZoaY+tFbeNKZLHo/9SAcRmOdT+bFzkGQ2lyX/toiroA4Xpeta7AGsoqRxuDNjWzYgZCMJlPKOomdR0zHo2oTc0snxOGAdpoZvOp64+YmqquqG3NZDairEvKsmY6mVDVJePJlLIqyIuc0/EIbTTT6RSjDXVZc3xyQlXljE4nGA1KKKSUvpSRLmORvvywCpT7d11rEC7L0toynpTEiURrQVXXBEHA9VdP2d/rMZ0WJLG7j8aXnrXWyx6ZEIuS1Wc+PmMBQZEXrs1gXbYZBQFGl4RhRFmWKCkJg4Cqqrl67Sbrwz5Jpblx+4Td3VUuv/IqSSgZrLS4fvMeRV6ThAHWaNTf+pvf+N237x6RJCnCal732AWOj0YMei02N/ocnUx4/HUXqSpNFAU8+cQDzGcVj1w6y+pan7SR8fhjFxEo9s5usbO9BjLmkYfPkiQpa+trnD27g4raPHBpj263Q6+3xgPnzxCmLc7sb7OxOqDZHvLgpT2arQE722fY2V2l0Vzh4oVder0uG2u7nN/fotHqc/7cPmtrQwbDLS5d2KHVGrJ/xr2m1V7ngUv7tLt9Njbca9qdFS5cOMPa6pDhcJNL57dpt1fYP3uGza1Vur11Hry0R6c7ZGt7j/3dNbr9VS5e2GNtdY3NjW3OX9il3VvhgUtnyTJFs9Pla9/4GN1uj/39ffb3NukN13nw4hlWVlbZ3jnD+f1NusMNHri4z/b6Ousb25w/t0W3N+D82X22tlYZTQrOn99ib2+f7e0d9s9sMFjZ4MKFXVbXV9ja2uXc2S16w1UunN9nc2ONtY1tLp7bYriyxv7+WfZ21lhZ2eDixT2GgxV2tvfYP7vNYLDOhbNnWNtcY2Njh/PnNukPVjlzZpft7XVWV7e5eG6bweoqOzs77O2tM1zZ4uL5fdbXVtjd3eHcuV3WNza5cGGPjY11NjZ3uLi/w3C4wpm9Lba311lZ3eb8/iaDwQpb2zvs7awxHKxy7uw2qysrrG9scO7MOr3eCmf3dlnbGLKytsr5vW36gxX2trfZ3lhjuLLOuf0tVoarbG9tsbu1Sr+3yv7uFqsrA1bX1tjfW6fXW2Vva52tjTVW1zbZ212jP1hhZ2uTrc0hncEqu1vrJFHM9vY2Z3Y3aHeHnDmzzspqn9WVdc7sbtHp9tndWWN7a42N9U3Ond+iPxiwvbXG5uYq3e6AM3ubhEFMq9nkwvkduv0huzsbrAwHbKytsbO9Qq8/ZHdnk9XVHv1hnzNb63S6fba31tja6NHu9Ti3v0W/36XTbbK9voZUvum8bPlYBK7fFMYRUjWoa4sQejkk0VoThAHSD2TCQCADSSON0NYShQohIYpTZNDwwaNkOq8IQulLVt9BEa70Uirg1s17aF0DcHR4Qrvd5Nr1m3S7HW7eOsAYTbPZQAlBu9XkzO4m/X6TIIDVfhNrKjbX+qyv9Fhf7fDEY2c4e3aD2oD6G3/l7d99eHDCJz/zFX7h1z7I449e4p3v/gPGkzlSCr7z+36KBy+e4Zd+9QP8ym98kLe/9Sm+41/8DGEAL1+/zff/yLt46vUP8O3f+1NcffUuvX6f/+nbf5IL5zb4pV/9AL/xWx9m/+wGf+8ffietRsxnPvcM3/Fd/543PHGR/+Gf/WuuXnuVOi/5B9/2PTz60Dne8TO/zm/+3h+zudnj//mP/gXDTouPfuwL/OCP/CyPP3yef/zPfpi7hyccnZzwT/+XH+KhB/f5oX//i3z4I59mpd/mH37b97G62uUP/ujP+amf/Q0eurjNf/9PfoB5XnD92l3+6f/ywzz00Fm+/V/8JJ/49BdIkpi/+w//d/Z313nvr32Qn33Pb7J/ZoN/8I++jzAQfOELz/K/fteP8/rHzvNP//mP8NJLVygKzf/nf/5hHn5wnx/58V/kP/32h9naHPJ3/tvvoN/p8Mcf/jQ/8G9/jscePcd/94//FYdHJ9y9d8r/+M9+mEce2Odf/dt382ef/BKtZsK3/ZMfYH9/h996/0d41y/+LvtnNvi2/++/QQjLM8+8xPf+4H/k0sV9vuNf/hSvvPIq8yLn2/6nf82F85v8zM//Fu//wz+n12vz//6n38+w3+aP/uRTvOOdv865C1v88+/5KabTObfuHPFvfvLXuHR+j59/7x/y/EvX0Ebz7d/3TrY3B/zyb/wRv/lbH2Z7Y8A//t9+nDgK+fTnvsK/e8d7uXh+i2//vp/m4N4xJ6cTvutf/gznzm7xjv/4Pj752WfIGin/6/f8JGurff7ww5/mN3//I+xsrvK9P/jzIODZF6/yE+/8T5zZ2eAHfvQXuH37HuPxlO/6V+9kf3+Ln/vF3+UTn3marJHyz//FT7I+6PLBD3+WX//tP2Z7fYXv/TfvQgh44eVr/PR7fo9z+1v8xDt/nduHx5xOpvzAj/4CZ/e2efcvvZ9Pff4ZGo2Mf/Gvf56VlS4f+vCneP8HP872xjr/8od/Diklz79wg3e+57c5f2aLH3vHL3P77jHjScG/e8d72d/b4D2/+gG+8KUXaKYxP/Bvf4HVlT5/9Cef4oMf+RS72+v82x/7ZZJQ8ewL1/ilX/8guzsb/Pv/8Oscn445OR3zjnf+J/b3tvjV932Iy1euE4YxP/4z72Nzbcgff+TzfOzjX+br3/oYSRJR+z7J8o+wy16INhZtKtcS9tO8q9fukmYRs1nJ+GRMo5ly69Zdev02V6/dJQgUWRovp2S6rsEYLJZQKZ8J2mVjV7guNY1mgziJCcOARjNDSEGzmaGUoNVoEscRYRhw8/Yh737v72OtYTSd8anPPsfKoMtvv/8jVJWh1jXPvXyT1z9ylocv7nJ0PEH97W/95u++c3DE6x+7xF/4hjfyzV/3JI8+eoG3fe3reN3DZ3jdw5f4xrc/zqMPn+cbv+GNvP3Nr+PchS2+8eue5HUPneOpJx7gm9/2JOfP7/CNb3uCp15/iUcePc83vvUxzu1v86Y3PsTb3vQQ58/v8he/4U08/MBZXv/YRb75G57gzN4G3/C2J3jDEw9y/uw23/z1T7K/v86TT1ziLW96HXtbq3zj1z3JxQvbPPLIHl/3ltezvjXgbV/zel73yHnOntngG77uSfa2V3jyiQu86cmH2drs8/Vvf4JzZzd5+IE93vY1j7GxMeTr3/o6Hry0w/7Zbf7CNzzJxkaPr3njo7zxDQ+yvt7jL3/zm9jZGvK6R8/x9rc+ztp6n69/y+NcurDNxQs7fPPXPcHaSp+vfeMjvPEND7K3t8k3f/0b2NtZ56nHL/KWNz3E+uqQb377E5w/u8nFCzvueFe6fP1bXsfDl3bZ2V3jm976OFvrfd7w+ks8+foL7O2u8xe+/kl2N1d4+IF93vLUQwwHHd72tY9y/uwGeztrfP2bH2Nt0OGNT1zi4Qf3WF3r8Y1vfYK1lS4PPbjPmx6/xHDY4u1vfoy9nTXOnd3ka596iH6vyZve8CAXzm2yvTXkzU9cYjBs88gDu1w8v8Vg0OJrn3qIlUGLBy/t8KYnHqDTbfKWpx5kZ2eFM7vrvOWNj9LpNHnj45e4cHaT1ZUub33Tw3R7bR59cJ9HH9yj32vzlqceYnXYZX9vg9c/eo5Wu8VTj19ke3PA2mqXNz5xiW6nyesfOecyqX6LNz/5AP1eiwcu7vDwpV067YyveepBVgYddvfWeP1j+zQaCY+/7iJbWytsrA144tHzNJopDz94hv2dNXqdJk89cZ5WK+HC2R0eurRD1kh48vEHWF/tsrO1wiMPnSFNI17/yHk213usrHR54nXnaaQJD106w97uGq1myusfvUArizm/v8XFczskScTjj11gMOxw7swGD13YJYpCHnv4HCuDNv1um8ceOksQBjx4aZftzSHNRsrrHztPM0s5t7/F2TMbtJoZjz50ll63yZkz65w/u4V0uAe+6o914x0hLGWRM5sumv1uEpU2UqIoII5d7ySIApIkJQik78O4YYLWNaYusEYjlSAMpf8s8ZoZECxmQlIFCOk+W7nuOGEQukmiCpaTPOsniufP7tDvtcjSlL3tVeIoZnd7jeFKl1Yr4fUPnOHs/hZ5WRJo7Uapf/yxz/KnH/08w36ff/kjP8vO7jp/+1v/Mt//I7/AP/snf5s/+NAn+MozL7G2MuQH/80v8Tf+6lsJQsXP/Nz7GP5oj3/773+ZCxd2+Mvf/Ga++wd/nu//nm/jIx/5IjfvHtNqNviBH/1l/uHf/avksynv/qX3s7W1xr/7yffy5Osf4Gvf/Bg/9KPvYX9vi/f8yu8zyzXNVpcf+fH3Apabd495/wc+zt7ODj/zrt/lbW9+PQ9eOMOP//RvsrOzxa/95h+TJBlxHPPOX/og7W6XZ5+9zCc/9TS7Wxv8x1/4fb7lL76Zbi/jHe/8dc6f2eDdv/T7rAy7YDU/9573s7m2wue/9DzPPf8qG+tr/Oy7fofqb1Xouubdv/oHPHhxn/f++h/y8KVzPPmGS/zHd/0WF/e3+a33/xmj8Yj+oMO73/sHtJsNXr11hw9++LM8+MAZfuk3PsQ3vO0JdrbXee+vf4iHL+zwOx/4OFkjIU4ifvFXP8TG2ipfeOYlLl++yZm9Td73+x/FKIvE8Dsf+BQPXjrHB/74E1w4t8tj+SV++/c/zoPnz/DRj3+ZvKpYW+nz+3/0OTbWVrl2/S4f/9yzXLywx4c/+gWKSrO+NuDPPvEsD104w9PPXKXZamCAT3zqBfZ3NvjSM9e4ffeAve11Pvyxz9NuZ0zHUz788S/xyMPn+fNPfZnJZMruzjof+fMv8ehDZ/ncl14ijgJ6vTZ//ulnOLu3xZVrt7ny6m3O72/y+adfptNKqXTN5790mUcunePzX36Z8XhGXld85vMv8OiD+zzz/DUEgpVel89+8QXOn9nk8tXbvHz1BufPbvKlL79Et9VCKMXTz1zmkUt7XH7lLnVlqUrNl567zCMPnuXlKzcRNmBlpcOXn3mZS3s7vHLtNleu3+bS+TM8+8JVVvpdqlrzzHNXed3DZ3n+pWtUdY3F8txL13jdo5e4cvU2KlCsrfR56fJ1Llzc5dWb97h7+4AL+9u8eP0Wa5tDynnJK9dv89gjZ3nl6g3CSIDRXL16i9PHpty4dUAzy+h3Wly5dpsL+7vcvXdMWVVuqoNc4lju402EH127rMXaRQ/KlTZJrJa/q5IQay2NzE0OG2nkf9981Qjb4aLMV32O9dgnYQRSSq69eou0kSKF4PRkzObGgKuv3mZzY8ide4cEYcDG6oBa1xyfjFgZdGmoBkKFGAvHpyOyZkLTNHj58nXuHV1ABQKLRvoRNxtrAx5/7ALDfpvXPXrJ9Vj6XR579AKrw757uB+5RKeZcu7MBsNei2G/zf7+No0sZm97jY3VLivDHptrXUJR022FDNoJ7Szl/N46/V6DTjtjfb1PMw3ZXO0x7HdIw4jzF/Z5+JGH6TRS3vjko2yu9RkMW2SNjFYzZWXQJg0DBv02nXaDLItYW+kQhYLdnU3+0l/6vyCs5W1vfooHL54llIJep0MUB3RbmeucBxHtVkYchnQaKWkcMlxZ4a/8pb+IFPDU42/gwQfOIawbDUeRJAolaRwhpUQqgQoEkZJEgUQFiiAABWSNlChWIA1xEiFthVLK7xICCehi7jAj6CV2BatZWxtSznPSNKPVaVHmc6gNRkNZzEEYZvOcsqox1MwmE7SpMBbe8MSTWK3pdbpcvHSRyXTMbDLCAuPJhLIoKaqC+TxHKklV1dRlhRSKnd09impOf7BCpzNgXuQcHp1QFDXzvOT4+Ji6qrl794TpbEZZVtw7OKSuNaejEUcnxzRbbcanE6qyQgURJydjjLYcHJ0wL0qm05y7d+6hteHW3XscjSfMpwU3Xr2DsZbbd+5ycjqirDVXrt1klpccnx5z69Yd6tLw6s27jEZjJqdjXr15QFlZbt89ZGtrm8l0CsRsbW1z7dU73Lp3wDwveeXKDSazCYcHJ7x6/Q5FWXH5yqvcPTqlqgxJmFEWFSpIEUHEyemEly5fI88LXr15mxs37zCdz/niV15kPJlx984hl6/fIi9rLr90jaPjU8Io5eVXXkWqgOPTKbdu3eF4NOaZ515hOp9z7eZtbt6+w2SW8/xL1xjNp9y4c8CzL1wBIUiSiDgKl19JFBPGIVEcEgYhWRYz6LfI4ogoVERRQBQGhKH6qi8lBVEUEIbuK45C4jgk8u/rfuZfHyn3/SAgCQPCQBLHITfvHDCdzSnyglu37lFpw0svX6eqDDdu3uP4+JQgUOR5zXPPX+XOnSOOT6ZcvXabyXjOiy9f4+7BCaeTKS++fJPT0QwpoSprxK/+3PfYrzx7mSiOGY1nfOtf/wb+9GOfY9Dr8ujD5/nAH3+Kb3r7G3juxSu8evOA/+H/9df5yvN3eO7KoUP1GrdIVKCQSjlwnXXIWzzQSyBRocQag4pihIGqnEOg3NxdG1SolvWoUuI1wCmWwKowcs0sXZYOvCUN0liEDJGBQNc1oQqwGLR2CGMpLNpYoigCK8jLHCU8KE0FBFJ6AJJBCIXBoIRb3FZapFRMTme89U3naWQBf/RnLxFIRV25xpmDCwiCMMDUDjlrBVjtgIJ1rZFCIq2lxqEbtVngV0J0VRNHkZuMGEsYCPKiduA/QFcVURSiDZRVSagkujKoUFBpSxLFKCyFb8LnRUGta5I4ZjafE4YhYRgxGo/JopjaONTyAuEcBBKrLXVVIqRlXlREQYAVhtF4xqWz65zbW+PPP/U8s8pQ1zXtRsK8qBAIsjQhn+VEaUReVeiyJklih+UJHcCxrDRx6DA9YRghpCCfFzSbCXleenxFwHgyo9FIXFAsK1ppyslsSpZECATzvKbVTJlNZzSaGVVVYmpJmkYcnZwgpSAKAk4nUxqNlKqsMRYaWcLJaEKahARCYoxABVDX7jmtjWEymdJsZBRFSVVrtjb77Gz2eenlOxydzDDG0G41GI0nJGlCEAScnJ7QaTeZTgssFUqFTCc5nU7GdJoDiiQOmExnNFsO/2QNtDsNj6j1oMQFtkX4Z11bqrp2G5TvoQj5GgSzB8BZD8xcIpk9qnYBZmQJGjRLRDgexYs1bq0q5Z59KcnzgpVei+FqB62Nw9IIB5C11jKb5Xz5uVfYWO0jleLoaMr2Vo8r127TajXotRrcuXfCX/i6R/i//oU3cnA8JqjrGongj/7kk/zJx77I/s4W3/tDP8uFc7v8vb/z1/mu738nQSD4T7/zYT71mWf4O9/6jdw6mPJr7/84GO12ZI+OVMrTDKxASEkQOkz+AjRZFDl7u7ucnp5ydHxMFCYePq3diNP/XhAEhFEIxvpGlaU0Nbt7e4xOx5wcn3qU8H1kqRAWKSVRFKGNoaoqpAXlwVE7O7uMpxPu3rtHEAQeFenAQ672lEgPhQY3Vg2iECsEzSTiidft0mzEfOyTL3D95gFSKbTRSCUJZIjRFcbUBGGIFIJABaggIAgCrDU0sgZRnPDCy68QBiHGVKhAIDz4KgglURgSqBDhEdCBcsEqjCIaWcaLz7+I8gHMWEdPkFKSJglSKQIVIZVACuEeDGPIWg2sgZdffBElFVEYIpQbKSdxgpAO5BYEirLSJFHkAiCWstAMekMeezjk5RsjPvm5F8kaKUoqwjAkjmMsEKkAK++3K6UfRc9nc8qypN/rcuPGLRpZRhSGGAFJElNWI6QQDjVtLUEQoOtTJtMJRVmAhcFgwGRy4LJFFSDsjDBQ5MUYpQKPbHV9h3k+J5/lDigoR/QHA8qyQFL6gqFCa/eQSaXAWsqqoqwrqrKkKo8JgwAhQ6Kk5KnHB/z5529y7XblJjAHI1QoqQ6mOBS/4eUbhwgh/OjaZ63X3bF1+33qoxIhAm6f5kipqCtNcfPIBQntNhtt9FehrMMgpNFsUteFv5eCsiypqsqjhN0zo/2mBA5Zba0mDGPSNEVrTV1ptNUYU/sWjPQoedeQvc/ksSgVutE/MFxto7VeAvO0NoRhwPHJiN/8nQ/zxicfIQwDXnnlLt/wda/jd9//UR564Cxnzmzzex/8OOf2+gSBJM9zArcALN/yl97ON3/T1/CWr32Uf/29/5h+t8lDl/b4sR/4x7ztax7jgQv73Lx5l8GghRV3KIuCdqtJkqQ+Otolr0YsuDA4PEQUxei6wurKIzFL0jQlS9LXAMq/GjIeBKFDrc6mWK1BQ6QkZZmTZDFpnCx5EK/l/kRxhNYVwnfLg0CBhSiNqcanNJpN4iRxiEZf5wZBgBSC+WyCkG53D4KQJImRUtLttonC0Jc8lkYjI80yqqrGAlJIqiqnLAsC6TAOQRiSpql770DR7XaZTqZ0O22iKMJoVyZVRbEMsGEYk6UpSimiOEaFjtfVyBrMZ1M63Q5BGJLnM09dcIEhyxpEUYQKFXESe9SlQgpJ1ki5c/s2vX7XQ8MFYRiiAkWapA7jECeowMH9pXQLOYxCJqMpSRIiUfR6HTrdNnEUocKILEtJ4tgFpyh0RaCQ/poHhGHIdDLl3sFd4ixhZXVIFMckaYJSahmIjbEoFYB/nRBwdHjEfJ4zn89p9zq0um0Cpfx4NvB4F/d8SSEI45jRaMRkPKaua4w2zPM56xvrGGtQ0lFOLAZrXFYdhRG1rhmPx5Rlia5dr6PWNZPxlF6vTVWW7O7uItICayrP+fJZtlQuEOYFda3RpnaoWuNQrZPJmLX1dYIgpCwrt+kEinmeM5/NMca4ZqwxnhJwP3DMplP2z+xRarMMMKPTEVVdLZ9ZXWv/+y4bVh4Jba1hf3+futLMZjPmRY41teMJWeE5XcZ3YTw9RCrm0wlSCHq9rg8uHgcsXODTWtNuZnzdW17H9tYmUgk6rYxhv8VTTzzA2uqQ1WGHr3nyAuurPbR2SPWg1o5E+InPPMunPvs05/e3eNd7P8DZ3XWq2vDO97yfNE350Ic/zReffp6/+lfetNzBwtAFAWPskqezIAEZo5eplQok1koPdVeEYQTCzfQXvI/FRbbWRWYhBGEYUPiZv86Nf3ADjHWBwyK/Ci5trYOxgyEIFIFS1HVN6KH6QaAwJvAZjEFo4z+LJb5AvGZHFcJlYvfjnsuSVBCglPK7SO0aWibABsZncoFbrIvXCOEh8o5MKoVAKEUoA6yusWYR1BRVXbnP9ZB6a9zfyn9uEIRIpbAGAuUWnJKS+WxG1mggrSMnRqE/FyHddQsCas/VCqRa8nYm0ylt5X5uuQ+IU1KiQncei2CtlEIpySJZEUIwHo1otdrESYrA4TIEEIbhkvMjfbCTuOuAsYyOT2h3OwRBCNbD0KUL4LVf7Eo5Et5iJ5VScnx4SKfTJQhDFv3Dxb3AumAvlCPWCnAcMwPHJyd0u11HefD3VgqJqY37XOUWkQDPmXLBWGsXsEYnp3Q6HYQvL+MoYjxxTViEXX6uv+kopdB1xWw6p9lsUOuaIEgIVOWDAst7LIRyz5ixWGGQSoKU2LoGqRw3bcFn8jwj6W+CEOo1/Cu3+LTWCKlcM9mxL5FywRuSBB7gyJIY6Z7NJcfJWviqAbq7XrWxnJzmDIc5UglmeYnWMJrMiZMJUaS4c++IsvKUEATBInNY6be4sL9Dp9ngyccusbY5pNNu8NDFswxX2lx64AxhHBMGIRJJFMUYo9G6Jk0b/sZIv0hdNuZam1CUc6I4IgxDkiT1pYwijhN/kaUbz/mb67rrhrquaLUaGG2Ik5RGlhEEAUq58ZzbndRrLoRxtatUNJtNhx/wwSJLU6IoXL52cf2s8UjNsiRrNFn03xfBUyjl0mYhkFYglUIFAc1m0/NWLHkxd6O9uOHJf5I4CImT2N3cQJFEMbrStJot4iSmLEtm8wlJEjmGduCykTBQJFGKkJIojAmUpJllGGNotVpUVU0YhMRB6AOnRClFp9MhSRKElIRB5DINpUijBKUCrBCE0kFEhec0CSHoDfoEQqKUIE4bBCpACkkUx4wnM7d4/a4Zx+59pVSESoEU9AcDlJBEsb9evqdljEaFAc1mg0C55mIQup+HKmBlZQUZKJSM/CJz+Xo+z2m2mo7EGijiKHY7qoAoCFldWSWIQx88XXmutSYJQ8JOh7IsfEatHWlXCiIVEK+tEYTREtGq/ebXbDVdOVHXblM07hlaPBtKKhqNkEbmr6PfALXWJFHieVsWXfuSRWuEhLIqSNOUbjf1bPjaEWJVQKPRWJIEjakdP8kzk0FQVjlxHBNFIXVdU9eaRiNd8rbccdY+gPhNTjl1g6ooicOYeVGSpvePzxjjSLXGOKazlsuqA4srGbH8//sjpWCelzzzwhUajQQVCp594To7m6vcvH0PKwRRHPPy1bucnM4QQlCVJYGUrpm4tblCp9tguNJjd2vAcNim32uxs91hbdjl7O4qcRSRxJFP6d0KHZ2eIqSg3Wq71Fy6XV8KRRC4aJ9mCcU8p6oqoigiCBST2Yx8PqXf66PCdPmQSSVcmSEktXFpXhhIyrLw5DHLdDKmLAr6/aFrLCsX2YVUZEIwnU4wde0CjM+sXJYlOTo9QghJq9XyjGzX61ikrlIsGLvSZw4uu2GhPiEE8/mMutUmyxqAJU4iRiennrVrUcIvQGsIw4gwjIjjmPF4wun4hO32NmmaogJBWeQooUAYwiBCBRFSKZIkIfEPWbPZYDQeURYlg/6Ak2MD0mVTgXJBMwwDlBKeq+JeG0YRSRRz49YN4jCi0cgIQ7egnRyCIAgiRzFIU8dJiRKCMEQF0kPNa8dmV5I4jsnSbFkCqSAgTVOSOCGKIqI48j0etyMfH5+SBCFG1wgMUZwQBuHyekRRTBCGPoBLrHAZ5cHBMUWR02gkDgiWZQS+5xPFEUEYEsjAywK4RXJ6espsNmM2E2SNDCEtcZzS9yVnGISuhPMsYmMt83nOdDplPs+p64q6rtFaLzclhMuUVwZDolgtJRiMrqnrivF0TpG70ris3CYl4oAze3t8/nOfp9NssbqxQZEXPjC50m2ezyhLR8at6wqtXc9wY2MTqRSHn7lLu9mk0WhQVCVVbZhNZxRlTl3546wVxgc6ooizZ/d55aXLHBQHdLsdmlZTV5X7jKqirEoqXWNqd4210o4p7smZVRhQ1fp+NuQrJFdWCepaszJs8z/+d3+TKIoQwBseu0QjS/i7/9VfRkhBHIU89dh5Hr64RVFW9HpdgrqqCKTgg3/yGf70zz7H3t423/n9P83Fi3v8l3/9m/iBH/kF2u0m7/vdP+XTn32W/9tfewtSudLEGoOuq2Uz1sGeha8rXUZRFAXD4YC7t29zeHBAp912PYYwAKWotUZpTVXppe5HUZTLPsFLL75EHIWUVUmgFFhBksRobSirEmp3HNZq8rxk0O9z6+YNpqOxK0Wk65zN85xGs0kURVRVxXw+w1pLXde+FDG8/OILbpcVEikkSRxR15qz5/aXpZmUrnma5zla1+SFY0jfvXeX6XiMkALld1cVKpRfUNdfvU6j0SAMFMfHRygVUhQzbr563TUrBURxsmTyRpFbeCqQpFnG+tom4/GYNEm4ceNVqqpABgqBcj2NICAIpA/gEVHkcBGbmxsEKmAynSCkZZCmzOdz7t69TVGUBIEL+CpwDeAwDFyWJhVr69uLWgiE4MqVq6RJvPw81zdyAS7LUtdXyxogBYPhkJPjY6zR1FXJs889SyNruh5PEKCUXP7tFjTEScre3h63bt1w49Q44vatm1RFRRzFbhIJ9Lo9qsqVGnlRcPbcBY6OT5iMJ1hrkEpwfHhEu9XiuWe+QhTFXlrElQG1NgyGAwbDFW7cuOkmdl4moypLjHZTlSAIuHb1BV698yxJGnndIomuay49+AD37tx2fQ/hmNHGGqIoQNdO2uPw8JCr169T5HPKIufM2XMIFXB4cA+pAqxxmToWtK6RQjKfTUmzlKOjI77w+S/Q6nbY293j5o0bSIkH4nk9Ho97SaKYqiypTU0YBnzpS1/k/MULHB0eUuYFiyTCaSgtpEzEUkupKApXoqvXVAN2gcURy/8qpVgZdB1HCmg2EuqqJonDpQZNp5GQJi74x1FEEEURxhj+y7/5DfzXf+sv8OY3PszP/cR30uk12FwfsLE24I1PPMCTb3iAo8MxvW6Lsr6HtBBHIVk2II0zh02WYglrDpXAWOkp/QFJmtBsNQjDEGsMcRCRZinaCt9cFNRVhbAQ+wZnICTtdoswUFSV24HneUGr2SIMI2a5kwTQrlNFkriUsJU1CHy/xOB6ODs7W9w7OKLdbhFFCWWZuyaXcA0/azStVtOT0Fy5trm5SVU7KQZr7osONZsOxWisIY5jQt/0xOpl3yNNUoarK5yejtja2mY+n5IXBSuDIXnh5CWiIKSRpsgwJJAhSknWNlbJ5yWNRka70eBkdEqcpYRJRLfXRUhBo5FR1y6DsFi67S6dbo/xZMTO9jYnp6cIIf0ky2WRkb/uKlDEsWPf7u7uMh7P6A+6Tk5iOiVJGihf5hwfH2PXuhhcI7zT6RCGEikVg0GfRqPBZDxla2uH09Mj0jSl0WhhBSRJQhQFXLv6Kp1Om167S5o1WN/Y4OT0mLXVNYqyoizmrult3H2PI5dN5fmc09NTkiRhZ2vbLWBh6PZ65POCqqqc9EJVkSQRaRpTlTlVXXN4cIDRhixJWVldYWW4yunpKaCRMqDWhkarSRiEpGmCtW6DcxvPFO3BbVprVlfXEImlLnIQDmqhjZOxSOLI9YyMdrJNVjCfznjpxRep65oojulFMWWZUVU5WdZAa0MaxWigshXKizwJCdevXaWqawSCOIoZDAckWYpSkjS5D6TTnsS46CXNplNeeOFFirJECmhkGaEKiKPYZykWaV4LwmMJ8ptMJpRlSZwkXyXkhYW6EtTWEAVuw610zWyeL/tYrqntpkwqUAShZF7lzPMSbTS10QRBEGKAhy7t8sRjD9BIUx557BJ6XlDpmseefATykkfMPkhFMZ8CljAMyBoN0jTFVF7VSroGZ1HkaGtJkgzrG34OiWyREsJAUdcVeZ7TaLac9kegKPOcWld0Gz2wwqffkW9+SSS45iWu7kySCCEkRe76NWEYEoUhWZq40sPvjMFrduf5PCeNE9IkZTQ6pSxz2o0m0ob3BYY8hDtKYmzpkJdSOuRlqAIaqRu3lmWJLmtk6nY1Y2okisq4oNRptcBYmllKns8oigLr1fiKPKfZaDhNtbrCKAtW0UwblPPC9S3SmPxegQwCdFlR5nMkTnCqMAahtQsaSpJlCUdHB7TbbY5Pjiny0jW6Q0lZFUynY8KwSxwGSGupipJWs8Xx8QlxHCOBk/wYKQKnNqhrZtMCRNePQaXDZNSW2tZEQUiaJBwfn9DtdLh37zYISRy5HptwsZuycBOaqqoIq5Jup8XBvbs0mw30aMTx8cxNNYzgvtaSwRqNqWsqq8myjKqsKaqcXrfH9fF194wZTVlUWNdnxRoXtKf1xE3VlCKJU7qdLgd377qOsNQUZenS/NQgXWcYESqMrp1Q2qJBbCxJmiAnJaPxyI30hVfrWzbxHFo2DBXaWKpptRxSOOa3oa4qqqL2/B/pG6xOmCwInHibtTCeTUiSxImmoanrCmFTv28bpAxwyHuJENar5ynmczeJjKOIui6pvY6NtQYpWE4jXV+zvo/m1W5MXxtDjPVCaJ7tjqQyFm0ESjgq5o3bJ9y6eULaiCjKivksp9FokKQOuySERSF48eUDOoMuw/4q4jfe/S/tF770HG/72sfZ2d3g1//TnyAk/MO//18A8NM/+1sIKfkHf+9baKYRoPnQx69zNGsSx65RGEiBlAFxmlDkhQfGGdIsQ9euEZokbncajUaMRiPiOCbwDbxAScLIUcPTNHNTDOGmIbWuSeOEUDlRpYPDQ1qtFtbT+KVyTd/aaLI0w1pDFEYUZYHR2i0epZjPZpyOxjQbTaq6WtLlg9A1n+9PnAJ3DlK4qC4EhwcHPLKraTVC/uDj92h3hygpqCqHe8ga2bLZrOuaMIyWWINms+WactZwcnzidRJdWSCVK82SOPZNOE3iMQyV1jS84FVRlBwcHoGAOIoJJBRVRRgES9yPg5In1HUFBuI0cyVcPufg4MAvNjfCLqtyqSVSlq4vFipFkReEUUwQBNRlwY3b91hrz3jsYoc//tRdtOjQyGKHsbHGlUpR5BQP/fTI1o6pi4DpeMp0NsFYQyBdXykIg+WOt6jzF4hnrTV5Pmc+nTrxKg8/iKOINElB4Vj9YYS1rjx3EySYTGfMZtPl1HDxd5qmywzVmBq5wHsYTVXVlGXhena6dguuLLFCsr0S8sSDQz7//Cm5bREoPOjMYWmMteRF7koTXaO1a8bqWtPudMnnc1JfNuq6Qkm/qRYldV1TVa73IoTrzbj7EJKmGZPJhG6v4wSyDFS6Ii9ytHYlPbjBxGISWJUV7Vabsi6pyopup4O2lqoq0HVF7Xsr1qvmGS+GpbVmNp1RVSXtThchFOs92NloUswdWLW2BiVdb/TopOLFy/eY5zlCCs6cPcejjz7KYDDgC5//Ah/+kw+xtrrCxkqPv/ktj3Hx/CWCRUqkpKTIS37kHe8ljgL+/t/9a9TG8O9+6r1YI/i//62/SLsZY42kKAo+9tHPU5Yzaq/qpaQizTKEVzlzYB/XvMqylKIoWFlZpd1uc/mVy5yORn7EZlBKkGYNrPHlVBRRViUycNiHuqoYDgasra7xlWeeYTyZLHVnoygkzRKqonTNxjhiluckcex7RJo4Tej2exwcHHB8eOylJg1p6pqHZT6n025R19p37DPm89w1FpOUqsh5ZPcxlAp45cor3Lj9aZRwI9F2q4WxlrIo6fW6S7W6ZrvN8fExWdYgUA501Gi1ufHqDRfcpKDZSMmLgjAMaWQNTo6P6fV6VFozmUwZ9ntMJxOMsXR6fa5eveaCcaAIopCqqmg0Gy5DqDWddovpeEIQBERxwtHxMY2Ge8hfuXyZJE5oNpsu+ApotVrMJlNf5gWcno7IGk2s0cwmE8K4weobd1FKMhqf8rkvfYlmMyVNM8qydEE4TqjKGqUEgXQZYhg5PZX5rECFil63w81Xb5BmKVIp6rIiTmK0l+FcbC4OXhAwn84pa02Wpi4zOzwkjmNqXQNuNK9rTRSqJY5Eha63NplMkUrQyFKazQb37h0QhrFHzboA44ERGOtG41IIprMJRVGglJt0rvcGIAXjyZivvPiCI/9ZsLpCyGChVuPG71JQ14b5fIY2NermLdI0pdVqcXBwd9m3cyNup5GjFv0O4bK8RR9ESkWWNSnLnMODQwIZoK0DPi5gFFLJJVp3Ps8xVcXd27cRgaLf6XE3v8u9owPCQLlg7j9rASoV1o3vi6Jwsq1RwNHRCXGcQC8DIzg4nfPqrVO0NZzdXaHXCum2E0Rg6bQ7DFdX+Lqv/zrOX7hErQ1BGNMb9plNZozuXaXfbbomuRDWY0Ykw36bd/+HbycIJJ2WA9C9+x3fgRCCtUHLYSnqilpXXL9xkzBwjTAHc9fIo5PlRYji2JUlQUBR1iAMeVUQ5AXXrr9KrSsCFVGWFUbXKN/UDaQiTRwUWwUBcRSB1czynKKqePXmLfdwKyfLKAQkcUzgG5PNZpO61m6kGsdICWY+J81Tbt64xfHxCUpKKo9OjJMYaWEynfrd0DDLC9qNJlVVY5jTamSuFJGS27fvcv3V2wSBQteuB9NsZJRFzuHhAd1+n+lkgtaWLGtycnzC+uqQTrfHjZu3uHz1yhLz0e92EAJmkwm7u3tUVc3tO/dcb2Q0odaWwWCVm7ducuPmTV65ehUpIAoDhsMBB4cHrK2u0esNODk+pd/pEYYxeVmysT3g5PSEPC85Ph5x/dUbBCpga2vTSWQaTbvZZjrLSdMGYZRg7ZjNjU0ODu4xGU+YTmfk85xABMxnOVevX2N1OKDT6VKUJasrw6Xu73CwwuHBEf3hgEajwa1bt5iXE6qJA3CNJmOEUm5MmyZEcUJZ1bRaLeq6JokTut0OB0dH3Ll74IK9rh1wUDrMU5o2PTIasizDaL3MlEeTMae37jIrcpIkoihq2m13f9OksRzDJnG6FEOXgWI6mTI6PSUvKhCuSV7XTmPZGkOSpHQ6faIw8Nis8DXC425Dms1mFNUEC8SRC+gOVuAGGgsowaK/V+sKYyxVVTGbzdDakgiX4S1Ennq9AVHkpm5CLjSW8dlOSV7kFHlBlipkJpY9FCEEq6srZM3M41vUEmBZluXyq64q4jRbgjqLvMDiKDWzeY2MV2j1Yk5PTwnSFYQs0OUcayW1rpASXr58mdlszvkL53nkkYf42rd8DZ/77Of5wG+/5HpTuiYo64rJNOfzX77GnaOcTtshTf/kY88QxxGtzipa1/zpx58HU/M1T10kDiPSJKHZTEmSxJW2Si6RiIvMQ1ioKtdAGo1OmE6ntFsdmk3XTI2T9KtGYm4C48ajQRCgpOLo8C5SSFQY0u12ybKUdqfjgFweMyN9bVxXNa1Wk5OTE6rKQat7vQ5hFGK0odVskSZuHGutk2uvdU3sR7e3bt0gS1ImkzGmrtnY3ORkdEISOVlBbSxJkrKzs0OSxBjtHpIkjsjnM8ajUybjMUmSUFUlw8YK89kMFbpAmSQxe7u77tgt1FXFaHSKCgJu3rpJp91ha2eb0ekpw8HAp9c1O9s7nEzHFHVNGseMT08AGA4GGK+Ru79/hrIo2dhYdwpqZcnKypAoTjg+OmZlZdXRLnzzMggCsixje2uLXrdLVVfYocsoWu027VYLTYDAoZWzLGN7e5tGEmMRrK+t0+22OTk+4fz5CxzcvUuz2SROYiaTCRsbG/SHK9y7c5c4DlgZOiTvYLACRtPrDyiriqqq3D2I3HRqa2NrCZ6sq4qiKFhf33ByBVlKlmbcvXvXafcKSLMW3V6Pqq4ZDAf0bY8wDJiOZ7RaLYJA+Sb0iLquCIKQosjpdjrIMOTq/AqtdptGq7XU1T05GS2fySRO2N3dYe7LrzRrMJ9OWd/Y4OjoiNPTESoI6LTbyG7X9aqA8WRMGCr6/b7rpQhBq9UG3zwvigIhJVmakSRulL4QZq9rl/Vba2l3OsRRxMnJiZ9euqlQFMbEUew3dOk1lnOq2l3TM2f2OTw6csLk/nUOzOlaCrLh8WceZGe0oapKpJTM84pGq0VeVtRVwXxekwrL6fEEKR3B8sorV5hMJghguLLC2vo6J8dHfO5zn2I2Kzk9mdHqGIK6htFoSilLrhwfk+c33chJe0lDIVxUr2rWBw3e8PrzTiNCeRSihDCKl/wXoSRSyaUdA0C73eL09JiqLF0wUIowiEjSxHNqHLpUeOhn6dPQSCmqyhEbRycnzAYDEJBkKXHk+haL0ZrDqBTESUwQSObzwgG38nzZC3GYnIwwjp1WhnR9F2HB0WfcTRLWkQx7edchGOtqqcQupesXZR78VlcBSRRzfHSINoZ8Pmc+mzMYDKjLgqKYk2YZt+/cpiwLOp3OMogWQjCbzZwgUBhyeHTI/v4Z7kxGKCUZ9Lu8/PINut0ujaxBliY0kpTT40PKvPLgKsF0MqbRzDgan7CzvYnRNQcHB+5805TUw/O1r8nLqsIaQxg4uLsUXaQQFMWc4xNN5LE1jXYHY47R1iCVI6NWpbsWSRIRKMVsOqXZbHD5pRP6/R6j0QlFUTEcrhDHhtPjGGMc5iOKIlZWB1x+6WU2Njeo6pKj40PSxDXloyhme2eXo5MjrDFMJ5bpeMTg3Dlmszl1XdJut3j55csYXZEkKaPxmMFgSMsDKx0IzslMNhquD9Vutzk9dQ39six807mm3WjQSDNkoO4HO3+vHUHQCY+LEk8F0MymU2xdEyWhmwg1MtJmhqlqx1SvqyV1xViDwolqTydThsPhkkSYNjISBLauKctyWeotkMJBGKBN7fBevT737h14Wojb1B3IdQEQNMtAAZbJ9JTdeM/1E4scpUIajQxjEh/Aan8cHkfDwp3Bo3sFbiJYtjg6PMbUNRJJsxWj7k2I0wbNdodOu0WUpBRlidaWXq/H/tlz3Ln+IlkWO/S8EI4FXVUlp+O5gyIb5y0zGY+9Crnmzq3bvPVNjxNF4dIepK5rTu9O6Pd6fsFpL2EDtYdpa629BsZ9WwnpwXDz+Yx2t4sInZ3HwprCaIPEUBlDXdUIb5fiOBcBk9GEPMhptpsOA+Oh5LXWlMsGmqtzJ+OxQ44OV0A4yHij2STzzVRtnI2Irtz4T0qJEpKyLCnKknoBZvKq6mA4OjohDBxdotYuTa6qiqIsnN6qgDyfU1alD1AO42C15eTolHan7Zptxjg2t3QYhCiMKIoShfCYiBxjSoypyfOcyWRCpALms5ljc3s2bMuDxPKypDKaeT5HVzVZI3Nq/j6gGGPJi8KN1LUD2s3GY/J+H2stRZ47xwBbIY0lLAtkQ3qLEc18OkOksXc7KJCdNp1eF2utm34ox28SuFKzqiriOMQaB5SsyngJ7lqgYa1vbmMtwkJd1dRaIzyZM06iJX3D0TxCur02kXIUFeFV87VZkPi0I6JqjRASFbjXV0XhhDOUY70b64mA1mK8o8NioTrErlharrjzN4RR5NwGpMJoTyko3ch48SwJJTm7d4ann/6yI68Gjg6TpQsEsSvPMNYB9oxe+l41m02CIGQ8ntxnvL8Gq7XIcBZBdMFDEkIyGAw4OTlmns9pekQ6Vrh74ZnWi+C2CIALFL1c0Fe8DxgCVBQyGPS4cf06xycnrHYHRLGjZwxXhjSbbaIgpCprrl25Sj6fs7oyZHR6QqAgiRyeKlhYyqRJQthw6lhZmqECxcnxiWswdpq8cvkyrWZrqewnPEW8qirKsiJNvZiNMUv7hUX5InBcmvucCveZ0+mUNHOfpY1e1qjWGKQXmY7iyEk1eLKhAMp8ztxa0izBSuUeHE81kP6BWHAhhKchGE/5ns2mSCVJ4th7znA/ei/G1AvjLH8zl35BvnavyooizwlUsKTaL8bYLkMWHsSnqWonGL0QEJpMxmQNV6Y5GHhJkmRIKZ3VSlVRlgVFWVDrCiFrEG4KNZvOGHR7CCEJg9CPMx0DtqprtDEumDgGJoWvt+ezOfM8d1mblp7U5wJAUbjfWfRS6qpCqgAC+VVEPO3JmQi/cdQ1RV4wHk886M3D0D0AsqpcAzHLUuZTpyVjjHGo16KgKArX4zLWE/HcsTsOmxuvOoLoIXVdOEiAdoG8LEoI3MLOy8oFVG9qVtc1vU6budevqcqCPM8pyhKjKxCaqnTXuK5dMLO8BkbvA59cGA9aQ1VpF1Arh6OxxjgRcJ89GHsfih/FEcPhyhIn4kqW0rG1q9pPnFxQWQQKx7+q6fcHToLCM6x17a7zMhh7mQaj70+FjDHEcUKv1+PewT1nlKc1ZekRv0Z7by3jv15jyObXYlEUfkMWrt+la7cG/aRTIrECTk5m5HnJc09/xQcqs0h+lsdnBeyf2eDwdEZ/TRG8Jvd3u1hRUFYVSRhTVzX37t2jrnrUnhvi++/UtUvnup2unxjVDpxkNUq4QFG9Nu30RlYCS1VXdNpttre3mEynSybrbDJdjpYpS6LIYUoEDuTjxrFO0KnRarmbZDRFVWH8e5jFDak1Vt733FnQBwb9AVkjo6oryqKgLiuyZmPJMcEYP1Ksmc1mjKdTWo3GMrvS2tBoZB4RXDtKvDJL9TErJAhLWVYcHh+6LO/klPFohDGC9fV18iJnNp97ryHXpzLC8YrG0zHj6RSEQlBTVjmz+ZjhSp9m1nB0BqUcdd+RRCjynNOTE4zW3Ll9m3mRE0UhVV0znoyXO3BZlGxtbbG+scEXP/8FDg4OMMZwfHy0NPwyix2nqjg8PGS713STviAgCF0fCmA6naFrTV2WvPrqqxSF496Udel5MhptLK/euOGg/nFEXhTcvnkLYy33Dg4oitLtmt7V0XicRlHkjmB4OkaguXvnFpUWbgFHEVnWZD4d+5Fr7YzxKpflGeDu3bvMJ1O0rhmNTnn11VeZzmdEofK7upOLtAZ0VYNnC+u6ZjyeLDeKRQY8GVlf4gnHYVpkXkZT1pVDo/vcfTIe87nPfdYPPozX2tHLxW5eI5dQa00g1TJzunHjVb9wXRZf69pNi3xZo5Qjw2prva6Nuxez6ZSXXn6R2WyGlM6McCGDYnTtHCYXLqNegGZBDnYbREnWSCnyEolC466FAycaBsMhVmuiWPkN1CKVABE41r4UtNPMTQjr2olhBW5TD4S4j1AVCOqqZj6fc+3khCgMiFSIrmuGqyusr29QVxVKBiAFzWaTJEncQ2edOJNUktHpKVVVsLq2gSpKJybcaCClS3GVcmO++XzuGk4+/XPMYEeCdHB0SZpkBNIxsNM4JZARcRq7NFMJhBUY4awxojghCGPiOEHKYKk1EihFM2uR567sEQhCFVBR+GwmxRo/thYSJRVCSprNNkmWkqUNb+XqJAWajSZRGJJ7gFOUxCRJ4mQmpCKKIhqNBs1Wi6Is6XRdED49GVFpJ4lAXZMmKY1mx/WgAkWaOVCYQtJud+j2mmTjmDhJqCu97DVlWQMdxSgBYRTSbLVotztkaYP1tXWms5kTABOSWteMTicEoVNQq6qayWjCYDCkPxgQpyndXpc4jBxYSgrCKAZtufrqTSxNb+kqaDUaxFGADAJ6vZ5H3LombDPLyBopZV273bg3ZDqbMTod0Ww26HR6pEnMyvo66XjKymC43OGtd7CMooRms0Wr0eL09ITj42PW1toMV9Zx+tUV6xvrVFXNyXHqJoTG0Gv30JVlnpdYo7lz200as6zBysoag+GQVruNMRXWCIzWNFstoth93mw+JYojcnKUFAgRYIxb5FnWYCVpUBVt77bpOEDNRossmyCYUVaOYCmVZDabceeOG00nSYMsSyh81tZqOihEPps72xFPqnTOnZI7d+44mY7AwTyGgwFRlJJmGY1G02XpxdzRCmSwRObmuVMXzLIEISSd7oBms8V0NvHNYycfEYSOTlLXmiTJmM6mSxRvFMWUpcbgNJSEkJS1Js8rqrLGJk64Kw4Conbm6CWeuDlYWeHRRx8lSROeeeYZ7l5/llYzpaoqAry6WxqHDFc3XC/m9JTNjSFJFHJ4eMhwOGR9c4d+M8RiODk9IpSW+fSUYj5yhYlPsaVUzOYzqrLkWEnyImc6jl2Hu6qYTUagKyaj+bJTv2hOLSjsk9GxB9FZRqMRgQpcna5LiqqimI8Qr7Fptd5LV1eakzhhNp8sd4VAKedzU+fU2jCejJlNo6W3tNaGyegUAYzGI9cTEcJPgmZoozm8c5fZ/ByBjBmPT5jOaianDr9Qm5rx6bHz1amcMFEYxeTFjMn4lPFkwnR0Sp7nbhxYlACOLHd8xOlo5K5/GpPPYuoiZ3wy4ii5S6OVMR6fIJVibW2b6fiE2VQyPh1535yKOI6YTSaMjo+YTifMJqc+a5EUZUUShyRJg2I+YT6dUMynjE+OvG5KyfHpCb1ujziMmUzGDqruJ03Ndo98niGR3Ll1m7t3brkAIxWz6ZgwCDk9dZOz+XQCGOZFidGaNGvQ6/ZQEo4O7nD37oGfvJXcu3vIUa+PUpJ5PmOaz7DG6QYN+kPm8ymTyRSB5tbNGxTzkjzXaFMxHo2YTqeOxmCc1Mid27coiwqplAPbVSW6KnjpheeYTKacHK0ym0+ZTMYerFbSbLpFO5/lqCCgKCoPfa+ZzkuOGhVCrPLyyy8yrVJ0VTAaTwmCEGM0Bwd3ODk+8bo6jsjqnC81aZIync148flnvauiK0cH/YGTMh2NSb341nQ6XZY9GIOpK+bzOc899wyT8YQ0ydz4/vDIqRHEDmQ4nxcLA1d0XRNIyWw6oa40o+NjTo+POB2dorUToaoq7wbqSzQlXFvC6No9n9MxeVFylBSc3VvB1FPCIKA/XKHfTwkZcXycOx8n4Vojw5Uhly5eYmV1lYcfeQRd13zkTz/MbFoxGuUkjQrxyz/7XfbzX3yRNz31eh596AJRHKLRNLMWgVSMJ6dIEdBstinrGXFsOLg74uBg5JXI7xOolIIwiKjrRePVPQCLRpIx+HLI90ykWKIKEc5ytKqNl3mwXltFLWHZVV0tf2bF/Qn3wjJU+xpT+b7LfVN1ly66QMiyW78AfAeB8iZXr1Flsw7mjZBoq3nwwg5RGPL0c684HRjHVHOfZUEF7u+61lghnIm4cXKhrmnttFIqXS05JM4Q2HgSm/RWsGbZzHNTsuA+BsKnywu9GOOPAWtdY3QB6ELeP1dbe8Els5QqMJ6ib4y7JrXnqyg/9sdatDdB39vaYGOjx9PPX1lqrbp+AyixKKtqjPHnKT173ZuXSyF9o7nEarts9js/7/vk0YXw2NKbW/vJlaf9L7yB7EKJ36vyO2O0RQ/O+Oasm25ar/imjSMjesGYpQm8NhbjRaucb7or4bUxDPpd9ndWefbFqxyfzpZ2ukbX/pn3VrBLsTPlumHW+Gsvlz2dxeZrTO3tWO+Ldy9G8kvRNS/wrbXT4bHLayPAOICos4l1aGorrVdidL7aSuJpK46waXz/RVpHbjQ4e1+xNK++7+dd1YaVYZdht8OkMMxyx/dII02kDKdjy1deusPdO7eptWF1bZW1tQ2qqqbb7aCU5OrVa6z1G/xXf/UJ1re3CaRfxGVdMZ2ekmVdqlnFyfwu3W7GbFbw6s2b9HsZjz2wS16WbG8OOLO7xjyvyMuaNA4Ync5odxocHE24fuOQtbUuG8MOeVnRbKacHE9ZG7aRyuVgJ8dj5rOSwaDD3cMRg16Tk9Oc6zeO6PcbrA8zyso1co+Ox2ys9hAOr818OmU8Kei3moxmbvZvjODO3VOiJODM5mAp8zed50SRotVtOqb2rGA0KQiVq0u1sWgEN24dk0QBu5tdjk4mdNsNpvOSNA5o99vUeYGw8KYnH6aua45PZ1htSKKISV4QhQFHp3NOR2Munl1jOq0JlFzKT66tdBFYxvOCybQgiUKKslpqo56cFpyM5+ztdqkL13BbvHbYa6GEYDYvOTidEgYu7a3KiiQKOZ3knIzm7Gy0qSuLDKQz0jKCYS/DCsOsqDg6mRMFgRMfMhahFKfjgvmsYHO967VmnN8zWHrNFKMNRVXy6KUzGATjSbHkDNWVMzyf5zXHpwWrw6bXILYEAcwLQ6cdEUi8MFEJnmIwL2qiWJLPDePRnN4wxWi3WJDOubCTOXxSpTXzeY2UCm0tpnaaxbOiZjrTdFrxkq+jrQPJNRLXoCwrw2xWe51nQ1VbZCQocs1sVtNqhH6iArVx16WRKjcirmoevLiLFZLZ3CxFr7QxKAFlbZnONWnsHDCNN5sW1qKUIVCCsrYUlXXBzwhXZknXwyxKSKKF97S9L4Sl3PE4rtDCN1qgDSAM2kBVWeLQ6dogFt7TEiWdr3xtQNf4YI2fkAoqDXVtCAOWQm+OMV0jlUHXUFeaKICkJam19SJXlk43A2GYTKdYY3nx+Rd44bkXQMDrH3+Cixcvsr6+QaSmtDspgQwIrHa77mg8ZjydkSQx03GJsTVhFHD1ym16wxb9XsZoNCFKouVoUUlBFMql7gsGDg5HbG/0WRm2sNoQKYUwNRKNsGapZRpHoVdlE95m0nL34Ji1YYu11TaBgjj0mhxKItx2AcLh65SwSAVhKDFWcvvuEZ1uxsqggxCGwD/kVlduU3FFtauxpZMYFEBtLXfvnNBuRqwNOwgJQSAQ3kHAcemrpZuMNdqT6gJU7HY+KSzHp1Nm84q97SGBf5iNBxrKQFLXjulalQXW1IAjdwprmReG6bxid7NDXbjGuBSOTBkGThkNIVzqX2sipSjLAoHg6GTMbF6ztd5ybHQhUFIwm7mRudaVm1JU1fJ9LBJT1Zyezigqw3qvga1KrDZYFVB56cU6DZ3Zu3V6rxZBXVZLsfC6rigqwdHxnH4vQUpNUc2JAgW1oKxq6kqCdKS5uq6IQqhrS21qyolhNM7pdTIUhqKonGIeTsZDG70sY7VnLFvrRMR1bpjMKzqtDCE0ZVm7TBDhlQYXt841/L2wm5PTHGtmpaadxUjPhg6UwGqN1o6rs1DxM9q48rt242ypnNg61n1+kioUgrr2GYKBuiqJYok10tFlauOeX28uX5eaea5JEgUGtHFCeE4Q3hAHFiGhroULEsKV+7q2VFpTa0EUugBUV8ZnlU58n8AihKGuLVq7SawbhBrKWlBrCAODrlwV4CgUbk0sRMiFsCjlLVNgSWEYz+ZIIdnbOUNVVxwe3iPyzHytaybjsSeJSqaTguFKiHjPT32n/fNPf5lOf4PhyiqT8ZQ7d26TZRlxHDGfT1gdrtLrDpDK8i3f9CA3bp9w5do9hHDj6AWHSAgIfWh0I6v7/AmneWGJ4hhd136y5GUpveBSEATOPtNot0uoYJEZu2AUBo7xWvk0UVikcI51LmB4CWNr/EwfhHTpZuiFvksP9hNiobwnlgA/cKmmksrzNty5mVrz+KN7JGnIJz9/hXlRopRYEial259cKWgttfHpthTesWAhcyiXnBMnfCSXuhzSS12YhVK8sEgZOGKb1gQqoChKrPUAR/zO4r1HlZBoHF5FOpiFb866a5TnOaFyE0NtrBe5cgLiAcL5Ni8a/XXtx9GW7fUeu+tdvvLSDQ5PpgRKLoXepVxIK7oHdFE6LSYZBuPlMt17LtUKFwp2xmCFWwSmNu5chMVq4/2VHdRA+/G4sPfLCA8ewS6kII11/1/ol8jXaJrgMR5o72LhJV6FE3m3fvMS1voSBVqNiI31Dq9cO6Aora/I7hMG75+5F4r319t8VQlrvcGaXY6YF+XvshT0n2+WigHOX1tb48TftcQIN9YWviSzApTFEUK5r0ft2gpiqdeMD6jLx/s1o2ntj8HiaRPCkVDj0NDpNClqXzYu2hDCcPveKc88f9OXh27qt7O3x87ODs888wzXrlym2+syGHT5b/7Gm7h06SKBtYKqrNGyydE0JM8jdNDns08/BwL6vT7TckYlV9jd7iGwPHf5kF9+3ycQwqMmvQSjsdbZhlhX20aBw4kEYUiRz2k0G2ysr3Pl2nWqonQYl0UnZGFxshBzVk60qShztHbyB2fPnePyK69QliVBGLmLY12ti3T9jjAIHFrTuHpYBQprNDs7u5yOJozHY6IwWo5jjae/W+ukEo2ukcor/IcOa9LMmuzurDGQit/+0LPcuHNIFIa+my+IgtBpvGiNlPfRvk7BLUCqgMzLWd66fcshhT2ob6EUL2XgJw8xUgVL1ThtNFnqOCmvXL3q5Rk10gcYGYREUUwcRCivFoiwzoLFWNLU8b2uXb1KGCqngYubWiWeM5PEqZPLqAtHDDQO5FaWmjc/Ktlab/Ppp2/x+S9fIY4jAv+ZUeTU9xbC8YuNRIUBCMF0PKbI57TaDhEaRU4DSOCuz0JrlwVxMHT6NqdHx05xXxsvvu2wOVJIz8auXUD3vTkVhMzmM4rZfGn/IrAMV1Yo64ooCJeYJuP7bIFU1MYR/qwX314QGIui5tJum7W1DpdvjDmZBIBejoWtdb2x+XzuAqm1aKvRVe1BqK6B2u87zJIDFDoKTa1rqqL0MpZOdmTxc7zTga5r+oMBWheeBiCZz+fLfox+DQ7GviaoLf5uNZsIaTwWRi/F1RdZ+H+uf608VaDWhq1hSK/XRnqph6WsJpZGoji/0/WZvSv3hCw5uv0826sROyuXQBjWBx3O7gwRJnc4GKmkR/BqpLREnjsjpWA46NFqZJTFDKNbDq0ZRwhpSROHhk2ShDRz2i8L0Jte+Ldo10cYT07Z6mzQ7rQJI+VEsgV0O13XyBQO7Wm1E/Opagdms8bQabdoNhtOfMov7EBJWp0uSijyvEBbTaAUVhsmkzGNRuqsT3xGkKUpk+kchCDLMtKGw5Ro7aj0k8mYuqro9jrLByj0hMter73U83VWnI4XpZTrdVRFxcnJicv6IjfCD8OQOPAEtiim1+9xOnLTnVazQVGW5LO5pw+0wTpHhDiOiILovjxkoGi1Wty9d+BEvoOAo/Eh7VaTMFBIr1sbRzFBFJGmiSehRl51TnDl6jX/UCk/TodQSZI48GJgmQcydgjDGAHcO7hH3MiIQuUDX0KapY4iEITEsdM4jsKQxLsSSD+iPxmdOgJjr0tZZ4ReRTCO3PkFXjJzoQuslLPzODi4R7PlSmspHHlVKYtsNlDKCXItfJXwvJp7d+6ggtBpCkeh24waDaaTCd1ux43dg+A+sjVQbto2m9KIM2YzR7Atq8pnMxbs1F0nY9lc3yCdBUju7/6379xxgVK5kXWtF2hcTagCVlfXePHFFxiurDquHjgRLGtIZEYdl2htlg39BSizP+xTVTXXr15lc3OToig5Ojqg1WotuUq1D0aLIYf1bOnBYMCNGzcoyoK0kRIo5V0GWIqEL7SNFxnUogcjpKQsCqbTGY1m06vr+c/wtAtrodtK6bUzH+g8LsxnRgLXS2xkMRf3V1hf6yBlSGCtWTItq3JM5R/8JM0IlOTewSHz6Yw0bbA2bPnSw9WI89mEeV6ggiGxP1HHf3C4gF6vy2QyQeuKYjYjTVKytOmQvYHLnGpvPCaUoq4dFrfdajGdzZhNx5RFztrZs0RJTJZlXiHdCR9LKwjigEDXSA1Z6ngReT5jfX2NVquJ9gI7zUaTg8NjlOcWRUFALixCSbIs5fj4iKLMWV09j67qpSWIY0s30J5bgrHksxmm3SRLGlSAjB1CeGXYp9vpuF0sCJz4VeYW78pw4Lx+jCsFlGeh17pmZWUF6wmIThg9IY5jkjghSRKarSaHx0cu6wsjJtMxmxtrNBuNpUVK4LE3SRyRRgmhx+ZMJg4LURYFcajodtpORD2OiKLYBaQ4Xn5mnMRgLc+/+Dxrq5uOyOrhA61Om6ZnukdRRJQkpElCFITEqdPybWQtTp85YT6b0u8PSUhdOdftECcJypMsF+fqGO0p08mMl196icHKius9KceENqYmThIC5RwLgzAkUJG/NxHXr10hEYI0SZFCUlal0wvyG1W/18F6sW3lZUSuXLnCtauvcHb/PDY2S2V9sEsApEuONEGgGPQHBIFjwBtreeGF58mamWP64zSalVIusw4CVldXePHFF4iiiI3NDZSU3L1zh6Io6Ha7REGw5C05KonGmIpuu0NV1VzRhmarQZrGXL78It1ehzBUpGmD6XTKwu65qmpqL2y/trrKwcE9qqrg7t1brK2uu+w6ipAyYD6fEScOB2W0JY5jiqJw4FBdLV01sNoB9KyfaAkv5mXtEgXseFaudyTs/e9JZSkrQZ5X1LUljMR9JK+DgTvphma7RbfXYT6bc+XaVeqq4uR0wtqgjRAPLGvJJMvImi0aWcPtKh40tJDhS9OEoihoNFJanQ6T2dRpySJJ4oxO27FBtdZerS4ED6e3WDrtNsV0zCuXXyZtNIjjFIyl1+8TqMCN5rQjPFopmU5nJGlMp93h6OgO49EdApUQRw3mLffgDAYDVBiQl4Xza9IOet7udMiLGVdefgUhBJ2OE/Wez3OWIprWOSd0e13SLGM6mzGfzWi320774/DQacCkKb1uz4+txzQbDa5dv850OqXX67s0v9ZUjYx5PuHq1asEUtJut+l0Op56UVFUFYfHR6g7ijhKGQyHSOkEy+/dO+Do8IhGI6PT6dBAcDw/pD/oMz4dLxGmcRwRJymdbpe6zDm4d7AMEL1ej9PTEc12k6qqODo8YjabEUUhnW6Ho8Nj7Nkm2rhN6ODOPU4DSZY16HQ6tIRDEbc7HWZFzmw6QyApi5L19XWsFVx+5TLNRsbo5ISs0WBldZWT0xMaWYOyLN01nM9RKFbX1sjSlNl0yngy4e7BPbI0ptvrEYVQlgVZo8np3GF9pBCEQUi/26OoKlRdo7Ti5qs3nOFbf8DJydghjKuJ901yZdHacMVJbmincBd6+Y/xeExV1QjRcedSzpnnI+azCdPplKzRoNNukaUZJ8UpoRc+X9AtptMZTz/9tDOCm0+5cuVlr7qnGQ4HgGQ0OvXyCnZJFVBK8sorryw1jkanI05PTxiurJBlGdPplDwvlqZqjlXtrH1msxlfeeYrzOe5Y8O32jRbbabTKWVVEYWS2WxO1shczxLthLWsEyGvSscyl0uLHun9scX/gVYglm6t3qFFCL5Kh/M1vmhY6wSnjNYEQUgjc6jS2CvIHR0d8fr+gOFgyNUr15xVib3v1Oj0K5wB2uJNtdZ0Ol0fYStvUeIU7h1uY5FyWebzOY1GY1kT1p4UqQKvnxE4/pL2kxtXwjnYe6Erx2HStYNG+2ZwEEbEScJ8lqNrgxKBFxfysOrZjNRD/xdkuzBwavhKuJLHeo7VovbNixwlvVeSlM64zTrtDOk77FEUOfU2rdFRvORWaa2RgYOcz+e5e3hl6jR5wwghHBfEKG8zqwIm4zFSScI4Zj6fEwQhYeQasQ6NGbjMzDiipUu3LcfHx170KqesK/cQaUe1cO6AFXFUE8UheeG8qo+Pj0iyFCEk8/mMsnAP6cKHyQpn0aU8DNwtOq+5qmtOTk7p9YeMx0fUZUW73aPSJQhBFETMps6aJc8LLII1JTm8c0iy5Zi9xTxnPpmjlFwiSqVS5Pmc6WSCdE055vM5RZHTarUpyoLR6NQ1h73BV/UandrxZOKHCprT01O2trcoioLpbEo+L5AWuj3nrVRrvZQ/LcuSsnK+3Syf55qyKimLgtlstvxeFEZLaYYllse6ezmdTtzUx1QUkxn5vML4z9H2tfgtu+zFWGs5OTnxGYdcUlXSNHWOCB63JAjvN4oXNif+eqRpugwAURgzl7mnXjh51Nqr7llPG7BYB/z0g4OFj5ldyoIvW8dLlcpFs3phS/ufezLhm+SLbweWChUKmrFhb8PV2HGSUNeavbU1b4eh2OrvoqicXewCs468bzq1mIwgXgN/ZmkOFaiQUDmfIWMtSRyTpq42X/juBmHoo6V2/Y7FdEhI1wD0daFSTuKx1pXr+wRq2TgNvCCQlJIwcARCPZtT+8Zg1mi8xvZVYZa+TN6nV0CgQkajkZMvnE7o9XqOELe8qY5XVSOxQhEEyjOindd1URaMJhOSJCVOYoqqZD6fEycxKnSNbVdTO7fAyAtmlWXBfDal0jVVXTObTJ01axwvjcyEn3A5A7WAqixdWh8GaO3gBtPZzLkMhAHtTttJVyxwFtKpF46LGbP5nKqqmU6nAORFTpZlKKEIZEC3t4a22pVIUiBDd361rpkXOQg3ij45OeHk5JRut8PWzhY3blo3nkfR6/V9k9FpzJ6ejCjLkslkQpGX6Eo7hC/GS27AbO522zAIMbZ2ZbaxlMWc09MT1MJ9MlBUReUU7syMUlfU1tDr95lNnbpcWc45PTnl6PiQQErSOHGeS2FAlCTgJzlCSqI0oW0Ms1nugYKW6XTO6bRiPpt4y5UYoZw+URiGzOdzD+S0XiKiQRzHnJwcoYREBhE2kpRF7rIEX26+liC6GAMPh0OCIODo6MiZ2Ueho9YEyustWeb5nPtGkG6BNxoNul3nCTWb5csNLwwi5wBpoTaOSLoAvAoBkpBWs+03U9cCEIuGi/3Pg8dX/7GvkXdYZjB2oRXoG8pCEAQS+u0Gb3h4nQv7q5S1JgxCOp0GQsDJaIYEOt0hSjgz79oTG914S3mKu1widL86oEmiOCJLEhreU2dh1q21H8V6waglg9VowihCSciypnt/6dTsF/T1yLsaIjyD2hu/BWFAlmYIWyKlJlYRUdQkyxyOxxhDGEdI416lrSYKQrCGLMlQCuI4oSyc6E4YR04bd3mxXQPXTZhcoAij0PUAFiNkz9NqtV1zrtloIoRkOpmCECRh4nYGox3/KQgIletJdDod0rqm0WyQpSl5njty37xwfkKJ65sYrQl947PT6dDudgiDgNXVVU5Go6UIV78/4M6de94utyZNM5dmW+h1u2Asg34fGSjGozFZkiKks1uJkww4Xj54aZISK4Hyx+lM5OYMh8Ol7o8QgjROaaZNauOIq0JAs9kkzZoMBkMEsDIcUlQV+XTuvaRdAzeJnSWt0YHPQBX9/sBrn7QY9AfMZzN0p4tSTqqy1WxRVm6nFgi00CivAdzt9hgMByx8R4V0kp2tZtv5QcXxUhVAaE2j2XAGZx45naQJ3cgNJgKlSLIMgSFNMqJ4vKQB1FIijUFKvfSMDqOYOAwJw5w8CkjSlLrW3kbF9QId299PerxX9sIiN8sarjEeJcRRisVPwrT1fUiPXVkq/LuNIE1SkiR2FiraOR8ILbCvsUpZMKvTNCNrwGw69pIp0v+O/SqXgdeWSfd9nsVrfmch62GXds7WWNeDsRbSOGZe1Pyj//mHabWavOenvovpbM7f/+//Fc1mxrv+w3eQNVzTzS5V5IRf4MbTAcR9dICfwZdeDmA8HhNHISvGWWAEXkZwYTu7tEpd+u4WVGiOj48AQRynFPM5gZQEXsoB/7oFHb0sCqq8II5Djg5nlNWEtbVN+oMexjpkr9GOkOgyEoe5KHWJ1iVHx/eIgoAkyZbjyLIsmU6mHkfhauXaA6O0ddyRShimkwkzL7u5sHqVSlEUBZ12x2vrOq8Y6dPsoigYj8dgLXHkspTNzU2qak5dOYLZ4eERVVnTbLUdvL0sKfIcXdVUygkVJWmKEB1Ojo85e/asc0soKncc/njmsxnj0WjZpD8+HXHu7NmloZ3RhsODA+ZpCkhkELC6to7MFjajMJ/NqLw3T7vTIZDK9VYuXODw4B5VkdNqNDk6PFo2hRd9htFojDauEX9tNCbY3mI6n3NweM+p4XuMVLvdpq6qpf9PURQEgcvU8vmcOI65eeMmx0eHngVt6HR7VKUjOkqXXqKUsxiZzWfEkfOuLosCqUKqskJbzSAMKL0Hl6OO6OXGucB6RGHE6TxnOp1Qls65oipKeoMV8vkcXTsFf4VFe9ay8GTByXTKqM6RMmQ2z+l2e173uXLTMJ8tSCdq7dwzrOsp5vmcu3fuOOGyqqIocifb6TOgRcVgrUNhCSmX5z2ZTCi8pKabuLqJnDEGLYyXW/HAQw8NcSWR/CrbEvt/4vRo7Gu++1qv6K9Kb+6PxAPtY7v1o6ssjckypxanjaHRSGk2Ui8UVGN8lP/Wv/FfIDBenMfN5cMw9MFHuTRSCm8BGlDXNVnq9FC3tzbR2lk9OCtLuxxZBnKB43CgMf22t2GtIE3deHUymfpMSfpIaRz7F8dIDZVy6Xj1ZgSWKHY78TR3XjpL7tPCy9rfaCkk5Vvf4gFwwluvhljg9OSEonKTjYcfepA4bS2758ZawiDkySce9yLQyjfqAg8gFCRxzMrqiuNhLfyXvZ7sU294nDAIlgr/7XYbbQ3zPKfVaLCxtkZV14RRRCPLiKOQs2fOLEfpQSgJwgis4OzuGaRSPHjxARJPwFNq4WkdEHsBpNovisGgT5ZmNJoNV+Za6HQ6WJwwlVIBWZxQG00Yhjz80EO0W43lw5PEKRcvnKfIZ1w8f96xo8uCfr/rApfRDPsDAJIoptVqUFc5q2srVFVNpALWVtf8uN94ouspUeQM2RqZkx6dTcZuVB6H3LxxHaUEnW7HyRfomtl07Mpqz7UJlWJlMCCfz0Abbt141fWUPEM/CGPquuL46MAhwevCGa75iUy320FKgxKSk6NjTkbGldvWUOY5VsCtm69i6tqvHai8xo1SEisEvW4LXdZMJnOULKnqiiuXLzsXCAxl6ZQW0WbpKCn9OD1LYsajEVYbDu/eYzI69ROqyPdELFVVe2E4b10TBBhhaaQZ+Tzn+WefW+JlwLUcQKLRGF82LQXXpMNHuWejRMgYre2yV/rVseM1PRrn2LLcjO0iliyZZRDIRT9BazqdBj/9Y//cp96CdjPlXe/4dgSSJAmWRMJ5nvPMczepqwLlMRcLpTpe41EdKOW9kJyYsq41aZZx996B8xgKQ6d5Ya2T2RTK77h4k3UXVV3dqGk2W9y+e9c1Zn2DDnAoYun8lZXfCaSQS39s6T2Gjg6PndVI4DxwlAy8q6HrMy1AR/gpmRMNVz7lHSCF4M6du0znNz0zWC/Fn4R02iSBcpIUQlikCt37SyesfHx8zMnJCUnmHBeEv/bS95+kkozGo2U3v5jN3XVRAQf3Djk8PHJ+xVWx9HyKksjbchiyRsMpuiGcgHoUIIzg7t0Dp+Tnew61rskSB7LLSyc2FPtxtfDo5CiOGI9nVLVCIiirytlVCOtZ804FMIwi5nlOHEZYL/SMlIRxwunJKZPJlCxLltOaoiwJA3/fvUEbAiJv+zKfzcmLcqnP0mq1KOva+XbHkUd0OxM+/Roi4HQ0Jp/Pvd2J26X7g56TRxWCRqNBo5GBFz6z1pLPnRDVbDZzzqQe/S1liG27XlkQhqQN7xmepUsqgrWWQjuHz7p29icL5UMpJXnuJmlZo0FVVgjpRL6MMZgq97axenme2hiC10BGNjc3HQS/dpIWMggcVaB2lI+qqu97Tlvr1JN1jdGG4WDopmVl4eglRjoKhNG+F2MQvrnsAIYCqyukNSCC+w4E/1kGY/8PWQpf3eD1QxyJ8JxMS7AIUAsrzyxNPIvVxaJWI/XgHE/EwlLVNc88+yxY52MzHK4uAVxSqqW+y+Ik+70ON2/c4OT4mCeefIo7d+5SlY5ZmmSZm4xI5coIa8jSdMmovXL5MmEYUdc5lx54iNFkumTapo0MJRz8XtduwtTutLnyyisIcqJAkJcGIRIefexR7t07ZDQeL8WjZ9MpZVk5U/m65OrVK86VMXZ+TWfPnWU6m9Nrd4jesoFQilu37nD73jErq0MCFbidRSquXn2F2XSypBn0ej0uPnDJKax1uxxeucJkMqWo6mVDti5Lrl29QhxFhKGr0c9fuEA+m9FqudH33QNnpiZFwLXrr5KmMVevXkXXpfNikoLtzS02tzb54pe+xJu/5mt45eWXqbTjkSz0YV566WXKfEan2yHNMk6OjnnDk0/y4ksvcv7ceabzGdevXydLnXGaDBQb69uU5cyppNUVX/7yl0nTCITg7P5Zgk7IlZde4qk3PsWXvvAFVlZX3fQjz1lbXafRbDEvSkbjCS+/+AKtdosnn3qKZ77yFR5++GHGkwk3btwgTZ1BfBKnnD17npPx2Os8S46PTzizv+9AiUXB/v5Zrl69ysHBPaRX7bt46QGshSNjCXC2OXfv3KXZbDOdTtje2eWZrzyNrkpCf2+73R5b2ztcu3ad/sCN6RdiZePxFGyEsZZmq0klJYeH91DKNc7rSrO/v8+tW7ecJ1etabXayw1vZ3uH559/jiAMUKKmKi3zvGBzaxslpaPipJ4YKsVSnCqJHWzj7t07ZI2MO3fu0MianNk/w7VXr6NUSLlUn3ODCus5Tp1Oh+OTIybjCZPZlAcfeIjj40Pv9qiWPZ9Fc3mZZVjH7p5525YwjDySW75mhuTjh/bSpdb4Lq+4r0xgHc1j0YtdZPdB7mvwX/vtDzM6nfD/+K+/hV/5zT/l/NlNzu1v8su/+iH+4d//6/z5J7/M8eGI7/xnf9f1C6KIKJDeU1osRbCVUpycnIAwDPorhLmzjU3TlMo76kVxTF27WXwniggTJxpe1RWYmiSNUYEzy2q3WqggpK5Dh3QtK2bTOZWp6EaxV9ZySnYqDEgzh/jFBE4LJtJYQo+KdeJZSrrspKpdxpE2UoIqdAvZy24GYUCcJGhriaJwKRERhQqlFrrQBlPVtIYtsiRGAdIbp2dZuvSjiZKYKIxQKqeazoiS2MHtVUCz1XAm8NKZy8dhhEkMQRQSJhFJGpOkMfNZTlkVdPtdskaGrhyQDyBJE19CNQiUIk5TIl/Ph0lEPTpFSkuz6ZqGSeSAdWGgSOOYMA7BQBJF/jglSMnR0SFrjZTF4xgGgcM8CUePUIG3fZHCjZe9HUvizdu0t2/FuoxzYaAXeopBFIRLTybhwXDGl9pKShqJw5coKVChRBmHPM4aKdPJyAW+xUhFSYRSoGtX9nkowiITDsMItZD/WPbtHHw/n82cgdxCzuA1khkSQSAloQpQKvQKbnYpNbGwurF+UYVBwGA4wD7vng8ZKISoPVxEewzZYurqNZB8D6zT6WAt3L59C+E3fWPrJdcJqz136P4g2XHTJCsrA8aTk6WDY1XlbrplDCIIOTo6IIoCBxcxLKdExoDWpYNnABiH7D84GPOxj3+Z8+e2KMqS6zfv8cSjF/nyM5dZGXRIkpgXLl/ldQ9f5PLLN4liydbWKs889wp/7S++gTe94WFGpzMC63e6a9fv8MLl63zLX3orX/rKS1RlTRxEfPRTX+Gvfcvb+PKzV7h+4y5V7coIZzgvaTYbZFnmHedY4gJALPVeq6peci4Wo7koioiTCBU6uLX1D4GwDpMgPaO1KAsCa528ZeVkB7u9rift6QXcB6Gk02CtvJOdqdB1gfb3ZpFSdjpuB6/q2rklWFc7G60pcue7K4R7cGuv+F6F5VKs2hjruvpx4tTgsZR1TVGWzHMnZ4llee7j8Zhur8dkMqYoC1rtNmEcYYylNs7TB2+xWnkN32KeE4URdWU8rmJGFEb0+wPCICCfzx2eyF/v2qvIzedzb9y+mLq5HS/wE4n5fOYFr4STpbSW6dwBrYwxTKfTZT2vrdM4MTZdOj9Y49wMW82WKyVxNi51bZgXBeFshi4rtIVVpSiKkns+06jKkul8RqU1Ze4yzlq7TcZohyGJ/n9lnemPJdd53n+n9rp1t75b793TPd2zcPYhh8NNhOklSmB/8F+QAPmQDwaSwLADIUhsy05kA7Kc0LQt2o5pWYtpRZQlc5EpUaIkihTJEZcRTVIkZ+Eyw+me6f3ut25VncqHc27dFjLAYBqN7rlVp6pOnfO+z/N7khS0+W4w6LPXVx2sJEmII3UtkjQhiaWGS6k43kF/oBgneoLb2tpSkRrCoN3ujpMU4wgjGSERlPJWxkqnpJIiY1rttjLTjhxSMmEYSUVCNEZJFBHDaMBwGGmxm61BXarF/u6776p0AZEi04QoHo59QQaaKOdqzx56Sy9YX1/PuqypTImHyl0eJypYL01TfC+XoW3HTN0BV65cVfefIRQPOZFqexUlGEaihXQmI4TQaPXSbrc0nN3JAOrqPAZcef8G5QkF5bry/horS/Ncu75JKiX5fI6rH26wND/LRzfWKRUDvCDHm+98wN3nDqkYlTDEUsUfwa/9q3vxcw7HjizxG//+12nUKzSqZT7t2Zw9sUI5H9Dth+R8RalPkgSvkMfRBdZ0n1M0n1dt2TiJVS3AVEVM11XgbvQefhQxSjre36nweFWUTKXUKw8HQ4BtO5B2VU1m9HnpCOFgYlnoeo8FqYNIU2IpME0vo/cLQ9kEFWQo0WY9GykMnTMzilVRVHTf97XPSr0NEIJCvqAFiW5WO/L8nK4lWZBKXL1qCYIAAfg5n1D7XXzTIhFS2QyEwA8CpKseIFNL4B3HyVrunutqlIEFhqHC5TQ9z9TtbdM0CYJcpvSNo1gVawchcZKQywUIQ32ebVqUyuXsZ23d2ZqYqBAEOYShGMjtVh85AlQhKJfLuL5Dzlf6nlFEjRCmmrh9D3z1hi4UCoRhyM7uNpWJKsVSiYnKBIapXkqObRM5NvkgwHVcMNRYu45CRg6aQ3b39qjXKpiWqYvx6vgdx1HHrVdJpVKJZruDYar7otVqZdlPlUpFxfvmcsSJMmnapvpcUxe9LY3GSBKdYqG7KSOFh6e7WxpIizBQRDrtfUq14UcIg16/r3QslqrvuY5LEhtYjvJIJXGC4zoZ0X/kD0LA1uaWysw2FLY1yHnkCkU819W2hPTnujapvi79fp+NjQ2CII9pKcOs0k6FJLHS6OTzed3qTzLRnJQ6KjdL/BiDskqFgAfuP8tko8QwjqnVy0zVitx1x2HyBWWTcDyHRmOCO84ewXVsKuUiv/rJu1manySKEnzfw1IUNfj2937M1Q9u8Nv/+d/xRw9+mXNnbuPMqSP8z88+wuc+8x/5p6de4Mb6Fr9wzwksy9SDSiYw2v9HFbuSzA6fSEXWD+NYkeU0g0GhMHV+mlT+CgORZcskScIgDHFSTelKEq3slQjTyApNphbqDUP1M1EUAUNMoXKLUxkr1ol2eQtdHBN6JTYyrEVJhJVaihCn2+VRFOm9LpkaeJRtrNgfEseUmi8bYymLqWrnaZ5GHCs4tCTFdqxsyxGGKkPJsm2iQagh0TKLXomiIcNoiO042q2eZOZR1f6N1TXQq6so0RBqzX0dhAPqk5OkaUen+cUqIjiRmiuS4DnqzZVR8hHIWJnkZmZnECicZbY6NY2M3k+k2vBxFJFEEd04ZvXwIbrdHt1uD2GZ1OsNvdpV/pc4igkjlc0Uharoa1qqBjccDhSVMJH4OZ9EFhlGKgUgjoeEYaQc71IS9kNMw2QYxySpVEt8KUlSSXlC5TNJqR6mQagylZSgTMGdoijG0G51NCnQdlSWdb8XZk2LKIoII1OlLRiGgrpHCgGRjIraGpinMA8BlYkJdnd2iOMUQ4TEyZBhGGtfnMiyxGWSqPtSi+2q1aoCv7fbKmMrGmKHoda6qCzqeBhm13s0yXjeKAN7vFoabZVSElJpanlJmqlxU02BDII8YThQND6dpmEKQbPV5tnnXuXsmcOEw5C33/kI/5fu4sVX32ZhepJCMeDCa2/zi/ef45Wfvke56HPuzFHefPsD5ieLGIagNxhgKWdqyvLSIvVGjQNzDf7Nr9zD8oEpluan+fVfu5+lxUnuu/sE27tt1dbTJ6dwmGLsUdCit7GcOM0I7qQi07tImWCZNo7rjieofbwKRZgn08aMMIwGiuqeJCqXeL8jdLRcNITQJDm1xLW0XX5rawsMte8fIwxVBd4U6NqLkbWpTdNka3sTgaBWnlATUmqOZ/uRu1bn2oxiRV3bzqj/164pe0W73VZvFtcDw1DtzTTF91VWtND7ecuyWFtbw/M9mklCu92iUCxoEZaehIWKmAlTSKWBZdl0ex2i9QjHtlW8TKGA5yvjYuD7tJotICUaDjE99X1boqNo8txavwlahWqZBgnKtOq7Pmna+znwEvp67WxvY5hKKXz5yiVygY9pGGxtbTIcRpTLqutmWSZxpGwV4WDA1StXsB2btfU1BErUKIQiwgnGIjBhCKWaTVPW1tZASEzD4qMPPqRQLCmFs+cRRlGW05yq/BNVP3Nd+oM+e7u77O7uYADmvtqLkjqkGcJ1VHfJF/LEkcxqG9s7O/QSn3wup4urCqGaSIkhhK6PpJmi1TANpC4FGAaYlqmlCbogq3PRUyn0ilhxYVRn1CKWUq3s9RZ3FEcjdT883SeuU8+dOl81bsnYuKmPZ9SmHkWMjDOq0aB7Fz/na57vmIbn+z5HVheYrJYV/CuWlAo+K0tzVEpFfM/h0MF5JooBB+encV2LnO+wOF9nYqJIKlNs28IaoXNM08TzHFKRYmmRmGS0LTHAUEFjiquR6r+SRO8fJVqbIhjn4UowDIkQFq4X6G2MTRRLjYTUg4tQy22txUj1lipNYoqlCWzTIY4ivCCPbLbUw5Yqx+tI8DcCjmOYuF6BVHNPLcMiSSzcoKCCwkkxDVtZHEzAlLqtLskXSjpe08RxXO3HMbF1SzdO1I1hmDaGqZTGhjARhkU+X8J1PbW10W1v27bx/Zw2bhZoNdtEUmktUl0Qdv1AFxBNxa5JUcVaWxkSS8Uinu+zu9fEdX1s28Nxc7iOr9IRHFsHghlKz2IIgiCPr/kzpWKB7Z0Wnl9Qq0bbpFAqINBtblv9vud5BEGgrCGGieM6hAO9SpOqOJnL5bFtC8fJKXSCZav8ZMejWq1gGCaeRnj4uYB2t4NlewgiiqUJgpzaRnqByj3PtkQ6N9oybXK5PEE+TzSMiYYS11ZbDcM0NELEpFQq43oeruMQBCpRYRgnRINI5RDFihho2x71xiRpol5ermsrq4bOtsaEoFDItgpSu9tB6MDAGMd1yQUNRTC0LL2tkfh+nsDPYwilbE905lFEol+UYBoWQVDE81OiYUKhMEEcR+Rz6jPjJM4g3GliZCu9JFET8tTktEr9dDzy+ZJ69kb5V3GUrX6Uyx9Fy4tVwqLn+USRRBi2DiUc10BH/+p1sNazKCSnHBV+ta1EGAZCppkS2kiFdgnpdr9IUb0MSbcfEmrHv0RikGLFkYIz/8s7l3n/gxvcfuYwTz7zIneePUbntpDHHv8+d91xlOdfvMjNmzv8h3/7SUQqWVqcwjCUKjZKUlX30FQ3Vak3sm5AFA5ZXpxWwj3fZmlhkna7i+dZ+mQTPNdTs55lYmjRnWPlqJWVCCyJY4JCDseZZm+vhWWmWLZJkqjuBkJimyo2Nj9VRRg1hGkQDUP18OSLNJsqH1vKIb5j6eW+BiZJqBTnlUJYi/YsU0WJ9PsDwrBPEFgUC67moabEicTLuUiZEMyogPSRgFB5fhR6QeiuVTHvcP3GTVxbIy8sg+J0NWObKNNdpPauto1jO9i2ASIi7wnankAQMtMoYaTaEGob6oLKBEtnhju2pSwQrkGa9CkGFmHJIS2UcRw7Wy3lcjnarQ5B3iHI+8RxhO+YJDLCSAXt5gZOQSELwmGfSjlPkHOV/cNTBtFwEJLP5bCk9rOEHRDQbXbY2dlDyAHFgkdoJfi+qaNtlEHPSC08287wAKaQ3Lh2majbJoyGyDgkV1CQM9MycB1oNffoOal6UYV9HFNwa+1Der0+YX9At6vA5LYh6bV2KBWKJKkKZ/O8EiQxpjBo7jTp9HpEcaJgTklCvz9QEHiR0u/FWMYUaRIhkiHN9rbKw7KV6vjGh5uEgwH9METoWpfamqt0SscUNHc36XdblMtlkkRya71JFEW6LhaPt6VJQhwlmponMVPYWL9GqVRGyoTrO1sqnjVNsoJ8EqnCPhp2le0iEomQLh+9f5koSVSROQw1NnVIrFdcw3CYdcCkFAhTmY07rQHeXIF+v887l67h+x7xMOHdy9dZXJzhyofrzAwH5PM+717+iLnpGu9/tI7r2biBhzBsbMciTiRhlCAe/pPfTK/f2CQXKETmJ+46wcuvvcfcdJ1atciFi+9x/z0nuXr1BoNBzP33HOfCaz8jFwTIJKbZbDM3O8X1j29RKgYUCwVubmwzN9vg1sY2UiY0ahN8dH2dqak64TCi2+szM1VjfW2TQjHAMgz2mh0OrS5x7do6lWoFQ0iuXP2Iubkper0BnU6fudkG6xtbqnVtCDa2tpibadBuD2jUJ+n3WqTCIZezuLF2izCMmZ6qcv3GLeq1CWzTVMc21+DGx5vYjkGjXiMcgm0mOLbHbquJ79vcWNuhXi8j45jNnT3uPX+cmzd32NppEfgea7e2mJttMOjHDMIBlYkiG5u7TDbK7O01abcHzM42uL62SbkYYDsO7c6AyWqRje09DNOglM9xa7PJwnyD3Z09MCxKeZ/LV69Tq5cghWarw3SjyuZ2C9u2KBZyrN/cYWpyQvFsK2XSpE+vG1GplFhbu8lgmFCvl7h5c5dyKY9hCW5t7DI7U2NjYw/f9SgUXcJI4toCmZr0BwMsARvbe0yUc/SHEc12l7PHD9Pud9jd62IbNru7beq1Mtu7TUSaMtmos7HdpFIO6HQHNHfb1KoFPl7fpFYtYxomu802jXqZjVu7uL5LznfY2Npjql5hMFTWE9eBj29sMVmvqPpMLKnVSmxttTLUZ7PVoVGfUL871SBNYlqdPrVqiWvX17Esk0q5yI2NTSZrVcLBkL1Wh0a1yOZWCz9wECmYhovvm3R7EbZtEschW9stJusVWp2uqj81KkggjCK2tpvEUUKllGNzp02QsylPlGk1exTyHpu7bdIkJp/z2dltU6uW6PQHJDLFdy02t1tUijkGUcRwGDNZr7DT7OG7FkkypN0JqZWLbDc7eK6N61jc2tqlVArod4YIA1zPpt3uU6tN0O8PESLFtgRb2y2KmnvUD4dUykVube6Q81wwDDqdPsVSjmQoyRfy9Ic9ZCzwHIudvSZIg1zgsdtsUwo8MMDzbFzH48pH60zWSsg4ZmOrzdLCJNfXtigEPo5j8vH6Fkuzk6xt7mLaFpPVAjvNDvfcvsInf+kc0VBi/utfvOPTvd6AH738Fs8+9xorBxf507/6Op1Wh15/yGcfepTjhw/ytW98nwsX32V2psFv//f/xcx0gzfeusTfPfot7rvrNP/tDz6vildC8Id/8kXOnTnC3/79k7x68R0OrczzW7/zEKtLM7z+xjt88e+f4M6zx/idP/prjco0+czn/o5ffuAuPvvQl1nf3KVSyfMbv/XHnLhtlR++8Bpff+KH3Hn7UT71ew/huza9wS5/9sgj3Hf+FF/5+re4tT1AJkMe+j+Pc+TIAZ76zjN8+9nnuf30bfyX3/s8xULAlfev8+DDX+OXH7iDT/3uQ1z/+BYz0w3+8H8/ysJclVfeeJ9vffclDixO8ruf+QJzMw3efu8D/vJvH+fo6gH+06ceVGpWA/7rH/wV95w/wbe++wovXniLxQPTPPTXT7K6PMMrb1zhH596kbvuOMrDX3oa3w8YDGO+/NXvcfupVR574gVubbaYrE/w51/4NiePr/DDH7/Bm+/c4NDKDL//uS/RqFfY3Nzlm0+/xPlzx/jsnz7K7m6Leq3GXzzyFCdPLPP9H7/JdjMiH9g8+s2XOLS6wIs/eYunv3+RUycP8fAXnsT3XXabHR597DnOnTnKs8+9Qak6RRT3+doTrzI/PcHLr1/hxZ+8zdLCNA8+/A2mJut8uL7Jlx/7NieOLPGb/+NBwkFIzs7z+Uee4szJQ3zjqRe48sE6ywfm+Mpjz7GyPMdP3/qASx9us3Jgkj//myeYKBe5tbnLVx77HqdPrvKlr36Xfj+iWMjzN48+zZFD8zzzw1d59/2PmZ2q8eBffoPZ6So/e/caP3tvjWNHFnn0m89jmSbNdpcnnvkJd5w+yj8/+xqunSOOIv7vP/2I0ydWeeyJH3D12i3mZuo88g/fZmGmwWtv/IyXLl7i9PFVHv7C4xSCIu1eyHMvvcXhgws8+Z2f0OkNMETKF7/6DEdXF/nB8z/lypWPmWxM8Md/9jWmpupcvnqNFy+8ybEjB/nKPz5LvhAghMMTT19gZWmGl1+/zNrNWwgMvvgPT3Pb4QO8cvEi126sMzvV4GuPP8fi7DSXP9rg9TffZ3lhhu/+8HkKRY/d5iYXXn+FuelZvvHkj1RkrBQ89Z0LHFmd5+VX3mZjq0WhGPD4t15gZWmei29d4fKVG9RrJZ7+3kvMTE/T7kS8c2WNWrXAU9/5MbZt0huEPPv8axxcnOXlV95G2C5ROOQnFy+zMD/JCy+9ztrNLeq1Cs8+9zqN2gTvXf2YC6++R6VS5rkf/xTTMtnaaXPxXy5Rb0zw4oWfMQgj+mHIy6+8Tb1e5tU3LrGz06JUyvPM919lulHhE+dvo9vtYf7qr9z16U6vi23bTNaq3HfnMZrtLkcOHWB5cYpur88D950kjtVK5M4zB9lrdzl/9jYKeZ8g53HvXSdotTqcPHmQhdk6nW6PT5w/QRInzM7UOXVsiXY35N67T+Fratq950/RbHc4c2KVhdlp2t0eZ04cpNfrkPNNTh45yN5ek0/cexLXMiiX89x9/jjb2zucOn6QA/NVJAn3nb+T3Z1dDJFy4ugy7166xPmzhwh8k8pEwLmzR9nZaXPHmSNMNibwcx73332GZqvNsaPLrByY4dKlK3zygfNsbG0R+CZ3nzvOXrPN+bOHKRV8LNPiF+47SRiGnDy6zNLyLFKmPHDPaYZRxPRUhZO3LdPsdDl9bJlyuUCQczh76iDhIOboyhyNShGZJJw9ucwgHDI7VWV5sU6r3eb44Xlsy8JzTI6uztDrDzh17CDVsgpDP3tqhV63z8rBKZYPzDAYDjl3ekWlNhiSw4dnubW5w9JCjXzOx/cszhxbpt3tcmR1humpOo7rcP7MKoVCgaNHVvCdlK2tLU4dO0Cv08N3LM6cOkgUR5w4tkQ5n6Pg5bnzzGEMaXPi8DILc9MI0+COU6sYhsH87CSLCzXarS63HZrFsAXTkzWWFqpIKTh5bIlC0ceybM6dPEgqDA4uzTDVKBOGQ24/ucowGlItBayuLtLr9Th9fJl84FIulzi0PM1g0Gdxvka5HGA7NmePLyMMk4JrUqvmaTU7rCzV8WyHRrXMyoEpBr0hxw4dwPMcJvIBR48s0u32Obo6Q72SV0rXwwt0u10a9QKL8w2SRHDq2BKClGq1xPLyLHESc2R1HscyybkORw7N0+v3OXRwHtsS9LpdbludQwiDqaky9WoJhODEsQOYQlKpFJmbrTEYDFhZnsN1TAqBz/xsnXDYYml+ksBzcZyUhfkFep0+c9NV6rUyqZQcPThHb9BjYiLP7FSNTrfL8sIUqYwwheTAwiRxnLC8OEMu5+E6FlONAt1uj7npBqViQJIkHFqeZRAO8TyLarnAzu4eczNVjBQmKnmmpqvEUczcbA3Pc8jlPeZna8TDmJmpKoXAw7AEB+ZU+3myXqJczCHTlMWFKWSaUCkVmGpUkVJy+sQC584cUhKGx774++nOzg4njx9icXYKz7N1BvWo62NkfXojI8ijiz4iI78jICHVLmfVQjZ04TdBZs5rjY7P3JwjfoQQpqaXp5mRasyeGPXBJWIEDdFAYlKlbRmrInW+stTtb6HhF+lYOZnKcZok+4ruIjNryYxtITLYTpLRuka0fpWqkWY8m1QmOilAiZUSJe9UhWshxhG9Iwq+7gKQCqTQhbQRh0Mfs+LPaAL9qJgn9AgmKftojz/nfh0BhQQqdmQUXJ8kuh9nyIz7ITAUa0e3MUf/nwo3ELpbkugWv8gkCvrss3iLdF8iAtk5j+hmMpM1jBI8VRtZ1aMSLRwctVfV1/o6j9y52e9rJzHq6zSNs/sq1XCxVI79NDLjm4wDzkbfG43aCGPAaNRSMt/VCHmiJBZau5LqSJCRUTjr3ijciNQwqCw0L0u6SEmTNGMmpbprJIShu3VJpjtKdTd1NDBjuhz7OkTKp5cpmrNBBKkFe1LrDJSQTuW5qLABQ3dSkywVIYPy6Hwpqa+H1JFDqUjVSe/LEx+ZHUUKOd9ldrrIsaPLGIaF+ME//0VPAK5lK+GWZeiHeIzHQ7eJTZFqERKZ41nR3Ud4CANzdENolqcQglS34YQ5ipvQMR06vTHNcJQiG58R90YYIvuGIFWKTdMYW6z2JdOph38MUh6xafZ/LXV4Flmbz0Cm4xv957CAwshuULE/HGIEb9LtanT7M01klhyIZnOkct/PjebklCxxMjsGfZMKnew3mjyVwmI8BuPPJos5+f/iPEj3JT+O8R3jsdqPQDSIZaxlBkIDt8nocAoWPZqsIJX6oRQjCYLInNDomxEtuIQRhCzN/j/2neNoUpb7xzKbpDQ8XmYIM9JEdRvTOCER2ug4mmx0Gx9j3+TNWLukhlpNQGk6ajGj41HG94hM9sWOZBPHOBpEjmlPaiw0qClNxkFm6l6SekLWOqURIWA0Se7TFmVpBVI/HOk4LT77vJSfu7czpEKqJvQk0ZOtofQ16ioZ4+RJOR6P/Wn06b70SEG6j0+sJu7RSyPVE4+UikudwabE6LhTvSgxMG0FWo/jhP8HNZk6AZ+00hoAAAAASUVORK5CYII=",
    "Arista 7050CX4-24D8": "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",
    "Arista 7050DX4-32S": "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",
    "Arista 7060DX5-32S": "iVBORw0KGgoAAAANSUhEUgAAARgAAAA1CAYAAACay/TQAACUNklEQVR42mT9Z7RlaXrXCf623/t476+PuDd8pK0sp6pKSSUHophuWCBgJED0AgmQ6NXNMA3TPdMLZnoN0xKIpoVwAglJ0CCpRTFSVcmUVJmVlS4iI8Pde8Nc7825x5+z/Z4P745TYjo/ZGaYfc/Z7n2f5+8e6e/+vf/nb968dfsHKuUyfuADEooiISERBCGyIhGGEQCKLCP+LyIMIiJAkkCWJYggiiIURSYIIqIoIiJC0zQODg75xX/zbygWC0hIDIZDWs0mG5tbNOo1Njc3mZ+f5/TsnGqlguM6+J6HZVkcHB7SqNc5PDpieXmZ7e1tlhYXubjo4LoOQRAyGA5p1GscHh/z6ssv8/DxY+q1Kjs7u6RTKSLAsW2uXrnCV3/7t/ne7/ke1tefUCoV2dvfp1DIY+gGo9GY5eXLPHr8mEa9wZOnT5hptThvn7OwsAgRdDod6rUaT58/o1DI8/TpM8qlIpIks7S0xHA4YmJPGA2HnJyccHn5Mu12m1defpm1tTUW5hc4ODwkCHxG4zFRGPHyyy9x//4DPvnGG9y5e5d6vcb29g6SLFMqFplMJty4cYOPPvqImzdu8PY336ZcLmPbNtVqlVQqxcVFh4WFBR4+eICZsHj29CkrK1eYTMYszC/guA6u66GqCo8ePqTRbNDpdPnc5z7H2toqiwtLnJwec3R8AkC/2+PGzZvs7e3yuc99jg8+eJ9kMsX+/j6SJJFMJlEUhU998lO8/c23ee3V13j/g/cxLZNOp0MikaBerTEaj7ly5Qrvv/8exVKJrY1NCsUijutweekSsizTvmhTLld4+OghmXSGs7NTPvXJT7O9s02j0WDQH9DpXmDbDvv7+9y+fZvzs3Nef/117t+/z9z8HFtbW/R6PWq1Gr1uj1defYW7d+7yxiff4P3338c0LWx7gud7zLRm6HQ6XL9+nQ/e/4CFhQXWnqxTLBQIgoBisUQykWB/f59Lly5x9+5d6vU6e/t7tFotJuMJ1VoV23Y4PT0ll8uys7XD0uUl9vcP+MTrr/Pg4SPqtSrD0Yhup0u+kGNvd4/Pf+ELvP/e+9x+6Rarj1fJ5fIMBn1sx6bRaHB8fMztW7f58MM73Lx5g7W1NQqFPMPhCFXVqNfrbG1tief00WPm5uZYW1tjdn4WQlBVFUVVuGi3aTQa3H/wgFs3b7K1tc3yyjLbW1sUSyXCIOTo6IiFhQUerz7m1VdfYfXxGjduXOfx41UKhQKSJBH6HvVmk/v3H/CpT77B2uoqjVaL8/NzyoUC550unU6XxcV5Np5vcuXqCu+8863oT/zJPyF98bu/2FY//elPpW3HpT/oE0URmqqwddDGdjwuz1W4+3gXzw9QFJmUZWDoKsOxw9h2SSUNZEni+LyPpioszZRo90bMN4pk0xa+H2AYBt1eh/X1VaqVKmEUYk9sVFXm+fMnmIbG49VHSDLs7OwwGvaZ2DZEEfl8nidP1rDtMVubm2iqwtr6GpqqcHx8jOM6BEFAv9/H9xyePX9GtVxife0x9mTE9vY2iUSCKALPc8lmM5yfnXJx0ebR4wfMzc3x9OlT5ufnSSSSnJ+fkUxaPH78kDDwWV9fRVUVjo+PCIMAWZE5Pj6m3++wurbG1atX2d7exHEm9Ho9ZFmi2+0ysSdoqsru7ja5XJbHq48pl0qsra3hei5bm1vouo5u6BweHZJMJXj46AGtVpMHD+/juDaPVx+TSCTo9TpcXFyQy2V58OA+mUya1bVVqhdVxuMxZ+dnpNNp+r0eqqpw7/49VpZXeP78GYmExfHJibjmtk2306VQKPDg4QOG4xF7e3ssLCzw6NFjJFlme2uLw6MjZEmm2+0yMzfDxx/fY3FxkXv3PqbZarK1uUUQhixfvszOzjYzMzPc/eguyWSSux/dpVQqcXh4yExrhiiM2N4R9+Cje/e4du0aH9+/z7Vr1xiOhviej5Ww2N7eptlscv/+fW7cuMGTp0/JZLNsbW3jui7tizYX7QtS6RQ7uzs0mw0ePHpIo1ln7ckaru9ysH+A7dgEYcDW1haZbIa19TVm52Z59vwZMzMzHB4eEoYhQRBwcnxCsVRkY3ODQrHA5sYGnU6HMAzoD/oUCgV29nZIpVM8ef4E27PZ2d5FVmTa521c3yUIAnZ2dqhVazzfeo5maGxtbzE7O8Ph0T62M2Y8GnHR6dAflTg42Gdvf5ft3S2qtQrbu9uUJyP6/T62bZNKp9jb32N2dpbt3S3yhRzbu9v4oY/jOPi+j6RIHBztk8ml2dndJpNLc9Fpk81nGI1G6JqGoqicnJxiJUw6nQu6vS4Hh/sk0wmOTo4IogAi6PY7XHQynJwec3xyzOHRAdVahaPjQzRdwfE8TFWl2+1weHzA6dkptmMznoxoX5yjKTLn7TM63Q5W0uC0fUJ9UKc/6OI4NkHgoSaSScIIfN9HVRR6wwlfffsxw7HDf/k9L/Ns95RSLsXecQdVkcmkTAZjh3zaYjRxWVmosnXQRpFldo86fO2dVT7z8hJf/PRVJEkiiiIs0+L6tevk8jmiKMJ1XZqNJp7rMTMzw+1bt5mbmyOVTFEqlXBdF4BUKoWiKJTLZZKpFHNzcyiKwszsDOl0GtfzCIOAyWRCtVrFMA3q9TrXr12nUqmQsBIYhkFERBiG1Oo1Go0GhUKBWzdvUSwWMQ1THGsYlIpFGo0GN67fYGZmBt/3mZubI5/PUSwWkSWZXDZHoVBAlhXxdzwf0zRpNBrMzc1RKpWwHRtFVshksszNzyHLMo16natXr1Kr1zANE0VVUFWVYqFIq9ViPBpTrVa5cf0GjWYDCQnTNEll0tQGQ/FnN25Qr9d56fZLZLNZHMchm8timRbjyZh6vc7NGzdoNJo4jsP8wjyFYpHZmVk8z2NYGpJKpZiMx1RqVYqFIpVqhStXrtBoNFAVlVw+j4TEeDKmUW9w8+ZNSuUS169fp1DIk0wkCcOQRrNBKiXu180bN2k0Gty6dYt0Kk25VKZcLlEslbAsi2q1yq2bt2jNtPBcj1arheM4FAoFdEPH0A2KpSKe5zE3O4uqKMzOzGEa4rrmcjkq5QqmaWIaJrOzc0QRVKs1rl29Rq1WI5VM4XoumUyGVDJFs9nkxo0b02taLBbJZrNEUUSpWKKQL1Cr1bh+/TqtVoubN2+SSqWIoohsLksqlULXdBrNBrdu3qJSrpDNZGk0GlTKFcrlMmEYkkwmyeVyaJpGa6ZFKp2m3qhPFwzHdhgMB6TTaQq5PI16g+vXrtNsNrEdm0wmw2QywXVcZmZmUGWVWr3GzRs3mZ2dJYoiisUCnu8TBqG4ZvFnOY7D3OwckiRRrVRxHAdVVZFliUKhQKPRIAhCZmZmiKKIRqNBwkqQy+XwPI9isUilUiYIAmZnZyFC3CPPo1Kp4Ac+o36fSqXCrVu3qNZquI5DrVZDUzUUWSaRTjOZTCgWiySsBK1mg5deepkgCPi1X/911CgMiaIISZIIwpA7j3ZIWjqzjQIfPNxBliRyaYunOyfcuNTA9QLqpSy94YTtgzatao5WNcdJe8DReZ/Xrs8yGNk82T7h6kIVSZIYj8fc+egujVqdMAwZT8a4rsu9j+/hBz7vf/A+E3vC9vY2s7OzTCYTiCCfz/Po8SPm5+fZ2NjAdz1W11YJwpDjoyNsx8b3fQb9AYtLizx9+pRsNstH9z5iYX6Bza1NkokkURTh+R6qorK7u8vZ2Rkf3vmQ+bl51p+ss7i4SDKZ5PT0FCS4c/cOE3vChx9+yMSecHR0RKvVQlEUDg8PaTaaPHr8iPFkwt27d2g0m3S7XaIIut0O4/EYVVXZ3trGcR0ePXpELp/j4/sfc2l0ic3NTTRNwzAMDg8OUTWVO3fvUG/U+ejeRwxHQx49fEgyfoHb7QsymTR3794lkUzw3vvvUa2KCqZaqZJOp+n1e8iyzJ27d1kZDnnvvXcZT8acnJzgeR6O7XBxcUG+kOfd995lcWmJ/f195ubmePDgAZIssbm5OW2Ber0e5VKZO3fusLi4xL17H9FoNtnc3CQIAlYGK+xsbzM/P8/du3dIplJ88MEHlMplDuKfOzszy9b2Fql0ig/vfMhoPOKD99/n6rVrjEYjmo0GViLB1uYWrVaLDz78gMlkwqNHj5Akmc3NDRzH5vy8Pa3U1tfWUFSFBw8eUKlWuHfvHpcuX2Jvbw/HcSiXy2xubmJaJnfu3qFarXL33l1mZ2bZ398nDMULd3JyQiqd4u5Hd1E1jQ8+/IBCsUAUhFSrNQqFAhubG0REfPDBB8zPz7Ozvc3l5WXOz89ZmJ/HDwK2t7ep1Wo8evSI68PrbG1tkc1muP/gPoVCgdFoxMXFBaVSif39fdLpNHc/uotu6Ny7d49yuUy/32cymWA7NmtrayTTST688yFBGPDgwQNmZmZEte4FNJtNnj57iuM63LlzB9/zefjwIYtLi6KC0Q2UuNIej8d8fP9j/ED8neFoyM7OzvTZ6Q/6LC0scfeju4REPHzwgIiIjz76iPn5eVzXJWmYBFHE++9/gGWaHB0dERKxs7NDs97g4OiITrfD7Owsm5ubhFHIR/c+wvd9nm88RyX+R5LA9QKa1Tyv31zAMlQ298/xvIAbyw1m6nlcL0BTFSa2h2GoVIoZmrUcnhdg6Bq3V1rUyxlO2wPGtksYRkhyhGEYrCwvUywWiaIIx3Go1+uMRiMajQbXrl1jdnYWXdeplCu4ngsRpNIpfN+jVquj6zrNVhM/8Gk2G5imged5BEHAeDSm0WggyzLVapXl5WVqtRqqpmIaJhERQRBQrpSpVqtks1muXL1CpVxBkiXq9TqmaZJOZ6hVa1xZucJMa4bRaMTs7CypVIpyqYysyFiWRTnGq2ZnZ3AmYzLpNG6lSqvVJJvN4DgOiqJgWea0EqpWqly6dIlWs4Usy6iqiqZpZNIZGvUGV1auUCqWWF5enh5jmibZbJZCvkCpXGZ5ZZlaVey6uVwOx3bI5XMkE0lGoxHlcpmVlRVmZ2bp9fvMzc2RzWRpNpq4rks2myWVTnHt+nWajSaZTIZSucTi0iLVapUwCEkmEiBJjEYjqtUKK1eukC/kuby8TKlUQtM0wjBkdmYGwzDIF/KsXLlCrVrl6tWrZDNZshlxHSuVCrIiUy6VuHLlCrMzswyHQ+bm5nAch2KxiGEYSJJEpVxhOBwyOztLEIgXSZIl6o0GiWSSbC5LwrKQZZlmszldTC4vX6bZbGLoBo7rkM/l0XWder3OlZUVSuUSK8srlMtlElaCMAqpVCqk02kq5QorKyvUazWuXr1KOp0mCiMKhQLpTBokqFVrXLt6lWq1RsKyaM3MkM/nqdVqBEGApmoUCkWiKGR+bh5DN6hWq1xaukQ6k8a2bcrlsqisUilqtRorV1ao1+ssX14mm8syHo9xHIdWs0UQBFQrVa5euUKr2cKxHSqVCp4vnvVSqUyEqEZWVlZotVq4nku9LqomVdVQFJl0Ok2z1WIymdBstqYVkq7r5PN5bNtmPBZV6ngyptVs4joOjUaD0WhErVrD931ce0K5VObatatUKlU826FSqQKQMAxUY5bSqESlUkFVVRp18b1mZmdQNfXbC0wUgaYqrCxUiaKI04sBhqaSSZnsHXUE4BNGuF5AwtIxdJVM2iQMI4IwpFZMM7JdJrZHtZQhihA3QJZxbLEy1+uigplMJqiKytr6Opqm8fDRI2RZZmtri9FohG07UwxmdXWN8WTCxsYGmqaztraGZVocHR9h26KC6ff7OK7D06dPadQbrK+vY9s2W1tbMQYjKphMOsPR0RHdbpfVx6uM5kasr68zmUymFUwikeDx2ipI8PDhQ2RJ5vD4kNFohKKoHB4eMBmPub+6ymVFY/HpBhNDpzCeUEhn+OjkGG8yRlFVtra2UDWNx48f02q2ePr0KWEY/ucVzOEh2VyW1bVVLl26xOraGlEY8fjxY5KpJKVSmYt2m1q9xtraGpVyhYcPH1KtVBiNRVuVyWTo9Xokk0lW19YIw5AH9++jyGInUzUV23boxBXM/QcPGI1G7O/vc/3aNZ49e0YqmWJzc5O9/T1kWWAw8/PzrK6ucvPmTdbX12k2m2xsbExxjO3tba5fu87j1VUq5SqPHz+e7tSDwQDHcdjc3qJaFX8G8ODBA4IgYDgc0mq2sBIWm5ubTCYTHj56iCzLPHr8mHQ6zcbzDRRF4fzsXFQwqRSr62tkMhlWV1dZXFhk/ck6YRCyu7eL7dhUyhU2NzcplUqsrq2xuLjE+to6o5HAnKIoYjQacXx8TLVSZXV1lWwmy+PHjykUCqKVrsUVzMYGlmnx6NFjBkOx+3u+z+nZGa7r4vs+W1tb1Ot1Hj16RBhEbG5t0mg2ePLsKcVpBdOmWBTXpVarsba6Rj6XZ219jXK5zKA/YDwZI8syT9afiOu1uophmqyurTIcDacYzGQy4cnTpyiKwurqKoaus7q2huM4cQWjoygCoySC1bVVTNNgbX2NMAq/XcGMxgwGA3zP5/Hjx1iWxerqKolEgrW1NdG2uS4py0JSFB49ekSpWOLs/AxJVdnZ2abVaLJ/eECn02EyHrO5tYVpWqytrqFrOlvbW2KBiSLB+gB4foAE9PoT1jaPGE5cZEnC9Xx8P6BRzTGxPUCiUkgxGNl0BxMMXaXTH/Mdr15ieb6K5/vIkkQQBBimyZUrVygWi4RhiOOIFXdluEyz0eT61WvMzc2h6zrVShXXdYmiiHQ6je/71Oo1dF1nZmaGMN7dTNPE9VwCP2A8HtNsfruCWVleoVaroWs6hmlAFBEEIZVqhVqtRjab5eqVq1SqFWRJptFoYFommXSaWq3KlRWx245HY+bm50ilU5TLZRRZIWElKJeLTPyAar3O/uNVvnqwz+cTaa5Xq8xbJoFto6gqlmkx25rF93yq1SqXL12m1WohywqqqqBpOpl0hvqLCqZc4sryCjMzM3ieh2mZ5LI5SoUC5VKZKytXqNVqXLt2nUI+j+3Y5PMCFxkOh1Qqlfi7z9C70WdhYSGuYBq4nk8umyWTyXDzxg2azSbZbJZSuczS4iWq1SpBEJBIJpEkidFwOK3mCvkCy5eXKZXL6JpO8KKC0Q0KhQJXV65Qr9e4duUamVyGbDZLrVanWikLDK1U4urVa8zNzjEcDpmfm8e2bUqlEoZpIksy5UqZ0XDE7NwsfhDQaraQkGnUGyQTSbK5XFzBKLRaM7iOS7lcZvnSMq2ZFrqh47ke2VwWXTeo1+rTa7q8vEylWsFKJCCMKFfKZNKZ6fWqN+pcu3qVdDpLGIUU8nky2QwSUny9r1Kt1UgmkrRmWuRyOeq1uthANU1U5mHE/Pw8hmFQrdS4vHSZTCaNHVcA2WyWdDojvtfyFeq1OivLy+RyOUajuIJptQiDkEq5wtUrV5n5Q+fp++L9K5dLRBE0m02uXLlCa2YG1/No1BuigtFUZFkhk87QarWw7QnNVgvHcZlpzaDrBvl8HucPVTCTyUQ8c65Hs9FkPBpTq9dwHAd3YlMqlrh+7TrVWhXPdahVBfSRMA3m9QXK5QqVagVN02k2GwyuXmFmZgZFUVGluFwP/xAWE4YRzVqBUiGN4/oA+EGAIsukkyajsYsiSyBJBGFAEETIssBwMkkLSZLR41Ja13Vc12V9fZ1GvTGtYHRd4+mzp5jxKq1qKtvb29i2g21PiMIXLNITHMfh+cZzTNPkyZMnJJIJjo7+8wrG932ePHlCqyUqBdd1/3MMxvPIZjMcnxzT6/VYX19jYk9YW1vDcZ1pBZNKp3nyZB1VVXi8+hhVUzk6OppWXYeHh9j2mKfra2QliWXHRVVUSq7Lo6Mjds5Pcceigtne3sYwDdbX1pmdEWxGRPR/wGDyhTzrT9ZZXlnm6dMnSLLE+vp6XMGUaLfb1OsNnjxZp1qrsrb6mEq1KkrZWo1MOk231yMdf3eIWFt9jK5pHJ8coxs6ru3Q7lxQyBdYffwY27bZ29vj5s2bbG4+J5NNs7Ozw97eLlJcwSwuLfLkyTovvfQSz549ZTQesbmxSRgGRFHIzvYON2/d5MmTdWr1Gqvrq5TLZfb39xmNRniey/bWFrV6jfW1VRRZZvXx42kVMZlMSCQsNje3cB13+hysra2Sy2bZ2HiOpqmcn59zfn5OKp1ifXWNXD7H+vo6S0tLPHv+DAnY2dvFdVxK5RKbm5tUymWePFnn0qVLPH36lIk9YX9/nyiMmNgTjo+OqdVrPHnyRFTKa2sUC0WCMJhWMJsbmyQSCVbXRBW9vb2NH/icn5/je/6UsRoMBjxefQwSAk+aabGx8YxCochoNKJ90Z5Wdo1GnfWn6xRKBZ48fUqlUpliMJqm8fTpU1Gtrq9hJSzW19cZjUe4jqiYXMfh2bOnaJrK+vo6lmnxZP0JvuczHA0x/hAGI8sy6+tPsBIJnjx9AhLs7uxSrYlnZzAYEIYhq2urJFNJ1p+siyp4dZXBcEAikSSbStLtdXn48CHlconzs3MUVWVzc4u5ZpOdgwMuOheMJuLZMEyDR48eoakamxubqL1ul4uLDkEUoWkqjuNgGAa+5wkqVQpQFIVIhSj08d0JUuSgqyau65AwTFzXRVFUga+M+5y7YzzXwTBNztvnBEHAyy+/TC6XgyjCcd0pzjA/N89oNGJ+fp5MJkO5XP42i5RMoWqqADIzaRYXFtFUjfn5ebLZLK7rEoQhk/GYWq2GlbBoNVvcvHWTalWAn4ZpEEWijavPzNBotshXytx46SXqlTJWwqJeq2MaJuVymVarxUsvvcTsjMACFuYXKBZLlEpFFFkml89RLBSRVZW5+Xm0icOlBx+TnF8ktbSIlM/iex6yLFMoFFiYX0BVVcFUjG4ITCGRmGIwlUqFudk5JpMJtVqNW7dvTwFl0zTJZDIMBgMazQa3X3qJmdYMr7z6KvmcqGByuRwJK8FoPIr/zm1ajRa+57GwsEi5UmZ+bh7P9yj3K6TSKWxnQq1Wp1IRFd2169dpNVuoqkqhWABgNB4x05rh9ksvUa6UuXlLsG7pdJooiqYVULlcFt9rZoZXXn6FTDZDtVqlUhFMSyKRoF6r89LLLzM7OxtjV7M4tkOhWMAwDEzTolQq4QUe8/PzaJrG/MI8pmXSarXIF/JUa1Us0yKZTLK4uIgsy9QbdW7evEm9XieVSYtNJJMlm80yOzfLaDyi3qhz6/YtyqUyhUJBsEilEqVSiUa9wUsvv8Tc3ByvvPLKlEXK5/Kk02lM06QVn1e1WqVQKNBsNqnVatSqNcIwJJVKkc/nMQyDudk5stlsXDnYZNIZbNtmMBwIvKtUYmZmRjxfs7OCBcxmmUwmOI7D7Mwsqq7RbDZ5+eWXWVxcRJIkyuUynucRBiHFYhHd1KfM4OLCIrIiU6vV/hCLJFMql2k1W0RELMwvIEnSFHfL5XLYjo09tqnVaoRRyMLiIkgSS5eWKJaK5HI58tkc648eUa1U+WNf+hLZXAlV1sR71Gjguy6zi4vYjk02k+XS0iWazSa5XJ6ZVou5uTnU3/7t32Fja4uTkyMqlSoff/wxN2/e5Mn6ExaXFjk4OKBcruC5Lr1+n4WFee7cucunPvlJ7n18j9defY2P7n0kqEfXpdNus7yywqNHj/jMpz/DW2+/xWuvvcbu7i6j0YgoirAnE0zDZGdnh4QlenDDNNjb28X3BecfRRHZbJbt7e1pv59MJtne3iKdTnFyKjj5IAgZDgZEUcT2ttBl7OzsEEURuzu7WJZJKIE2mnADmexgQGpjE3l3lz3fZ2tjkzAISSQStM/PyWQyovIwDMFGmCanJ6cEvj/Vwfiez+72FrKm4R7s8Ve0BD+3v0vr+IhRu83YtlEUhb29PSzLYmtri9mZWXZ2d5FVhd3dXTRNQ9d1jo+PKRaLbG9tcfnyZXZ2dlA1barhKRQKdC4uaDQagrGoVtnc3KRcLjMejyiXK6SSKQbDPtlMhu3tHVRFZWNjE8M0Ba5kJXBdh06nQy6fF4yc53N4dMSNGzfY39snm81ydHjI4eEhSBL9QZ9Li5fY2d7m9u3b7O7u4LoO29s7RGGILMvs7+9z48YNtre2qNcbbG1tki8UODk+Fm1uGLG/t0+j3mB7S2h/Njc3UWSZyUSI3kzTZH9/nyAIptd7a2uLQr7A3t4epmHSbrdpd9qkkik2Np5TKBTY2tpiaWmR3d1dFFnm8PAQx3UpFotTnGF7e5tLS5fY3tnG8zxxboDneZyenk5Fay9+Xi6XIwxD7MmEiZ1nf3+fVCrF1tYWfuCzt7eHJElcXFwAAmPc29tjMpmwubmJqgqWcmZmhv29PfL5AqPxiG63Sz6fFwxks8nW1halUomdnR2KxSKj0ZDJZIJhGOzu7FCvie+VTqfZ3hZaIM/zCPwA3/fY3d2dXqdkIsn21hZRFE2rIEVROD09RVd1tra2SCWTbG9voygKBwcHTCYTxuMxo+FIVF1bW2SzWTafb7C4sMBf/At/kYltMxz0eXDvHvlCnk989gu8+9E6yZyLahV5/dWXebK2yu2XXsG0TEzDQJIUIiJMXSWMIlzPR+0NBpRKJRKJBPl8Dtdxp2h4rVYjl8uRzWTxfR/btqnXRe+5GK94s3OzIEnkslmCMGQ4HFKrVqZo/+3btwUPH0bk8nl8z5uWoWLXbXF5ucNMawbDMCkU8qKCiSCZTOJ5HvV6HcMwqdfqEEGtJn4dBCGu54g+tVIBoFQssbCwQLVSFTx9IkkoyySOj9HefZ+d40MOL/p85tZNnszOYioqpXIZTddIJkVLsrS0RK1W5/LykGajiWWJHVZRFIEHZLNEYUi51SLyfG6PPG7iYTQa+Mk0w/EQRVUxDKHL8VyPcrnMpaVLlCtlNFVDkkRrms3mqFSqU5ZmYWGeelXoDUzTJJ1JUygUqJQrLC4uUq83WVlZIZvJ4nkeqXSKVDLNcDSgWCyytLhIo95gsNwXu0k2R6PRxHYm5HIFTMvgyspVarU6yVSKSrnK3PwcpWIR3/cxTFNgMKMRpVKJxaUlspks83MLFEtFdN3E911mWnMYukEul+PKlauUyyUuL6+QzWRIp1KUKxVKpRKSLJHP57l8eVkwc8Mh8wuLjMcjCoUCCSsBQKVcZTyZiOvleVSrgmwoV8okkymhNdE1oU1pNIRWo1xlfn6eZlNgC47rkMlkUVWVcqnM4uIi5UqFy0uXKRQKpJJpPN+lUq6QTqUpFossL69QrVRZWloilUpBBLlcjmRKtNblcpmlS0tUKhVMQ1RUmYzAzXzfQ1U1SqUSURQxNzeHaVoUi0Vm5+ZIp9I4jkM+nyeXy5FOxczVi89cXCJfyNPvDwiCQFQFvk+pWBTPYLUaa7xq+J6H54tzjoB6rcF4eUytXhf4YqXEeDJBUzVkWSaZSFKtVXE8l3q9GXcNs+iaTr6Qx3FcRqMhjXpzqiNbvLQ4ZZjef+9dHj54QGumhaLp/P7v/Q79wRAV2Buc4w2OuDg/Z/3JEywrwRuffIPdk0e0akscXSRJWDrXF/NIf+bP/Z/f6vZ63zEaCZDw3r17/NAP/RDf9Z3fFWMlOpIkIUlSXO51KOTL9Ac9ZEUmaaVpd07JZ4s4jtiV8rkSkgQgTXGd0XjIZDKkkK9w0T3H0M1Y5dsmny0zHg9Akshm8tNjoiiK8YAL/MClkCtz3j4mYaVRFIXReEAuW6I/uMAwDFIJAdJNj5VkLjqnhJJM3Uzy4d/7e/w3b7/FX75+gx/8O38LrT5Lp31EOpPHNBIQhQRhKCwOihZbJ0BRZEDCcWyG4y65bJl+9wLVNLBCmd7jB+Su32KIj++4FArlmPr/Q+c/GuK4Y3K5Mmfnx6SSKTRV56J7TqlQZTTpAxLZ9B86fyIkJDqdNhEBuVyJ4+MDctkCkiwxHPYp5iv0Bm1MI4FlJf/zaydJnJ2foKoqmXSWs/MTCoUKrjsmCHxSyTzn7WPyuQK6bhJF0RSL0zQNz/OQJAlZkZGQcD2H4ahHLlPionOGZVmoisFZ+5h6tclw1MfzAorFMkQRknCQICEzGg1w/QnZdJHTsyMymRyyLNPptqmUGwyGHWRJIZPOTc87isR/250zZEVcm8PjA4r5EhERw9GAUqFCt3+OZSaxzBRRFIIEsaeFs/MTDMMgmUjRvjijWKgwsYeEUUjSzHDROyWbKWLoxvT8QUjuvbjVlWUJkLGdsXjm0kW6/TaWaSHLGt1+m3KpxmDQjReo4v/hPgxHfTzfJZ3M0emdkU5miYDBsEe5UKXTb6OqOpmUEAOKiyeuXrd3jqLIWGaG84tjSoUKjmvjODb5bIlO/wzLTJH4/7v/EREXnTNM3cIwTDq9cwq5CqPxQGzgiRSd/jnZdAFdM6ZyDoA/+Prvs7v/nMs3S1RKV4jcFMN+m0G3SyqbYWFugbfe+02QAzrHEa+/8TonvTXqpSV2z1KRZWjSp2832qqqqGiqhqqoKLKCqijf/oJhxIMHD7i4uEDTdc7aR3RH28xUbrF//BTLMilkZ9ncv0ujeBXb7zK2+7TKN9B0lSAQjJSq6RydbDO0j1lsvcrT7btkkgWy6RL7p6tUMlexwxOCIKJWWEFRRPkpyTKaqvN08z6RNGFx5mXWN98jm2iQyaY57WxTSi3TnWyTSuQpZuYII58oisSDISk8370n+tDaFVzD5iUzSVWZ8PWPfpdQrnNwco/Z1lVSZgXfd8jnC5imGUvSW0RhyHn7HFXRuOieMPYPKSZX2Dl8TLVWQSPP2tZ7XO20GdlnXFy0uTz/GooqE/gByKApOnuHG8jGkGr2Gh+vvcX87BKmnuHJ1h2Wmp/Al88Z9hxatStIckTgC2uCqmh8/Og98mWDVvkGdx79LjPVq+TyKbb21mgUbuOwh6HmyCbqRFJAFEbIsoIsK9x7/BbJVJLFmes8evZN6rmbaAmbMHLBKXLSf8jl+ZdQpQxB6FEuldE0je3tLeYXFnFsm/P2OZqq0x+3sYMjLBbYO3nA4sIik4HK6sbbvH77e+kMdzk+anNz5VMgh4RBiCxJyLLK/tEGiUxAQpnjwdPfZ+XSbRRJ49GT97l95TuZBAf0LhzmW9cJI58gCFBVFQmFjx+9Q62Rp5hZ5MOHv8Py/GskUgqb209YaLzM0N9BI0sh1yQKA8IoErhhBA/Wv0kxX6JWnmN1431mKy8TKj1830UNi3QmT2mUrmKZWYLAp1QsIUkyB4f7zM7MYTs23U4HVdXoDU/ojQ/JGUuc9p9SKTawxxKH54+5fvmzHJ4+w7E9lhdfIQwDAj9AURWIZI7PN5E1m4TaYu/kPjP1FVzP4+DkGdcvfZbD81UIDGYbVwjD+BlWZAI/4tnOxxSLGRJqjed7H3Jp/hVsp89Z+4jF5kscd1cx1SLV8hxB4MeeQIXAD3i6fYdSsYalZ9k+eMCl2dfoDg/wvIC0VaM9fEops0QuU8YPPKqVKpcvXyaZSvHKy68yd6lCtxvy5OkmzmSI6zicnp9jmRbZVIn5xTn2Um2B16pJDD1BtZhC1xRUVUP6cz/8I28NhoPvGI/HlEtl7t+/z5/4E3+CN998k8FgwE/91E9xfnZGJpNBURU8b4yhJRlOBliWiWv7RHjIko6qKSBFSKEam+scEokEnu9jWSa2PcLQk7jeBEkWL08YeRCqhJEQ5umaBcBwOCSZSOAHAaomY9tjdD2BYchMJh66puH6NlGgoJsyUQhECrIs0e/3Sacz2I5DIqFDFDHyQm77HnM7R+zPNXiW0HA80HUJIpkwFLjD0qXLvPmFN/l3/9u/5Y/+kR9kY3ODD95/j0K+QBSFBKGLLBl0+21KxQL93ghNlzE0C9u1URSJwJdwXY8g8Ekmk0QRKIrEaNwnncozGvdIpdJIkoLtjNAUC9cbI0sKoBBGoQDZNR0/CFFUmNhjsukCfmgTBBJJy6R9cY6hp9AMCRkFXbdwHJteX2hibNsmlxNUv2FYhKHL4cEptUYV13ORQoVkSsdxfGRJ5aJzwWuvvsYnP/kpfv5f/zw/8sN/no8/vscHH7xPqVjC9RwkOcC1odM7Y6bZ4vSsTTabRFVMBqMuumYwHjlToDiXzaIbBp7n4vk2CTPLcNyhmC/hBwHdfpuUlcN2RuiaiarqeL5HFIaAxMS2SSZMgtAjaWXxIxvPDTEMnXb7lHSqSCR56KqBomiMJ2PG4xEJK4kfBKRSBq7nCxIi9Oh0hlRrJcajEZpmoekS46GNomgMR0Nee+11Vlau8OX/9GX+5H/5J/jwzh1WHz0im8viuDZh5BEFKl4woZDL0+uPSCQ0wkDG8SaxadZG1wR7alpmbBz2QIqQJQ3XH5NOZbFtG893scw0tj3AMpMEIfiex3gyxjIFI6toQqimKgZB5OA6AbqmMrEnpJNZ/NBBVw38IGRi24RhhJWwIAJVjYgiCIMIP3Bw3YhcLk2/3yeZSOO4Y6JQQtdNOt0OC4uL/PiP/TgPHz6gVi5xdHzGV7/220wmIwxdJ5VI0h8OMQwhsXjzO79IGPkgRxx3HtGsLHPYzkbplCHdXMq31TCKcByX8XiMbdvChOb70yoGCVzX5eBgH13TcRwX3egJsNZwcD2XKARJRuzYkoQkCSDt+rXrjMdjtre2hQdmYmNafRRJQYpp7jCIiKIAx3GQJAlFkTEMk5deeomNjQ0ODg6wLIvJxMZKjDENE88XpbvrOIRxGS1JEAQ+lWqNVqvF2toanudhGCZSFOHLMpuSzKcUhff7IzY7PnoYICsqkgRhFOJ6HhKQsCyCIEDXNbIZoczd291FUVVx/rqGYzu4tsClRN/bn9LvfhgQ+D6feP0Ner2uoBMTCQb9AcOMTeD5DAcOkgS+5yMrfUajMYah4/se+VyOL3z+C7zzrW9xeHREMpFgMBwyGTpISIREdCWJ0WiMbkxiRak4j1y+QLlY4tnzZwRhiD2e4Hk+mq6hKSqj0YjDgxM810XTVDodnSDwY3tAF1mRSSQShEGArmnMzszy/rvfYnt7GwkJz/dQFJnRaAzhEePxCMcWrN9gMCBpJRhNxsiSxMqVFTqdLns7OyiKymg0JpMZ47kezjggCAPxzGlCJJZKJvF9j0qlxmc+82l+53d/l9PTEzIZwbSk0+Ppd5AkifFwhD32xUZimgRBQK5QoJAvsrW1SRhGDKwEjuuiqWJHHY2HBJ44xjB0iMTPgwjPExuCaeiEYYBu6NRrVe7dvcP+Xp8gDPF8H0PX8Dwfe+ThuDaDvoHvu7iui2VaDIYDioUCb7zxST6+f5+z01NkRcH3AyzTwPd8xgMHNwZuFXWAY9skkkJkmsvlKJcq7Oxs43ueaFf9QBAWQYjni9bNcz0G5hjf8zFMHXsyoVQqUymV2NjcIPB9VE2PP0NGiiS8wGcymjAaj7Cscaw6lwnDEMMwseLrOBwM2B4PWV17wttv/wGvvPwK2UwWVZFhGDEaDXFtm8GgS/uizeLSEpZWQJISXLtUQVVlkFRU0xRgbj6mX/uDPplsRvSiksAR2u02vX5viit4nseP/ZUf4+VXXsZzPRRV4e6du/zyr/wytm0jybIwJc7McH7e5vjkBLXdxgs8VpZX+JEf+RFBGYYRw9GQf/Ev/yW7z5+hGwa+75NIJLh0aYnD42MOj49QFAVFUfhTX/xTfPYzn8X3fTRd55vf/Ca//Mu/LKomxPfyggDD0NmJ2YUIiMKAH/qhP8t3fu5zLO/sU6yU+Pd3PuTX/u2vvGjVURSFMAzjfnnI8+fP6ff7yLLM2dmZcEsrCmEQkMlk+PM/8udptpoEvtCE/Muf/1fs7e2gGUZc3ioMhwNOTk84ONhH1XXBPEQBf/Ev/ugUVA2jiH/6z/4ph0f76LqB67rYjsNwNOLo5ITjk2NUVcX3Pa7fuMH3fPGL+L6PrmsMBkP+2T//55yenaAqKp7jUG+1qFer7B8coOs6Z6en+L7P4qVL/Okf+tMkLAtJlhmNRvzsz/4sZ6enqJoABl3bRpaV6fmPJmNkWeLw6Iiz83M0TSMIAizL4id/4ifJZrOiZ5fgV/7tv+Xg8EC0NTFuM2vPcXJ2yv7ODpquExExcWx+8id+gnQ6DUTYts0/+bl/yunZCe2Oiue4BET0ul2OT465uLjgotMhCAO+eP2LvPnmm4RhiKqqDIdDfvaf/CydTgdZlvFdl6bnUQkCDg4PkWWZKIrwPY+Vq1f5s3/2z6KqKqqi0u12+Sc/93NcXLTRVCFoD+PWutfvi/MfjQA4PD5mMOgL4WgU8sf+6B/jM5/5DF4s5Thvn/NzP/dz9Ho9FFUhDIUUYzAYcHh0xNHhAZquEQH/xR//L3j99ddwXRdN07l//z6/+mu/ShBHpQRBgO26GIbB8ekJjm2L51NV+Us/+qMsLizgBwGyJPMbv/EbfOu9d9FiHVsQBESShCRL7O3v4/s+URii6Rp/5s/8Oa5dvRpLShTeevstvva1ryEJsJQwDCkWROwIEkiywqDfI5PJMNOaIZVOUSgWUCSJwWiIYWTRNY1yuczZ+Tm2PcGNLugPk8haGVWVCT0bNQgCzs7OabfbjEYjHj9e5bXXXo9vzrdfvnQ6jaGLkt3zXD73+c/znW++yVe+8lXefPMLJBNJfusrX8G2bWRZZmJPhGJVU8lksySTSfqDHjMzs3zpj32Jvb09xuMx333zu/naV7/G/t4eyWQSIiHqk2UZQ9fJ5fMCG1IVPvuZz/J93/d9fPVrX+ULn/88siTz5S9/eYqH6YaOpmnIioJlWZimRRSFaKrKpz71Kb74/d/Pv//FX+S7v+OzfE5T+cqX/yOmYeB6ouUaDIcApNNpli8vk8vmGA2HaKo2dcy+8FH9mT/zQwwGQ7a2tvniF7+b3/v673N0dEg6nWEyGRMEIYoioygqhaJg6S66Heq1OrMzMywuLgqj5nDI0uIS7bNzMtkMrit2LFmW0XSNbC6HaRgMBkNu3bzJrVu3mJ2d4eP7D0inU3z1a1/j4qJNoVBAUdTpZ5qmiWUlYkwN6rU683PzLC8v89FHH/GJ1z/Bb/3WbwpqU9fRNZ3Tk+Pp+V9eXiaVSDLs94VatVBEVmRcx6XRbHL58mXq9TqSJHF8fEyjXufs5JQwChlPJiiyjCzJyLJMrdFAlhXa7XNqtRr1ep1qrcp4PCEb60P6/T6pVBLHcdEUIXfXNHH/VUXFtie8/vrrLC8vk8/nRYmfTPLrv/G/MxyOKBYL+DFu9UJDpKoauq4RBiGtZpOlpUs0Gw0hG5idZXFhAc9zMXSdKG7LAbLZLMuXl0ml0xwfH6FpgpXyg4AwDHjzzTep1WpC2tBu8/LLL/Orv/prqIoKkoTve5iGKe6hplEql6dq+c98+tPU6oLBu2i3GQwGFArF2Eekiool1rLomk4ymSQMQgzD4Auf/wKGaTIaDpFlmcXFRR6tPkZV1bi7cFBi4axpmaiKhixJWAmLT77xBolEgmazyWA4pN/v89577xGFEaqq4HoesiIDAnvNZDJUygX+4Pe/wXn7nHqzQefiAns8ZjwZE0Xg2BPOzs5EEkI6yWBSJJsqkk0ZyLJE0lRQFUWNLehlcnmhAyiVijGaLtiETCbN2fkZTizh9zwPx3EIw5C9vV0uLi5wXRfHFsi2LMm4segnnUzheS6uo+K7Pr7n4Xoew9GIjz/+WIivfB/PdXFVlSAQLI5lJUgmExwdH6FrOmHg43qiDN3Z2WVza0tQ1K4LMesQBj4ykMtkyaQz9Ad9VEXBdVwcV+R3jIlww1B8XqzV8ANfeEs8H0VWGA4GPHr8iC9+8XvQdJ1EIkGn2yEKw6lOx3U9jo+P+fDOh6ysLBPGP9OxbSEADAIkSRIqWs9FcRR8zxMahbMzxpMJszMz3L17F6IoPlbgVrIskUwmsAyDU3uCLEn4njvdbfqDIRvPn4vqK96hHdtBklxhGK1USKczDAcDDNPAsW00TcX3fU5OTtg/OCAIQ7HT2raI0LAdojBEURSGwyGPHgm3uKIopFIphqMT5FDG81yiKOTg8BA/CKiUy5ycnJBMphiNhsiKgue6eICuiQd8PB5j6DqB76NpKltb2xwcHpJMJNhwXUbDIb7vYds2ruPieS6JRBJD1+n3e0Sahhc/excXF2iahu/77O7sEv2h6+55PooiU63V2NnbZTAYANG0Cri4uCBhWezu7aEoMq4nrvmLKicIAlRFpdfr8Xj1EaPhEEURsRudi/a0SrBtm6OjI4qlEhsbG/HCJHQoiqLEbaSI4zBNg85FG0mWAbAdh+PjYwqFAt1eD9M0cRwb13XiZ1xURdlsFsPQRbJAzGS6rsvp6Sm243CwfyD0XmGIY9uEgYAZ/FRSbAaSjGNPkBVlyg49XlsT99rz6PV70+dU8RVs28bQDWRZBknCsW1SiRzXr9+g1x9SbzQJAw8ZKJQrpFIpet0OpmkxmYzxAxcnOuZiYOBRQFVl5EhBjYKAvYMDzs5OqdVqvP/++1y7dk2g8GGEIis0Gi16/T6dbgdFFqudFlc1r7/+GsViEVVTcV2HcSyTz2YyVEolJrZD4H9Mb9DHs23CKESRZSqVCq+/9pqoWohwHSfGbyQq5TLFYpFySRj7fN0XLUwQYsa+pkqlwvNnz/A8T1CTooGj2WhSrlQplUqcnJ6gqqL3VRUFx3F49eVXuHzpEn/wB3+A7wu2IopCUqkMuWyeiIhyucIXvvAF6rUa29tCRDYcDqdt4gu39EsvvYRhGEITFH37HKIoIhe7oENgMrFFSp/rYTs2165epVgqUSoWkSSJ9979Fp7nip0hjJgpFCgVy+RyBdafPEFCGEZVVWV5eZnJeMz169cB+LVf/zWiOAIDYG52llZrhv39fR6enxGEAa5tI0kSV69dI2EJEF1TVSF2c12QIJPOommi1C6Xyrz55psU8iJtbX5+nrPzc/qDAWEQ0Ov3uXrlCtVqlWQySbPZ5IMPP2A4GKCbJgC5bI5sNks+l2d3dxdbVfGDAMd2ePnllykU8liWxWg85ld/7Vdx7IlQXPuBcJAXi2RzOXZ2d/BiytxxRMDYC1Xs4dGhULhGAYPhEAmJhYUFmq0W+WfPOD8XKnKh4RILSSKR4PatWyDBL/zCv8bzXIIwIJvOoOkCYG7UG3z+81+gWChy0W4z02xycnzMxJ5MW+h8oUCr2SSZSIhFxfMYjYbohgGAZSbQDWMq4nsh9WhftLl0STjAFxYW2NjYwJ5McDwPWZJQFIVarUalWqVSrbK2ukoYVz/n5+ek02lu3rzJtavXODo+4p1vvSM2Uc/D0HQqpTL1RoN0Ks3B4f5UKqKqKq++8gqzMzNEwNPYgvOiYEgmEuRygiKXJYnhcIgiw82bN0lni1RqNQxdZXfzOdeu32Bnd4eHH98XQsRHm7z62qvMWN+LphlYVhIvCNEUCTUIfGFPT6eEqnA4Ip/LE8Rtiu3YdLsXlIrCZBWGAYkI3nr7bU7Pz7Fth8era6ytrZLN5bGSgoufnZnFNC1Oz84ox3Zz1/UYDEf877/xG6iKgqZrrK6t0h8Myebz6IaBqqo0WzPCwu46tGZm45dH4pvvvMPZ+TnD4ZDt7W0ePXpIOpNGVVWiMELXNZYuXeLs7JQwiijFtoOIiG+8/Rbdbo/ReMSHd+5w/8F90pmMwC58j3qtTj5fQFVV2hdt3nnnHV5/7XUAcf7lMlEMyqqqxn/8j/+RfF5oVnZ3d+n1+5Ti4CrHcWM7Q469g33q9fo0fc+N3av5fB7HdSGK6A+HZAsFDEMnCqE1O8dgOBC2/GaT8WSMoqmsP3nCb/zGb8QxFWHcGkZUG02iSPi+5ubm2dzYQDcMSpUKjuOgGwbdXo+33voGkiRPS+mJbZPJ58XCtDAvAGdZ5qJzwTvf/CZ/9I/8USQJzs7OaDSamJ1OXKFK3Pv4Y7LZbExDy+zu7pEvlYSvLQiYX1ggmUrheT6tGRF9EcYsx5Mn6yRTKdwY2PeDgEKxPGUci6USw+FACPAqVYLAJwhCNjY3yWazcSWSoD8cEEYRxWIZSZawLItWq8XO9haGaVIuV0ASrc8gjjA9Pz9HQgSsTWyHVDaDZSaYabYIwiCuME/51jvv8OYX3sT3A87Oz6lWa/QGPYIg4Nmz5+i6wf6+UBr7vg+SRL5YjKl1iUuXLiFLMr4n4kaGI9HWHBwckk6lOTs9JZFM8vjxY4px/ClRhK4bzMSmUFmWqdXqIiFR09jZ2SFfEArnZCrJxcUFmVwOPV68i4UCzVZLVJSpJJlMjiAK0DSdb33rW1y6dImNjQ0kJDY2t8hkskJzJMs06w3y+fx0QTIMA1XV+E//6ct8/fd/n5nWLKqmAhFvf/ObovrSNGqNBoZhMHFDrFQKWZGRJUiYugix88OIk5MTYVgajXj46CFvvPEGiixKKwBZVmg2qxTyBXr9HsPhkH//7/+3uD0RgjBFUWJaTSIKAuzJBD8I0A2DS0tLeK5Hf9Dn7OSEf/DTPy0oX18AhLpuCHVrFOHGFxogmUhwaekyo9GQfr/HW9/4Bl/9yleQZEnoROIeNwoCJKRpKawqCoV8nmpFZIwMRyM+ePc93v6DbxDErZ+qaliGUK0qkqgQtDhlrlIu8+bnv0C9Xmd9bQ3TtCiXK+RzeQb9HoPhkJ/7uX+CHwQQ7y6GbmAYOoHnQRjS6/bwfA/LSnBp6RKO4zAY9On1uvzjf/yP8T0vxpokDMNEVzUIxQ7uux6e65FOpli5tMxgOGA0GvHhB+/z+7//9akAK4qiaTZuEAR4joOiKkiyTMKyuH71OsPhkNFoSKfd5qd/6qemC1MYRpiWSTKRIPADRoMBuXwBRVGolMp84QtfoFgo0D47wzQtqlVRkXW7Hfr9Hv/LP/qZ6SYUBqK10g0dKYqIwpBOpxM74pPUalUGgwHDwYBOt8M/+Ac/TRCGQkxH/DDLCoHvEXg+UgSe55NJZ8jnclNj3rvf+ha///WvT/GMFy/CCxYkiBf/F2rYcqnEeDym0+nQPjvjZ//X/5UwFNqcCNB1jaRpicV2PCJfKKDIMvVajc9//vOUSyX2dndJpVI0my0G/T6D4YBv/MEf8NXf+i38MBBMawSmaaLIsnDuhwF2vChkMlnS6SzD+B7+3u/8Dr/5//1PBEEQg9UapimYTlFNuDj2BDWZImFZFC8vTz/3V375lwUNHYUCvFU1FFUlCkOkKGIyHgvtkSxTrVQplyqMxyMGwwFf+cpvxRuaIGoMXccyDSEsDUWLaMbVZxQJDCabSeEHPuPRiK3NDcaTMWEkrtvK8jL5SoVcPoekKLS7Y3ZOdzBUhdduzGHFwLkqx2aqbDZDqViif6UXezIEUh2GAfUYmNM0jW6ng6KqnJ2dIQFBfJEFCyMukCzJyIrCyckx5XIZWVFIWBbt83NUVaXb6+G5LqZp4gcBkiTaCNd1sSyTdCbD4eGhCEGKQqF47bRRZAXf9RiMBtOYSEGnC+2AoqoYmsZoPGJ2ZkaEYse7+GAwJAoD+oMhiYQ1VSxK8QsiyxJhLAxsty946+23ePW114iARr3O3NwcQRCI5DhJZn9/D8u0hDnUFJXXC9bJc30UVWZjY4NyuYxZNVFV4cpOJa9yenaGpmmYpiFAVlXjonOBqqjxTmzy9NlTqtWKwHFiz9LNGzfodXu4rkMqneLs7Ezs+p6Iz0inUqiKgiyJEK3xaESr2WAQe7VsW/T/pVJRvACqhqppTMaCXvd8H1VRaV9c8PZbb/ODf/RL9IcDalUhyReL1Rg/8NnZ3qZQKNDv9ykViwCcn59jmAa9Xp9kKsX+3i6zM7NkMhlc1+Xk9ISbN25ydHxEOpUSuTO9LpaV4PxcnIumaqTSKXZ3d2g1GwRhSCopdutEIkG/12c0HpJIJDk7OyWXyzEYDjF1AythIRESBgGVSgXXcanX6gz6fVzfxXU8Op0LyqUSg9GQhGkRhiHD0QjTNImAIAg5Ozvj7W++zZtfeFNEgTQa1Ot1hsMR49GIiCi+9pZIfUskmdh2LFlQGQyHZNMZtre3RBSIYWLbE0ajEZqqcnp2JqQQYSgqTE2j1++TSiQIowjTMLDtMXOzc+i6hiy1REWjyHQ7HWzHwTJNhqMhmVSG4UhoVAQL5RNFIubihY56PB6JvJjxGNexyWSydHtdUsnUFNi2LIt+r4umqSiKEr+jE1RFo1AU0aeZdJp0OkOv18UyTQ4PDrDHYy7a59x+eYZyucrEdlAVeboBqAAX7TYXnQtcx+XJ06d89rOCkn2xOo/HY2GaSyboDwbkclnCePeQY8WiaZqih/VcVEVhYosy3Pd9Ls7OKBTyDEZD0ukMEaAZBoZlIvsepmGhqBqObZPNZgEYBxNGYxGKk0om6Pf7JCzR72q6jmbo6KH43BcUtaqKFzSZTDKMd71cNivE6rJEKpsnAgxDrNS6rmNZJoqiYNsO/b4A3bI5kXiXy+Vot9uMJxNOT89QVJnhUOTaOq5LOp3B9QU+lM5kQZJQZBnX8/F8j6QlNAUvgqw63Q6JpBAPJpJJdN3A833S2Syu7019JEKuL2ItBsMBqaSwzJuWJWwMho6uGyBJpDNZASpKCulMCqKIZNKi1+3SHwxEQh0SyUQinj7QxrIs4RrO56fZvmEYipc4mSCdSXPl6lWSSQtd15nYE87b5wLcdlxUTWXi2GiaBrKEZuiYhsnEcURFFEZTPMe2JziuSxgE9Ht94aHyPXRTAIpSXyaTyTC2J+QyWVRNQ1UVMuk0p6dndDodqtUqo/FIiNZkCU030HUdJIlMNgeSRCKRJGFZU2q51+uJl1fXCIkwTSteCCaidfN9SpUKuqoxHI+IwpDReIymq2Rjf1UqlUbTdcbjMeftNpPJOHYsazieS07PEYQhummgGQaapmOahqj7ZUmwjrZNv98j8IO4orXwAx/dNARjGEXkcsLHl4ufA9MwkByJi4u2YMQMEyemrqNIdBSKoqLrJrl8HlkVOUV+4OPFLORoLFpSyzQA8V2ymQzjiUYqlcL1PKq1GolBH13TiSSJ9rmIYgBwXY+EqfOlL32J2698AkVVqVZKlIp5Tk9OOTzYZ+3xYyrVGls7IlrXMjR0TY7fNxlFVVElRaZSKZPP5ygUi4zGI/L5/HSHl1WFh/cf0u114wUnAlmm1RDxkJIkEQYhvX6Po+NjwkCI7WRZ5jOf+hRbO9usrq1NM2dSqRT1Wg09jkp0XZfDgwOGo9EfKl113vjEG3x450P29vfj7BmZhYUFIeUGRqMxJ6enbO9sT4Epz/epVSp84hNv8NXf/to0qk+SJObm5qhVa+Li+QOOj4/Z2d2N/1wWD66icHllmeFwyPr6E3q9HpZp8uChOH9JkojCEN0wuHrlKr1BnzAQu9C7779Pt9dDic9BUVW+97u/mydPn/LgwX00XQQ1WZbFtWtXifrQ6/UJQp933n2XwWCAIssiUyeT4Tu/8CZ37t5ld38PVZEJgpDZuTlmWi08z2c0nhCEIb/79d+bZtW4rsPiwiJXVlb42u/8Npqu8+GHHxAhkcvnWLm8jG6Y9AcDXNflw4/uYsfMxwtG6rPf8R0MB0PWn4gUuEK+wL2P73N6dhpjXSGyqnL75k0uOh0ADg4OebbxnIuLC1HqSxK6pvPpT32Kew8esLu7O73/Hz+4z62btzg5PROaKtflt772NYEzxVqW+cVF/sj3fT/vffABZ+dnqIpCGON6M62WiOiYTIiA3/rqV3BsW7BXnghMqlWrPHr8mIhwOk6nkC+wsrKMLMuct9u4rstvfTWWVUgyYRRimSaf+exn6XV7PHnyhOFoQDqV4oM7d+gP+nHFHrK4sEi9XuP07AxFFRXf47VVXMdFTPCR0FSV7//e7+ODO3fY2dlG1TSiKJoaXk/Pzqcaqz946xtCgxVjQ4uLiyzML/Ct997FcV2kMERWFa5fv04qmSYIxWK1sbHJN95+m1izihfHnzSbLe7dv4fv+RBGyKrM5UuXKRaK+IFP++KC/f193n3vPaIoQJLEc1cpV/h8S8R2ZtIpcrksq2uPeeed9yiWyzEcEMRTQVQk4KLToV4XYW9hFDEexyI+0xJMsq7p9Cc27fYFkixzfHTEeDyeUqJETDM+VVkRLIrr8jd+8id545NvsL9/QKVc5v0P3udnfuYf4dg2kizFuzBxun5GrMKOza1bt/m//q2/RTKZYDQao6gK/9P/63/io3sfYZkWfhjEi1Ywpes0ReAKf+FH/jw/+IM/KCjCYpHf/d3f5f/99/8+sizmOLm+hxZn2ZiGIXZYBDD9wz/8w/zA9/8Au7u7zM/P8+Uvf5mf/of/IO6bAQmCOLk9lUyxML9AOp2h3+ujKDKZdDru7z2KxRJ/9cd/nOXlZVzXRZZl/t7f+3u8+967pJMp/DCIP1cIt9KZDJZpCTdspcKP/eUfi2coCdf1//g//o88fPiApJXEDYRFwPM8dEOcv6kbjCdjvu97vpc/+Sf/JNlsll6vh+d5/Hd/52+z8XwjtmLYU1GeaZokEgnBbvk+l5Yu8RM/8RPMtFr0h8Ls9t/+zf+Wra0t0R5EEePxOG5JUszPz2NZiXgXlclmMmiaju95ZLIZ/sZP/o1pNq6qqvyDf/gP+cZb38AyDPwX+EoUoioK2UwGQzfi1P8sf/Wv/TXm5+YYjUYEQcB//z/89zx/LgLFbNvG1HVc18E0DPK5HJqq4bguf+wHf5Dv/d7vxbKsKaP0f/lbf0uozGORoqqpBGEwrUwlwPU8rl67xl//a3+NWr0OUcTR0RH/w//j/87+3j66rsVsosCP0pk0C/MLJJOpmLoW5y9LMn4Q8Kf/1J/iO77jO0Q1EsdY/uR//Tc4Oz0TPyv+OUIQKe6hrulEUcQP/dAP8elPfTo20MKHH37IP/yZnxHfXVGwXUfIMuLN6IXbXJFlfuwv/xhXr14V7GcY8ou/+At8+ctfRtP0+DxdNFUj8H1M3UDSTcIoxDRM/tKP/iWuXr02pbu/9rXf5hf/zS/E4ll5quYOY0b2Rfbywf4hT9bXmHfsWLQaCsV2MjHN8rZiZtIwDL75zW/yS7/8S7z80sts7WyjXlpYYmtnS8jMc7mpgOiFTUCSJCzDZLY1QzIpAnnGoxFLi4ssLizy7OkzbMdhaXGJqysruK6Qkp+fn6PIEul0ipVLl0mlRHzgpcVFZmdnefDgAYeHh/zAD/wAK8vL2BM7BpkiDg8PkYBysUSlVEbTdIIgYG5ujiiK+M3f/E2+9KUvxcHJl6f9p+e5dDodQGK2NTON6PR9j6XFJSaTCf/u3/07/ru//beZmZlheenSFNjyA5/Njc0XCcUxriGwGUM3mJ+dI5FITsc9nMdsluu6VKtVioUC165eI5VMEUYh3W4HWZZIWBbLl1fIxGVpviDyWIIwpFqp0L64YGV5Gc91SSUFqHZ6ciqo/GKZcrGEES/OxUKBdrtNtVbjd3/v91haXOTW9RsYqo5lWXGfP0SRFRbnFyiVSvH5+zQbTY6Pj9ENg/fff5+Xb7/E7Zu3sAwTK7ZGPHz4AGGCj/A9Hym+/4amM7s8gxljTvV6nafPnrF/cEC73ebqlSs0Gw2urVyNF6uQs7NTiEDXdK4sr2BZCTzPRZJkwkAwMx/dvcvrr7/O7MwshqZjGCa2IzQdiqJSLpWYnZlBVTVc12Vudm6a+XN0fIwsSdy6eZNMKjUdrHbR6aCpGgtz87FaWFhdWs0mnW4XwzT5+te/zkyrxe0bN8kkUzHzJ1ITpVi1+SL0TJIkkokkzWYDRdGmo2yePn3KeDxmPJlw+9Ytrq1c46xwgq4bhFHIyckJEpDP5SgVikLJG0U0Gw2ebzwXc6q6PVRF4daNG/EkCuGlCuK2u1IUYdpRJFTGRBF3P/pIqMmzWQzd4NaNm9MKfDIZCzxN05mdmSGdSk8XqnQ6zTvfeofv+Oxn2dreJopCbt+8hRdrs0ajIWfn5wIEliUGgwH97gW5fH4aqKWqqvBEqTKypMZyjBx37t6hXClPRw3Nz89TqVYIwgD1s5/7LLcHt6eK3Rey4ReZLIZhUCqX2dndwQ98wdY4Lv345To5OaHZagkV8NpqLDaSCYOIpaUldMPhW+++i6Zp2LZNOisCqvf29uh2u9i2zc7eLo8ePcBMJAQijsTtl17i5OSEjz66i2lZcVs0FDF/UcTxyQkXFxc8ffZ0alH3PY9CPs/83Dw7uzt8fP9jNE3gQt1ul2q1OtUsDAYDnj57KtgyCeRYp6CoCkEgSnDfD1BVjUIhz/bO9lRTMTc3z/d83/cyHo1E8DZwcHjI2upjDMualrtXVlYwLYuHjx6iGwau43B5eYXv+q7vwrFtAbq5Ljvb26w+foSVTIoMY12nUqlydHTE49XHJJNJxuMxr3/iE9TrdTEk7OKCTj7Ps+fPePjoAYlEAsdxxYt+/Tpb29vcu3cPPRZrZbJZ5ubmGI/H1KpVIiKePHvK6upjLCuBRBSfv3DBTyYTwlgHValWebaxQRSFuI7DYNjn1ddenS6wYRiyv7/P6tqqeJHiyIfllSscn57waPURlpXAcRwq5TLdXo/xeCxym2WZza1NMVhP13EdJ06Nq+J6Hs9iC4nrunzu/HNxDos/nau0/mSd58+eYZimuP+FIleuXuW9d99lY2sTLV6cMrkso+GQi3ZbUMRWgqfPnvH02VNR6UagqkrMyIVM7AlhICjeUrnC+pOnU0LjxfiRMG7Nj09OeL7xjN3dHXTDiN3sErn8GxyfnvJ49ZH4DEni4OBAzPtSVTzXoT+ZsPZknV6vh6aquJ7H7MwsrVaLre0t7j94gCxLgvVMJAjCkL39ffL5PAcHBzxaFWHqsiTh+z71Wp25+Tl+//e/zs7ODsTztSIiMuk0xycnOI6D4zg8evxoKgiNwohMNis8gpHQlFmJBAeHR+wf7IuspHKZwPfRdZOL9gW2bU8JixeL8WQy4fT0lGqlytnpGaoSg1FhGNLv95EkiUwm8+1ZSVMA1+DipCso4iDAc11Gw5EYA5LJsGE72I7DJBZ11as1Uqk0fk9krDgjgWSP4+SuL33pS1xcXCDLMuOJAHSDeJGrVqqoioKqCeNgL5arD0cjWs0m3/PFLzIzO8vp6Smj8fjFYARBMTaaqJqCoqqMJhOYiHzf0WjEzMwMX/rjf5xcNovtOIzGE2RZFiNNyiVKhSISEolkYroDnJ+fYRgmqqZz0T2NhWY9qtWqmFcTn69hmozHY5BlvLhiSKcz9AdD/CDAHgwI4vzghQVRXewf7FOvVukPh4wnE8K4LW02m0iKjKJpuJ6H1+/hTmxCBDBbrVaZnZ2l0+kwGI4EiApISDRbLUEPZ7I829xAtm1xryZjSuUylmnGLZtJr9dnNBrher7IoY3B30QiyezsDJZlCVbDNNE0weT5ns9Zu82Vq1epVCrY4zGariMpsvCoBAZRIEZ4JBIJEjHo2+v3xbUbDJAkiaVLl5ibnxe4ToRgdaIkvu8LIiCSBMPlONix4nQ0GlOtVMjn8yIeM5ejPxgwmkzwYhVupVKJs6ANBsMhqqoS+D6DwZB0Os3i0hJ//coVjo6O+Hf//t8xGo/FM1euks2K5z6VTjEzMyNCwuN2wQ8DBvF3n9gTrl+/TrVaYzweIcX+nBffQ5IkFubmhV1AUfCCIE45FBqka9euCS/atWs8fPiQ/mAoWChJEjqwZlOo4NMZDg6FmNCyLAbDITdv3uTmzZs4rkupXBbvhq4ThYEItKpWkZDQTZOjk2PBsAYBw+FoKqBVVZWtzS16/cG0UykXy+QL+ansIpNJUyzkKBTLtC96XJyf4zkuESBLMgsLi6QzKXLZHKqmCLlIfKzv+bHq2UcNwghVUXiyscHP/KOfIZ1K8+N/9cdpNVtxvKDL+fkZzWaDhGVNS7if+Zmf4V9l/5W4gUFAr9slm8mQSacJgoBavY5lmRwc7LG0sBjLsm2ODg75G//130DX9alE++DggFKlgqYKiqxer+H5Hr7ncv3adTqdDq7n8Qu/8Av8+q//uqBzJYnz83Oy2cy0v1UVlbm5Oc7PzpCIWFleYTQa4Lkev/RL/4avfPUrEIcKdTodCoU8mqri+T75XJ56oz410QkJ+ACQ6HQumGm1BEsxHhEGAT/9U/8zpmXFNwS2t7eYnZ9DlhWceBZOLieCq68srzAcj4Q9wbH5qZ/+qancXUbi/PyMaq0mZNog5uC4goW7du0a7fM2YRTy9d/9PR58fF8A07KYHe46NnNzs9i2I6YLtlpsxyXwleUVhqMhrieA9P/b3/nbAmyKwcTxeES1KjJZS8WiYCRkEbOwsbHBxB4jSdBun3NpaZFevxgHrHv8g5/+aTRNnV6/5xsb1CqVKdiay2XJZjP4nseNa9e5uLgQYkvH4dd+9T8gK4qwOQQhvdijlbAsPM+jUCjgujaKJHFleZnxeILrufzBH3ydtVURGq5ruhjg59jUqtUpgdBoNtnb3cU0Da5fvYYbt83Hx0f80i//EmEgdFAiarVPMZ/HshKUKxWy2QyKotAf9Nnc2GAymRAEHr3uBZcvXY4pYpuvfe1rfHT3rqCl46or8H3K5ZLwI0XQajVJJBPIEly+dJler0sUhnzta1/lzp0PRWKBLNPv9SjksqSTojpRVZVSsYg9ERXUlZUr9Ps9wjDi3/7Kr/AfYjOloigcHB5QLBTicDCXfKFAtVLl/PyMTCrF4sLidNzJL/zrfyUysQFZUTg/P6dU+nYwVr1Wo1wpx/PmJRzXIQwCvvu7vosr127z9tvfIJ8VOcVHR8csLMxTKYs26J13vjmdlaSqKlbCQjd0TCshaGpZVhiPx+zu7pLNZqcgbzzenkq1QbVapTUT0ut2sScTjo6POD09R5IlJEkY80wjEWspIhzHo9cbUq42yBUryEhCzDccsr9/hOs46IYorQzdJJ/TcV0/Br9kPD+iVm/h+z6tVkC326Xb7bK3d4DrCs8NQC5TICLC9wMgYjAaU8gVmJldRJYl7IlNv9/n7PyM45M1XMdFkiVURUXTDGRFxpA1xmObwXBCiEQ6laQ50ySdSXNyekqzNUe90aDVcuj1eozHYqbQi5ZRURUsS+BWQRCi6xLjsc3xaZtytUG+WAUi2udtHMdmZ3tPUJW6wJasRAJV1QnigCbPCxmNXarVBqVKyNzcIhftC4ajIZubolU1TYEbpFIpFFnHMJRY/u9iJtJUqk1kWbB0vW6X3qDPk6cbTOIdOwwjEgkL0xJtWbfbx7RSRMik4xc1lUyx5/rMzIrg8/F4RK/XYzQcsbm5PY30MCyDRCJNYPgxyehgOx7n7S6tGVHJNJoO7XYbz3V5vrGFhNitPd8T5+A4RJGMohogKQxHNs3WnAhdCgK6nS6D4YCnTzfifBsdOw7NFq7hCEM3cT2fZCpLLi/wJ9dxyGY7dLtdHj9eF5YLTY3PP4GuC0yo0+lhmkn8ICQTDy1LJZMEQURrdnE642gQiwXX1p5++/xNQ4w8CUKR5eMH9PpDLrp9mq1ZoghsWzyHwue0HhtBJSRZwTITSLIbCw+hPxwLcV9rDstK4MYZP91Oh4tOR7RuuoYkSZRKFZE7YyaRUBmMxiSsFLNzS1OJSa/X5bx9zv7BsQikV2QkSQwRDOO2rz8YkkhmSKaEeHIwGLC9uYFpJQklkW1z9+6H00iKWrXMxuZzTs/OePr0KZeXl6epl+fn5wz6Ay4u2kJoN3EdLl++zN/9u38XRVGYm50Xu6ukIOGhBX2iSYih66S1MaW0Sc4qTCcJRJFQD0YgxGoxKn168JBMJossyRgJi5Q2ply3qOYrU1l0EAqbumM7+IEfq4F9OkdrlMsVoijE1OLPbaWRZjI4jo2uG9iOPc2C8eMSWXbPON7ZE9qJ0YhKNkkxlaBRrGGZpqCDY7qVKEKLB1V5nke/38MdX7B7cMJb33iHN7/zeyF0UbxzsBUMItKGTSltkFTzJJIJvHixe1H5qPGOHoYhu88+JJfJCp2EqmEpfWq1DIVkGd3Q0XU9fuC1eHi9hqzIhMGI4+2PKRaLEAktQ1Ib0pzLMlsx4kXJohOLzzzPQ1YUkokETn+Xni0A4cFwSKNQoGBZ6HNZZGmOw6NDslkRdqTrGqZp4XseSBIXnTb24Jz9gwPeeestjn/4zzPonuIP9tByYEQOBculkNDQI+EHGg6H5HJCa9TpCgHWcDhAVSVOdx+QzxeQ3RFGFJBUBuQbBfKJCul0ahqNYJkW3W5nOm0hjDo8ffA2hmXi+j6ZdBosh5lKEaeZxLYdLMvkotMhnU4zGU8wDB3TNBmOjgTmUiji+i7FfIasaSHVE6jKLO32eTyLaIRlWXHb4oIkMRx0cccX7O1JvPXWW3zpS/8nRoNTsI9QvAA9sskYHvlGgkqmTDKZxPU8LNPEdT1c14mFi2M0LWD36QfkC0U0VUWPfHKmTzWXpZ6XSSRF5o7Qb4n2X2iIAnBOOO/uCLLF7pJQNbSUT6NQYjJJ4HligR1PxiQTKSb2JNbIRNiTIyaOQj6uVnIFlVI6yVIzKTxr9oRkIkmv35sSLy86gvbFCZ4tdDzNVotut8NHH39MKplkY2uXvf1j0SloOorxkFIhzdlZm9bMDKmUYNySSTFDvlwRNh3p3Q8+eGsynnzHC5BXlmVs2xaAZhBy/+1foapuo6oaQRDGWIdYaVVVGBCDMIzVe9Mo1G+HosY6hBe//8K7IkkQhFFM5QohnHBSi7/z4vgwFC2ILH3bkvBC6v5iWNyLPwtDYlNZNJWh+34Y/3w5/myJID5WloUwzg9CwgiU0KZYrjLRL/Eknlmdli9oH28RSmos0RZdhiLLaKoiflYYEkYRmqrg+eGUfYFvp4lFiF5XRkJWpCmYSHxtXhz7wgw6PTZ2PYufKSNJEqoaX+swIohCdFXB9WL9kRTFTAg4no+mKrHfJ8TQNGQZ/DAiDMK4kpPj6ZwRcuSiVj5JV1nh2doDlq/eJuFtwOlbhLI+PU9VETEMiiITRUKO8OIe+aHQnsTdXowBxNck/rWqytPzf5G7KytxTGvE1Cry4t/i/KW4NRDX3fWCODtZaGQgPocYrP/Dx734PUl6sRnFucOqSL9/IamQ8VHLn+A8nGdr8zmLl6+SdteQLj4kQJs+58SbmjJVrCL0L/Hz/6LteHEBwrgVVBQ5ln1IcbZQOH0OJaSY3n/RxIp/gjgjWDzjkjhWkvAD8QwLjRhTpkn8UlzLMLaUvPgqSqzy9uM2UeQlRdOWKwo8OtIlFl7+45imEbeSEaoi8eDZIUdn/em7c3m2zPJ8RVhPZJkgznH63d/7Xf71v/7X0auvvCptbW211W++9TaTeEGxLIuT0xOuX7vO/Pw8vm+TrNwgVf4cuq6zfdhhMHZoVjIcnQ1oVjN4XsD69jmNchpDUzluD9E0mUY5QymbIAJGY5fNwwsySRNNlZnYHrO1LAQhT7fO0FWVfMbk4LSP64XcuFQhmzJRZInTzpjtwwsWmnlOL0ZIElyZr9AbTtg96pG0NDRV4eh8gOcFXFuqUshY8diEgIPDDpomHubByOHmpSrO2Gd9+wxVkakWUxyd93G8iE9eyZLnW3T2PqRZSHGy9wgqRYo3/hxDT+fJ9imjiUchYzEauyw28iRMnac754wmLovVAo+en2DoKstzJbIpAz+M6A9tdo+6BEHEXCPH4VmfpUYBWZY5POvTHdhU00mOz4eoisy1hSqmrhKEIee9MeubpyQTOglTp90d8enbc7hewPZRh4ntcblZ5MGTY1zPZ6aWZXmuxGDs8NZ7G9xeriPLEo83Tpmr57i+WOH8rM/x+YC5ao4whNHE5eCsz+vXmsiKSjJQeONTnxFJcPIKauESrh/yfPccxwu4Ml9mbeuUq7MVkpbO/adHOH7AK1caPFw7ZGx7XF0sUyummdgeB8dddo+6ZJMGmqZgaCrLsyV812N184zh2OXKYpndww7ZtMVCI0/S0ugObE4vRtiuj+cHBIS4bsDrl1tMemMOzvpIkYSmKnQHNhPH4zO3Z0mnDM47Y9a3zqgURcbQaOKhKBLXFst02kM29ztUkik0ReL4Yii+01wRVJ1sqPKJNz4pWnHlJeTyTZ7tXnDUHtCqZhiNPbqDCS9frZMwdB49P0YC0gmDdm+CqavMNXLkMxb9oc3R2YDe0CGbMOgNbUIv4tZ8Ddv22D3qoiBTyid4ttumkE1QyiVoVTJ0BzbP99oMRw6Ncgbb9XG9gFuXq3S6E846Q5KWRhBEdAc2IHHjUoV0Qqc7sNk76QstkqrSG0zIJ0yW50psH3Y5bg8oZZOEUcjx+ZBWNct8I4fZG4qtOV7k1RjzubpYI5uyOOsMyaZMKoX0VLH7gkEKgoByqcxrr73G0uISqUwa9YMPPuTk9ITBcEi1UuH9D97nv/pL/xXLy5cZTyaofpukvY8WqLQ0G8cKSPgamuFiTlRUWeZqdoweKRhoJBIuiiKRi0wStgjyMcIArAmmqoIEE8kjMbFQZImV9FhUQ4FMOhsQhhFlLjAdQZnXZA89PSEbHpNK+DiujzU6RAtD1ISNZQoGLJPxxJgJLjBtjSgK8YKQlYzY6VwvYBy6JMYnJCK4mhOhULqvkkyJti4XHCIpAVamgeP5FI0Mlg7m+CFSoDJvDgl1SCZ0hpGDNdJIRgYz+gh0CW2yx82iiHMscYrhCNl1VgtJZAXtW9BOMawRick+CUND1W2qmQA8iVxGzJTJ+meoUTxjRvVJ1ARuoikyDcUlMeliRRFzhoNkguUc8krVw3F9UuY5GecIIwj4/OKAvDUijCA7ayNLZxijQ2a0gHLRJ6ufMxq7FI2IaiUg751jRy0Gfo3J+AJFS2DJ5+TYJYxk5PQERZbIRGfYZg9rdIgV6jTVLpECifEZV7NjnIRPWWqTsg0SYYSZdsl7QyxDxTTi+MfxPilZ4nJqiK37FPwz1OSEtGlQCBJotoLku2iqi6yD64kc2rHtog/OmNFlcjmX4dhB11VqsjCOFsIh+liB0GUlMyIV5xo7uvC8maNDZvSQZNEmikIMWSWf8bFMnUxwhC01GfllxuMhimaSDE9IBgcsJlwaioehqTiJgInskbbPSKCxYA3w/ZCEYlBI+RiaQjYUz7/qe+imC5aoXh1NPMMp+5SMLKGnJgRBSCoysIoOpqGSUHRSjoHkuyynbBzDI2WYhFrI2PZITI5pqhH5tCeKJCWimhGTV4vhObqtoIYeZsoVkbKShKMEyDJYowPmDJd81p1WQ8WCjyEdkRybjPwMEQtIIBi60RjTNFBVmcl4yOnJGVKQQcUn8h38IBDK32yGRCLB2dkZH37wIWEgZrCrhmmwsLiIhBDaqaqg+gI/QELm7W/d4esXj4SSVRNWfFGei9T/F6Wy7wfTKQIRIp/3RciTpmnomsAmXqx2L8pdObbrh2EUQ1yihPXjnFlFUdA1FTcWfglaOURVhVfK9/1pifpixG0QhPEAKnnq9iUuaX1fHPvC9SqEi2JMxGjQ5xPf8UeoLr3GP/on/5Af/Ys/ytnFMd/6D/+edCaDpgnGLAojYQZV1DgxT5tqh+RYxRwE4td+GKJr2jTwKQpFWjwR8TgQUQa/uHZhDBT7vo8WH6epCp7nT71O/h86/xeuXAlJtD+BCNDSNB1dVcR4Xz+Yjl7xfB899gl5fjCNfFBkhcGgy+d/4C+QrBb4n/8/f5+/+bf+Dhv7O9z7xq+QLZSQJfBcL7YVhKiaLl7SGKx+ZzwR18j3CSOYxM54wzDQVEHfR5FoYaNI5C+LdjfE83xkWZrSqkGcCayqqrBQvLCgSKKVVlSFIAyQIpGn/KIl9jwxVcDQtWkUZhC3gxLgBQG6qhHG0wdejCkBmIxHfO77fhjPhH/18/+SH/9rP8HezipP7n6FXL4oWgY/ACmKmTwlZi+Fm/1FHGUYhQSBCKCSZQld06axFC/UxUEUoUgvoIJApPHJQo8ShJFIItA0dF2d+ttkKc6xDkNURSWMgm+3mdKLdtSPw/N1NE2ZxnDKsb7FDyOM+DkO45b3RUs2cRyqS5/hB+c+iSTLPH/2jG9+85tkMxkG/T6JZBLH9diPz9c0Dfr9Ptlcji/98T8+nTX16quvijlTySTqKDYyTsZjqtUq73/wPteuXY1NTyG7Zy6es0haSaOpInk9nU5zfn7+bYu6JGFaJrquo8gquq5j2zYXozZI4A088WUGg1hxKlLUTFNkaZimFc9fAit2uJ6enaL6IqQ6nUljOw6qoojAK9fFMHVGozGWlSCRsFBVMevZ8zwOjw+xDDOefSzEe14s2x6ORlimiDM0DINEMjU1ZfbVPk/Pkyx/osXY1THTNXYuHA78FbJ+ltANGY/FPOXjkxOKhQKT8RjDNEmnM3iRS8JITBeIzqhDFEZErljwzs/PKcS5x8lEQiTPey6pVJqxMyaZSE4DsjqTDrIvEQ4DDNPk4uKCQqGI44hrl0wkuLjoUCyWUFQZ3TBIp9KMR2P2DvZQFREoVa2UmdjCmChJEienJxTzRTzfmw5kF5uAytnokNNxis81a4QRNGoVDvZznHALXyoyHAzpDwZkMmn29veZnZlhPB6RSgn6chSOyVkCQFUUmaE7FIFgo1CYKbtdyqUync4FhUIBSZLo98XAuMF4QCFfmJorz87OYme6KxzTgwG5XA43zrrNZjIcnZww05pB03Ss2Gzb63c5Pz/DjEca57JZXNfDcUVIWKfTETEOti0UtpaG7wcYhsF+75DjYZKrM2UkSaJaKrG3U+UkusXAFsHzfpzK1+31KBUKjGN7hmUKij2XzImFD4m9iz2Bc4yj6Uz2XC43fYYCPyCMQtKpDBNnQqFQEARBEHB+fhbPZJLRVBU7HsQ3mUyQEO+bbduUSmWCICCVShOGAYNBn8FkiOZpEIWCRo/FkC/sIMViMZYS5OJoVwVd1zkcHDE59aeLvmlZeK7Lu996l5WrV7h56xa+LyY0HB4ecPfOHfb2dvnCF96cYqtnZ2e89/57YlLn1ibKrdu3/0IiYc1lc1khSw4jbt26yczMDJPJhCfr6xRyGfZ2tzg83GPQ73J+doIig6rIuM6EMPBwJxPGowGyJHYPz53QqNfIZ7Osrz9i0O8yGvZxXRvLEiUXUYAsgetM0FQZyzRIJEw0VeHWzes47oSdrQ0mkyGT8QDHnmAYqgAQowBdV/E9RwTcWCYJy0BTFRbm5xj0uhwe7DIeDRgN+yiKhGFoSIQoioTvO4S+h6Gr6LpKLpMmCFxy2Qwvv3Sb3d1tXr59GykSo0Q3nj/lYH+X0bDHxcUZqiy+v++7hIHHaNhnMhkCIaauQxRQKRdJJCx2Np/T7V7gOhNse4xl6iiKRBT6EAVMxgM0RSZhGWTSSXRd4XOf+QyDYZ/N509xnDGuM2E8HmIamghUDjx0XcGZjFBkCcsySJg6qgzLly/Rbp9ydnLEeDxkOOwhS6DKAmDVVInAd3GdCaoioWsqhXyW9tkprZkm169f5/nz57zxiU8ShQGDfo/Hjx5weLjHaNCj02mjqzJEIa4zwfcc7MmIyXiEJIkdUpJCPvmJTzAeD3n29An2ZIxjj3DsIamkhSRFhIGHIsFo2MM0dBKWQdIyIQq4dfM652cnHB8dMpkMmIyGDPtdDFOffrZpCDWspkpYlh7ff5mrV1Y4Oz3m9OSI4aDHsN9FVSQMXUWRQVYkAs/Fc21UVcY0NHLZDINBl0tLwspydHzMKy+/jGWadC7OefToPu3zU4aDHoNBF0sXvrTAcwh9l173gigIgBBdV1EVmYW5GXzPZWd7k8l4iGOPURSwDI0w8EAKcZwJrjPGMjQSloFlGWRSCa5cWeb87IST4wNx7GSMRIBhaMhyBIT4nhOfg4QZH68o4vyPDvc5OtpnNOgzsUeYhoaiSGiqTBQFjEcDwsDD0MVxqVSCyVgkJdx+6SVUVeWifcH29jbD4Yjv/4Hv59Of+QxXr1yhVCpRLBa4d+8eAEtLl1i6dAnLsmift7m4uGBhcUFSFGWihkHARbsjcjU9n62tLQaDYUw7R4LXDyRkTceLUXrbtvmrf/2vc+vW7emIk3sf3eOf/Yt/hr2zQyqVIpVMISsKqWSKIALPdbEdm4WlS/zoj/4o5XJZWORHI3725/4Jjx49QourkGw2G4t1TCJFZuJ6+IHH3OwcP/ZXfoxGvS5myngeP/O//CPuP3iAaZqkkimymQyLi4vCdiDLjGIR1J/8U3+K7/ni9wj6XVG499FH/PN/+S84PD7G83yq1Sq+61Kt17i4uOCDDz/kzTffBAlG47GwAPS6yJJMEAb8N3/zbzI/N89oNESSZL75zjf5+Z//ef5/Tb15kCTneZ/55FGVmZV1V9/H3CdmpmcwOGhSFkCRICkyRBFLUTYpMXiYkqVdryVFKGyvvRHW2ru2NyxzaVHaFQVJu9ogQUsyJULaFUlAJKgVKQ0wmMHMYKbn7Puq7q77rsrKY/94v64R/kFExwzQWflV5ve97+99niD0cZwE+Vye6ckpIg2GYUhPDecdPnqMX/mVX8FNJOgrTMJ/+k+/zr37DzBjJkk3iWPbzM7MynAhYIQRXhCST7v883/xP5DN5YjCkP6gz7/5N/+Wm3fewXEcXDdJJpXkQiLB5NQMaxsbdBQj+Bf/2/+O97znR6hWqkDE1bfe4qtf+ypryrd84vhJtnd2RiHEt956i+bPNtRcVYNI0/CCAB0NU9f5p7/0y5w8eUodC4R982//l/8ZNmVyupAvcPzocRrNFoG0OOh5HrPzh/jn/+yfYdk2ge8z9H3+9a/9a+49eij8XzeJm3AojI9j2Qn8KCToD/CHPmNjY/zLf/U/Eo/HCdWR5N/9+3/HO4syipDNZLAti1Q6TSqdIdJ26PT7hGHIz/3CL7BwYUHxfwLeePMN/q8/+ANWNzaIopDDhySgGUYhpXKZa9eu8ZM/8VG8oUdvMMCIWfi9AVoUcur4CX7ll395JPirVCr8H1/5bZZWVgSXkUwyMT6BYR4lACLVmQWNf/APP8mli5fQdDkev/797/PVr30V2ENDw7ItJicmsB2HmGUxDEN8dYT96X/4SZ599tmRcfLq1at85aXfkXug6+TzBRxH1LUJN4kXBHQHA04cP8Gv/uqvkk6lGKjh3C//5pe5du3aaA5tfm6eRr1OriBpdjRtNBoRi5ksLy+zUyxy+tQp6vUGhh4St2I4TkJ1saQr1Wq3WF0T3/fW5iYmRKRSSdykiNZnZmekRx+GI+Tf9t42a6srtDuS7AyDgLHCGFubW4yPj1EqidGw2+lSroih4NjRYyQSLhsbG+yX9vD9AF8hEvu9HuVSiXqjIRoNoLS7S8y20TWNTDoNwOLiHXZ3d6Wm4XnMTE3jDQZUqqKK3dzcpN/r0azV6FoWtVqVw+/5+3S7XW7dvEm1VhVKmGJp7BR36PcHJByHre0tGo0G5XJZBdIGPP3U09iWTTKZ5OLCAtlsjt1ikZ2dbZaWHgmTNhTCeyGf5+GjhxxSg3e9XnckMa9GVeJmjIkLC9xZvENxtygTsJ5HdOYMm5ubHJqfp9ls0leEsmq5RNy2KZdKnDxxkiAIefToIfv7e1JrGXrYlmAIG/UGtVpVbXF9WvW6DPpVqsw8+yw7O9s8fPiQcrlMGAQEwyGpVIqbN26QSqcwDJNarUa306FSESB1zDCZnz+EoZskk0kWFi7iui7lcplicYfV1RUGQ0+mzZMuyaTL+voatuNQq9Zwkwn29/elRub7pNykKvrts72zLSiC4ZAjhw+zurrKwsICSxsb+MMhVjxOdX+fmGVRLpU4/8Q5up0OKytLVMplqel5HtlshmZDVBoCq2rQ6/ep7O9jxGI06jXe/ffezc72NncWF9nb2yNUXZQojLh16xZPPfUUd27fxjTMESkONGzL4tjR41Lsz2ZZOH+BVDpFq9ViY22d9bVVhr6PPxhwVuk/yuUyJ06eYPX6GrVqlUpFFCiVSoV8NkfCcbhx4wZ7u7sjnoumaSwuLnLu/DkePHhIsVik2WjS6/dUPAGOzB+m0+7w6NEj9vb31LiO2C+uv/02Fy9epNeT7E+j0RiNq/QHAy4/eZliscjS8hKlUonA95mfm+Pu4iKnTp9i6A1FlxOGVEsloQ+o6etDhw9jjjhQUlsyDYMgDEmlUjxx7hwJJ8Hs3BxbG0ukEwa9jvjCD7QvCTfBzMwM+XxeBjgdO0F/0KDX6wngqCXR+oPCTxRFtBoNspkME+MTQmkfDLAsS1inrZaKnXc5ND9PUiEc/aGnEJE1MqkMCceh1+upsf8YjUYD27KoVqskEy5TU9M4joM39PCHQ/q9Hu1Wm8mxcUzTxPOGZDNZcexWqxTGxsjl88zPzrExsYbrJhkMBvR6PSmuqgdSFMnvm0om6feEBm/bNvt7+0xPTmHH4moeRmaxIKJWq3H9+nU+8IEPyBuqXCKZSDBWGFMoBIdischf/+AHfOTDH4ZIyPWHDx+mp2ajDEOn0+3QbDbJZUQ9MhwOMTSdH/7whzzz9NNMTU0xGAwYy40xMSEA7YMp3qHv0et1mSiMjRK/8VicK1euMDs7Qy6Xp91uY1sW09MzWLbNcDCg0agz8By6nQ6zU9OqaOyzubHJfqnEmdOnZQr91Ely2RwJ2xkV6suVEmgH13+NxoEXan+f8TGZ6h4OpSaytrbOo6UlLi4sUK/XmdKmOH70mGSPhj6agqMPBgMmCmOKni/0t0QiIeut26VSrTI5PsHkpEzx9/s9ut0Ova48sKcnpzBMg0F/QMJJYFkWe3t7zM3P02g0cG3h8BoKpdFoNNTgn7BhDoDwhUKBUqlEvV4HTWNra4vZmdnRfNGBwUDXdcqlEtdvvM1/U/84YRgJmXFsDMu26ff6uIkEtuNQbzSolCvMTE9z7OgxSafHRR9CJDvfdqvFmFK+aJpONpOlXq+zt7vH+vo6zWaT+dk5ut0OhgLTH9DvfM9jZnKKSA0dt9uibu0odtJg4DE7PUO/3xs92NutJt7Awvc85qZn5IUYi7Ozs8P4+Phoutw5WDeWpXxgAuk6mIrWFF+p3e7QbDQpl8sS1OsK37jb7lDc3mSIK9er/hl6Mkjc6/Vod9qYumkqXotFOpNmcnJSEc+UvB3EbZRK4yQchV6UQuPc3Byu69LpdOj3+zy4f184oYZOuVJmb28Xy7aZmZ4eqUzT6gFz9uwTREQ0G03u3bvHzMyMbNfCkFazSb3eIJlMkkomRyL2bCYrZ8yzZ7Esm3Q6xV+9/jozs3O4KtHaaDSwHZv8mFgJokiAULpucOzYMU6fPo2mMKG7xSJuwlXdi4i1tXWOHT9ONpfl0qVL5HJ5dotFdMMkn0/jqmlniDh16hRPPvnkaKZof3+f7K3bpF1BBDTbLba2tojH40xPTeO6ciSampri537u50gmBXk5OTXF9WvXmJ2dI5FwGA59uj0h+aXTaTKZrPiohj5OwuETn/gE2VyWzY1NbNtmZnqWoeeP8I3NVpOYGROzQqEgapJBn0uXLnH27Fl2d/fIZDME9wJZcAdhRV3nrWvX8DyPTDbDxUtPCgGvUsYwDHLZHLbj4A9F+nbu3Dk+9MEP4gcB5UqZKIyU11nJwwYyaXvwQEk4QmXLpDPkcjlmZmYojI1Rq1ZZeviQ2dk5ecF4A5qtJvVGg0KuQC6XU188j0Qigeu6TExM0O31OHPmDDMzAjuKx2V04IBKOD42TjqTGU12J5NJpmdmSKfTpNKi033w4IFwXlSX6t79eww9j3w+z6WLl0inUjTqdUzlhTrAOtjKgPjkpUtkMhlmZmd4/fXXGcvLg3Q4HDL0h5TKJZKpJLlsbsS4tiyLixcvks/nOXToEFevXqW0t6+uU45SA29Au9Min88/nh/SDU6eOMHM7AzTU9PYts3u7q7q+Areodfr02q1Sac09cJKEAQBs7OzvO9972NsbEwIkakUt995h+lp+e+gThXbO9scPXZ0FBKUznKGj3/ip6hVKrz26ndJZwTkXiqVuPD08wJgUzsYQW/aTExMkMlmKHQKmJ1WU+hogagya7WavEW1x4nEXr/P2vqGJAIVwe7Lv/mbzM3NjvgvxWKRO4uLhL4vHlkNnjhzlm6vy+raGjFDQEA7u7uUygKSFgezz81bN6lVqgJLCiQROD8/T6VaYW19DUPRstY21un2uiSSScJAlCM3btyUmQdFVs9lc8ylkmxub7O9swORtIG//l++zpU3rjD0fWJmjO2dbe7evSsEPjUARiSt80q5yptXr/LC+18QnKY3YHV9XdLK6un+a//Tr1EoFEbtw83NTe4/uA9hRKRJavL82SfoDwYsryw/Bvjs7NBst0bRbn845Nq1azSbTQxDYFFZtSDLFbFiHqRVLcvmP/yv/wEnkVAJ6oC3rl6l1WoJ0W7oMTY2RjKZYnVtjc3tLQiljval//yfmZ2Zxg9lrGNrY5MHDx+MxvVlXEJ4ypVylatX36RRr2MYJgPP4527d0Y8EE3X+eIXv8jE5MSo7Vsq7XPjnZvoaLKlTqe4dPESrU6LtbW10S5sU81wGTFlUwwC3njjDbrdrtgZfZ98ocC0rrNfLrG5vSXOqyjEth1++yu/jWU7UmD2PK6+9RbdTkc6TsMhk5OT2HaClbU1Wa+KsPfl3/wyMzMz+GGIoWkKr3F3tMYjwBsM0JW36upbV3nxxRcxdINur8fWnXcE5hT4bBW3abZbEndQDqFr16/TarUxdEnK5rPZkftoY2sLUxdq4Eu/97vMTE/j+wGGabK6usLSo0ejxO1w6DM3N0smk2V7t8j65saIHe39wZC52VnhWKOxU9zh3r17I2qj7wdMTIyTSqVYWV8lUBGOtc0NOopiIMB8nxtv36BcrahjmbT4bXWEO6gtNZtNGs0mn/vsZ3Eci7947Y84NHOWxQfXOMM0H/3QZ/ir73+PH/zwByMr6sDzZF6v06XVbGLGYhaGORwVdA6ORYxMQ5BwEqRSSeLxOJ4C1CzeXWRxcZFYXM63mi5OY0KJDh8we7vdrtxEXYMgolIp851vfwc0FEYwxDBMhbwcqngzozH+QMnAwiCg0Wjy3e/+JSGovIXwWnT9IEsjWz1TxbBRCgVNg9u3b3Pj7bfB0DENQ/E/YqOLjJSN4EA892PvfS8Tk5Ps7hRJJ1P0sj0sdf26pnH92nV5KGlgaDqGKbNAoyEHhXDg70THgyCgWqvy7W99C00Z+FDXHwGRL6aBSAnvDghrKONfGHZ57dVXQRMkox8EgkpAk/yD4pNouo7vD9FNA12TVOa169d484rM3JiK33Hwb009NA6yQQV1/ZlMRnZSmTR+GGCaJoO+tHtv3Lwh0QJdQ1cjDK7rYuiaOgrJmpExkYOof0itXucv/uL/RVPYgFDlpCKVSQnUQtXUkGMQhRiarKder8u3v/3tEUJhOBxi2bYyWRzkQXRlGQjQDWOEOb127ZoYHwxDZYgEzRqpHIy8teXlOTk5yXuff558LsfuwCOVThEhNQl/KDWMv/r+94nFhfGiKUSq6yZGhodkSkBW4cE9VA/P69ev86bnoSsdsqZrGLrUOQSZGjy+hiBQozMy/f7222/z1htvoJnm6BoOxh10TSMMH2eFDr7wuq5Rr9V49dXvjH6PA3Ok+LJlqluwDY+HFA7ul4DXwLYtNNMjmXa4eOEy7U6dKIyo1mri1vo7E0JRGI1GKMyDD9owZLoymUzKB6e2ze1Oh9mZGd71rmdxEy71ep1sToqfmUxGZhiU2Mn3ffxAyPTtTpvSfonZJ87x9FNPkUqlKJVK5HI5+gOxCCYSiceT26pWYjs2RBHr6xv82PPPM/AGjI9P0O10iMfjuIkEnW4Xx3HYL+2ja4Z6k8hUtuf12djY5BMf/zidbldBv6Wvn0qJodJNCHckAmxLZOTtjpxvdd2gXCnz5ptv8txzz1Fv1Dl86BDPP/ejaMhTPZVJs7W5ydzcHPV6HTfh4rgO5VJZpnz7AwaeR7VSYeHcOX70PT+CZdtsrK9z5MgRqgoVYVlC4Hdsi+1iEefgyxJFrKyscPnSZWzbxnVdtre3OHL48MiumUrJLiWfy42wlblslkazwf0HD3nxYy/S7XY5euQInU5HjqamyeK9exyan6fRbOIm5H632x10TWenuINhSJHy6tWrfOpTn2J7Z5tTJ09x+tQpGo0GlYpQ+R8tL3Hh/HnqjQa5TBbDNMTbk8tRLBZxHIfV1VUuLVzkvc89z9D3Ke7scOzYMfb29zg0f4goEnphLpdjfX2dsTGpN3W7XVZWVnjvc89LHmVykkq1yuzMLIE/ZL9UolAocPfeXY4eOUoYhVhxQaSWymVK+yV++uOfYKgQCp7n4Q09bMtiY1PyO3v7+4wVxI/ebLWIxePs7hbpD/qUyiXefPNNPvLhj7C+vsrF8xeYmRH53nA4xHYcqtUa83OzNJtNeVEApXKZQj4vfnZNY2Vlhed+5O+TSCREE9xqjewM6XSaXq9Hp9PFdRPsFHeYmpykfeDD3t7mA+9/Add1icVidLs98vncyCKZSLiUymUmxsaoNxqkUikGA5n2b7VavPjRn8Q0TSzbwht4own6SrXM/Nw81Wp19AIRfk6cre2t0W4wCESAd/zYMe7du8fK8gpX3rzNzUIRXZM80VNPVfCGQ44cPTpat7GYWCEcx8FNupiDQZ9ytUK/3yPwA9Wmbo3o9olEgrhhsry0rFqj0oVptlrE43EJ2BgGqWSSdDpNwk1iORZBEIrx0TTZ2tomFjPpdrs0m02RoamHUhiGKvCVIpPOkEyl8IYe8/OHCNSibLfaInEyxVfsKf9Pvz8gl83iZHMkXBdH8USCIKLZbLK3t0ujXpcnumKTNlstmW61LDLpDK7jkMjIubxerxMBmUyWy089RTabZ3+vBJrGg/sPRG3qeVi2Tb0uga5Bf4Bl2WRzWZW8jeO6SUxTEKCmYbC5tYGuG9TrNSCi3e7QqIuwfeDJscaKxUmnM9It8Iakkkkq1SqbmxtYliQmiYS7KpI1i0azQTwWw3VdUskUqXQGXTfkAdJoUC6X1MSujNjrhk65XMIfepJ+Hh8n6aZIJVM4iQStThsiSKfTPHn5Mo6dwLEdrHicWzdv0WpJ12u3uEOpUsbr9+n1+6SSScFTql1aPl8QQ+bYOM1mg9WVZfwgVFoXjXq9jtcXTkmn20XTZPebTmWwHRvDNDlx4oT4jMplut2OMGH6fXw/kBpNrUa71aLbFbSB68qiDtXwXbVWpVatjTgs3nBILGZSqVTxBgOGvk/ClgdsPl8Y1RJ1TSefy/PkU5dJJlPShgVuv/MOvb7AywzDpNvrUNrbpT/oY1kWqVSamBmHSCPhugAcO3YczxuwsbEhkLbhkDAUaLatAqcaMDY+geu4JN0UjsJnmLpJtValXC7LbtX3aTTqqv4pPqWhL5PclmWpemUKXTdIpdLUalVardbjIq7aWbfaLQY94evGYhILcWwH23FoNJuygz44wWgaxeIuv/4ff51UQuPI0WM4MR9D8+lS40+/8V9IZ8Y4c+b04w1Ju83a6hpjhQKbm5uYdsJmKj5FGAbk83lOnT5FJp1RU7whbiJBzIzzaGlJWrqGtK5jsTimwktGROIh1g1sxyGTyaAB09PTBGHEw0cPpTWmRPRyHg9H2zlN03BVMTehjhnixG2ysbWNpu3IdKxKHWqajCLELYsNVUh1bJtkKoWhG5w+fZpSpcz6xuYoJn1Azo+pY1FEhGM7OI50UQqFAvVajVNnz9But1laWqLRqBO3xAZQ3N+XorWCVxuGuKHQpACnbcg52bJsMtksMdPkyKHD+H7Ag0dLeCpJurm1haak8HK8iVhaXlaogpgq6kW88L4XqNRqPFpeFl1JGIphwIzJSEEoEf3t7R3iliVf0HQaDY2FhQXqjQY7O0V2ikXJNRz8HdWF0TSdldU14paoW+Zm57l7d5Ef//Efp9NRwK1Oi4QCIT1aEUynDL9JPcQbbBGoupKua5ixOJYlLm/LsvnQCx9gc3ubxfsP5EjjeWxtbxGLxVnb2MDQBea+tLJMOp3h0fIy2UyW4dDj3e9+N5vbW6xtrKNvbYImahr5Eul43kAoi9evY9sWrpsSjGXgs7CwwDt7e2xsb+GvrRKGsu4ORrqLu4IdWF1bw3EkRT45Mcn6uhT5G40GK0vLtNotSZuHUv9rtdpi31RfVzEjMKK8xS1LFcSzuAmXc+eeYGu7xaOlpdHU+frmBqYhDwzbEeXO0uoqruvyaGWZhJPATTicO3eOja1NlpaX1UiFroq5Oro6UmnA+sYm8Zjcw0w2SxiEPPPM0yyvLLO0tDT6/WJmjDCS6Mn29g66prG0vIybdInF4uRzeYrFIidPnyRSw46mYWAYOt1ul4985GO88P73Y5gGURiys7nC7/3+/02z0x9N+R9ofU+eOsn0zAwhYPqez15pn25XMhz3793nPe9+j0IqaLLtqjfxfKnThFHIMAj43Oc/zcWLFxl6HrFYjOtvv83LX3+ZcrXCfmmfudk5kc4PBOc4UOL6J544x6d/9mfJZDKYhkGr1eL3/s/f59HDhwq+YzM1NUW1UqHVaau5FB8/CJibmeUzn/kMk0pFGwYhv/O7L3H37qJ8yIkEJ44fp1YVsJUfBnhDmYf65Cc/yft/7H3CDDZN7ty+zde+/jKlSlkYve0WuVxecIOxOJPjEzi2zW6/T6XyWHzeVTL6X/qlf8LRI0dptWSLfPWtt/jDP/pDwrDOfmmf2ZlZJfUSbu3A8wh8n9Onz/DZz36GZDKJbTliSfzff4uVlWVMw8Tac5ianKBcKdPpdBkGPlGvJ8SyXI5/+k/+e7LZLIYhkLAvful/Y21tDduycBIJjh05yu5ukTCUmaQgCPEDny/8oy/w7DPP0Ol2icdi3Lhxk699/WsMKgNVh5AvSKQJqHtifELtFoW7PBwO8cMA35N2+Wc/9znOnztHry8q2UdLj/iN3/iN0Tn+0Pwh2p0OzaYYLoMgoNPtcuLEcX7h5/8xMYUDDYKAL33pS6xvrIsDyLaZm52jXCmLyM8PiPDF1jg2xr/6F/8S27EJo4hGo8Fv/dZvsb6xQTweJ5fLMT87x87ODkPPY+AN1K4h5NOf/jTnz1/A90Uu/7dXrvDH3/hjyhXxVx9YLA4ewuMTE1jxuORsKmVp94cB7W6XJ86e5fOf+7xq7xu02i1+56WXWFtdVVqUMseOHKXT6YoTSYUiAb7whS9waeGiRP8tix/88Af88X/9r1RrNTRNyhVnTp2mWqvRH8jRjmGErpv8zKc+xeXLl9VRXuftGzf4+tdflvCcppMvFJiZnmZvbx80sWz4vs/Ro8f4xz//8/Ly1jRCP+Cl3/9dFu/cIVaT4vvxY8cxY8Zo96KpmS9NExFgudrkte/9f6TTGelUuQbTYwlaHbm/KPlio9Hgwf0HpJIpVlZW0A1TVJknjp/k8KHDLFxYoJArPIYBRxH7e7uU9vbo93r0uj28/oDz584RM01Onz5NKp0mnUzK0NvQp9/t0u10SGfSbG1tUq2U6ff79Dod0ik5SqXU8KSTSDCWL9BuNgn8IfVajTCSo9nq8jL1WpVup0Or0cC2LZKuS0GlDdPpNGP5Al5P2ub1apWkm2ToD7l37x7tZpOh59Hrdjlx/PhoG53LZkkmkyMFg+/7lPZLTE5MiD2w1WR9Y10dFQ1Ke3tsb23S7UiuYTAY8MzTT6MRceb0aTKZDFmlVwmDAK8/oN/rMjU1Rblcpl6TbXmn3SadTpHP5Tk0f4hcPkcikaCQy9Pvivy9Vq0QqNmY1bUVWvUGjXqNeq2GaZhMTU1x7NgxNE1janqKXDZLoL5EtWoVTUPlWN5S8YEunXabhYUFzFhMBtBMk3QmLVkKherY3togn8vJvFmrzfr6Ot2u2B/L5TKVcmn0WZqmgRWPs7m1xelTpxh4HgsXFqS4FwQMej0C36dQKFCtVqhWKtQbNbodye0YhsHRo0c5ceIEp06eJJl08VRdrlqp4HkDNDQePXxEp92m3+vRbbcVYtPn6LFjYlucmsJ1EwyUVXFvd1cMhc0md+/epV6r0Wm3GQ48pqamaDWbnDx5kl6vx9TEhKhuBgOiIKRSqTA9M62uv8XGxgbdroTfdra3KJdEPNeq10kmk4yPj5PL5nBdV5LrKiahAZ1WC4jIZnNsbGxQb9To9XoMPY+Z6Rm63S5HDh8W+V8sLhaDgbCT67XaKPqwurJMu9mi2WjS7bTFHd/pcO7cOdLpNBMq1xIGAWHgU1NSvWajzqOHD+h1u/S6XRzLIgwCpiYnmZ6eJuEmGCsU6HYE4zro99nf3yNfKEjjQzGcDNPAG3ryovO8x+I+O06t0WGt2BKOt+pyBUFALp/jwoULHD58mNOnT2Oapsnu7h6NZoOJ8Qlu377NM888MyLURSrToekGmUwS3/flHKgCacsrK6yurtJUhaZ+r0dcpWrX19dotaVWY1kWsZhUrw1d5/69exR3d8lmMtTrNVJqkjuVilHeL1GrC4c3kZDKfMJ1MQwTwzRZWV3hxo2bI51rKpMhFosTi8VZ31hnYnxChghTqdG2evHOIqurYgb4e+96F9fffptUMjXy4Wiaxu07t8lms8RjcVKpNGYsJgGkZhPdMMjlsnR6PRzb5v79+3zve9/jYy++yKDfp9EQQtjBG7zebLK6ukKr1cJ2ErhugrYZo93u8Cd/+qecP3eOtbU1Uum0dCjicRxlH2y1W9TrNfr9PpZtjRKgnU6bP/vzP+fUyZMsLS1xYeECtVoNN6mKaq7L7u4eY2OFkWURYFzd1/39fcYKBVLpNLduKmKeCkcdXP+lJ5/EjMdIp1Mq1Skq1ZQqEu/t74/a2t1Oh7W1NTY3N6UWYMvDw0kkRjWwXv9xMK3T6Sj/8pCSkpZVKxU0TTpqmUxGsieqfjTw+hgxU7qYydQIeHb37l2uXLnC1OQkunJ2xWJxAt9nfX2NZDKF5w9xXVdCdJaFGZOaxg9/+EMGnsf29hZZtYvu9fvSin/nFgsXLmCaMVKplHSEwpBqrSZ8YbVWQjXtv3jnjhRdNY1Ot0sqlRyt0UqlSnF3h3anMzKS6rrO+toaccui2WxRLpdYXVvFtsUrJGaIAXv7e1i2Rd8bCE7VMDBVXL/RELXzbrEoVDrXFfxozGQ49Nne3pJhxiAgmUyOhhxv3LzB0Pe5cuUKc7Oz9PsDiUPETGxFAlh+tETu2fxjiL5hsL9XYmVlmZ/6xE/x1OXLIwb30tIyf7zzDWq16ujP67pOrVrj9p3bWJbFyuoKJprG7Owsc3NzZLPZUQjtoDCkaRq2ZWPGTIU8MEYZhqNHj/HU03mI4Duvfodbt26ptp3KFXjDEZHeMEwMXeTksXicZ9/1LkkKNpv87ZUrcNBihdGX3rJFnqWrtvKB7F48PLNYlsXVq1fVxWmA4A9N08SybHRNl+xCGHD2ibN8+Mc/zM6O1Cye+9Ef5c6dO+i6QajQE+12R4T2B61r1WqLW3E1pi/tYSI4d+4cTz75pOqsVJifnx/J4DVNw/ckVWzbtjpDS70pnU7xjz7/efKFgigvdndZXLyDaRhoxmN4jwbyuRumtLHDkGQyxac++UlmZmbY3NwkFouRSqXZ3d19HCrQIB63lBTeHCU3nzh7lp/9mZ9hp1iUwrymce/ePWkx6zqabtDrdmUXEgplL4zC0aS8xMuVLljXOXz4MLlcThapYWKYEivXNI1QkxrX0JPUs26Y6IaJacaIx+PMzMwwPj7O8sqKBMx0XeFXJfdnqIiCzLn0RvEBy7aYnJxkZnaGC+fPU6tVef37r6sMiaZyNNJOt+L2SG5GBNlsjuPHT0gxV+2GwlCOAzHFKTpQ4hwcEw5YKgfuLF3TxOdtmhQKBZ5917sIg5B2u80P/vqviULQTU11bIJRODJoyfrSNI0zZ88yqwJ/jUYDNI233rqm7tXjVrl+EHNQERBdNzh/7hwnT55E0zQKhYISsEWyblQtM/AFcyLFXUGruK7L+9//AjPT0zx1+TKeN+Tho0ejTBe6ThRG9Af9UfLZMAwxdeoaFy6c58033mBtdVXa/wp1msmmcZMJKtXqCP8wNj7Gs888y/Hjx+Ul3Wo2o739UtTv9ZicmuTNN97kzJkzI1IVClhcr8rMSoQGQcCffONPOH7i+CjC/uDhA3EHHTBfDNletdttapUyGAYEAbdu3eRb3yqQTKbUIvR4+PABrUYDDB2CkLhtE4YhrVaTWqWCZhhEgdR//vK7f8n1a9eINAiDkHfeeYdWo0FL1yWDoyGJ3loV1E2NgoBXX32V/f190V7GTFZXV9na2sT3JBuiGQLNPuC6tFpNBoMBmibt80athmboimcCv/PSS8zOzjAYSPF28c4ixd3i3znDymLv9XvUq1Xq6vdbXFzkm9/8prTjlSxucXGRfrdLfzCAICCbF9p7q92iUa+Nrr8/GPDNb36TZCo5GutfX1+j3WzKmzQMiSZk99ZuNOiq6yEM+caffoM7dxcZ9PrE4jGWl5dZXVuVCWCVnYmCQNxHQ0EieN5QebD6VEpl+T2Q9fCHf/SHzM/Pjwj/GxsblCsVVDUZN50GTUGna1WaTbmGhw8f8sorr2ApN/VwOGR5ZZlep02v24EoojAxSRCGNJsywtLUZM31+n1e+bNXSCaTmKZJr9fn4cOHNGo1YXSGgsVIp9PUa5XRz4giXn75ZU6ePDHarS4tLbG+voqwUo3Rnzt4ILdaLRHFAb1en2a9hq5yO3cW7/Dy176GpbAfvV6XtfU16rXqaJ1ncjmiKBQXU7kkP48i/uzPXuH48eP4vuR/br9zi3J5Xx4uKpOTTEpattVsMhwMRrvi77z2Kisry6Ns2MOHjygWd0a/t7B3BM9QKUttiTBk8e4ir732Kq7rYqrA6507d0bfkYN7lkpnRineMAw5cuQIn/zUp7Btm8Afsrlb5dH6PkdnCjxxIU066QpDWLmXdF1nf2+fv/nbv4m84ZCV5eVI+4+//sW/qTcb7wnVlmpra4snn3yS02dOUylX+MpXvkK1IjT8VDJJu9MhZsao1WqYpil0c/X2POjUaMgsSDqdJh6P0VXzG41GHcdJiDI09NVsiwCMdU0fQZYMwyCXy9Pv99jb2yWbzYlDWE2g9lSBrNlqYlnWKKp8UCSMxePU6lWGg+HIUnnwIGi32zgJR725FAgqCJTJUOP4yRP85E++yNde/iof++jHuP/gPq+9+iqObatr6WHoxihPE4RSLzENA88bjvJAQRBw6NAhNE2jWq3iODalcoV8Lke1VsVxHCl0DjySqSTNpkjIwyjETbgcOnyY9fU1Op3OaOiwkC/Q7rQJgoCE0rrm83kBGekGjuNgmgbecEiz2ZQ3SmFMBuk04fju7O4wPjYuRgLXlfi7J7u+/f09nv+x9/GhD36Il373JT732c9x795d/p8//3PVPYFmUz7zvd09xsbGCEIZxItCJGXtJGio4/LTTz/N1tYmjUYTNKhWq0yMj1MqlVS3TKPZbJDPF2QmLZUU20M8RjxuUa1VGXoeuWxWwEaZLP1+j0ajSTKZpFgsMjc3C8pQoGsaummgabrsUojkuOR5o2xKVfFg2u02uWx29MA0TZNms8kLH/wgCwsLvPLKK/yDn/5pbt26xfe++z3icQm0ecoN1Go2SSZTBFGAqcsusN/rKYOlHM+mp6ep1WqqEA69Xk/YP92usIt8H6IQ101Sq9XIZuX68oUCsVicvb1dTMPENE1RpCipPVGE7dj0un3y+Rzdbk+NWQiA3kk4tJot0BixZAI/IAgDWq0242MFhr5P0nXpq5a1jBr0mJye5hd/8RdJq4HjgwS6aRrsVpps7FRJJWzG8knGMi6BAlYJvFyOcW/feFsK9eVy3Uylk3/TbrdmM/l82ozFwnPnz2tuwmVtdY1IvRHKlTLpdAZvKKQyTdeJ25aIpRTW4SDOjYI/a6HG9s422VwOx04QRKGkN2MmbjJJGITE4jEGg6GwYZCXyYFs7cY7N9UZW24sui5bbCuOEYthmAa2P1StTgNNZ3QD9tbWmJ6exmNIEEYYpo7tOBLPB8x4XB3JZDuOkn/3ez38IGR7a5Nv/8W3uHzpMt1ul1arSSKRwFPHBNPUpa6STNH3ZHGKTSCQXZNhoEUhdx/cJ5/LkXCThBGSIo7FcFVuQ9c0NHUE0nU5Ipm6Sbff4/Xv/xVjY3msuEUQCD1NNw2SqdQo0GT3+xixGCHyxYrF47RabTY2N5iZmabXHxCEIbphKAmYidNKErcsQkA3TfksoxBNN0bJ3u2dbV799rf46E/8BHt7e1TrNWZnZ+l1e3Js0A3shIOTcBl4A0xTIujdvrxtDdNk4A957bt/ST6fJ5VKSwLajGGYJgk3SVKBruTnIsozzRhmzKTVbrO19YDpqSkpHoby/zRMAyfhMlRWBcdNYKjYgWHKMa1er1Or15mcmGQ4FGSkbhhYji2O66FH3LKIDT10lYaVY3+MCJmz29jc4Fvf/hbPP/ccO8UirVaTwtgYw+FAUuSmiZNwSbgJhT8QEh+6AYaOgUlv0OfqtWtMT08Ri8WEEKnJOtQMA9uyGHgDoSAaOkbMRDcNzJhFpVplv1RivDBGZAj9TtPl76JA4zEzhh9EaIaBYcr3IUacRqvFdrHI+Ni4bIoijVgsjmVJGjoCLNsh6PXke2OaaERiQ6jX0DSNWlUyNAdT1Qe9bk2HyZROEHZpVro0K48DvJpCSsbjcU4cPxE5jqP5/rD6/wMtIU1IejCI8wAAAABJRU5ErkJggg==",
    "Ceres DBox (1U)": "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",
    "MLK DBox (2U)": "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",
    "GEN5 Genoa CNode": "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",
    "GEN6 Turin CNode": "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",
    "Ceres 338TB (1U)": "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",
    "Ceres 1350TB (1U)": "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",
    "Ceres 2700TB (1U)": "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",
    "MLK 1350TB (2U)": "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",
    "MLK 2700TB (2U)": "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",
    "MLK 5400TB (2U)": "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",
    "GEN5 Genoa": "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",
    "GEN6 Turin": "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",
    "Arista 7060DX5-64S": "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",
}
# Device image filename mapping (images/ folder mounted in container)
DEVICE_IMAGE_MAP = {
    "NVIDIA SN3700":       "NVIDIA_SN3700.png",
    "NVIDIA SN4600":       "NVIDIA_SN4600.png",
    "NVIDIA SN4700":       "NVIDIA_SN4700.png",
    "NVIDIA SN5400":       "NVIDIA_SN5400.png",
    "NVIDIA SN5600":       "NVIDIA_SN5600.png",
    "NVIDIA SN5610":       "NVIDIA_SN5610.png",
    "Arista 7050CX4-24D8": "Arista_7050CX4-24D8.png",
    "Arista 7050DX4-32S":  "Arista_7050DX4-32S.png",
    "Arista 7060DX5-32S":  "Arista_7060DX5-32S.png",
    "Arista 7060DX5-64S":  "Arista_7060DX5-64S.png",
    "Ceres 338TB (1U)":    "Ceres_338TB_1U.png",
    "Ceres 1350TB (1U)":   "Ceres_1350TB_1U.png",
    "Ceres 2700TB (1U)":   "Ceres_2700TB_1U.png",
    "MLK 1350TB (2U)":     "MLK_1350TB_2U.png",
    "MLK 2700TB (2U)":     "MLK_2700TB_2U.png",
    "MLK 5400TB (2U)":     "MLK_5400TB_2U.png",
    "GEN5 Genoa":          "GEN5_Genoa_CNode.png",
    "GEN6 Turin":          "GEN6_Turin_CNode.png",
}

def _get_device_img_b64(device_key):
    """Load device image as base64 for SVG embedding. Returns None if unavailable."""
    import base64 as _b64mod, os as _os
    fname = DEVICE_IMAGE_MAP.get(device_key)
    if not fname:
        return None
    img_path = f"/app/images/{fname}"
    if not _os.path.exists(img_path):
        return None
    try:
        with open(img_path, "rb") as fh:
            return _b64mod.b64encode(fh.read()).decode()
    except Exception:
        return None


@st.cache_data(max_entries=50, show_spinner=False)
def _strip_white_bg(b64_str):
    """Return a base64 PNG with near-white pixels made transparent. Cached across reruns."""
    try:
        import numpy as _np
        from PIL import Image as _PILI
        import io as _pio, base64 as _pb64
        _img = _PILI.open(_pio.BytesIO(_pb64.b64decode(b64_str))).convert("RGBA")
        _arr = _np.array(_img, dtype=_np.uint8)
        _white = (_arr[:, :, 0] > 200) & (_arr[:, :, 1] > 200) & (_arr[:, :, 2] > 200)
        _arr[_white, 3] = 0
        _out = _pio.BytesIO()
        _PILI.fromarray(_arr).save(_out, format="PNG")
        return _pb64.b64encode(_out.getvalue()).decode()
    except Exception:
        return b64_str


@st.cache_data(max_entries=20, show_spinner=False)
def _svg_to_pdf_cached(svg_str, out_w, out_h):
    """Convert SVG string to PDF bytes via cairosvg. Cached — only reruns when SVG changes."""
    import cairosvg as _cairosvg
    import io as _io
    buf = _io.BytesIO()
    _cairosvg.svg2pdf(bytestring=svg_str.encode(), write_to=buf,
                      output_width=out_w, output_height=out_h)
    return buf.getvalue()


@st.cache_data(max_entries=20, show_spinner=False)
def _svg_to_jpg_cached(svg_str, out_w, out_h):
    """Convert SVG string to JPEG bytes via cairosvg. Cached — only reruns when SVG changes."""
    import cairosvg as _cairosvg
    from PIL import Image as _PILImage
    import io as _io
    png_buf = _io.BytesIO()
    _cairosvg.svg2png(bytestring=svg_str.encode(), write_to=png_buf,
                      output_width=out_w, output_height=out_h)
    png_buf.seek(0)
    img = _PILImage.open(png_buf).convert("RGBA")
    white_bg = _PILImage.new("RGBA", img.size, (255, 255, 255, 255))
    white_bg.paste(img, mask=img.split()[3])
    jpg_buf = _io.BytesIO()
    white_bg.convert("RGB").save(jpg_buf, format="JPEG", quality=92)
    return jpg_buf.getvalue()


@st.cache_data(max_entries=5, show_spinner=False)
def _build_multipage_pdf(svg_strs, paper_w, paper_h):
    """One rack per PDF page. svg_strs must be a tuple (hashable for Streamlit cache)."""
    import cairosvg as _cairosvg
    from PIL import Image as _PILImage
    import io as _io
    page_imgs = []
    for svg in svg_strs:
        buf = _io.BytesIO()
        _cairosvg.svg2png(bytestring=svg.encode(), write_to=buf,
                          output_width=int(paper_w), output_height=int(paper_h))
        buf.seek(0)
        page_imgs.append(_PILImage.open(buf).copy().convert("RGB"))
    if not page_imgs:
        return b""
    pdf_buf = _io.BytesIO()
    page_imgs[0].save(pdf_buf, format="PDF", resolution=150,
                      save_all=True, append_images=page_imgs[1:])
    return pdf_buf.getvalue()


@st.cache_data(max_entries=5, show_spinner=False)
def _build_consolidated_pdf(svg_strs, paper_w, paper_h):
    """All racks side-by-side on a single landscape page, top-aligned so rack
    bodies sit at a uniform level and summaries hang below each rack."""
    import cairosvg as _cairosvg
    from PIL import Image as _PILImage
    import io as _io
    HGAP = 30
    V_MARGIN = 24   # top and bottom margin in output pixels
    rack_imgs = []
    for svg in svg_strs:
        buf = _io.BytesIO()
        _cairosvg.svg2png(bytestring=svg.encode(), write_to=buf)
        buf.seek(0)
        rack_imgs.append(_PILImage.open(buf).copy())
    if not rack_imgs:
        return b""
    max_h   = max(img.height for img in rack_imgs)
    total_w = sum(img.width  for img in rack_imgs) + HGAP * (len(rack_imgs) - 1)
    # Scale to fit within page, reserving vertical margins
    scale = min(paper_w / total_w, (paper_h - 2 * V_MARGIN) / max_h)
    # Centre the rack group horizontally
    scaled_total_w = sum(int(img.width * scale) for img in rack_imgs) + int(HGAP * scale) * (len(rack_imgs) - 1)
    x = int((paper_w - scaled_total_w) / 2)
    canvas = _PILImage.new("RGB", (int(paper_w), int(paper_h)), (255, 255, 255))
    for img in rack_imgs:
        nw, nh = int(img.width * scale), int(img.height * scale)
        rgba = img.convert("RGBA").resize((nw, nh), _PILImage.Resampling.LANCZOS)
        bg = _PILImage.new("RGBA", (nw, nh), (255, 255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[3])
        # Top-align all racks at the same y so rack bodies are level;
        # summaries of different lengths extend naturally downward.
        canvas.paste(bg.convert("RGB"), (x, V_MARGIN))
        x += nw + int(HGAP * scale)
    pdf_buf = _io.BytesIO()
    canvas.save(pdf_buf, format="PDF", resolution=150)
    return pdf_buf.getvalue()

# Data reduction estimates by use case (min, typical, max multiplier)
DR_ESTIMATES = {
    "AI Training / Inference":  (1.0, 1.2, 1.5),
    "HPC":                      (1.0, 1.3, 2.0),
    "Video":                    (1.0, 1.1, 1.3),
    "Backup / Archive":         (1.5, 2.5, 4.0),
    "Enterprise (Mixed)":       (1.5, 2.0, 3.0),
    "Genomics":                 (1.2, 1.8, 2.5),
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_sw_suffix(model_key):
    if "NVIDIA" in model_key or "Mellanox" in model_key:
        return "NVIDIA"
    elif "Arista" in model_key:
        return "ARISTA"
    return "SW"


def get_port_mappings(side, num_dboxes, num_cnodes, dnode_start,
                      cnode_start, pfx="VAST",
                      dbox_label="DBOX", dnode_label="DNODE",
                      cnode_label="CNODE"):
    mappings = []
    port_side = "1" if side == "A" else "2"

    for i in range(1, num_dboxes + 1):
        for dnode_idx in range(1, 3):
            swp_num = dnode_start + (i - 1) * 2 + (dnode_idx - 1)
            mappings.append({
                "port":  swp_num,
                "swp":   f"swp{swp_num}",
                "eth":   f"Ethernet{swp_num}",
                "desc":  (
                    f"{pfx}-{dbox_label}-{i}-"
                    f"{dnode_label}-{dnode_idx}-P{port_side}"
                ),
                "dbox":  i,
                "dnode": dnode_idx,
                "type":  "dnode"
            })

    for i in range(1, num_cnodes + 1):
        swp_num = cnode_start + (i - 1)
        mappings.append({
            "port":  swp_num,
            "swp":   f"swp{swp_num}",
            "eth":   f"Ethernet{swp_num}",
            "desc":  f"{pfx}-{cnode_label}-{i}-P{port_side}",
            "cnode": i,
            "type":  "cnode"
        })

    return mappings


def validate_port_counts(num_dboxes, num_cnodes, dnode_start,
                         cnode_start, profile):
    errors   = []
    warnings = []

    total_dnode_ports = num_dboxes * 2
    total_cnode_ports = num_cnodes
    dnode_end = dnode_start + total_dnode_ports - 1
    cnode_end = cnode_start + total_cnode_ports - 1
    isl_start = min(profile["default_isl"])

    if dnode_end >= cnode_start:
        errors.append(
            f"❌ DNode ports (swp{dnode_start}–swp{dnode_end}) "
            f"overlap with CNode start (swp{cnode_start}). "
            f"Reduce DBox count or adjust port ranges."
        )

    if cnode_end >= isl_start:
        errors.append(
            f"❌ CNode ports (swp{cnode_start}–swp{cnode_end}) "
            f"overflow into ISL/Uplink range (swp{isl_start}+). "
            f"Reduce CNode count or adjust port ranges."
        )

    total_needed = total_dnode_ports + total_cnode_ports
    if total_needed > profile["max_node_ports"]:
        errors.append(
            f"❌ Total ports needed ({total_needed}) exceeds "
            f"available node ports ({profile['max_node_ports']}) "
            f"on this switch model."
        )
    elif total_needed > profile["max_node_ports"] * 0.85:
        warnings.append(
            f"⚠️ Using {total_needed} of {profile['max_node_ports']} "
            f"available ports "
            f"({int(total_needed/profile['max_node_ports']*100)}% capacity). "
            f"Limited room for expansion."
        )

    return errors, warnings


def render_cable_summary(profile, isl_short):
    supplier_ok   = "✅ VAST ships"
    supplier_warn = "⚠️ Customer/Partner must supply"

    if profile["customer_cables"]:
        st.error(
            "⚠️ **400G CUSTOMER-SUPPLIED CABLES REQUIRED** — "
            "This switch has 400GbE native ports. "
            "VAST does not ship 400G MPO cables. "
            "Customer or partner must supply all 400G cables "
            "**before install day.**"
        )

    isl_cable = (
        profile["isl_cable_short"] if isl_short
        else profile["isl_cable_long"]
    )

    st.table([
        {
            "Connection":  "DNode (BF-3) → Switch",
            "Cable":       profile["node_cable"]["spec"],
            "Supplied By": supplier_warn
                           if profile["node_cable"]["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
        {
            "Connection":  "CNode (CX7) → Switch",
            "Cable":       profile["node_cable"]["spec"],
            "Supplied By": supplier_warn
                           if profile["node_cable"]["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
        {
            "Connection":  f"ISL / Peerlink ({'≤1m' if isl_short else '>1m'})",
            "Cable":       isl_cable["spec"],
            "Supplied By": supplier_warn
                           if isl_cable["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
        {
            "Connection":  "Spine / Uplink",
            "Cable":       profile["spine_cable"]["spec"],
            "Supplied By": supplier_warn
                           if profile["spine_cable"]["supplier"] == "CUSTOMER"
                           else supplier_ok
        },
    ])


# ============================================================
# PENDING LOAD / CLEAR
# Must run before any widgets are instantiated so that
# session_state values are set before widgets read them.
# ============================================================
# Keys we save and restore — explicit whitelist.
# Excludes button/download_button keys which Streamlit forbids setting from code.
_SAVEABLE_PREFIXES = (
    "proj_", "tab7_", "tab8_", "spine_", "name_", "sizer_", "rack_",
)
_SAVEABLE_EXACT = {
    "se_name", "customer", "cluster_name", "install_date",
}
_SKIP_SUFFIXES = ("_dl_A", "_dl_B", "_dl_a", "_dl_b", "_download",
                  "_handoff_dl", "tab7_download", "tab8_download")
# Buttons, file_uploaders, and download_buttons whose keys start with rack_ but
# must NOT be restored from saved state (Streamlit forbids setting them via session_state).
_SKIP_EXACT = {
    "rack_cust_add", "rack_cust_img",
    "rack_cust_rm",   # prefix match handled below
    "rack_cust_name",  # old key — keep excluded for backward compat
    "rack_pick_add",
}
_SKIP_PREFIXES = (
    "rack_inv_add_", "rack_inv_del_",
    "rack_cust_rm_",
    "rack_dl_", "rack_gen_",
)

def _is_saveable(k):
    if k in _SAVEABLE_EXACT:
        return True
    if k in _SKIP_EXACT:
        return False
    if any(k.startswith(sp) for sp in _SKIP_PREFIXES):
        return False
    if any(k.startswith(p) for p in _SAVEABLE_PREFIXES):
        if any(k.endswith(s) or k == s for s in _SKIP_SUFFIXES):
            return False
        return True
    return False

_just_loaded = False
if "_pending_load" in st.session_state:
    _pending = st.session_state.pop("_pending_load")
    for _k, _v in _pending.items():
        if _is_saveable(_k):
            st.session_state[_k] = _v
    if "_db_project_id" in _pending:
        st.session_state["_db_project_id"] = _pending["_db_project_id"]
    _just_loaded = True

# Purge any button/file_uploader/download_button keys that may have
# leaked into session_state from an old project snapshot saved while a
# widget was active. Streamlit forbids setting these keys programmatically.
# Only run during project loads — running unconditionally would delete button
# click state before widgets get to read it, making those buttons silently fail.
if _just_loaded:
    for _wk in list(st.session_state.keys()):
        if _wk in _SKIP_EXACT or any(_wk.startswith(_sp) for _sp in _SKIP_PREFIXES):
            del st.session_state[_wk]

# Deferred rack-device removal: button sets _pending_rack_rm index, we apply
# it here (before widgets render) then clear the button states so the click
# is not replayed on subsequent reruns triggered by st.rerun().
if "_pending_rack_rm" in st.session_state:
    _rm_idx = st.session_state.pop("_pending_rack_rm")
    _cur_devs = st.session_state.get("rack_custom_devices", [])
    st.session_state["rack_custom_devices"] = [
        d for i, d in enumerate(_cur_devs) if i != _rm_idx
    ]
    for _wk in list(st.session_state.keys()):
        if _wk.startswith("rack_cust_rm_"):
            del st.session_state[_wk]

# Deferred rack-device add: button stages _pending_rack_add dict, we apply
# it here so we can also pre-set the rack placement widget key (rack_rack_*)
# before the widget renders, and clear rack_pick_add to prevent cascading.
if "_pending_rack_add" in st.session_state:
    _pa = st.session_state.pop("_pending_rack_add")
    _pa_devs = list(st.session_state.get("rack_custom_devices", []))
    _pa_name = _pa["name"]
    _pa_base, _pa_idx = _pa_name, 1
    while any(d["name"] == _pa_name for d in _pa_devs):
        _pa_name = f"{_pa_base}-{_pa_idx}"
        _pa_idx += 1
    _pa_devs.append({
        "name":         _pa_name,
        "product_name": _pa["product_name"],
        "u":            _pa["u"],
        "weight_lbs":   _pa["weight_lbs"],
        "avg_w":        _pa["avg_w"],
        "max_w":        _pa["max_w"],
        "img_b64":      _pa["img_b64"],
    })
    st.session_state["rack_custom_devices"] = _pa_devs
    # Pre-set rack assignment so the placement selectbox starts on the right rack
    _pa_rack_key = "rack_rack_" + _pa_name.replace(" ", "_").replace("-", "_")
    st.session_state[_pa_rack_key] = _pa["rack_no"]
    # Clear add-button state to prevent this from firing again on next rerun
    if "rack_pick_add" in st.session_state:
        del st.session_state["rack_pick_add"]

if "_pending_clear" in st.session_state:
    st.session_state.pop("_pending_clear")
    _internal = {k: v for k, v in st.session_state.items()
                 if k.startswith("_") and k != "_db_project_id"}
    st.session_state.clear()
    st.session_state.update(_internal)
    st.session_state["_db_project_id"] = None
    # Explicitly reset all proj_ and tab5_/tab6_ keys to defaults.
    # This runs before any widget renders so Streamlit accepts it.
    _str_defaults = [
        "proj_psnt", "proj_license", "proj_sfdc", "proj_ticket",
        "proj_slack", "proj_lucid", "proj_survey", "proj_peer_rev",
        "proj_install_guide", "proj_vast_release", "proj_os_version",
        "proj_bundle",
        "proj_nb_mtu", "proj_gpu_servers", "proj_site_notes",
        "proj_ip_notes",
        "tab7_sw_a_ip", "tab7_sw_b_ip", "tab7_gw", "tab7_ntp",
        "tab7_isl", "tab7_uplink", "tab7_vlan",
        "tab8_sw_a_ip", "tab8_sw_b_ip", "tab8_gw", "tab8_ntp",
        "tab8_isl", "tab8_uplink", "tab8_vlan",
    ]
    for _k in _str_defaults:
        st.session_state[_k] = ""
    _bool_defaults = [
        "proj_phison", "proj_dual_nic", "proj_dbox_ha",
        "proj_encryption", "proj_ip_conflict",
        "tab7_isl_short", "tab8_enabled", "tab8_isl_short",
    ]
    for _k in _bool_defaults:
        st.session_state[_k] = False
    st.session_state["proj_num_dboxes"] = 1
    st.session_state["proj_num_cnodes"] = 4
    st.session_state["tab7_mgmt_vlan"]  = 1
    st.session_state["tab8_mgmt_vlan"]  = 1
    st.session_state["tab8_vlans"]      = ""
    st.session_state["sizer_drr_override"] = 0.0
    st.session_state["sizer_num_dboxes"]   = 1
    st.session_state["sizer_num_cnodes"]   = 4

# ============================================================
# SIDEBAR — persistent status bar
# ============================================================
with st.sidebar:
    st.markdown("## ⚡ VAST Data")
    st.markdown("**SE Installation Toolkit**")
    st.markdown("---")

    _sb_se       = st.session_state.get("se_name",      "—")
    _sb_customer = st.session_state.get("customer",     "—")
    _sb_cluster  = st.session_state.get("cluster_name", "—")
    _sb_date     = st.session_state.get("install_date", "—")
    _sb_proj_id  = st.session_state.get("_db_project_id")
    _sb_milestone= st.session_state.get("_save_milestone", "—")

    st.markdown(f"👤 **{_sb_se}**")
    st.markdown(f"🏢 {_sb_customer}")
    st.markdown(f"🖥️  {_sb_cluster}")
    st.markdown(f"📅 {_sb_date}")
    st.markdown("---")

    if _sb_proj_id:
        st.markdown(f"💾 Project **#{_sb_proj_id}**")
        st.markdown(f"🏷️  {_sb_milestone}")
        if _DB_AVAILABLE:
            try:
                # Cache version info — only re-query when project or save milestone changes
                _sb_ver_ck = f"_sb_ver_{_sb_proj_id}_{_sb_milestone}"
                if _sb_ver_ck not in st.session_state:
                    # Clear any stale version cache entries
                    for _vk in [k for k in st.session_state if k.startswith("_sb_ver_")]:
                        del st.session_state[_vk]
                    _sb_vs = _db.get_project_versions(_sb_proj_id)
                    st.session_state[_sb_ver_ck] = _sb_vs[0] if _sb_vs else None
                _sb_latest = st.session_state[_sb_ver_ck]
                if _sb_latest:
                    st.caption(f"v{_sb_latest['version_num']} · {_sb_latest['saved_at'][:16].replace('T', ' ')}")
            except Exception:
                pass
    else:
        st.caption("💾 Unsaved project")

    st.markdown("---")

    if "_online_status" not in st.session_state:
        try:
            requests.get("https://www.google.com", timeout=3)
            st.session_state["_online_status"] = True
        except Exception:
            st.session_state["_online_status"] = False

    if st.session_state.get("_online_status"):
        st.markdown("🟢 Online")
    else:
        st.markdown("🔴 Offline")

    st.markdown("---")
    st.caption("⚡ VAST SE Toolkit v1.2.0")
    st.caption(f"📅 {date.today().strftime('%d %B %Y')}")



# ── Always-available derived values ─────────────────────────
# These read from session_state with safe defaults so that
# all tabs work correctly even before Tab 1 has been filled in.

pfx          = st.session_state.get("cluster_name", "") or "VAST"
num_dboxes   = int(st.session_state.get("proj_num_dboxes",  1))
num_cnodes   = int(st.session_state.get("proj_num_cnodes",  4))
topology     = st.session_state.get("proj_topology", "Leaf Pair")

# Naming convention values (set in Tabs 5/6, defaulted here)
include_ru   = st.session_state.get("include_ru", False)
dbox_label   = st.session_state.get("name_dbox",  "DBOX")
dnode_label  = st.session_state.get("name_dnode", "DNODE")
cnode_label  = st.session_state.get("name_cnode", "CNODE")

dbox_ru_raw  = st.session_state.get("dbox_ru_raw",  "")
cnode_ru_raw = st.session_state.get("cnode_ru_raw", "")
dbox_ru_list = [l.strip() for l in dbox_ru_raw.split("\n")  if l.strip()]
cnode_ru_list= [l.strip() for l in cnode_ru_raw.split("\n") if l.strip()]

sw1_ru       = st.session_state.get("sw1_ru",      "")
sw2_ru       = st.session_state.get("sw2_ru",      "")

# Switch model for suffix
sw_model_current = st.session_state.get(
    "tab7_sw_model", list(HARDWARE_PROFILES.keys())[0]
)
vendor_suffix = get_sw_suffix(sw_model_current)


def _build_sw_name(sw_num, ru_val, vendor_sfx, gpu=False, spine=False):
    parts = [pfx, vendor_sfx]
    if include_ru and ru_val:
        parts.append(f"U{ru_val}")
    if spine:
        parts.append(f"SPINE-SW{sw_num}")
    else:
        parts.append(f"SW{sw_num}")
    name = "-".join(parts)
    if gpu:
        name += "-GPU"
    return name


full_sw_a = _build_sw_name(1, sw1_ru, vendor_suffix)
full_sw_b = _build_sw_name(2, sw2_ru, vendor_suffix)

# Always-available identity values — read from session_state
# so all tabs can reference them regardless of render order.
se_name      = st.session_state.get("se_name",      "")
customer     = st.session_state.get("customer",     "")
cluster_name = st.session_state.get("cluster_name", "")
install_date = st.session_state.get("install_date", str(date.today()))


# ============================================================
# MAIN HEADER
# ============================================================
st.title("⚡ VAST SE Installation Toolkit")
_hdr_se   = st.session_state.get("se_name", "")
_hdr_cust = st.session_state.get("customer", "")
_hdr_clus = st.session_state.get("cluster_name", "")
_hdr_date = st.session_state.get("install_date", "")
if _hdr_se and _hdr_cust:
    st.markdown(
        f"**SE:** {_hdr_se} &nbsp;|&nbsp; "
        f"**Customer:** {_hdr_cust} &nbsp;|&nbsp; "
        f"**Cluster:** {_hdr_clus} &nbsp;|&nbsp; "
        f"**Date:** {_hdr_date}"
    )


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "🧑‍💻 Session",
    "📏 Capacity & Performance Sizer",
    "📋 Project Details",
    "📄 Confluence Install Plan",
    "✅ Validation & Pre-Flight",
    "📋 Installation Procedure",
    "🔌 Internal Switch — Southbound",
    "🖥️ Data Switch — Northbound",
    "📐 Rack Diagram",
    "📦 Device Inventory",
    "🤖 AI Assistant"
])
#=============================================================
# ============================================================
# TAB 3 — PROJECT DETAILS
# ============================================================
with tab3:
    st.subheader("📋 Project Details")
    st.caption(
        "Complete all sections before generating configs or the install plan. "
        "Fields marked ⚠️ are required."
    )

    # ── Cluster Inventory ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📦 Cluster Inventory")

    inv_col1, inv_col2 = st.columns(2)
    with inv_col1:
        proj_num_dboxes = st.slider(
            "Number of DBoxes", min_value=1, max_value=14,
            key="proj_num_dboxes"
        )
    with inv_col2:
        proj_num_cnodes = st.slider(
            "Number of CNodes", min_value=1, max_value=28,
            key="proj_num_cnodes"
        )

    # ── Topology ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🌐 Deployment Topology")

    proj_topology = st.radio(
        "Select topology",
        options=["Leaf Pair", "Spine-Leaf"],
        horizontal=True,
        key="proj_topology"
    )
    if proj_topology == "Spine-Leaf":
        st.info(
            "**Spine-Leaf mode** — Leaf switches connect to nodes. "
            "Spine switches provide the uplink fabric. "
            "Both leaf and spine run as MLAG pairs. "
            "Spine must be same vendor and equal or greater speed than leaf."
        )

    # ── Opportunity Links ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔗 Links & Identity")

    link_col1, link_col2 = st.columns(2)
    with link_col1:
        proj_psnt    = st.text_input("System PSNT",
                         placeholder="e.g. VARW255117024",
                         key="proj_psnt")
        proj_license = st.text_input("License Key",
                         placeholder="e.g. LS-003197",
                         key="proj_license")
    with link_col2:
        proj_lucid    = st.text_input("Lucidchart URL",
                          placeholder="https://lucid.app/lucidchart/…",
                          key="proj_lucid")
        proj_survey   = st.text_input("Site Survey URL",
                          placeholder="https://docs.google.com/spreadsheets/…",
                          key="proj_survey")
        proj_peer_rev = st.text_input("PreSales Peer Reviewer",
                          placeholder="e.g. Eric ElMasry",
                          key="proj_peer_rev")
        proj_guide    = st.text_input("VAST Install Guide URL",
                          placeholder="https://kb.vastdata.com/docs/…",
                          key="proj_install_guide")

    # ── Software Versions ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 Software Versions")
    st.caption("Find latest approved releases on the [FIELD dashboard](https://vastdata.atlassian.net/wiki/spaces/FIELD).")

    ver_col1, ver_col2 = st.columns(2)
    with ver_col1:
        proj_release  = st.text_input("VAST Release",
                          placeholder="e.g. 5.4.1-sp4",
                          key="proj_vast_release")
        proj_os_ver   = st.text_input("VastOS Version",
                          placeholder="e.g. 12.15.15-2123585",
                          key="proj_os_version")
    with ver_col2:
        proj_bundle   = st.text_input("Bundle Version",
                          placeholder="e.g. release-5.4.1-sp4-2248419",
                          key="proj_bundle")
        proj_phison   = st.toggle("PHISON drives present",
                          value=False, key="proj_phison")
        if proj_phison:
            st.warning("⚠️ PHISON drives require FW update check before install.")

    # ── Hardware Details ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🖥️ Hardware Details")

    hw_col1, hw_col2 = st.columns(2)
    with hw_col1:
        _dbox_options = list(DBOX_PROFILES.keys())
        _dbox_current = st.session_state.get("proj_dbox_type", _dbox_options[0])
        if _dbox_current not in _dbox_options:
            _dbox_current = _dbox_options[0]
        proj_dbox_type = st.selectbox(
            "DBox Model",
            options=_dbox_options,
            index=_dbox_options.index(_dbox_current)
        )
        st.session_state["proj_dbox_type"] = proj_dbox_type

        _cnode_options = list(CNODE_PERF.keys())
        _cnode_raw = st.session_state.get("proj_cbox_type", _cnode_options[0])
        _cnode_current = _cnode_raw.replace(" CNode", "").strip()
        if _cnode_current not in _cnode_options:
            _cnode_current = _cnode_options[0]
        proj_cbox_type = st.selectbox(
            "CNode Generation",
            options=_cnode_options,
            index=_cnode_options.index(_cnode_current)
        )
        st.session_state["proj_cbox_type"] = proj_cbox_type
        proj_dual_nic   = st.toggle("CNodes have Dual NIC",
                            value=False, key="proj_dual_nic")
        if proj_dual_nic:
            st.caption(
                "Right port (BF-3) → Internal Switch (Tab 7) for storage.  \n"
                "Left port (CX7) → Data Switch (Tab 8) for client traffic.  \n"
                "Uplinks removed from Tab 7 storage switch config."
            )
    with hw_col2:
        proj_ipmi       = st.selectbox("IPMI Configuration",
                            options=["Outband (Cat6)", "B2B (Back-to-Back)"],
                            key="proj_ipmi")
        proj_second_nic = st.selectbox("Second NIC Use (Dual NIC only)",
                            options=["N/A",
                                     "Split Ethernet (GPU/Client traffic)",
                                     "Northband mgmt bond"],
                            key="proj_second_nic")
        proj_nb_mtu     = st.text_input("Northbound MTU (if second NIC)",
                            value="9000", key="proj_nb_mtu")
        proj_gpu_svrs   = st.text_input("GPU Servers (count + type)",
                            placeholder="e.g. 8x Dell R760xa (4x L40S each)",
                            key="proj_gpu_servers")

    # ── Cluster Configuration ────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚙️ Cluster Configuration")

    cfg_col1, cfg_col2 = st.columns(2)
    with cfg_col1:
        proj_dbox_ha    = st.toggle("DBox HA enabled",
                            value=False, key="proj_dbox_ha")
        proj_encryption = st.toggle("Encryption at Rest",
                            value=False, key="proj_encryption")
    with cfg_col2:
        proj_similarity = st.selectbox("Similarity",
                            options=["Yes w/ Adaptive Chunking (Default)", "No"],
                            key="proj_similarity")
        proj_ip_conflict= st.toggle("Internal IP range conflict with customer",
                            value=False, key="proj_ip_conflict")
        if proj_ip_conflict:
            proj_ip_notes = st.text_input("Alternative IP range",
                               placeholder="e.g. 10.10.128.0/18",
                               key="proj_ip_notes")

    # ── Site Notes ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📝 Site Notes")

    proj_site_notes = st.text_area(
        "Site Overview / Important Notes",
        placeholder=(
            "e.g. Cluster installed in shipping container DC.\n"
            "GPUaaS POC. 8x GPU servers with 4x L40S each.\n"
            "Network design: NVMe Ethernet for data and client traffic."
        ),
        key="proj_site_notes",
        height=150
    )

    # ── Completeness indicator ───────────────────────────────
    st.markdown("---")
    required = {
        "Customer Name":    st.session_state.get("customer",          ""),
        "Cluster Name":     st.session_state.get("cluster_name",      ""),
        "SE Name":          st.session_state.get("se_name",           ""),
        "System PSNT":      st.session_state.get("proj_psnt",         ""),
        "License Key":      st.session_state.get("proj_license",      ""),
        "VAST Release":     st.session_state.get("proj_vast_release", ""),
        "VastOS Version":   st.session_state.get("proj_os_version",   ""),
        "Bundle Version":   st.session_state.get("proj_bundle",       ""),
        "SFDC URL":         st.session_state.get("proj_sfdc",         ""),
        "DBox Type":        st.session_state.get("proj_dbox_type",    ""),
        "CNode Type":       st.session_state.get("proj_cbox_type",    ""),
        "NTP Server":       st.session_state.get("tab7_ntp",          ""),
        "Site Notes":       st.session_state.get("proj_site_notes",   ""),
    }
    missing = [k for k, v in required.items() if not v]

    if missing:
        st.warning(
            f"⚠️ **{len(missing)} required field(s) not yet completed:**\n\n"
            + "\n".join(f"- {m}" for m in missing)
        )
    else:
        st.success("✅ Project Details complete — ready to generate configs and install plan.")


# TAB 7 — INTERNAL SWITCH — SOUTHBOUND
# ============================================================
with tab7:
    st.subheader("Internal Storage Fabric — Leaf Pair Configuration")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("#### Switch Selection")
        sw_model = st.selectbox(
            "Switch Model",
            options=list(HARDWARE_PROFILES.keys()),
            key="tab7_sw_model"
        )
        profile = HARDWARE_PROFILES[sw_model]

        st.info(
            f"**Vendor:** {profile['vendor'].capitalize()}  \n"
            f"**OS:** {'Cumulus NV' if profile['os'] == 'cumulus' else 'Arista EOS'}  \n"
            f"**Ports:** {profile['total_ports']}  \n"
            f"**Speed:** {profile['native_speed']}  \n"
            f"**Form Factor:** {profile['form_factor']}  \n"
            f"**MTU:** {profile['mtu']}  \n"
            f"**Notes:** {profile['notes']}"
        )

        st.markdown("#### Port Reservation")
        dnode_start = st.number_input(
            "DNode start port", min_value=1,
            max_value=profile["total_ports"], value=1,
            key="tab7_dnode_start"
        )
        cnode_start = st.number_input(
            "CNode start port", min_value=1,
            max_value=profile["total_ports"],
            value=15 if profile["total_ports"] == 32 else 29,
            key="tab7_cnode_start"
        )

        st.markdown("#### Switch Networking")
        vlan_id = st.number_input(
            "Storage VLAN ID", min_value=1, max_value=4094,
            value=100, key="tab7_vlan"
        )
        sw_a_ip = st.text_input(
            "Switch A MGMT IP/mask", value="192.168.1.1/24",
            key="tab7_sw_a_ip"
        )
        sw_b_ip = st.text_input(
            "Switch B MGMT IP/mask", value="192.168.1.2/24",
            key="tab7_sw_b_ip"
        )
        mgmt_gw = st.text_input(
            "MGMT Gateway", value="192.168.1.254", key="tab7_gw"
        )
        mgmt_vlan = st.number_input(
            "Management VLAN ID", min_value=1, max_value=4094,
            value=int(st.session_state.get("tab7_mgmt_vlan", 1)),
            key="tab7_mgmt_vlan"
        )
        ntp_srv = st.text_input(
            "NTP Server", value="",
            placeholder="Enter customer NTP server IP",
            key="tab7_ntp"
        )

        st.markdown("#### ISL / Uplink Ports")
        isl_ports_input = st.text_input(
            "ISL Ports (comma separated)",
            value=",".join([f"swp{p}" for p in profile["default_isl"]]),
            key="tab7_isl"
        )
        uplink_ports_input = st.text_input(
            "Uplink Ports (comma separated)",
            value=",".join([f"swp{p}" for p in profile["default_uplink"]]),
            key="tab7_uplink"
        )
        isl_short = st.toggle(
            "ISL cable run is ≤1m (use DAC)",
            value=False, key="tab7_isl_short"
        )

    with col_right:

        errors, warnings = validate_port_counts(
            num_dboxes, num_cnodes,
            dnode_start, cnode_start, profile
        )

        if errors:
            for e in errors:
                st.error(e)

        for w in warnings:
            st.warning(w)

        if not ntp_srv:
            st.warning(
                "⚠️ NTP Server is empty. "
                "Confirm the customer NTP IP before applying config."
            )

        st.markdown("#### 📦 Cable Requirements")
        render_cable_summary(profile, isl_short)

        st.markdown("#### 🗺️ Port Mapping / Cabling Guide")
        table_map = get_port_mappings(
            "A", num_dboxes, num_cnodes, dnode_start, cnode_start,
            pfx=pfx, dbox_label=dbox_label,
            dnode_label=dnode_label, cnode_label=cnode_label
        )

        isl_list    = [p.strip() for p in isl_ports_input.split(",")]
        uplink_list = [p.strip() for p in uplink_ports_input.split(",") if p.strip()]

        # Dual NIC — second NIC handles client traffic via Tab 8 (Data Switch)
        # so the storage fabric switch does NOT need uplink ports to customer core.
        dual_nic = st.session_state.get("proj_dual_nic", False)
        if dual_nic:
            uplink_list = []
            st.info(
                "ℹ️ **Dual NIC mode** — uplink ports removed from storage fabric config. "
                "CNode right port (BF-3) connects to this switch for storage traffic. "
                "CNode left port (CX7) connects to the Data Switch (Tab 8) for client traffic."
            )

        table_rows = []
        for item in table_map:
            table_rows.append({
                "Switch Port (A)": item["swp"] if profile["os"] == "cumulus"
                                   else item["eth"],
                "Switch Port (B)": item["swp"] if profile["os"] == "cumulus"
                                   else item["eth"],
                "Device":          item["desc"].replace("-P1", ""),
                "NIC":             "BF-3 200GbE" if item["type"] == "dnode"
                                   else "CX7 200GbE",
                "Cable":           profile["node_cable"]["spec"],
                "Supplied By":     profile["node_cable"]["supplier"]
            })

        for p in isl_list:
            isl_cable = (
                profile["isl_cable_short"] if isl_short
                else profile["isl_cable_long"]
            )
            table_rows.append({
                "Switch Port (A)": p,
                "Switch Port (B)": p,
                "Device":          "ISL / Peerlink",
                "NIC":             "—",
                "Cable":           isl_cable["spec"],
                "Supplied By":     isl_cable["supplier"]
            })

        for p in uplink_list:
            table_rows.append({
                "Switch Port (A)": p,
                "Switch Port (B)": p,
                "Device":          "Uplink to Customer Core",
                "NIC":             "—",
                "Cable":           profile["spine_cable"]["spec"],
                "Supplied By":     profile["spine_cable"]["supplier"]
            })

        st.dataframe(table_rows, use_container_width=True)

        st.markdown("#### ⚙️ Generated Switch Configurations")

        env       = Environment(loader=FileSystemLoader("templates"))
        tmpl_file = (
            "cumulus_nv.j2" if profile["os"] == "cumulus"
            else "arista_eos.j2"
        )

        try:
            template = env.get_template(tmpl_file)
        except Exception:
            st.error(
                f"Template `{tmpl_file}` not found in /templates. "
                "Please create it to generate configs."
            )
            template = None

        if template:
            cfg_col_a, cfg_col_b = st.columns(2)

            for i, side in enumerate(["A", "B"]):
                port_map = get_port_mappings(
                    side, num_dboxes, num_cnodes,
                    dnode_start, cnode_start,
                    pfx=pfx, dbox_label=dbox_label,
                    dnode_label=dnode_label, cnode_label=cnode_label
                )
                context = {
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
                }
                config_text = template.render(context).replace('\r\n', '\n').replace('\r', '\n')

                with (cfg_col_a if side == "A" else cfg_col_b):
                    st.markdown(
                        f"**Switch {side}** "
                        f"({'Primary' if side == 'A' else 'Secondary'})"
                    )
                    st.code(config_text, language="bash")
                    st.download_button(
                        label=f"💾 Download Switch {side} Config",
                        data=config_text,
                        file_name=(
                            f"{pfx}_VAST_SW{side}_"
                            f"{profile['vendor'].upper()}_"
                            f"{date.today().isoformat()}.txt"
                        ),
                        mime="text/plain",
                        key=f"tab7_dl_{side}"
                    )

    # ── SPINE-LEAF SECTION ───────────────────────────────────
    if topology == "Spine-Leaf":
        st.markdown("---")
        st.markdown("### 🔺 Spine Switch Configuration")
        st.caption(
            "Spine switches provide the uplink fabric between leaf pairs "
            "and the customer core. Always deployed as a pair. "
            "Must be same vendor as leaf and equal or greater speed."
        )

        spine_col_left, spine_col_right = st.columns([1, 2])

        with spine_col_left:
            st.markdown("#### Spine Switch Selection")

            leaf_speed_rank = SPEED_RANK.get(profile["native_speed"], 1)
            leaf_vendor     = profile["vendor"]

            valid_spine_models = [
                m for m, p in HARDWARE_PROFILES.items()
                if SPEED_RANK.get(p["native_speed"], 1) >= leaf_speed_rank
                and p["vendor"] == leaf_vendor
            ]

            spine_model   = st.selectbox(
                "Spine Switch Model",
                options=valid_spine_models,
                key="spine_sw_model"
            )
            spine_profile = HARDWARE_PROFILES[spine_model]

            st.info(
                f"**Vendor:** {spine_profile['vendor'].capitalize()}  \n"
                f"**OS:** {'Cumulus NV' if spine_profile['os'] == 'cumulus' else 'Arista EOS'}  \n"
                f"**Ports:** {spine_profile['total_ports']}  \n"
                f"**Speed:** {spine_profile['native_speed']}  \n"
                f"**Form Factor:** {spine_profile['form_factor']}  \n"
                f"**MTU:** {spine_profile['mtu']}  \n"
                f"**Notes:** {spine_profile['notes']}"
            )

            st.markdown("#### Spine Port Reservation")
            num_leaf_pairs = st.number_input(
                "Number of Leaf Pairs",
                min_value=1, max_value=16, value=1,
                key="spine_num_leaf_pairs"
            )
            spine_downlink_start = st.number_input(
                "Downlink start port (to leaf switches)",
                min_value=1,
                max_value=spine_profile["total_ports"],
                value=1,
                key="spine_downlink_start"
            )
            spine_isl_ports_input = st.text_input(
                "Spine ISL ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in spine_profile["default_isl"]]
                ),
                key="spine_isl_ports"
            )
            spine_uplink_ports_input = st.text_input(
                "Uplink ports to customer core (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in spine_profile["default_uplink"]]
                ),
                key="spine_uplink_ports"
            )
            spine_isl_short = st.toggle(
                "Spine ISL cable run ≤1m (use DAC)",
                value=False,
                key="spine_isl_short"
            )

            st.markdown("#### Spine Networking")
            spine_a_ip = st.text_input(
                "Spine A MGMT IP/mask",
                value="192.168.3.1/24", key="spine_a_ip"
            )
            spine_b_ip = st.text_input(
                "Spine B MGMT IP/mask",
                value="192.168.3.2/24", key="spine_b_ip"
            )
            spine_mgmt_gw = st.text_input(
                "Spine MGMT Gateway",
                value="192.168.3.254", key="spine_mgmt_gw"
            )
            spine_ntp = st.text_input(
                "Spine NTP Server", value="",
                placeholder="Enter customer NTP server IP",
                key="spine_ntp"
            )

        with spine_col_right:

            if not spine_ntp:
                st.warning(
                    "⚠️ Spine NTP Server is empty. "
                    "Confirm the customer NTP IP before applying config."
                )

            if spine_profile["customer_cables"]:
                st.error(
                    f"⚠️ **{spine_model} requires customer-supplied "
                    f"400G cables.** Confirm all spine cables are "
                    f"on-site before install day."
                )

            spine_isl_cable = (
                spine_profile["isl_cable_short"] if spine_isl_short
                else spine_profile["isl_cable_long"]
            )

            st.markdown("#### 📦 Spine Cable Requirements")
            st.table([
                {
                    "Connection":  "Spine → Leaf downlinks",
                    "Cable":       spine_profile["spine_cable"]["spec"],
                    "Supplied By": spine_profile["spine_cable"]["supplier"]
                },
                {
                    "Connection":  f"Spine ISL ({'≤1m' if spine_isl_short else '>1m'})",
                    "Cable":       spine_isl_cable["spec"],
                    "Supplied By": spine_isl_cable["supplier"]
                },
                {
                    "Connection":  "Spine → Customer core uplink",
                    "Cable":       spine_profile["spine_cable"]["spec"],
                    "Supplied By": spine_profile["spine_cable"]["supplier"]
                },
            ])

            st.markdown("#### 🗺️ Spine Port Mapping")

            spine_isl_list    = [
                p.strip() for p in spine_isl_ports_input.split(",")
                if p.strip()
            ]
            spine_uplink_list = [
                p.strip() for p in spine_uplink_ports_input.split(",")
                if p.strip()
            ]

            spine_vendor_suffix = get_sw_suffix(spine_model)
            spine_sw_a_name     = f"{pfx}-{spine_vendor_suffix}-SPINE-SW1"
            spine_sw_b_name     = f"{pfx}-{spine_vendor_suffix}-SPINE-SW2"

            spine_table_rows = []

            for lp in range(1, num_leaf_pairs + 1):
                port_a = spine_downlink_start + (lp - 1) * 2
                port_b = spine_downlink_start + (lp - 1) * 2 + 1
                p_a = (f"swp{port_a}" if spine_profile["os"] == "cumulus"
                       else f"Ethernet{port_a}")
                p_b = (f"swp{port_b}" if spine_profile["os"] == "cumulus"
                       else f"Ethernet{port_b}")
                spine_table_rows.append({
                    "Spine-A Port": p_a,
                    "Spine-B Port": p_b,
                    "Connects To":  f"{pfx}-Leaf-Pair-{lp} (Leaf-A / Leaf-B)",
                    "Cable":        spine_profile["spine_cable"]["spec"],
                    "Supplied By":  spine_profile["spine_cable"]["supplier"]
                })

            for p in spine_isl_list:
                spine_table_rows.append({
                    "Spine-A Port": p,
                    "Spine-B Port": p,
                    "Connects To":  "Spine ISL / Peerlink",
                    "Cable":        spine_isl_cable["spec"],
                    "Supplied By":  spine_isl_cable["supplier"]
                })

            for p in spine_uplink_list:
                spine_table_rows.append({
                    "Spine-A Port": p,
                    "Spine-B Port": p,
                    "Connects To":  "Customer Core",
                    "Cable":        spine_profile["spine_cable"]["spec"],
                    "Supplied By":  spine_profile["spine_cable"]["supplier"]
                })

            st.dataframe(spine_table_rows, use_container_width=True)

        # Spine configs — full width outside columns
        st.markdown("#### ⚙️ Generated Spine Configurations")

        spine_env       = Environment(loader=FileSystemLoader("templates"))
        spine_tmpl_file = (
            "cumulus_spine.j2" if spine_profile["os"] == "cumulus"
            else "arista_spine.j2"
        )

        try:
            spine_template = spine_env.get_template(spine_tmpl_file)
        except Exception:
            st.error(
                f"Template `{spine_tmpl_file}` not found in /templates. "
                "Please create it and rebuild."
            )
            spine_template = None

        if spine_template:
            spine_cfg_col_a, spine_cfg_col_b = st.columns(2)

            for i, side in enumerate(["A", "B"]):
                spine_port_map = []
                for lp in range(1, num_leaf_pairs + 1):
                    port_num = (
                        spine_downlink_start
                        + (lp - 1) * 2
                        + (0 if side == "A" else 1)
                    )
                    spine_port_map.append({
                        "port": port_num,
                        "swp":  f"swp{port_num}",
                        "eth":  f"Ethernet{port_num}",
                        "desc": (
                            f"Downlink-to-{pfx}-Leaf-Pair-{lp}-"
                            f"{'Leaf-A' if side == 'A' else 'Leaf-B'}"
                        ),
                        "type": "downlink"
                    })

                spine_context = {
                    "se_name":       se_name or "—",
                    "customer":      customer or "—",
                    "cluster_name":  cluster_name or "—",
                    "install_date":  str(install_date),
                    "hostname":      (
                        spine_sw_a_name if side == "A"
                        else spine_sw_b_name
                    ),
                    "mgmt_ip":       (
                        spine_a_ip if side == "A" else spine_b_ip
                    ),
                    "mgmt_gw":       spine_mgmt_gw,
                    "ntp_server":    spine_ntp or spine_mgmt_gw,
                    "vlan_id":       vlan_id,
                    "mtu":           spine_profile["mtu"],
                    "isl_ports":     spine_isl_list,
                    "uplink_ports":  spine_uplink_list,
                    "clag_id":       300,
                    "peer_ip":       (
                        spine_b_ip.split("/")[0] if side == "A"
                        else spine_a_ip.split("/")[0]
                    ),
                    "port_map":      spine_port_map,
                    "clag_priority": 1000 if side == "A" else 2000,
                }

                spine_config_text = spine_template.render(spine_context).replace('\r\n', '\n').replace('\r', '\n')

                with (
                    spine_cfg_col_a if side == "A"
                    else spine_cfg_col_b
                ):
                    st.markdown(
                        f"**Spine {side}** "
                        f"({'Primary' if side == 'A' else 'Secondary'})"
                    )
                    st.code(spine_config_text, language="bash")
                    st.download_button(
                        label=f"💾 Download Spine {side} Config",
                        data=spine_config_text,
                        file_name=(
                            f"{pfx}_SPINE_{side}_"
                            f"{spine_profile['vendor'].upper()}_"
                            f"{date.today().isoformat()}.txt"
                        ),
                        mime="text/plain",
                        key=f"spine_dl_{side}"
                    )


# ============================================================
# TAB 8 — DATA SWITCH — NORTHBOUND
# ============================================================
with tab8:
    st.subheader("GPU / Data Network Switch — Leaf Pair Configuration")

    gpu_enabled = st.toggle(
        "Enable GPU / Data Network Switch Configuration",
        value=False, key="tab8_enabled"
    )

    if not gpu_enabled:
        st.info(
            "Enable the toggle above to configure an additional "
            "leaf pair for CNode to GPU / Data Network connectivity."
        )
    else:
        col_left2, col_right2 = st.columns([1, 2])

        with col_left2:
            st.markdown("#### Switch Selection")
            sw_model2 = st.selectbox(
                "Switch Model",
                options=list(HARDWARE_PROFILES.keys()),
                key="tab8_sw_model"
            )
            profile2 = HARDWARE_PROFILES[sw_model2]

            st.info(
                f"**Vendor:** {profile2['vendor'].capitalize()}  \n"
                f"**OS:** {'Cumulus NV' if profile2['os'] == 'cumulus' else 'Arista EOS'}  \n"
                f"**Ports:** {profile2['total_ports']}  \n"
                f"**Speed:** {profile2['native_speed']}  \n"
                f"**Form Factor:** {profile2['form_factor']}  \n"
                f"**MTU:** {profile2['mtu']}  \n"
                f"**Notes:** {profile2['notes']}"
            )

            st.markdown("#### Port Reservation")
            cnode_start2 = st.number_input(
                "CNode start port", min_value=1,
                max_value=profile2["total_ports"], value=1,
                key="tab8_cnode_start"
            )
            gpu_start2 = st.number_input(
                "GPU Server start port", min_value=1,
                max_value=profile2["total_ports"],
                value=15 if profile2["total_ports"] == 32 else 29,
                key="tab8_gpu_start"
            )
            num_gpu_servers = st.slider(
                "Number of GPU Servers",
                min_value=1, max_value=profile2["max_node_ports"],
                value=4, key="tab8_gpu_count"
            )
            gpu_nic_speed = st.selectbox(
                "GPU Server NIC Speed",
                options=["200GbE", "100GbE", "400GbE"],
                key="tab8_gpu_nic"
            )

            st.markdown("#### Switch Networking")
            gpu_vlans_input = st.text_input(
                "GPU Network VLAN IDs (comma separated, max 8)",
                value=st.session_state.get("tab8_vlans", ""),
                placeholder="e.g. 101, 102",
                key="tab8_vlans"
            )
            # Parse and validate
            _raw_vlans = [v.strip() for v in gpu_vlans_input.split(",") if v.strip()]
            _valid_vlans = []
            for _v in _raw_vlans[:8]:
                try:
                    _vid = int(_v)
                    if 1 <= _vid <= 4094:
                        _valid_vlans.append(_vid)
                except ValueError:
                    pass
            if len(_raw_vlans) > 8:
                st.warning("⚠️ Maximum 8 VLANs supported — only the first 8 will be used.")
            if gpu_vlans_input and not _valid_vlans:
                st.error("❌ No valid VLAN IDs found. Enter comma-separated integers between 1 and 4094.")
            sw_a_ip2  = st.text_input(
                "Switch A MGMT IP/mask", value="192.168.2.1/24",
                key="tab8_sw_a_ip"
            )
            sw_b_ip2  = st.text_input(
                "Switch B MGMT IP/mask", value="192.168.2.2/24",
                key="tab8_sw_b_ip"
            )
            mgmt_gw2  = st.text_input(
                "MGMT Gateway", value="192.168.2.254", key="tab8_gw"
            )
            mgmt_vlan2 = st.number_input(
                "Management VLAN ID", min_value=1, max_value=4094,
                value=int(st.session_state.get("tab8_mgmt_vlan", 1)),
                key="tab8_mgmt_vlan"
            )
            ntp_srv2  = st.text_input(
                "NTP Server", value="",
                placeholder="Enter customer NTP server IP",
                key="tab8_ntp"
            )

            st.markdown("#### ISL / Uplink Ports")
            isl_ports_input2 = st.text_input(
                "ISL Ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in profile2["default_isl"]]
                ),
                key="tab8_isl"
            )
            uplink_ports_input2 = st.text_input(
                "Uplink Ports (comma separated)",
                value=",".join(
                    [f"swp{p}" for p in profile2["default_uplink"]]
                ),
                key="tab8_uplink"
            )
            isl_short2 = st.toggle(
                "ISL cable run is ≤1m (use DAC)",
                value=False, key="tab8_isl_short"
            )

        with col_right2:

            if gpu_nic_speed == "100GbE" and profile2["native_speed"] in ["200GbE", "400GbE"]:
                st.warning(
                    f"⚠️ GPU Server NIC speed ({gpu_nic_speed}) is lower "
                    f"than switch native speed ({profile2['native_speed']}). "
                    f"Breakout or speed-matching cables will be required."
                )
            if gpu_nic_speed == "200GbE" and profile2["native_speed"] == "400GbE":
                st.error(
                    f"⚠️ GPU Server NIC ({gpu_nic_speed}) requires "
                    f"400G→2x200G AOC breakout cables on this switch. "
                    f"Customer/Partner must supply these cables."
                )
            if gpu_nic_speed == "400GbE" and profile2["native_speed"] == "200GbE":
                st.error(
                    f"❌ GPU Server NIC ({gpu_nic_speed}) exceeds "
                    f"switch native speed ({profile2['native_speed']}). "
                    f"Incompatible — select a higher speed switch."
                )

            # GPU switch validation — ranges can be in either order
            gpu_end2   = gpu_start2 + num_gpu_servers - 1
            cnode_end2 = cnode_start2 + num_cnodes - 1
            isl_start2 = min(profile2["default_isl"])

            errors2   = []
            warnings2 = []

            # Check the two ranges don't overlap each other
            if not (gpu_end2 < cnode_start2 or cnode_end2 < gpu_start2):
                errors2.append(
                    f"❌ GPU Server ports (swp{gpu_start2}–swp{gpu_end2}) "
                    f"overlap with CNode ports (swp{cnode_start2}–swp{cnode_end2}). "
                    f"Adjust port ranges so they don't collide."
                )

            # Check neither range runs into ISL
            if gpu_end2 >= isl_start2:
                errors2.append(
                    f"❌ GPU Server ports (swp{gpu_start2}–swp{gpu_end2}) "
                    f"overflow into ISL range (swp{isl_start2}+). "
                    f"Reduce GPU server count or adjust start port."
                )
            if cnode_end2 >= isl_start2:
                errors2.append(
                    f"❌ CNode ports (swp{cnode_start2}–swp{cnode_end2}) "
                    f"overflow into ISL range (swp{isl_start2}+). "
                    f"Reduce CNode count or adjust start port."
                )

            total_needed2 = num_gpu_servers + num_cnodes
            if total_needed2 > profile2["max_node_ports"] * 0.85:
                warnings2.append(
                    f"⚠️ Using {total_needed2} of "
                    f"{profile2['max_node_ports']} available ports "
                    f"({int(total_needed2/profile2['max_node_ports']*100)}% capacity)."
                )

            if errors2:
                for e in errors2:
                    st.error(e)
                
            for w in warnings2:
                st.warning(w)  

            if not ntp_srv2:
                st.warning(
                    "⚠️ NTP Server is empty. "
                    "Confirm the customer NTP IP before applying config."
                )

            st.markdown("#### 📦 Cable Requirements")
            render_cable_summary(profile2, isl_short2)

            st.markdown("#### 🗺️ Port Mapping / Cabling Guide")

            isl_list2    = [p.strip() for p in isl_ports_input2.split(",")]
            uplink_list2 = [p.strip() for p in uplink_ports_input2.split(",") if p.strip()]

            table_rows2 = []

            for i in range(1, num_cnodes + 1):
                swp_num  = cnode_start2 + (i - 1)
                port_str = (f"swp{swp_num}" if profile2["os"] == "cumulus"
                            else f"Ethernet{swp_num}")
                table_rows2.append({
                    "Switch Port (A)": port_str,
                    "Switch Port (B)": port_str,
                    "VLANs":           ", ".join(str(v) for v in _valid_vlans) or "—",
                    "Device":          f"{pfx}-{cnode_label}-{i}",
                    "NIC":             "CX7 200GbE",
                    "Cable":           profile2["node_cable"]["spec"],
                    "Supplied By":     profile2["node_cable"]["supplier"]
                })

            for i in range(1, num_gpu_servers + 1):
                swp_num  = gpu_start2 + (i - 1)
                port_str = (f"swp{swp_num}" if profile2["os"] == "cumulus"
                            else f"Ethernet{swp_num}")
                if gpu_nic_speed == "200GbE" and profile2["native_speed"] == "400GbE":
                    gpu_cable = "400G→2x200G AOC breakout ⚠️ Customer"
                elif gpu_nic_speed == "100GbE":
                    gpu_cable = "Breakout AOC ⚠️ Check compatibility"
                else:
                    gpu_cable = profile2["node_cable"]["spec"]

                table_rows2.append({
                    "Switch Port (A)": port_str,
                    "Switch Port (B)": port_str,
                    "Device":          f"{pfx}-GPU-SERVER-{i}",
                    "NIC":             gpu_nic_speed,
                    "Cable":           gpu_cable,
                    "Supplied By":     (
                        "CUSTOMER"
                        if profile2["customer_cables"]
                        or gpu_nic_speed != profile2["native_speed"]
                        else "VAST"
                    )
                })

            for p in isl_list2:
                isl_cable2 = (
                    profile2["isl_cable_short"] if isl_short2
                    else profile2["isl_cable_long"]
                )
                table_rows2.append({
                    "Switch Port (A)": p,
                    "Switch Port (B)": p,
                    "Device":          "ISL / Peerlink",
                    "NIC":             "—",
                    "Cable":           isl_cable2["spec"],
                    "Supplied By":     isl_cable2["supplier"]
                })

            for p in uplink_list2:
                table_rows2.append({
                    "Switch Port (A)": p,
                    "Switch Port (B)": p,
                    "Device":          "Uplink to Customer Core",
                    "NIC":             "—",
                    "Cable":           profile2["spine_cable"]["spec"],
                    "Supplied By":     profile2["spine_cable"]["supplier"]
                })

            st.dataframe(table_rows2, use_container_width=True)

            st.markdown("#### ⚙️ Generated Switch Configurations")

            env2       = Environment(loader=FileSystemLoader("templates"))
            tmpl_file2 = (
                "cumulus_nv.j2" if profile2["os"] == "cumulus"
                else "arista_eos.j2"
            )

            try:
                template2 = env2.get_template(tmpl_file2)
            except Exception:
                st.error(
                    f"Template `{tmpl_file2}` not found. "
                    "Please create it to generate configs."
                )
                template2 = None

            if template2:
                cfg_col_a2, cfg_col_b2 = st.columns(2)

                for i, side in enumerate(["A", "B"]):
                    port_side = "1" if side == "A" else "2"
                    port_map2 = []

                    for c in range(1, num_cnodes + 1):
                        swp_num = cnode_start2 + (c - 1)
                        port_map2.append({
                            "port": swp_num,
                            "swp":  f"swp{swp_num}",
                            "eth":  f"Ethernet{swp_num}",
                            "desc": f"{pfx}-{cnode_label}-{c}-GPU-P{port_side}",
                            "type": "cnode"
                        })

                    for g in range(1, num_gpu_servers + 1):
                        swp_num = gpu_start2 + (g - 1)
                        port_map2.append({
                            "port": swp_num,
                            "swp":  f"swp{swp_num}",
                            "eth":  f"Ethernet{swp_num}",
                            "desc": f"{pfx}-GPU-SERVER-{g}-P{port_side}",
                            "type": "gpu"
                        })

                    context2 = {
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
                    }
                    config_text2 = template2.render(context2).replace('\r\n', '\n').replace('\r', '\n')

                    with (cfg_col_a2 if side == "A" else cfg_col_b2):
                        st.markdown(
                            f"**Switch {side}** "
                            f"({'Primary' if side == 'A' else 'Secondary'})"
                        )
                        st.code(config_text2, language="bash")
                        st.download_button(
                            label=f"💾 Download GPU Switch {side} Config",
                            data=config_text2,
                            file_name=(
                                f"{pfx}_VAST_GPU_SW{side}_"
                                f"{profile2['vendor'].upper()}_"
                                f"{date.today().isoformat()}.txt"
                            ),
                            mime="text/plain",
                            key=f"tab8_dl_{side}"
                        )

            # Customer Handoff Document
            st.markdown("---")
            st.markdown("#### 📄 Customer Network Handoff Document")
            st.caption(
                "Share this with the customer's network team. "
                "Covers what they need to configure on their side "
                "to accept the VAST uplink."
            )

            handoff_doc = f"""
VAST DATA — CUSTOMER NETWORK HANDOFF REQUIREMENTS
==================================================
Cluster:      {cluster_name or "—"}
Customer:     {customer or "—"}
SE:           {se_name or "—"}
Date:         {install_date}
Generated by: VAST SE Toolkit v1.0.0

YOUR NETWORK TEAM MUST CONFIGURE THE FOLLOWING
===============================================

1. PORT-CHANNEL / MLAG
   - Create Port-Channel 200
   - Mode: LACP Active
   - Member ports: as agreed with SE on-site
   - MTU: {profile2["mtu"]} (MANDATORY — do not use 9000 or 1500)

2. VLAN
   - Allow VLANs {", ".join(str(v) for v in _valid_vlans) if _valid_vlans else "—"} on the port-channel
   - Configure as Trunk mode

3. UPLINK CONNECTIVITY
   - Connect to VAST Switch A uplink ports: {uplink_ports_input2}
   - Connect to VAST Switch B uplink ports: {uplink_ports_input2}
   - Both connections form an MLAG/LACP bond

4. CABLE REQUIREMENTS
   - Cable type: {profile2["spine_cable"]["spec"]}
   - Supplied by: {profile2["spine_cable"]["supplier"]}
   {"⚠️  NOTE: 400G MPO AOC cables are NOT supplied by VAST." if profile2["customer_cables"] else "✅  Cables are included in VAST shipment."}

5. ACCEPTANCE TEST
   After cabling run the following to confirm connectivity:

   [Mellanox / Cumulus]
   net show lldp
   net show mlag

   [Arista EOS]
   show mlag
   show port-channel summary
   show lldp neighbors

6. VAST REQUIREMENTS SUMMARY
   - MTU:          {profile2["mtu"]}
   - VLANs:        {", ".join(str(v) for v in _valid_vlans) if _valid_vlans else "—"}
   - LACP Mode:    Active
   - Port-Channel: 200

For questions contact your VAST SE: {se_name or "—"}
==================================================
"""
            st.code(handoff_doc, language="text")
            st.download_button(
                label="📄 Download Customer Handoff Document",
                data=handoff_doc,
                file_name=(
                    f"{pfx}_Customer_Handoff_"
                    f"{date.today().isoformat()}.txt"
                ),
                mime="text/plain",
                key="tab8_handoff_dl"
            )


# ============================================================
# TAB 5 — VALIDATION & PRE-FLIGHT
# ============================================================
with tab5:
    st.subheader("Validation & Pre-Flight Checks")
    st.caption(
        "Run through all checks below before starting the VAST bootstrap. "
        "Every item must be green before you proceed."
    )

    # Grab state from other tabs
    profile_t3     = HARDWARE_PROFILES.get(
        st.session_state.get("tab7_sw_model",
        list(HARDWARE_PROFILES.keys())[0])
    )
    vlan_t3        = st.session_state.get("tab7_vlan",   100)
    sw_a_t3        = st.session_state.get("tab7_sw_a_ip","192.168.1.1/24")
    sw_b_t3        = st.session_state.get("tab7_sw_b_ip","192.168.1.2/24")
    ntp_t3         = st.session_state.get("tab7_ntp",    "")
    isl_t3         = st.session_state.get("tab7_isl",    "")
    dnode_st_t3    = int(st.session_state.get("tab7_dnode_start", 1))
    cnode_st_t3    = int(st.session_state.get("tab7_cnode_start", 15))
    isl_short_t3   = st.session_state.get("tab7_isl_short", False)
    gpu_enabled_t3 = st.session_state.get("tab8_enabled", False)
    sw_model_t3    = st.session_state.get(
        "tab7_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )

    sw_a_ip_only = sw_a_t3.split("/")[0]
    sw_b_ip_only = sw_b_t3.split("/")[0]

    # ── Section 1: Port Count Validation ────────────────────
    st.markdown("---")
    st.markdown("### 1️⃣ Port Count Validation")

    errors_t3, warnings_t3 = validate_port_counts(
        num_dboxes, num_cnodes,
        dnode_st_t3, cnode_st_t3, profile_t3
    )

    if errors_t3:
        for e in errors_t3:
            st.error(e)
    elif warnings_t3:
        for w in warnings_t3:
            st.warning(w)
    else:
        total_ports_used = (num_dboxes * 2) + num_cnodes
        st.success(
            f"✅ Port allocation valid — "
            f"Using {total_ports_used} of "
            f"{profile_t3['max_node_ports']} available node ports "
            f"on {sw_model_t3}."
        )

    dnode_end    = dnode_st_t3 + (num_dboxes * 2) - 1
    cnode_end    = cnode_st_t3 + num_cnodes - 1
    isl_ports_t3 = [p.strip() for p in isl_t3.split(",") if p.strip()]
    isl_range    = (
        f"{isl_ports_t3[0]}–{isl_ports_t3[-1]}"
        if isl_ports_t3 else "—"
    )

    st.table([
        {
            "Range":        f"swp{dnode_st_t3}–swp{dnode_end}",
            "Reserved For": "DNodes (BF-3)",
            "Count":         num_dboxes * 2,
            "Status":        "✅ OK" if not errors_t3 else "❌ Error"
        },
        {
            "Range":        f"swp{cnode_st_t3}–swp{cnode_end}",
            "Reserved For": "CNodes (CX7)",
            "Count":         num_cnodes,
            "Status":        "✅ OK" if not errors_t3 else "❌ Error"
        },
        {
            "Range":        isl_range,
            "Reserved For": "ISL / Peerlink",
            "Count":         len(isl_ports_t3),
            "Status":        "✅ OK"
        },
    ])

    # ── Section 2: Cable Pre-Check ───────────────────────────
    st.markdown("---")
    st.markdown("### 2️⃣ Cable Pre-Check")

    if profile_t3["customer_cables"]:
        st.error(
            f"⚠️ **{sw_model_t3} requires customer-supplied 400G cables.** "
            "Confirm all cables are on-site before proceeding."
        )
    else:
        st.success(
            f"✅ All cables for {sw_model_t3} are included "
            "in the VAST shipment."
        )

    isl_cable_t3 = (
        profile_t3["isl_cable_short"] if isl_short_t3
        else profile_t3["isl_cable_long"]
    )

    st.table([
        {
            "Connection":   "DNode (BF-3) → Switch",
            "Cable":        profile_t3["node_cable"]["spec"],
            "Supplied By":  profile_t3["node_cable"]["supplier"],
            "Confirmed ✓":  "☐"
        },
        {
            "Connection":   "CNode (CX7) → Switch",
            "Cable":        profile_t3["node_cable"]["spec"],
            "Supplied By":  profile_t3["node_cable"]["supplier"],
            "Confirmed ✓":  "☐"
        },
        {
            "Connection":   f"ISL / Peerlink ({'≤1m' if isl_short_t3 else '>1m'})",
            "Cable":        isl_cable_t3["spec"],
            "Supplied By":  isl_cable_t3["supplier"],
            "Confirmed ✓":  "☐"
        },
        {
            "Connection":   "Spine / Uplink",
            "Cable":        profile_t3["spine_cable"]["spec"],
            "Supplied By":  profile_t3["spine_cable"]["supplier"],
            "Confirmed ✓":  "☐"
        },
    ])

    # ── Section 3: MGMT & NTP Check ─────────────────────────
    st.markdown("---")
    st.markdown("### 3️⃣ Management & NTP Pre-Check")

    if not ntp_t3:
        st.error(
            "❌ NTP Server not set in Tab 1. "
            "Set the NTP server before running bootstrap."
        )
    else:
        st.success(f"✅ NTP Server configured: {ntp_t3}")

    st.table([
        {
            "Check":  "Switch A MGMT IP reachable",
            "Value":  sw_a_ip_only,
            "Action": f"ping {sw_a_ip_only}"
        },
        {
            "Check":  "Switch B MGMT IP reachable",
            "Value":  sw_b_ip_only,
            "Action": f"ping {sw_b_ip_only}"
        },
        {
            "Check":  "MGMT Gateway reachable",
            "Value":  st.session_state.get("tab7_gw", "—"),
            "Action": f"ping {st.session_state.get('tab7_gw', '—')}"
        },
        {
            "Check":  "NTP Server reachable",
            "Value":  ntp_t3 or "NOT SET",
            "Action": f"ping {ntp_t3}" if ntp_t3 else "❌ Set NTP first"
        },
    ])

    # ── Section 4: LLDP Validation Script ───────────────────
    st.markdown("---")
    st.markdown("### 4️⃣ Post-Cabling LLDP Validation Script")
    st.caption(
        "Paste this into both switch CLIs after cabling is complete. "
        "Every expected node must appear before starting bootstrap."
    )

    expected_neighbors = []
    for i in range(1, num_dboxes + 1):
        for d in range(1, 3):
            expected_neighbors.append(
                f"{pfx}-{dbox_label}-{i}-{dnode_label}-{d}"
            )
    for i in range(1, num_cnodes + 1):
        expected_neighbors.append(f"{pfx}-{cnode_label}-{i}")

    neighbor_grep = "|".join(expected_neighbors)

    cumulus_lldp = f"""#!/bin/bash
# VAST SE Toolkit — LLDP Validation Script
# Cluster: {cluster_name or "—"}  |  SE: {se_name or "—"}
# Run on BOTH Switch A ({sw_a_ip_only}) and Switch B ({sw_b_ip_only})
# ============================================================

echo "=== LLDP NEIGHBOR CHECK ==="
echo "Expected nodes: {len(expected_neighbors)}"
echo ""
nv show interface lldp

echo ""
echo "=== FILTERING FOR VAST NODES ==="
nv show interface lldp | grep -E "{neighbor_grep}"

echo ""
echo "=== MLAG STATUS ==="
nv show mlag

echo ""
echo "=== PEERLINK STATUS ==="
nv show interface peerlink

echo ""
echo "=== BRIDGE VLAN STATUS ==="
nv show bridge domain br_default vlan

echo ""
echo "=== MTU VERIFICATION (expect {profile_t3['mtu']}) ==="
nv show interface | grep -E "swp[1-9]|mtu"

echo ""
echo "=== QoS PFC STATUS ==="
nv show qos roce

echo ""
echo "Expected {len(expected_neighbors)} VAST nodes:"
echo "{chr(10).join(f'  - {n}' for n in expected_neighbors)}"
"""

    arista_lldp = f"""#!/bin/bash
# VAST SE Toolkit — LLDP Validation Script (Arista EOS)
# Cluster: {cluster_name or "—"}  |  SE: {se_name or "—"}
# Run on BOTH Switch A ({sw_a_ip_only}) and Switch B ({sw_b_ip_only})
# ============================================================

echo "=== LLDP NEIGHBOR CHECK ==="
show lldp neighbors

echo ""
echo "=== FILTERING FOR VAST NODES ==="
show lldp neighbors | grep -E "{neighbor_grep}"

echo ""
echo "=== MLAG STATUS ==="
show mlag

echo ""
echo "=== PORT-CHANNEL SUMMARY ==="
show port-channel summary

echo ""
echo "=== VLAN STATUS ==="
show vlan

echo ""
echo "=== MTU VERIFICATION (expect {profile_t3['mtu']}) ==="
show interfaces | grep -E "Ethernet|MTU"

echo ""
echo "=== QoS PFC STATUS ==="
show priority-flow-control
show qos

echo ""
echo "Expected {len(expected_neighbors)} VAST nodes:"
echo "{chr(10).join(f'  - {n}' for n in expected_neighbors)}"
"""

    lldp_script = (
        cumulus_lldp if profile_t3["os"] == "cumulus"
        else arista_lldp
    )

    st.code(lldp_script, language="bash")
    st.download_button(
        label="💾 Download LLDP Validation Script",
        data=lldp_script,
        file_name=(
            f"{pfx}_LLDP_Validation_"
            f"{date.today().isoformat()}.sh"
        ),
        mime="text/plain",
        key="tab3_lldp_dl"
    )

    # ── Section 5: Pre-Flight Checklist ─────────────────────
    st.markdown("---")
    st.markdown("### 5️⃣ Pre-Flight Checklist")
    st.caption(
        "Work through this checklist top to bottom. "
        "Do not start VAST bootstrap until all items are confirmed."
    )

    checklist = f"""
VAST INSTALLATION PRE-FLIGHT CHECKLIST
=======================================
Cluster:  {pfx}
Customer: {customer or "—"}
SE:       {se_name or "—"}
Date:     {install_date}
Switch:   {sw_model_t3}
Topology: {topology}
Generated by: VAST SE Toolkit v1.0.0

PHYSICAL
--------
☐  All DBoxes racked and powered on
☐  All CNodes racked and powered on
☐  All switches racked and powered on
☐  {"⚠️  400G customer-supplied cables on-site and verified" if profile_t3["customer_cables"] else "VAST-supplied cables verified against packing list"}
☐  DNode (BF-3) cables run: {profile_t3["node_cable"]["spec"]}
☐  CNode (CX7)  cables run: {profile_t3["node_cable"]["spec"]}
☐  ISL cables run:          {isl_cable_t3["spec"]}
☐  Uplink cables run:       {profile_t3["spine_cable"]["spec"]}

NETWORK — SWITCH A ({sw_a_ip_only})
{"─" * 40}
☐  Switch A powered on and booted
☐  Switch A MGMT IP configured: {sw_a_ip_only}
☐  Switch A config applied (downloaded from Tab 1)
☐  Switch A MLAG primary (priority 1000)
☐  Switch A NTP synced to: {ntp_t3 or "NOT SET — SET BEFORE PROCEEDING"}

NETWORK — SWITCH B ({sw_b_ip_only})
{"─" * 40}
☐  Switch B powered on and booted
☐  Switch B MGMT IP configured: {sw_b_ip_only}
☐  Switch B config applied (downloaded from Tab 1)
☐  Switch B MLAG secondary (priority 2000)
☐  Switch B NTP synced to: {ntp_t3 or "NOT SET — SET BEFORE PROCEEDING"}

{"SPINE SWITCHES" if topology == "Spine-Leaf" else ""}
{"─" * 40 if topology == "Spine-Leaf" else ""}
{"☐  Spine A config applied (downloaded from Tab 1)" if topology == "Spine-Leaf" else ""}
{"☐  Spine B config applied (downloaded from Tab 1)" if topology == "Spine-Leaf" else ""}
{"☐  Spine MLAG peerlink UP on both spine switches" if topology == "Spine-Leaf" else ""}
{"☐  Leaf-to-Spine uplinks confirmed UP" if topology == "Spine-Leaf" else ""}

VALIDATION
----------
☐  MLAG peerlink UP on both switches
☐  MLAG state MASTER/BACKUP (not SOLO)
☐  LLDP validation script run — all {len(expected_neighbors)} nodes visible
☐  MTU confirmed {profile_t3["mtu"]} on all node ports
☐  PFC / RoCEv2 QoS confirmed active
☐  Customer uplink LACP bond UP (if applicable)
☐  Ping Switch A MGMT: ping {sw_a_ip_only}
☐  Ping Switch B MGMT: ping {sw_b_ip_only}

{"GPU / DATA NETWORK SWITCH" if gpu_enabled_t3 else ""}
{"─" * 40 if gpu_enabled_t3 else ""}
{"☐  GPU Switch A config applied (downloaded from Tab 2)" if gpu_enabled_t3 else ""}
{"☐  GPU Switch B config applied (downloaded from Tab 2)" if gpu_enabled_t3 else ""}
{"☐  Customer handoff document delivered to network team" if gpu_enabled_t3 else ""}
{"☐  GPU switch uplink LACP bond confirmed UP" if gpu_enabled_t3 else ""}

READY FOR BOOTSTRAP
-------------------
☐  All above items confirmed
☐  VAST bootstrap bundle available on laptop
☐  Customer sign-off on network readiness obtained
☐  SE confirms: GO FOR BOOTSTRAP ✅
================================================
"""

    st.code(checklist, language="text")
    st.download_button(
        label="📋 Download Pre-Flight Checklist",
        data=checklist,
        file_name=(
            f"{pfx}_PreFlight_Checklist_"
            f"{date.today().isoformat()}.txt"
        ),
        mime="text/plain",
        key="tab3_checklist_dl"
    )

    # ── Section 6: Cable Label Generator ────────────────────
    st.markdown("---")
    st.markdown("### 6️⃣ Cable Label Generator")
    st.caption(
        "Format: SOURCE-SWITCH-PORT : TARGET-NODE-PORT  |  "
        "Download CSV for label printers or plain text for printing."
    )

    tab3_map = get_port_mappings(
        "A", num_dboxes, num_cnodes,
        dnode_st_t3, cnode_st_t3,
        pfx=pfx, dbox_label=dbox_label,
        dnode_label=dnode_label, cnode_label=cnode_label
    )

    isl_list_t3   = [p.strip() for p in isl_t3.split(",") if p.strip()]
    label_rows    = []
    csv_rows      = []
    cable_number  = 1

    for item in tab3_map:
        port_num   = item["port"]
        sw_a_port  = f"{full_sw_a}-P{port_num}"
        sw_b_port  = f"{full_sw_b}-P{port_num}"
        node_end_a = item["desc"].replace("-P2", "-P1")
        node_end_b = item["desc"].replace("-P1", "-P2")
        cable_spec = profile_t3["node_cable"]["spec"]
        supplier   = profile_t3["node_cable"]["supplier"]

        label_rows.append({
            "Cable #":    f"CBL-{cable_number:03d}",
            "Switch End": sw_a_port,
            "Node End":   node_end_a,
            "Cable Type": cable_spec,
            "Supplier":   supplier,
        })
        csv_rows.append(
            f"CBL-{cable_number:03d},{sw_a_port},{node_end_a},"
            f"{cable_spec},{supplier}"
        )
        cable_number += 1

        label_rows.append({
            "Cable #":    f"CBL-{cable_number:03d}",
            "Switch End": sw_b_port,
            "Node End":   node_end_b,
            "Cable Type": cable_spec,
            "Supplier":   supplier,
        })
        csv_rows.append(
            f"CBL-{cable_number:03d},{sw_b_port},{node_end_b},"
            f"{cable_spec},{supplier}"
        )
        cable_number += 1

    for p in isl_list_t3:
        port_num     = p.replace("swp", "")
        isl_spec     = (
            profile_t3["isl_cable_short"]["spec"] if isl_short_t3
            else profile_t3["isl_cable_long"]["spec"]
        )
        isl_supplier = (
            profile_t3["isl_cable_short"]["supplier"] if isl_short_t3
            else profile_t3["isl_cable_long"]["supplier"]
        )
        label_rows.append({
            "Cable #":    f"CBL-{cable_number:03d}",
            "Switch End": f"{full_sw_a}-ISL-{p}",
            "Node End":   f"{full_sw_b}-ISL-{p}",
            "Cable Type": isl_spec,
            "Supplier":   isl_supplier,
        })
        csv_rows.append(
            f"CBL-{cable_number:03d},"
            f"{full_sw_a}-ISL-{p},"
            f"{full_sw_b}-ISL-{p},"
            f"{isl_spec},{isl_supplier}"
        )
        cable_number += 1

    st.dataframe(label_rows, use_container_width=True)

    plain_labels = (
        f"VAST CABLE LABELS\n"
        f"Cluster: {pfx}  |  SE: {se_name or '—'}  |  "
        f"Date: {install_date}\n"
        f"{'='*65}\n\n"
    )
    for row in label_rows:
        plain_labels += (
            f"[{row['Cable #']}]\n"
            f"  FROM: {row['Switch End']}\n"
            f"  TO:   {row['Node End']}\n"
            f"  TYPE: {row['Cable Type']}  |  "
            f"SUPPLIER: {row['Supplier']}\n\n"
        )

    csv_header = "Cable #,Switch End,Node End,Cable Type,Supplier"
    csv_output = csv_header + "\n" + "\n".join(csv_rows)

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="💾 Download Cable Labels (CSV)",
            data=csv_output,
            file_name=(
                f"{pfx}_Cable_Labels_{date.today().isoformat()}.csv"
            ),
            mime="text/csv",
            key="tab3_labels_csv"
        )
    with dl_col2:
        st.download_button(
            label="🖨️ Download Cable Labels (Print)",
            data=plain_labels,
            file_name=(
                f"{pfx}_Cable_Labels_{date.today().isoformat()}.txt"
            ),
            mime="text/plain",
            key="tab3_labels_txt"
        )

    # ── Section 7: Equipment Checklist ──────────────────────
    st.markdown("---")
    st.markdown("### 7️⃣ Equipment Checklist")
    st.caption(
        "Quantities generated from session inputs. "
        "Add custom items at the bottom."
    )

    total_node_cables   = (num_dboxes * 2 * 2) + (num_cnodes * 2)
    total_isl_cables    = len(isl_list_t3)
    uplink_t3           = st.session_state.get("tab7_uplink", "")
    uplink_list_t3      = [
        p.strip() for p in uplink_t3.split(",") if p.strip()
    ]
    total_uplink_cables = len(uplink_list_t3) * 2

    node_cable_line = (
        f"☐  ⚠️  {total_node_cables}x "
        f"{profile_t3['node_cable']['spec']} "
        f"(node cables — CUSTOMER SUPPLIED)"
        if profile_t3["customer_cables"]
        else
        f"☐  {total_node_cables}x "
        f"{profile_t3['node_cable']['spec']} "
        f"(node cables — VAST supplied)"
    )
    isl_cable_line = (
        f"☐  ⚠️  {total_isl_cables}x "
        f"{isl_cable_t3['spec']} "
        f"(ISL cables — CUSTOMER SUPPLIED)"
        if profile_t3["customer_cables"]
        else
        f"☐  {total_isl_cables}x "
        f"{isl_cable_t3['spec']} "
        f"(ISL cables — VAST supplied)"
    )
    uplink_cable_line = (
        f"☐  ⚠️  {total_uplink_cables}x "
        f"{profile_t3['spine_cable']['spec']} "
        f"(uplink cables — CUSTOMER SUPPLIED)"
        if profile_t3["customer_cables"]
        else
        f"☐  {total_uplink_cables}x "
        f"{profile_t3['spine_cable']['spec']} "
        f"(uplink cables — VAST supplied)"
    )

    dbox_lines  = "\n".join(
        f"     ☐  {pfx}-{dbox_label}-{i}"
        for i in range(1, num_dboxes + 1)
    )
    cnode_lines = "\n".join(
        f"     ☐  {pfx}-{cnode_label}-{i}"
        for i in range(1, num_cnodes + 1)
    )

    custom_val = st.session_state.get("equip_custom", "")

    equip_checklist = f"""
VAST INSTALLATION — EQUIPMENT CHECKLIST
========================================
Cluster:  {pfx}
Customer: {customer or "—"}
SE:       {se_name or "—"}
Date:     {install_date}
Switch:   {sw_model_t3}
Topology: {topology}
Generated by: VAST SE Toolkit v1.0.0

🔧 TOOLS
========
☐  SE go bag
☐  Laptop with VAST SE Toolkit running
☐  Console cable (RJ45 to USB)

💾 SOFTWARE & BOOTSTRAP FILES
==============================
☐  VAST OS bundle downloaded to laptop (latest version confirmed)
☐  Switch firmware verified ({"Cumulus NV" if profile_t3["os"] == "cumulus" else "Arista EOS"})
☐  SE Toolkit configs downloaded:
     ☐  {full_sw_a} config
     ☐  {full_sw_b} config
{"     ☐  Spine A config" if topology == "Spine-Leaf" else ""}
{"     ☐  Spine B config" if topology == "Spine-Leaf" else ""}
{"     ☐  GPU Switch A config" if gpu_enabled_t3 else ""}
{"     ☐  GPU Switch B config" if gpu_enabled_t3 else ""}
{"     ☐  Customer handoff document sent/printed" if gpu_enabled_t3 else ""}

🔌 SWITCH HARDWARE
==================
☐  2x {sw_model_t3} switches
     ☐  {full_sw_a}
     ☐  {full_sw_b}
{"☐  2x " + spine_model + " spine switches" if topology == "Spine-Leaf" else ""}
{node_cable_line}
{isl_cable_line}
{uplink_cable_line}

📦 COMPUTE NODES
================
☐  {num_dboxes}x DBox enclosure{"s" if num_dboxes > 1 else ""}:
{dbox_lines}
☐  {num_cnodes}x CNode{"s" if num_cnodes > 1 else ""} (with CX7 NICs):
{cnode_lines}

🗄️ RACK EQUIPMENT
==================
☐  Rack rails for all nodes and switches
☐  Cable managers / D-rings
☐  PDU capacity confirmed for node count
☐  1U blanking panels

➕ CUSTOM ITEMS
===============
{custom_val if custom_val else "(none)"}
========================================
"""

    st.code(equip_checklist, language="text")

    st.text_area(
        "Add custom items (one per line)",
        placeholder="e.g. Customer PO number confirmed\nData center escort arranged",
        key="equip_custom",
        height=100
    )

    st.download_button(
        label="📋 Download Equipment Checklist",
        data=equip_checklist,
        file_name=(
            f"{pfx}_Equipment_Checklist_"
            f"{date.today().isoformat()}.txt"
        ),
        mime="text/plain",
        key="tab3_equip_dl"
    )
# ============================================================
# TAB 6 — INSTALLATION PROCEDURE
# ============================================================
with tab6:
    st.subheader("Switch Installation Procedure")
    st.caption(
        "Step-by-step procedure personalised for this session. "
        "Work through each section in order. "
        "Do not start VAST bootstrap until all switches are validated."
    )

    # Pull session state
    proc_sw_model   = st.session_state.get(
        "tab7_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_profile    = HARDWARE_PROFILES[proc_sw_model]
    proc_sw_a_ip    = st.session_state.get("tab7_sw_a_ip", "192.168.1.1/24")
    proc_sw_b_ip    = st.session_state.get("tab7_sw_b_ip", "192.168.1.2/24")
    proc_ntp        = st.session_state.get("tab7_ntp", "")
    proc_gpu        = st.session_state.get("tab8_enabled", False)
    proc_gpu_sw_a   = st.session_state.get("tab8_sw_a_ip", "192.168.2.1/24")
    proc_gpu_sw_b   = st.session_state.get("tab8_sw_b_ip", "192.168.2.2/24")

    # Build filenames matching what the toolkit generates
    today_str       = date.today().isoformat()
    vendor_up       = proc_profile["vendor"].upper()
    fname_sw_a      = f"{pfx}_VAST_SWA_{vendor_up}_{today_str}.txt"
    fname_sw_b      = f"{pfx}_VAST_SWB_{vendor_up}_{today_str}.txt"

    proc_gpu_model  = st.session_state.get(
        "tab8_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_gpu_profile = HARDWARE_PROFILES[proc_gpu_model]
    gpu_vendor_up   = proc_gpu_profile["vendor"].upper()
    fname_gpu_sw_a  = f"{pfx}_VAST_GPU_SWA_{gpu_vendor_up}_{today_str}.txt"
    fname_gpu_sw_b  = f"{pfx}_VAST_GPU_SWB_{gpu_vendor_up}_{today_str}.txt"

    spine_enabled   = topology == "Spine-Leaf"
    proc_spine_model = st.session_state.get(
        "spine_sw_model", list(HARDWARE_PROFILES.keys())[0]
    )
    proc_spine_profile = HARDWARE_PROFILES[proc_spine_model]
    spine_vendor_up = proc_spine_profile["vendor"].upper()
    fname_spine_a   = f"{pfx}_VAST_SPINE_A_{spine_vendor_up}_{today_str}.txt"
    fname_spine_b   = f"{pfx}_VAST_SPINE_B_{spine_vendor_up}_{today_str}.txt"

    proc_spine_a_ip = st.session_state.get("spine_a_ip", "192.168.3.1/24")
    proc_spine_b_ip = st.session_state.get("spine_b_ip", "192.168.3.2/24")

    TEMP_IP = "192.168.2.101/24"

    # ── Section 1: Prerequisites ─────────────────────────────
    st.markdown("---")
    st.markdown("### 1️⃣ Prerequisites")
    st.markdown(
        "Before touching any switch hardware, confirm the following:"
    )

    switch_list = [
        f"**{full_sw_a}** config file: `{fname_sw_a}`",
        f"**{full_sw_b}** config file: `{fname_sw_b}`",
    ]
    if proc_gpu:
        switch_list += [
            f"**{full_sw_a}-GPU** config file: `{fname_gpu_sw_a}`",
            f"**{full_sw_b}-GPU** config file: `{fname_gpu_sw_b}`",
        ]
    if spine_enabled:
        spine_vsuffix = get_sw_suffix(proc_spine_model)
        switch_list += [
            f"**{pfx}-{spine_vsuffix}-SPINE-A** config file: `{fname_spine_a}`",
            f"**{pfx}-{spine_vsuffix}-SPINE-B** config file: `{fname_spine_b}`",
        ]

    st.markdown("**Config files downloaded from this toolkit:**")
    for s in switch_list:
        st.markdown(f"- {s}")

    st.markdown(
        "\n**Tools required:**\n"
        "- Laptop with VAST SE Toolkit\n"
        "- Console cable (RJ45 to USB)\n"
        "- Ethernet patch cable (for eth0 MGMT)\n"
        "- Serial terminal app (PuTTY on Windows / Serial.app on Mac)\n"
    )

    st.info(
        "💡 **Serial connection settings for Mellanox/Cumulus:** "
        "115200 baud, 8 data bits, no parity, 1 stop bit, no flow control."
    )

    # ── Helper to render per-switch steps ───────────────────
    def render_switch_procedure(
        switch_label, hostname, mgmt_ip, config_filename,
        switch_side, is_primary, peer_ip
    ):
        priority = "1000 (Primary)" if is_primary else "2000 (Secondary)"
        mgmt_ip_only = mgmt_ip.split("/")[0]

        st.markdown(f"#### Connect to {switch_label}")
        st.markdown(
            f"Connect your **serial cable** to the console port "
            f"and your **Ethernet cable** to the `eth0` port on "
            f"**{hostname}**."
        )
        st.info(
            "⚠️ You may need to hand-type serial terminal commands. "
            "Copy/paste can be unreliable over serial connections."
        )

        st.markdown("**Step 1 — Factory reset the switch:**")
        st.code("nv action reset system factory-default", language="bash")
        st.caption(
            "Wait for the switch to fully reboot before continuing. "
            "This ensures no previous config interferes."
        )

        st.markdown("**Step 2 — Set a temporary management IP:**")
        st.code(
            f"nv unset interface eth0 ip address dhcp\n"
            f"nv set interface eth0 ip address {TEMP_IP}\n"
            f"nv config apply",
            language="bash"
        )

        st.markdown(
            f"**Step 3 — SCP the config file from your laptop:**"
        )
        st.caption(
            "Run this from your laptop (not the switch terminal)."
        )
        st.code(
            f"scp {config_filename} cumulus@{TEMP_IP.split('/')[0]}:/tmp/",
            language="bash"
        )
        st.warning(
            "If you see a host key warning run this on your laptop first:  \n"
            f"`ssh-keygen -R {TEMP_IP.split('/')[0]}`"
        )

        st.markdown("**Step 4 — Back on the serial terminal, remove the temp IP:**")
        st.code(
            f"nv unset interface eth0 ip address {TEMP_IP}\n",
            language="bash"
        )

        st.markdown("**Step 5 — Make the config executable and apply it:**")
        st.code(
            f"chmod +x /tmp/{config_filename}\n"
            f"sed -i 's/\\r//' /tmp/{config_filename}\n"
            f"/tmp/{config_filename}",
            language="bash"
        )
        st.caption(
            "The `sed` command removes Windows line endings. "
            "The config will apply, save, and set the permanent MGMT IP."
        )

        st.markdown("**Step 6 — Connect MGMT cable to customer network and validate NTP:**")
        st.code(
            f"# Confirm date is correct\n"
            f"date\n\n"
            f"# Check NTP sync"
            + (
                f"\nntpq -p\n# Look for * or + next to {proc_ntp}"
                if proc_ntp else
                f"\nntpq -p\n# ⚠️ NTP server not set — check Tab 1"
            ),
            language="bash"
        )

        st.success(
            f"✅ **{hostname}** configured. "
            f"Permanent MGMT IP: `{mgmt_ip_only}` — "
            f"MLAG priority: `{priority}`"
        )
        st.markdown("---")

    # ── Section 2: Internal Storage Fabric ──────────────────
    st.markdown("---")
    st.markdown("### 2️⃣ Internal Storage Fabric Switches")
    st.markdown(
        f"Switch model: **{proc_sw_model}**  \n"
        f"OS: **{'Cumulus NV' if proc_profile['os'] == 'cumulus' else 'Arista EOS'}**"
    )

    render_switch_procedure(
        switch_label    = f"Switch A — {full_sw_a}",
        hostname        = full_sw_a,
        mgmt_ip         = proc_sw_a_ip,
        config_filename = fname_sw_a,
        switch_side     = "A",
        is_primary      = True,
        peer_ip         = proc_sw_b_ip.split("/")[0]
    )

    render_switch_procedure(
        switch_label    = f"Switch B — {full_sw_b}",
        hostname        = full_sw_b,
        mgmt_ip         = proc_sw_b_ip,
        config_filename = fname_sw_b,
        switch_side     = "B",
        is_primary      = False,
        peer_ip         = proc_sw_a_ip.split("/")[0]
    )

    # ── Section 3: GPU Switches ──────────────────────────────
    if proc_gpu:
        st.markdown("---")
        st.markdown("### 3️⃣ GPU / Data Network Switches")
        st.markdown(
            f"Switch model: **{proc_gpu_model}**  \n"
            f"OS: **{'Cumulus NV' if proc_gpu_profile['os'] == 'cumulus' else 'Arista EOS'}**"
        )

        render_switch_procedure(
            switch_label    = f"GPU Switch A — {full_sw_a}-GPU",
            hostname        = f"{full_sw_a}-GPU",
            mgmt_ip         = proc_gpu_sw_a,
            config_filename = fname_gpu_sw_a,
            switch_side     = "A",
            is_primary      = True,
            peer_ip         = proc_gpu_sw_b.split("/")[0]
        )

        render_switch_procedure(
            switch_label    = f"GPU Switch B — {full_sw_b}-GPU",
            hostname        = f"{full_sw_b}-GPU",
            mgmt_ip         = proc_gpu_sw_b,
            config_filename = fname_gpu_sw_b,
            switch_side     = "B",
            is_primary      = False,
            peer_ip         = proc_gpu_sw_a.split("/")[0]
        )

    # ── Section 4: Spine Switches ────────────────────────────
    if spine_enabled:
        spine_vsuffix   = get_sw_suffix(proc_spine_model)
        spine_a_name    = f"{pfx}-{spine_vsuffix}-SPINE-A"
        spine_b_name    = f"{pfx}-{spine_vsuffix}-SPINE-B"

        st.markdown("---")
        st.markdown("### 4️⃣ Spine Switches")
        st.markdown(
            f"Switch model: **{proc_spine_model}**  \n"
            f"OS: **{'Cumulus NV' if proc_spine_profile['os'] == 'cumulus' else 'Arista EOS'}**"
        )

        render_switch_procedure(
            switch_label    = f"Spine A — {spine_a_name}",
            hostname        = spine_a_name,
            mgmt_ip         = proc_spine_a_ip,
            config_filename = fname_spine_a,
            switch_side     = "A",
            is_primary      = True,
            peer_ip         = proc_spine_b_ip.split("/")[0]
        )

        render_switch_procedure(
            switch_label    = f"Spine B — {spine_b_name}",
            hostname        = spine_b_name,
            mgmt_ip         = proc_spine_b_ip,
            config_filename = fname_spine_b,
            switch_side     = "B",
            is_primary      = False,
            peer_ip         = proc_spine_a_ip.split("/")[0]
        )

    # ── Section 5: Post-Config Validation ───────────────────
    section_num = (
        3 + (1 if proc_gpu else 0) + (1 if spine_enabled else 0)
    )
    st.markdown("---")
    st.markdown(f"### {section_num}️⃣ Post-Config Validation")
    st.markdown(
        "Run these checks on **every switch** after all configs are applied."
    )

    st.markdown("#### MLAG Validation")
    st.markdown(
        "Run on both switches. One must show `primary`, "
        "the other `secondary`. Both must show `peer-alive: True`."
    )
    st.code("nv show mlag", language="bash")

    sw_a_ip_only = proc_sw_a_ip.split("/")[0]
    sw_b_ip_only = proc_sw_b_ip.split("/")[0]

    st.markdown("**Expected output — Switch A:**")
    st.code(
        f"local-role      primary\n"
        f"peer-role       secondary\n"
        f"peer-alive      True\n"
        f"[backup]        {sw_b_ip_only}",
        language="text"
    )

    st.markdown("**Expected output — Switch B:**")
    st.code(
        f"local-role      secondary\n"
        f"peer-role       primary\n"
        f"peer-alive      True\n"
        f"[backup]        {sw_a_ip_only}",
        language="text"
    )

    st.markdown("#### Peerlink Validation")
    st.code("nv show interface peerlink", language="bash")
    st.caption("Confirm `oper-status: up` and `link.state: up`.")

    st.markdown("#### MTU Validation")
    st.code(
        f"nv show interface | grep mtu\n"
        f"# All node ports should show {proc_profile['mtu']}",
        language="bash"
    )

    st.markdown("#### LLDP Validation")
    st.markdown(
        "Once all nodes are cabled, run the LLDP validation script "
        "from **Tab 3 → Section 4**. "
        f"Confirm all **{(num_dboxes * 2) + num_cnodes}** "
        "expected nodes are visible before starting VAST bootstrap."
    )

    st.success(
        "✅ All switches validated — ready for VAST bootstrap."
    )

# ============================================================
# TAB 4 — CONFLUENCE INSTALL PLAN GENERATOR
# ============================================================
with tab4:
    try:
        st.write("TAB5 ALIVE")  # ← add this as the very first line
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


# ============================================================

# ============================================================
#=============================================================
# ============================================================
# TAB 1 — SESSION
# ============================================================
with tab1:
    st.subheader("🧑‍💻 Session")
    st.caption("Set your identity and manage project saves. All fields feed the sidebar status bar and the install plan.")

    st.markdown("---")
    st.markdown("### 👤 SE & Customer Identity")

    id_col1, id_col2 = st.columns(2)
    with id_col1:
        se_name = st.text_input(
            "SE Name",
            value=st.session_state.get("se_name", ""),
            placeholder="Your full name"
        )
        st.session_state["se_name"] = se_name

        customer = st.text_input(
            "Customer Name",
            value=st.session_state.get("customer", ""),
            placeholder="e.g. Acme Corp"
        )
        st.session_state["customer"] = customer

        cluster_name = st.text_input(
            "Cluster Name",
            value=st.session_state.get("cluster_name", ""),
            placeholder="e.g. ACME-VAST-01"
        )
        st.session_state["cluster_name"] = cluster_name

    with id_col2:
        _saved_date = st.session_state.get("install_date", date.today())
        if isinstance(_saved_date, str):
            try:
                from datetime import datetime as _dt
                _saved_date = _dt.strptime(_saved_date, "%Y-%m-%d").date()
            except Exception:
                _saved_date = date.today()
        install_date = st.date_input("Install Date", value=_saved_date)
        st.session_state["install_date"] = str(install_date)

        proj_sfdc   = st.text_input("SFDC Opportunity URL",
                        placeholder="https://vastdata.lightning.force.com/…",
                        key="proj_sfdc")
        proj_ticket = st.text_input("Install Ticket URL",
                        placeholder="https://vastdata.lightning.force.com/…",
                        key="proj_ticket")
        proj_slack  = st.text_input("Slack Internal Channel",
                        placeholder="#cust-acme-corp",
                        key="proj_slack")

    # ── Project Save / Load ──────────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 Project")

    if st.session_state.get("_save_msg"):
        st.success(st.session_state.pop("_save_msg"))

    if not _DB_AVAILABLE:
        st.warning(
            "⚠️ Database unavailable — projects cannot be saved or loaded. "
            "Check that `db.py` is present and `/app/data/` is writable."
        )
    else:
        # Auto-backup on first render each session
        if not st.session_state.get("_auto_backup_done"):
            _db.auto_backup_if_stale()
            st.session_state["_auto_backup_done"] = True

        proj_id = st.session_state.get("_db_project_id")
        proj_id_label = f"Project #{proj_id}" if proj_id else "Unsaved project"

        db_col1, db_col2, db_col3 = st.columns([1, 1, 1])

        with db_col1:
            if st.button("🆕 New Project", use_container_width=True):
                st.session_state["_pending_clear"] = True
                st.rerun()

        with db_col2:
            save_milestone = st.selectbox(
                "Milestone",
                options=[
                    "Initial / Sizing",
                    "Pre-Install",
                    "Post-Install / Config",
                    "Other",
                ],
                key="_save_milestone",
                label_visibility="collapsed"
            )
            if save_milestone == "Other":
                save_other_notes = st.text_input(
                    "Describe this save",
                    placeholder="e.g. post spine-leaf config",
                    key="_save_other_notes"
                )
                _final_label = f"Other: {save_other_notes}" if save_other_notes else "Other"
            else:
                _final_label = save_milestone
            if st.button("💾 Save Project", use_container_width=True):
                try:
                    _save_data = {k: v for k, v in st.session_state.items()
                                  if _is_saveable(k)}
                    _save_data["_db_project_id"] = st.session_state.get("_db_project_id")
                    pid = _db.save_project(
                        _save_data,
                        label=_final_label
                    )
                    st.session_state["_db_project_id"] = pid
                    st.session_state["_save_msg"] = f"✅ Saved — {_final_label}"
                    st.rerun()
                except Exception as e:
                    st.error(f"Save failed: {e}")

        with db_col3:
            try:
                projects = _db.list_projects()
            except Exception:
                projects = []

            if not projects:
                st.info("No saved projects yet.")
            else:
                proj_options = {
                    f"#{p['id']} — {p['name']} ({p['updated_at'][:10]})": p['id']
                    for p in projects
                }
                selected_label = st.selectbox(
                    "Load project",
                    options=list(proj_options.keys()),
                    key="_load_select",
                    label_visibility="collapsed"
                )
                _load_col, _del_col = st.columns([1, 1])
                with _load_col:
                    if st.button("📂 Load", use_container_width=True):
                        try:
                            pid = proj_options[selected_label]
                            state = _db.load_project(pid)
                            st.session_state["_pending_load"] = state
                            st.rerun()
                        except Exception as e:
                            st.error(f"Load failed: {e}")
                with _del_col:
                    _del_pid = proj_options[selected_label]
                    if st.session_state.get("_confirm_del_proj") == _del_pid:
                        if st.button("⚠️ Confirm", use_container_width=True, type="primary"):
                            try:
                                _db.delete_project(_del_pid)
                                if st.session_state.get("_db_project_id") == _del_pid:
                                    st.session_state["_pending_clear"] = True
                                st.session_state.pop("_confirm_del_proj", None)
                                st.session_state["_save_msg"] = "🗑️ Project deleted."
                                st.rerun()
                            except Exception as e:
                                st.error(f"Delete failed: {e}")
                    else:
                        if st.button("🗑️ Delete", use_container_width=True):
                            st.session_state["_confirm_del_proj"] = _del_pid
                            st.rerun()

        # Version history expander
        if proj_id:
            with st.expander(f"🕓 Version history — {proj_id_label}", expanded=False):
                try:
                    versions = _db.get_project_versions(proj_id)
                    if not versions:
                        st.caption("No versions saved yet.")
                    else:
                        for v in versions:
                            v_label = v['label'] or "—"
                            v_col1, v_col2, v_col3 = st.columns([4, 1, 1])
                            with v_col1:
                                st.caption(
                                    f"v{v['version_num']} · "
                                    f"{v['saved_at'][:16].replace('T', ' ')} · "
                                    f"{v_label}"
                                )
                            with v_col2:
                                if st.button("Restore", key=f"_restore_v{v['id']}", use_container_width=True):
                                    try:
                                        state = _db.load_version(v['id'])
                                        st.session_state["_pending_load"] = state
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Restore failed: {e}")
                            with v_col3:
                                if st.session_state.get("_confirm_del_ver") == v['id']:
                                    if st.button("⚠️", key=f"_confirm_del_v{v['id']}", use_container_width=True, help="Click to confirm delete"):
                                        try:
                                            _db.delete_version(v['id'])
                                            st.session_state.pop("_confirm_del_ver", None)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Delete failed: {e}")
                                else:
                                    if st.button("🗑️", key=f"_del_v{v['id']}", use_container_width=True, help="Delete this version"):
                                        st.session_state["_confirm_del_ver"] = v['id']
                                        st.rerun()
                except Exception as e:
                    st.error(f"Could not load version history: {e}")

        st.caption(f"Current: {proj_id_label}")



# ============================================================
# TAB 2 — CAPACITY & PERFORMANCE SIZER
# ============================================================
with tab2:
    st.subheader("📏 Capacity & Performance Sizer")
    st.caption("Indicative sizing only — based on published VAST performance data. Not a formal quote.")

    st.markdown("---")

    sizer_col1, sizer_col2 = st.columns([1, 1])

    with sizer_col1:
        st.markdown("### 🖥️ Hardware Selection")

        sizer_cnode_gen = st.selectbox(
            "CNode Generation",
            options=list(CNODE_PERF.keys()),
            key="sizer_cnode_gen"
        )
        sizer_num_cnodes = st.slider(
            "Number of CNodes",
            min_value=1, max_value=28, value=4,
            key="sizer_num_cnodes"
        )
        sizer_dbox_model = st.selectbox(
            "DBox Model",
            options=list(DBOX_PROFILES.keys()),
            key="sizer_dbox_model"
        )
        sizer_num_dboxes = st.slider(
            "Number of DBoxes",
            min_value=1, max_value=14, value=1,
            key="sizer_num_dboxes"
        )

        st.markdown("### 🎯 Workload")
        sizer_use_case = st.selectbox(
            "Use Case",
            options=list(DR_ESTIMATES.keys()),
            key="sizer_use_case"
        )

        _dr_min, _dr_typ, _dr_max = DR_ESTIMATES[st.session_state.get("sizer_use_case", list(DR_ESTIMATES.keys())[0])]
        st.caption(f"Typical DRR range for this use case: {_dr_min}x — {_dr_max}x (typical: {_dr_typ}x)")
        sizer_drr_override = st.number_input(
            "SE DRR Override (leave at 0 to use use-case typical)",
            min_value=0.0, max_value=10.0, value=0.0, step=0.1,
            key="sizer_drr_override"
        )

        sizer_ratio = st.selectbox(
            "Workload Read/Write Ratio",
            options=list(CNODE_PERF["GEN6 Turin"].keys()),
            key="sizer_ratio"
        )

        st.markdown("### 📈 Growth")
        sizer_growth_years = st.slider(
            "Growth projection (years)", min_value=1, max_value=5, value=3,
            key="sizer_growth_years"
        )
        sizer_growth_pct = st.slider(
            "Annual data growth (%)", min_value=0, max_value=100, value=20,
            key="sizer_growth_pct"
        )

    with sizer_col2:
        st.markdown("### 📊 Results")

        dbox  = DBOX_PROFILES[sizer_dbox_model]
        cperf = CNODE_PERF[sizer_cnode_gen]

        # Capacity
        raw_tb      = dbox["raw_tb"]    * sizer_num_dboxes
        usable_tb   = dbox["usable_tb"] * sizer_num_dboxes
        dr_min, dr_typ, dr_max = DR_ESTIMATES[sizer_use_case]
        # Use SE override if set, otherwise use typical
        sizer_drr_override = st.session_state.get("sizer_drr_override", 0.0)
        dr_effective = sizer_drr_override if sizer_drr_override > 0 else dr_typ
        eff_min_tb  = usable_tb * dr_min
        eff_typ_tb  = usable_tb * dr_effective
        eff_max_tb  = usable_tb * dr_max

        # Performance
        perf_per_cnode = cperf.get(sizer_ratio, 0)
        total_perf_gbs = perf_per_cnode * sizer_num_cnodes

        # Growth
        growth_factor = (1 + sizer_growth_pct / 100) ** sizer_growth_years
        future_tb = usable_tb * growth_factor

        # ── Capacity block ───────────────────────────────────
        st.markdown("#### 💾 Capacity")
        cap_data = {
            "Metric": [
                "Raw Capacity",
                "Usable Capacity",
                f"Effective (min @ {dr_min}x DR)",
                f"Effective ({'SE override' if sizer_drr_override > 0 else 'typical'} @ {dr_effective}x DR)",
                f"Effective (max @ {dr_max}x DR)",
                f"Projected Usable in {sizer_growth_years}yr ({sizer_growth_pct}%/yr)",
            ],
            "Value": [
                f"{raw_tb:,.1f} TB",
                f"{usable_tb:,.1f} TB",
                f"{eff_min_tb:,.1f} TB",
                f"{eff_typ_tb:,.1f} TB",
                f"{eff_max_tb:,.1f} TB",
                f"{future_tb:,.1f} TB",
            ]
        }
        st.table(cap_data)

        # ── Performance block ────────────────────────────────
        st.markdown("#### ⚡ Performance")
        st.metric(
            label=f"{sizer_cnode_gen} × {sizer_num_cnodes} CNodes — {sizer_ratio}",
            value=f"{total_perf_gbs:.1f} GB/s"
        )

        perf_rows = []
        for ratio, per_node in cperf.items():
            total = per_node * sizer_num_cnodes
            perf_rows.append({
                "Workload Mix":     ratio,
                "Per CNode (GB/s)": f"{per_node:.1f}",
                f"× {sizer_num_cnodes} CNodes (GB/s)": f"{total:.1f}",
            })
        st.dataframe(perf_rows, use_container_width=True)

        # ── Hardware summary ─────────────────────────────────
        st.markdown("#### 📦 Configuration Summary")
        st.info(
            f"**{sizer_num_dboxes}× {sizer_dbox_model}** "
            f"({dbox['form_factor']}, {dbox['usable_tb']:.2f} TB usable each)  \n"
            f"**{sizer_num_cnodes}× {sizer_cnode_gen} CNode**  \n"
            f"**Use case:** {sizer_use_case}  \n"
            f"**Switch fabric:** VAST internal storage fabric (200GbE)"
        )

        # ── AI / GPU note ─────────────────────────────────────
        if "AI" in sizer_use_case:
            st.warning(
                "⚠️ **AI workloads** — NFS over RDMA / GDS required for full throughput. "
                "Confirm GPU servers support RoCEv2 and GDS before sizing."
            )

        # ── Erasure coding note ───────────────────────────────
        st.caption(
            "VAST uses a unique Wide Stripe Erasure Code which benefits customers with typically larger environments. "
            "Usable figures shown are per-DBox actuals — overhead is cluster-size dependent (~2.7% at scale). "
            "Data reduction estimates are indicative ranges based on use case — actual results vary. "
            "SE DRR override allows you to apply a customer-specific reduction ratio to the typical effective capacity."
        )

    st.markdown("---")

    apply_col1, apply_col2 = st.columns([1, 2])
    with apply_col1:
        if st.button("📋 Apply to Project →", use_container_width=True):
            _apply = dict(st.session_state)
            _apply["proj_num_dboxes"] = sizer_num_dboxes
            _apply["proj_num_cnodes"] = sizer_num_cnodes
            _apply["proj_dbox_type"]  = sizer_dbox_model
            _apply["proj_cbox_type"]  = sizer_cnode_gen
            st.session_state["_pending_load"] = _apply
            st.session_state["_save_msg"] = (
                f"✅ Sizer applied — "
                f"{sizer_num_dboxes}× {sizer_dbox_model}, "
                f"{sizer_num_cnodes}× {sizer_cnode_gen}. "
                f"Review and complete Tab 3."
            )
            st.rerun()
    with apply_col2:
        st.caption("Optional — applies hardware selection to Project Details. You can also fill Tab 3 manually.")

    st.caption("Performance data: VAST GEN5 Genoa and GEN6 Turin, 1MB Random I/O. Source: VAST internal benchmarks.")


# ============================================================
# TAB 9 — RACK DIAGRAM
# ============================================================
with tab9:
    st.subheader("📐 Rack Diagram")
    st.caption("Configure rack constraints and device placement. The diagram auto-splits into multiple racks if limits are exceeded.")

    st.markdown("---")

    rack_col1, rack_col2 = st.columns([1, 2])

    with rack_col1:
        st.markdown("### 🗄️ Rack Constraints")
        rack_u          = st.number_input("Rack Height (U)", min_value=10, max_value=52, value=42, key="rack_u")
        rack_use_kw     = st.toggle("Show power in kW", value=True, key="rack_use_kw")
        _power_unit     = "kW" if rack_use_kw else "W"
        _power_div      = 1000 if rack_use_kw else 1
        rack_max_power_kw = st.number_input(
            f"Max Power per Rack ({_power_unit})",
            min_value=0.0,
            value=10.0 if rack_use_kw else 10000.0,
            step=0.5 if rack_use_kw else 500.0,
            key="rack_max_power_kw"
        )
        rack_max_power  = int(rack_max_power_kw * _power_div)  # always in W internally
        rack_use_lbs    = st.toggle("Show weight in lbs", value=False, key="rack_use_kg")
        _weight_unit    = "lbs" if rack_use_lbs else "kg"
        _weight_conv    = 1.0 if rack_use_lbs else 0.453592
        rack_max_weight_disp = st.number_input(
            f"Max Weight per Rack ({_weight_unit})",
            min_value=0.0,
            value=1134.0 if rack_use_lbs else 500.0,
            step=50.0 if rack_use_lbs else 25.0,
            key="rack_max_weight_disp"
        )
        rack_max_weight = rack_max_weight_disp / _weight_conv  # always in lbs internally
        rack_top_down   = st.toggle("Top-down orientation (U1 at top)", value=False, key="rack_top_down")

        st.markdown("### 📦 Device Placement")

        _dbox_model  = st.session_state.get("proj_dbox_type",  list(DBOX_PROFILES.keys())[0])
        _cnode_gen   = st.session_state.get("proj_cbox_type",  list(CNODE_PERF.keys())[0])
        _sw_model    = st.session_state.get("tab7_sw_model",   list(HARDWARE_PROFILES.keys())[0])
        _gpu_model   = st.session_state.get("tab8_sw_model",   list(HARDWARE_PROFILES.keys())[0])
        _gpu_enabled = st.session_state.get("tab8_enabled",    False)
        _spine_topo  = topology == "Spine-Leaf"
        _spine_model = st.session_state.get("spine_sw_model",  list(HARDWARE_PROFILES.keys())[0])

        _dbox_spec   = DEVICE_SPECS.get(_dbox_model,  {"u": 1, "weight_lbs": 50,  "avg_w": 750,  "max_w": 850})
        _cnode_spec  = DEVICE_SPECS.get(_cnode_gen,   {"u": 1, "weight_lbs": 44,  "avg_w": 500,  "max_w": 775})
        _sw_spec     = DEVICE_SPECS.get(_sw_model,    {"u": 1, "weight_lbs": 25,  "avg_w": 250,  "max_w": 630})
        _gpu_spec    = DEVICE_SPECS.get(_gpu_model,   {"u": 1, "weight_lbs": 25,  "avg_w": 250,  "max_w": 630})
        _spine_spec  = DEVICE_SPECS.get(_spine_model, {"u": 1, "weight_lbs": 25,  "avg_w": 250,  "max_w": 630})

        rack_multi      = st.toggle("Multiple Racks", value=False, key="rack_multi")
        num_racks       = st.slider("Number of Racks", min_value=1, max_value=4, value=2, key="rack_num_racks") if rack_multi else 1

        # Build per-device template (all devices, no RU yet)
        _tpl = []
        _tpl.append({"Device": "Storage SW-A",  "type": "switch",     "u": _sw_spec["u"],    "color": "#E8821A", "model_key": _sw_model,    "weight": _sw_spec["weight_lbs"],    "avg_w": _sw_spec["avg_w"],    "max_w": _sw_spec["max_w"]})
        _tpl.append({"Device": "Storage SW-B",  "type": "switch",     "u": _sw_spec["u"],    "color": "#E8821A", "model_key": _sw_model,    "weight": _sw_spec["weight_lbs"],    "avg_w": _sw_spec["avg_w"],    "max_w": _sw_spec["max_w"]})
        if _gpu_enabled:
            _tpl.append({"Device": "GPU SW-A",  "type": "gpu_switch", "u": _gpu_spec["u"],   "color": "#8B5CF6", "model_key": _gpu_model,   "weight": _gpu_spec["weight_lbs"],   "avg_w": _gpu_spec["avg_w"],   "max_w": _gpu_spec["max_w"]})
            _tpl.append({"Device": "GPU SW-B",  "type": "gpu_switch", "u": _gpu_spec["u"],   "color": "#8B5CF6", "model_key": _gpu_model,   "weight": _gpu_spec["weight_lbs"],   "avg_w": _gpu_spec["avg_w"],   "max_w": _gpu_spec["max_w"]})
        if _spine_topo:
            _tpl.append({"Device": "Spine SW-A","type": "spine",      "u": _spine_spec["u"], "color": "#EF4444", "model_key": _spine_model, "weight": _spine_spec["weight_lbs"], "avg_w": _spine_spec["avg_w"], "max_w": _spine_spec["max_w"]})
            _tpl.append({"Device": "Spine SW-B","type": "spine",      "u": _spine_spec["u"], "color": "#EF4444", "model_key": _spine_model, "weight": _spine_spec["weight_lbs"], "avg_w": _spine_spec["avg_w"], "max_w": _spine_spec["max_w"]})
        for _i in range(1, num_cnodes + 1):
            _tpl.append({"Device": f"{pfx}-CNODE-{_i}", "type": "cnode", "u": _cnode_spec["u"], "color": "#16A34A", "model_key": _cnode_gen,  "weight": _cnode_spec["weight_lbs"], "avg_w": _cnode_spec["avg_w"], "max_w": _cnode_spec["max_w"]})
        for _i in range(1, num_dboxes + 1):
            _tpl.append({"Device": f"{pfx}-DBOX-{_i}",  "type": "dbox",  "u": _dbox_spec["u"],  "color": "#2563EB", "model_key": _dbox_model, "weight": _dbox_spec["weight_lbs"],  "avg_w": _dbox_spec["avg_w"],  "max_w": _dbox_spec["max_w"]})

        # Append user-uploaded custom devices
        for _cd in st.session_state.get("rack_custom_devices", []):
            _tpl.append({
                "Device":    _cd["name"],
                "type":      "custom",
                "u":         _cd["u"],
                "color":     "#6B7280",
                "model_key": _cd.get("product_name") or _cd.get("vendor", "") or "Custom",
                "img_b64":   _cd.get("img_b64", ""),
                "weight":    _cd["weight_lbs"],
                "avg_w":     _cd["avg_w"],
                "max_w":     _cd["max_w"],
            })

        # ── Add Device from Inventory ─────────────────────────
        st.markdown("### ➕ Add Device")
        _inv_all_rack = _get_inventory_cached()
        if not _inv_all_rack:
            st.caption("Your device inventory is empty — go to the **📦 Device Inventory** tab to add products.")
        else:
            _pick_opts = ["— select a product —"] + [d["product_name"] for d in _inv_all_rack]
            _pick_col1, _pick_col2, _pick_col3, _pick_col4 = st.columns([3, 2, 1, 1])
            with _pick_col1:
                _pick_product = st.selectbox("Product", _pick_opts, key="rack_pick_product")
            with _pick_col2:
                _pick_dname = st.text_input("Device Name", key="rack_pick_dname",
                                             placeholder="defaults to product name")
            with _pick_col3:
                _pick_rack = st.selectbox("Rack No.", options=list(range(1, num_racks + 1)),
                                           key="rack_pick_rack",
                                           disabled=(num_racks == 1))
            with _pick_col4:
                st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
                _pick_disabled = (_pick_product == "— select a product —")
                if st.button("+ Add", key="rack_pick_add", disabled=_pick_disabled,
                             use_container_width=True):
                    _sel_inv = next((d for d in _inv_all_rack if d["product_name"] == _pick_product), None)
                    if _sel_inv:
                        st.session_state["_pending_rack_add"] = {
                            "name":         _pick_dname.strip() or _sel_inv["product_name"],
                            "product_name": _sel_inv["product_name"],
                            "u":            _sel_inv["u_height"],
                            "weight_lbs":   _sel_inv["weight_lbs"],
                            "avg_w":        _sel_inv["avg_w"],
                            "max_w":        _sel_inv["max_w"],
                            "img_b64":      _sel_inv["img_b64"],
                            "rack_no":      int(_pick_rack),
                        }
                        st.rerun()
            # Show selected product specs as a hint
            if _pick_product != "— select a product —":
                _hint = next((d for d in _inv_all_rack if d["product_name"] == _pick_product), None)
                if _hint:
                    _hint_v = f" · {_hint['vendor']}" if _hint["vendor"] else ""
                    st.caption(
                        f"{_hint['category']}{_hint_v} · {_hint['u_height']}U · "
                        f"{_hint['weight_lbs']:.0f} lbs · {_hint['avg_w']}W avg / {_hint['max_w']}W max"
                    )

        # ── Devices added to this rack ───────────────────────
        _existing_custom = st.session_state.get("rack_custom_devices", [])
        if _existing_custom:
            st.markdown("**In this rack:**")
            for _ci, _cd in enumerate(_existing_custom):
                _crl, _crr = st.columns([6, 1])
                with _crl:
                    _prod_lbl = (f' <span style="color:#888">({_cd["product_name"]})</span>'
                                 if _cd.get("product_name") and _cd["product_name"] != _cd["name"]
                                 else "")
                    st.markdown(
                        f'<p style="font-size:12px;margin:4px 0">'
                        f'<b>{_cd["name"]}</b>{_prod_lbl} — '
                        f'{_cd["u"]}U · {_cd["weight_lbs"]:.0f} lbs · '
                        f'{_cd["avg_w"]}W avg / {_cd["max_w"]}W max'
                        f'{"  📷" if _cd.get("img_b64") else ""}</p>',
                        unsafe_allow_html=True,
                    )
                with _crr:
                    if st.button("✕", key=f"rack_cust_rm_{_ci}",
                                 help="Remove from this rack"):
                        st.session_state["_pending_rack_rm"] = _ci
                        st.rerun()

        # Compute sequential defaults
        _def_ru = {}
        _cur_ru = 1
        for _t in _tpl:
            _def_ru[_t["Device"]] = _cur_ru
            _cur_ru += _t["u"]

        # Per-device placement rows — individual widgets, no data_editor
        _hc1, _hc2, _hc3, _hc4 = st.columns([2, 2, 1, 2])
        _hc1.caption("Device Name")
        _hc2.caption("Model / Type")
        _hc3.caption("Rack")
        _hc4.caption("Start RU")

        _device_placement = {}
        for _t in _tpl:
            _k  = _t["Device"].replace(" ", "_").replace("-", "_")
            _dc1, _dc2, _dc3, _dc4 = st.columns([2, 2, 1, 2])
            with _dc1:
                st.markdown(f'<p style="font-size:12px;margin:8px 0 0 0">{_t["Device"]}</p>', unsafe_allow_html=True)
            with _dc2:
                st.markdown(f'<p style="font-size:11px;color:#aaa;margin:8px 0 0 0">{_t["model_key"]}</p>', unsafe_allow_html=True)
            with _dc3:
                _rack_val = st.selectbox("Rack", options=list(range(1, num_racks + 1)),
                                         key=f"rack_rack_{_k}", label_visibility="collapsed")
            with _dc4:
                _ru_val = st.number_input("RU", min_value=1, max_value=int(rack_u), step=1,
                                          key=f"rack_ru_{_k}", label_visibility="collapsed")
            _device_placement[_t["Device"]] = {"rack": _rack_val, "ru": _ru_val}

    with rack_col2:
        st.markdown("### 📊 Power & Weight Analysis")

        # Build device list from per-device placement widgets
        devices = []
        for _t in _tpl:
            _pl = _device_placement.get(_t["Device"], {"rack": 1, "ru": _def_ru.get(_t["Device"], 1)})
            devices.append({
                "name":      _t["Device"],
                "ru":        int(_pl["ru"]),
                "rack":      int(_pl["rack"]),
                "u":         _t["u"],
                "weight":    _t["weight"],
                "avg_w":     _t["avg_w"],
                "max_w":     _t["max_w"],
                "color":     _t["color"],
                "type":      _t["type"],
                "model_key": _t["model_key"],
                "img_b64":   _t.get("img_b64", ""),
            })

        # Group devices by rack, sort each rack by RU
        rack_groups = [[] for _ in range(num_racks)]
        for _d in devices:
            _ri = max(0, min(_d["rack"] - 1, num_racks - 1))
            rack_groups[_ri].append(_d)
        for _grp in rack_groups:
            _grp.sort(key=lambda d: d["ru"])

        # Totals (across all racks)
        devices = [d for grp in rack_groups for d in grp]
        total_weight = sum(d["weight"] for d in devices)
        total_avg_w  = sum(d["avg_w"]  for d in devices)
        total_max_w  = sum(d["max_w"]  for d in devices)
        total_u_used = sum(d["u"]      for d in devices)

        # Metrics
        _disp_weight = lambda w: f"{w * _weight_conv:.0f} {_weight_unit}"
        _disp_power  = lambda p: f"{p / _power_div:.1f} {_power_unit}" if rack_use_kw else f"{p:,}W"

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total U Used", f"{total_u_used}U")
        with m2:
            st.metric(f"Total Weight ({_weight_unit})", _disp_weight(total_weight))
        with m3:
            st.metric(f"Avg Power ({_power_unit})", _disp_power(total_avg_w))
        with m4:
            st.metric("Racks", num_racks)

        # Warnings per rack
        for _ri, _grp in enumerate(rack_groups):
            _rw = sum(d["weight"] for d in _grp)
            _rp = sum(d["avg_w"]  for d in _grp)
            if _rw > rack_max_weight:
                st.warning(f"⚠️ Rack {_ri+1} weight ({_disp_weight(_rw)}) exceeds limit ({_disp_weight(rack_max_weight)}).")
            if _rp > rack_max_power:
                st.warning(f"⚠️ Rack {_ri+1} avg power ({_disp_power(_rp)}) exceeds limit ({_disp_power(rack_max_power)}).")

        # Power & weight table
        # ── SVG Rack Diagram ─────────────────────────────────
        st.markdown("### 🖥️ Rack Diagram")

        def _render_rack(rack_devices, rack_num, rack_u_height, top_down,
                         with_summary=False, use_kw=True, use_lbs=False, display_scale=1.0,
                         light_theme=False):
            """Render a single rack as SVG.
            with_summary=True appends a device list + totals table below the diagram.
            display_scale < 1.0 shrinks the rendered SVG for screen display via viewBox scaling.
            light_theme=True uses a white/print-friendly colour scheme (used for PDF/JPG exports).
            """
            # ── Colour theme ─────────────────────────────────────
            if light_theme:
                T = dict(
                    page_bg    = "white",
                    hdr_fill   = "#ccd3e8",
                    hdr_text   = "#111",
                    body_fill  = "#dde2f0",
                    body_stroke= "#000",
                    umark      = "#555",
                    divider    = "#bbc",
                    slot_fill  = "#eaeff7",
                    slot_stroke= "#99a",
                    name_text  = "#222",
                    sum_title  = "#444",
                    sum_hdr    = "#666",
                    sum_div    = "#bbb",
                    row_even   = "#f0f0f6",
                    row_odd    = "#e8e8f2",
                    row_text   = "#222",
                    tot_fill   = "#dde3f0",
                    tot_text   = "#111",
                )
            else:
                T = dict(
                    page_bg    = "#1a1a2e",
                    hdr_fill   = "#000000",
                    hdr_text   = "white",
                    body_fill  = "#000000",
                    body_stroke= "#000000",
                    umark      = "#555",
                    divider    = "#1a1a1a",
                    slot_fill  = "#000000",
                    slot_stroke= "#1a1a1a",
                    name_text  = "#ddd",
                    sum_title  = "#aaa",
                    sum_hdr    = "#888",
                    sum_div    = "#444",
                    row_even   = "#1e1e2e",
                    row_odd    = "#161626",
                    row_text   = "#ccc",
                    tot_fill   = "#2d2d44",
                    tot_text   = "white",
                )

            U_H      = 40      # pixels per U
            RK_W     = 360     # rack interior width (reduced to make room for name column)
            LABEL_W  = 28      # U label column width (left)
            NAME_W   = 160     # device name column width (right)
            NAME_GAP = 8       # gap between rack edge and name column
            PAD      = 10      # outer padding
            HDR_H    = 36      # rack header height
            BAR_W    = 6       # colour bar width
            SVG_W    = PAD + LABEL_W + RK_W + NAME_GAP + NAME_W + PAD
            RACK_H   = HDR_H + rack_u_height * U_H + PAD * 2

            # Summary table geometry (only relevant when with_summary=True)
            ROW_H    = 16
            SUM_PAD  = 14     # gap between rack and table
            SUM_HDR  = 22     # "Device Summary" title height
            COL_HDR  = 18     # column header row height
            TOT_H    = 20     # totals row height
            n_devs   = len(rack_devices)
            SUM_H    = SUM_PAD + SUM_HDR + COL_HDR + n_devs * ROW_H + 4 + TOT_H + PAD

            SVG_H = RACK_H + (SUM_H if with_summary else 0)

            _out_w = int(SVG_W * display_scale)
            _out_h = int(SVG_H * display_scale)
            lines = [
                f'<svg width="{_out_w}" height="{_out_h}" viewBox="0 0 {SVG_W} {SVG_H}" '
                f'xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'style="font-family: Arial, sans-serif; background: {T["page_bg"]};">',
                # Explicit background rect (cairosvg ignores CSS background property)
                f'<rect x="0" y="0" width="{SVG_W}" height="{SVG_H}" fill="{T["page_bg"]}"/>',
                f'<defs><clipPath id="clip{rack_num}"><rect x="{PAD+LABEL_W+BAR_W+1}" '
                f'y="{PAD+HDR_H}" width="{RK_W-BAR_W-2}" height="{rack_u_height*U_H}"/>'
                f'</clipPath></defs>',
                # Rack header (spans rack body only, not name column)
                f'<rect x="{PAD}" y="{PAD}" width="{LABEL_W + RK_W}" height="{HDR_H}" '
                f'rx="4" fill="{T["hdr_fill"]}"/>',
                f'<text x="{PAD + (LABEL_W + RK_W)//2}" y="{PAD + HDR_H//2 + 5}" '
                f'text-anchor="middle" fill="{T["hdr_text"]}" font-size="12" font-weight="bold">'
                f'Rack {rack_num} — {rack_u_height}U</text>',
                # Rack body background
                f'<rect x="{PAD + LABEL_W}" y="{PAD + HDR_H}" width="{RK_W}" '
                f'height="{rack_u_height * U_H}" fill="{T["body_fill"]}"/>',
                # Outer border encompassing header + body
                f'<rect x="{PAD}" y="{PAD}" width="{LABEL_W + RK_W}" height="{HDR_H + rack_u_height * U_H}" '
                f'rx="4" fill="none" stroke="{T["body_stroke"]}" stroke-width="2"/>',
            ]

            # U position markers and slot dividers
            for u in range(1, rack_u_height + 1):
                if top_down:
                    y = PAD + HDR_H + (u - 1) * U_H
                else:
                    y = PAD + HDR_H + (rack_u_height - u) * U_H
                lines.append(
                    f'<text x="{PAD + LABEL_W - 4}" y="{y + U_H//2 + 4}" '
                    f'text-anchor="end" fill="{T["umark"]}" font-size="9">{u}</text>'
                )
                if u > 1:
                    lines.append(
                        f'<line x1="{PAD + LABEL_W}" y1="{y}" x2="{PAD + LABEL_W + RK_W}" y2="{y}" '
                        f'stroke="{T["divider"]}" stroke-width="0.5"/>'
                    )

            # Draw devices
            for d in rack_devices:
                ru_start = d["ru"]
                height_u = d["u"]
                if top_down:
                    y = PAD + HDR_H + (ru_start - 1) * U_H
                else:
                    y = PAD + HDR_H + (rack_u_height - ru_start - height_u + 1) * U_H

                block_h = height_u * U_H - 2
                color   = d["color"]

                lines.append(
                    f'<rect x="{PAD + LABEL_W + 2}" y="{y + 1}" '
                    f'width="{RK_W - 4}" height="{block_h}" '
                    f'rx="2" fill="{T["slot_fill"]}" stroke="{T["slot_stroke"]}" stroke-width="1"/>'
                )
                lines.append(
                    f'<rect x="{PAD + LABEL_W + 2}" y="{y + 1}" '
                    f'width="{BAR_W}" height="{block_h}" '
                    f'rx="2" fill="{color}"/>'
                )
                # Device image — custom upload takes precedence over built-in
                _b64 = d.get("img_b64") or _get_device_img_b64(d.get("model_key", ""))
                if _b64 and block_h >= 14:
                    # Strip white backgrounds for cleaner rendering on both themes
                    _b64 = _strip_white_bg(_b64)
                    _ih = block_h - 2
                    _iw = RK_W - BAR_W - 2
                    _ix = PAD + LABEL_W + BAR_W + 1
                    _iy = y + 1
                    # Use both href (SVG 2) and xlink:href (SVG 1.1) for cairosvg compat
                    lines.append(
                        f'<image x="{_ix}" y="{_iy}" '
                        f'width="{_iw}" height="{_ih}" '
                        f'href="data:image/png;base64,{_b64}" '
                        f'xlink:href="data:image/png;base64,{_b64}" '
                        f'preserveAspectRatio="xMidYMid meet" '
                        f'clip-path="url(#clip{rack_num})"/>'
                    )
                # Device name in right-hand label column, vertically centred on slot
                _name_x  = PAD + LABEL_W + RK_W + NAME_GAP
                _name_y  = y + max(block_h // 2, 1) + 4
                _fs      = 9 if block_h < 24 else 10
                lines.append(
                    f'<text x="{_name_x}" y="{_name_y}" fill="{T["name_text"]}" font-size="{_fs}" '
                    f'dominant-baseline="auto">{d["name"]}</text>'
                )

            # ── Outer rack frame (drawn last so it sits over device edges) ──
            if light_theme:
                _frame_x = PAD + LABEL_W
                _frame_y = PAD
                _frame_w = RK_W
                _frame_h = HDR_H + rack_u_height * U_H
                # Header/body separator
                lines.append(
                    f'<line x1="{_frame_x}" y1="{PAD + HDR_H}" '
                    f'x2="{_frame_x + _frame_w}" y2="{PAD + HDR_H}" '
                    f'stroke="#000" stroke-width="1.5"/>'
                )
                # Outer frame
                lines.append(
                    f'<rect x="{_frame_x}" y="{_frame_y}" width="{_frame_w}" height="{_frame_h}" '
                    f'fill="none" stroke="#000" stroke-width="3" rx="2"/>'
                )

            # ── Summary table (download only) ──────────────────
            if with_summary and rack_devices:
                _w_conv  = 1.0 if use_lbs else 0.453592
                _w_unit  = "lbs" if use_lbs else "kg"
                _p_div   = 1000.0 if use_kw else 1.0
                _p_unit  = "kW" if use_kw else "W"

                def _fw(lbs):
                    v = lbs * _w_conv
                    return f"{v:.0f} {_w_unit}"

                def _fp(w):
                    if use_kw:
                        return f"{w / _p_div:.2f} {_p_unit}"
                    return f"{int(w)} {_p_unit}"

                ty      = RACK_H + SUM_PAD  # top of summary block
                x0      = PAD               # left margin

                # Column x positions
                cx_name = x0
                cx_u    = x0 + 248
                cx_w    = x0 + 290
                cx_ap   = x0 + 360
                cx_mp   = x0 + 430

                # Section title
                lines.append(
                    f'<text x="{x0}" y="{ty + 14}" fill="{T["sum_title"]}" font-size="11" font-weight="bold">'
                    f'Device Summary — Rack {rack_num}</text>'
                )
                ty += SUM_HDR

                # Column headers
                for cx, label in [(cx_name, "Device"), (cx_u, "U"),
                                   (cx_w, f"Weight ({_w_unit})"),
                                   (cx_ap, f"Avg ({_p_unit})"),
                                   (cx_mp, f"Max ({_p_unit})")]:
                    lines.append(
                        f'<text x="{cx}" y="{ty + 12}" fill="{T["sum_hdr"]}" font-size="9" font-weight="bold">'
                        f'{label}</text>'
                    )
                ty += COL_HDR
                lines.append(
                    f'<line x1="{x0}" y1="{ty}" x2="{x0 + LABEL_W + RK_W}" y2="{ty}" '
                    f'stroke="{T["sum_div"]}" stroke-width="0.5"/>'
                )

                # Device rows
                tot_u = tot_w = tot_ap = tot_mp = 0
                for idx, d in enumerate(rack_devices):
                    row_y    = ty + idx * ROW_H
                    row_fill = T["row_even"] if idx % 2 == 0 else T["row_odd"]
                    lines.append(
                        f'<rect x="{x0}" y="{row_y}" width="{LABEL_W + RK_W}" height="{ROW_H}" '
                        f'fill="{row_fill}"/>'
                    )
                    # colour dot
                    lines.append(
                        f'<rect x="{cx_name}" y="{row_y + 5}" width="6" height="6" '
                        f'rx="1" fill="{d["color"]}"/>'
                    )
                    row_data = [
                        (cx_name + 10, d["name"]),
                        (cx_u,         str(d["u"])),
                        (cx_w,         _fw(d["weight"])),
                        (cx_ap,        _fp(d["avg_w"])),
                        (cx_mp,        _fp(d["max_w"])),
                    ]
                    for rx, rv in row_data:
                        lines.append(
                            f'<text x="{rx}" y="{row_y + ROW_H - 4}" fill="{T["row_text"]}" font-size="9">'
                            f'{rv}</text>'
                        )
                    tot_u  += d["u"]
                    tot_w  += d["weight"]
                    tot_ap += d["avg_w"]
                    tot_mp += d["max_w"]

                ty += n_devs * ROW_H + 4
                lines.append(
                    f'<line x1="{x0}" y1="{ty}" x2="{x0 + LABEL_W + RK_W}" y2="{ty}" '
                    f'stroke="{T["sum_div"]}" stroke-width="1"/>'
                )
                ty += 2

                # Totals row
                lines.append(
                    f'<rect x="{x0}" y="{ty}" width="{LABEL_W + RK_W}" height="{TOT_H}" '
                    f'fill="{T["tot_fill"]}"/>'
                )
                for rx, rv in [
                    (cx_name + 10, "TOTAL"),
                    (cx_u,         str(tot_u)),
                    (cx_w,         _fw(tot_w)),
                    (cx_ap,        _fp(tot_ap)),
                    (cx_mp,        _fp(tot_mp)),
                ]:
                    lines.append(
                        f'<text x="{rx}" y="{ty + TOT_H - 5}" fill="{T["tot_text"]}" font-size="9" font-weight="bold">'
                        f'{rv}</text>'
                    )

            lines.append('</svg>')
            return "\n".join(lines)

        # ── Display SVGs (scaled down for on-screen view) ────
        _DISP_SCALE = 0.62
        # ROW_H=16, SUM overhead ≈ SUM_PAD+SUM_HDR+COL_HDR+TOT_H+PAD = 14+22+18+20+14 = 88
        _disp_summary_h = lambda n_devs: int((88 + n_devs * 16) * _DISP_SCALE)
        _disp_rack_h = int((36 + rack_u * 40 + 20) * _DISP_SCALE)  # HDR_H + rack body + PAD*2
        svg_cols = st.columns(min(num_racks, 3))
        for _ri, _rack_devs in enumerate(rack_groups):
            _disp_svg = _render_rack(_rack_devs, _ri + 1, rack_u, rack_top_down,
                                     with_summary=True, display_scale=_DISP_SCALE,
                                     light_theme=True)
            _disp_h = _disp_rack_h + _disp_summary_h(len(_rack_devs)) + 20
            with svg_cols[_ri % len(svg_cols)]:
                st.components.v1.html(_disp_svg, height=_disp_h, scrolling=False)

        # ── Downloads ─────────────────────────────────────────
        # PDF/JPG are generated on demand (button click) to avoid
        # blocking cairosvg conversions on every render.
        try:
            import cairosvg as _cairosvg_probe  # noqa: F401
            _cairosvg_ok = True
        except ImportError:
            _cairosvg_ok = False

        # Paper size dimensions at 150 dpi (landscape only)
        _PAPER_SIZES = {
            "A4 Landscape": (1754, 1240),
            "A3 Landscape": (2480, 1754),
        }

        st.markdown("#### ⬇️ Downloads")

        if _cairosvg_ok:
            _pdf_size = st.radio(
                "PDF paper size",
                options=list(_PAPER_SIZES.keys()),
                horizontal=True,
                key="rack_pdf_size",
            )
            _pdf_w, _pdf_h = _PAPER_SIZES[_pdf_size]

        for _ri, _rack_devs in enumerate(rack_groups):
            _base_fname = f"{pfx or 'rack'}_rack{_ri + 1}_{install_date}"
            if num_racks > 1:
                st.caption(f"Rack {_ri + 1}")

            # Download SVG computed here — fast string ops, no cairosvg
            _dl_svg = _render_rack(_rack_devs, _ri + 1, rack_u, rack_top_down,
                                   with_summary=True, use_kw=rack_use_kw, use_lbs=rack_use_lbs,
                                   display_scale=1.0, light_theme=True)

            _dl_c1, _dl_c2, _dl_c3 = st.columns(3)

            with _dl_c1:
                st.download_button(
                    "⬇️ SVG",
                    data=_dl_svg,
                    file_name=f"{_base_fname}.svg",
                    mime="image/svg+xml",
                    key=f"rack_dl_svg_{_ri}",
                    use_container_width=True,
                )

            if _cairosvg_ok:
                _pdf_ss = f"_rack_pdf_{_ri}"
                _jpg_ss = f"_rack_jpg_{_ri}"
                _pdf_size_ss = f"_rack_pdf_size_{_ri}"

                # Invalidate cached PDF if paper size changed
                if st.session_state.get(_pdf_size_ss) != _pdf_size and _pdf_ss in st.session_state:
                    del st.session_state[_pdf_ss]

                with _dl_c2:
                    if _pdf_ss in st.session_state:
                        st.download_button(
                            "⬇️ PDF",
                            data=st.session_state[_pdf_ss],
                            file_name=f"{_base_fname}.pdf",
                            mime="application/pdf",
                            key=f"rack_dl_pdf_{_ri}",
                            use_container_width=True,
                        )
                    else:
                        if st.button("🔄 Generate PDF", key=f"rack_gen_pdf_{_ri}",
                                     use_container_width=True):
                            st.session_state[_pdf_ss] = _svg_to_pdf_cached(_dl_svg, _pdf_w, _pdf_h)
                            st.session_state[_pdf_size_ss] = _pdf_size
                            st.rerun()

                with _dl_c3:
                    if _jpg_ss in st.session_state:
                        st.download_button(
                            "⬇️ JPG",
                            data=st.session_state[_jpg_ss],
                            file_name=f"{_base_fname}.jpg",
                            mime="image/jpeg",
                            key=f"rack_dl_jpg_{_ri}",
                            use_container_width=True,
                        )
                    else:
                        if st.button("🔄 Generate JPG", key=f"rack_gen_jpg_{_ri}",
                                     use_container_width=True):
                            st.session_state[_jpg_ss] = _svg_to_jpg_cached(_dl_svg, _pdf_w, _pdf_h)
                            st.rerun()

        # ── Multi-rack PDF exports ────────────────────────────
        if _cairosvg_ok and num_racks > 1:
            st.markdown("---")
            st.markdown("##### 📑 Multi-Rack PDF Exports")
            _all_svgs = tuple(
                _render_rack(grp, i + 1, rack_u, rack_top_down,
                             with_summary=True, use_kw=rack_use_kw, use_lbs=rack_use_lbs,
                             display_scale=1.0, light_theme=True)
                for i, grp in enumerate(rack_groups)
            )
            _all_fname = f"{pfx or 'rack'}_all_racks_{install_date}"
            _mp_ss  = "_rack_pdf_multipage"
            _co_ss  = "_rack_pdf_consolidated"
            _mp_sz  = "_rack_pdf_multipage_size"
            _co_sz  = "_rack_pdf_consolidated_size"

            # Invalidate if paper size changed
            if st.session_state.get(_mp_sz) != _pdf_size and _mp_ss in st.session_state:
                del st.session_state[_mp_ss]
            if st.session_state.get(_co_sz) != _pdf_size and _co_ss in st.session_state:
                del st.session_state[_co_ss]

            _exp_c1, _exp_c2 = st.columns(2)

            with _exp_c1:
                if _mp_ss in st.session_state:
                    st.download_button(
                        "⬇️ All Racks PDF (1 per page)",
                        data=st.session_state[_mp_ss],
                        file_name=f"{_all_fname}_multipage.pdf",
                        mime="application/pdf",
                        key="rack_dl_pdf_multipage",
                        use_container_width=True,
                    )
                else:
                    if st.button("🔄 Generate All Racks PDF (1 per page)",
                                 key="rack_gen_pdf_multipage", use_container_width=True):
                        st.session_state[_mp_ss] = _build_multipage_pdf(_all_svgs, _pdf_w, _pdf_h)
                        st.session_state[_mp_sz] = _pdf_size
                        st.rerun()

            with _exp_c2:
                if _co_ss in st.session_state:
                    st.download_button(
                        "⬇️ Consolidated PDF (all racks on 1 page)",
                        data=st.session_state[_co_ss],
                        file_name=f"{_all_fname}_consolidated.pdf",
                        mime="application/pdf",
                        key="rack_dl_pdf_consolidated",
                        use_container_width=True,
                    )
                else:
                    if st.button("🔄 Generate Consolidated PDF (all racks on 1 page)",
                                 key="rack_gen_pdf_consolidated", use_container_width=True):
                        st.session_state[_co_ss] = _build_consolidated_pdf(_all_svgs, _pdf_w, _pdf_h)
                        st.session_state[_co_sz] = _pdf_size
                        st.rerun()

        # Legend
        st.markdown("---")
        _has_custom = bool(st.session_state.get("rack_custom_devices"))
        legend = [
            ("#2563EB", "DBox"),
            ("#16A34A", "CNode"),
            ("#E8821A", "Storage Switch"),
            ("#8B5CF6", "GPU Switch"),
            ("#EF4444", "Spine Switch"),
        ]
        if _has_custom:
            legend.append(("#6B7280", "Custom"))
        legend_cols = st.columns(len(legend))
        for i, (color, label) in enumerate(legend):
            with legend_cols[i]:
                st.markdown(
                    f'<span style="background:{color};padding:2px 8px;border-radius:3px;'
                    f'color:white;font-size:12px">■ {label}</span>',
                    unsafe_allow_html=True
                )

        # ── Device Power & Weight Table ──────────────────────
        st.markdown("---")
        st.markdown("### 📋 Device Power & Weight Details")
        _wlabel  = f"Weight ({_weight_unit})"
        _aplabel = f"Avg Power ({_power_unit})"
        _mplabel = f"Max Power ({_power_unit})"
        _detail_rows = []
        for d in devices:
            _detail_rows.append({
                "Device":  d["name"],
                "Rack":    d.get("rack", 1),
                "RU":      f"U{d['ru']}",
                "Height":  f"{d['u']}U",
                _wlabel:   round(d["weight"] * _weight_conv, 1),
                _aplabel:  round(d["avg_w"] / _power_div, 2) if rack_use_kw else d["avg_w"],
                _mplabel:  round(d["max_w"] / _power_div, 2) if rack_use_kw else d["max_w"],
            })
        _detail_rows.append({
            "Device": "TOTAL", "Rack": "—", "RU": "—", "Height": f"{total_u_used}U",
            _wlabel:  round(total_weight * _weight_conv, 1),
            _aplabel: round(total_avg_w / _power_div, 2) if rack_use_kw else total_avg_w,
            _mplabel: round(total_max_w / _power_div, 2) if rack_use_kw else total_max_w,
        })
        import pandas as _pd2
        _detail_df = _pd2.DataFrame(_detail_rows)
        st.dataframe(_detail_df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download as CSV",
            data=_detail_df.to_csv(index=False),
            file_name=f"{pfx or 'rack'}_power_weight.csv",
            mime="text/csv",
        )

        # Hardware Photo Gallery
        st.markdown("---")
        with st.expander("📷 Hardware Reference Gallery", expanded=False):
            _gallery_devices = []
            # Add devices in use
            if _sw_model in DEVICE_IMAGES:
                _gallery_devices.append((_sw_model, "Storage Switch"))
            if _gpu_enabled and _gpu_model in DEVICE_IMAGES:
                _gallery_devices.append((_gpu_model, "GPU Switch"))
            if _spine_topo and _spine_model in DEVICE_IMAGES:
                _gallery_devices.append((_spine_model, "Spine Switch"))
            if _cnode_gen in DEVICE_IMAGES:
                _gallery_devices.append((_cnode_gen, "CNode"))
            if _dbox_model in DEVICE_IMAGES:
                _gallery_devices.append((_dbox_model, "DBox"))

            if _gallery_devices:
                _gcols = st.columns(min(len(_gallery_devices), 3))
                for _gi, (_gname, _glabel) in enumerate(_gallery_devices):
                    with _gcols[_gi % len(_gcols)]:
                        import base64 as _b64
                        _img_data = DEVICE_IMAGES[_gname]
                        st.markdown(f"**{_glabel}**  \n{_gname}")
                        st.markdown(
                            f'<img src="data:image/png;base64,{_img_data}" style="width:100%;border-radius:4px;border:1px solid #444">',
                            unsafe_allow_html=True
                        )
            else:
                st.caption("No device images available for current selection.")

# TAB 10 — DEVICE INVENTORY
# ============================================================
with tab10:
    st.subheader("📦 Device Inventory")
    st.caption("Build your global product library. Devices saved here are available across all projects and can be added to any rack diagram.")
    st.markdown("---")

    _dinv_all = _get_inventory_cached()
    _dinv_cats = ["All"] + (_db.DEVICE_CATEGORIES if _DB_AVAILABLE else [])

    _dinv_left, _dinv_right = st.columns([1, 1])

    with _dinv_left:
        # ── Browse / manage inventory ────────────────────────
        st.markdown("### 📚 Product Library")

        _dinv_s_col, _dinv_c_col = st.columns([3, 2])
        with _dinv_s_col:
            _dinv_search = st.text_input("Search", key="inv_search",
                                          placeholder="Filter by name…",
                                          label_visibility="collapsed")
        with _dinv_c_col:
            _dinv_cat_sel = st.selectbox("Category", _dinv_cats, key="inv_cat_sel",
                                          label_visibility="collapsed")

        _dinv_search = st.session_state.get("inv_search", "")
        _dinv_filtered = [
            d for d in _dinv_all
            if (_dinv_search.lower() in d["product_name"].lower() or not _dinv_search)
            and (_dinv_cat_sel == "All" or d["category"] == _dinv_cat_sel)
        ]

        if _dinv_filtered:
            for _dinv_d in _dinv_filtered:
                _dil, _dir = st.columns([5, 1])
                with _dil:
                    _dinv_v = f" · {_dinv_d['vendor']}" if _dinv_d["vendor"] else ""
                    _dinv_n = f"  *{_dinv_d['notes']}*" if _dinv_d["notes"] else ""
                    st.markdown(
                        f'<p style="font-size:12px;margin:6px 0 0 0">'
                        f'<b>{_dinv_d["product_name"]}</b>{_dinv_v}<br>'
                        f'<span style="color:#888">{_dinv_d["category"]} · '
                        f'{_dinv_d["u_height"]}U · {_dinv_d["weight_lbs"]:.0f} lbs · '
                        f'{_dinv_d["avg_w"]}W avg / {_dinv_d["max_w"]}W max'
                        f'{"  📷" if _dinv_d["img_b64"] else ""}'
                        f'{_dinv_n}</span></p>',
                        unsafe_allow_html=True,
                    )
                with _dir:
                    if st.button("🗑️", key=f"inv_del_{_dinv_d['id']}",
                                 help="Delete from inventory permanently"):
                        _db.delete_inventory_device(_dinv_d["id"])
                        _inv_cache_invalidate()
                        st.rerun()
        elif _dinv_all:
            st.caption("No products match the filter.")
        else:
            st.caption("Inventory is empty — add your first product using the form →")

    with _dinv_right:
        # ── Add / update product ─────────────────────────────
        st.markdown("### ➕ Add Product")
        st.caption("Define the product specs once. Use the Rack Diagram tab to add instances to a rack.")

        _inv_prod    = st.text_input("Product Name *", key="inv_prod",
                                      placeholder="e.g. APC Smart-UPS 3000")
        _inv_vendor  = st.text_input("Vendor / Brand", key="inv_vendor",
                                      placeholder="e.g. APC, Vertiv, Raritan")
        _inv_cat     = st.selectbox("Category", _db.DEVICE_CATEGORIES if _db else ["Other"],
                                     key="inv_cat")
        _inv_notes   = st.text_input("Notes (optional)", key="inv_notes",
                                      placeholder="e.g. 208V input, phase A")

        _inv_phys1, _inv_phys2 = st.columns(2)
        with _inv_phys1:
            _inv_u       = st.number_input("Height (U)", min_value=1, max_value=20, value=2,
                                            key="inv_u")
            _inv_avg_w   = st.number_input("Avg Power (W)", min_value=0, value=500, step=10,
                                            key="inv_avg_w")
        with _inv_phys2:
            _inv_weight  = st.number_input("Weight (lbs)", min_value=0.0, value=50.0, step=1.0,
                                            key="inv_weight_lbs")
            _inv_max_w   = st.number_input("Max Power (W)", min_value=0, value=800, step=10,
                                            key="inv_max_w")

        _inv_img = st.file_uploader("Device Image (PNG, max 2 MB)", type=["png"], key="inv_img",
                                     help="Landscape PNG preferred. Displayed inside the rack slot.")

        _inv_errors = []
        if not _inv_prod.strip():
            _inv_errors.append("Product Name is required.")
        if _inv_img is not None and _inv_img.size > 2 * 1024 * 1024:
            _inv_errors.append("Image exceeds 2 MB limit.")
        for _ie in _inv_errors:
            st.warning(_ie)

        if st.button("Save to Inventory", key="inv_add_btn",
                     disabled=bool(_inv_errors) or not _inv_prod.strip(),
                     use_container_width=True):
            import base64 as _b64mod
            _inv_img_b64 = ""
            if _inv_img is not None:
                _inv_img_b64 = _b64mod.b64encode(_inv_img.read()).decode("utf-8")
            _db.upsert_inventory_device(
                product_name=_inv_prod.strip(),
                vendor=_inv_vendor.strip(),
                category=_inv_cat,
                u_height=int(_inv_u),
                weight_lbs=float(_inv_weight),
                avg_w=int(_inv_avg_w),
                max_w=int(_inv_max_w),
                img_b64=_inv_img_b64,
                notes=_inv_notes.strip(),
            )
            _inv_cache_invalidate()
            st.success(f'✅ "{_inv_prod.strip()}" saved to inventory.')
            st.rerun()


# TAB 11 — AI ASSISTANT
# ============================================================
with tab11:
    st.subheader("🤖 AI Assistant")
    st.caption("Ask questions about your current project in plain English. Runs locally via Ollama — no internet required.")
    st.markdown("---")

    # ── Connection settings ───────────────────────────────────
    _ai_c1, _ai_c2 = st.columns([3, 1])
    with _ai_c1:
        _ollama_host = st.text_input(
            "Ollama URL",
            value="http://host.docker.internal:11434",
            key="llm_ollama_host",
            help="Mac/Windows: host.docker.internal works. Linux: use http://172.17.0.1:11434"
        )
    with _ai_c2:
        st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
        _ollama_ok = False
        _models    = []
        try:
            _chk = requests.get(f"{_ollama_host}/api/tags", timeout=3)
            if _chk.status_code == 200:
                _ollama_ok = True
                _models = [m["name"] for m in _chk.json().get("models", [])]
        except Exception:
            pass
        if _ollama_ok:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Ollama not found")

    if not _ollama_ok:
        st.info(
            "**Ollama is not running.** To get started:\n\n"
            "1. Download Ollama from **ollama.com** and install it\n"
            "2. Run: `ollama pull llama3.2:3b`\n"
            "3. Ollama starts automatically in the background\n\n"
            "Recommended model: `llama3.2:3b` (~2 GB, fast on CPU)"
        )
    elif not _models:
        st.warning(
            "Ollama is running but no models are installed.\n\n"
            "Run: `ollama pull llama3.2:3b`"
        )
    else:
        _ai_m1, _ai_m2 = st.columns([2, 1])
        with _ai_m1:
            _selected_model = st.selectbox("Model", options=_models, key="llm_model")
        with _ai_m2:
            st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Clear chat", use_container_width=True):
                st.session_state["llm_chat_history"] = []
                st.rerun()

        st.markdown("---")

        # ── Build project context ─────────────────────────────
        def _build_llm_context():
            _pfx        = st.session_state.get("cluster_name",    "UNKNOWN")
            _se         = st.session_state.get("se_name",         "Unknown SE")
            _cust       = st.session_state.get("customer",        "Unknown")
            _idate      = st.session_state.get("install_date",    "Unknown")
            _n_dbox     = int(st.session_state.get("proj_num_dboxes", 1))
            _n_cnode    = int(st.session_state.get("proj_num_cnodes", 4))
            _dbox_type  = st.session_state.get("proj_dbox_type",  "Unknown")
            _cnode_type = st.session_state.get("proj_cbox_type",  "Unknown")
            _topology   = st.session_state.get("proj_topology",   "Leaf Pair")
            _sw_model   = st.session_state.get("tab7_sw_model",   "Unknown")
            _sw_a_ip    = st.session_state.get("tab7_sw_a_ip",    "Not set")
            _sw_b_ip    = st.session_state.get("tab7_sw_b_ip",    "Not set")
            _vlan       = st.session_state.get("tab7_vlan",       "Not set")
            _ntp        = st.session_state.get("tab7_ntp",        "Not set")
            _mgmt_vlan  = st.session_state.get("tab7_mgmt_vlan",  "Not set")
            _gpu_on     = st.session_state.get("tab8_enabled",    False)
            _gpu_model  = st.session_state.get("tab8_sw_model",   "Unknown")
            _spine_on   = _topology == "Spine-Leaf"
            _spine_mdl  = st.session_state.get("spine_sw_model",  "Unknown")
            _vastver    = st.session_state.get("proj_vast_version", "Not set")
            _site_notes = st.session_state.get("proj_site_notes", "None")
            _sfdc       = st.session_state.get("proj_sfdc",       "")
            _ticket     = st.session_state.get("proj_ticket",     "")

            # Capacity from sizer if available
            _sizer_dbox   = st.session_state.get("sizer_dbox_type", _dbox_type)
            _sizer_ndbox  = int(st.session_state.get("sizer_num_dboxes", _n_dbox))

            return f"""You are an AI assistant embedded in the VAST SE Installation Toolkit. \
You help VAST Systems Engineers answer questions about their current cluster installation. \
Be concise and precise. If a question cannot be answered from the project data provided, say so clearly.

=== CURRENT PROJECT ===
Cluster:        {_pfx}
Customer:       {_cust}
SE:             {_se}
Install Date:   {_idate}
VastOS Version: {_vastver}
SFDC:           {_sfdc or "Not set"}
Ticket:         {_ticket or "Not set"}

=== HARDWARE ===
DBoxes:  {_n_dbox}x {_dbox_type}
CNodes:  {_n_cnode}x {_cnode_type}
Topology: {_topology}
Storage Switches: {_sw_model} ({'Spine-Leaf' if _spine_on else 'Leaf Pair'})
Spine Switches:   {'Enabled — ' + _spine_mdl if _spine_on else 'Not used'}
GPU/Data Switches: {'Enabled — ' + _gpu_model if _gpu_on else 'Not enabled'}

=== SWITCH CONFIG ===
Storage Switch A IP:  {_sw_a_ip}
Storage Switch B IP:  {_sw_b_ip}
Internal Storage VLAN: {_vlan}
Management VLAN:       {_mgmt_vlan}
NTP Server:            {_ntp or 'Not configured'}

=== SITE NOTES ===
{_site_notes}

=== VAST PLATFORM CONTEXT ===
- VAST is a shared-everything NFS/S3 flash storage platform
- DBoxes are storage nodes (all-flash), CNodes are stateless compute nodes
- Internal fabric uses RoCEv2 with MLAG leaf switch pairs
- MTU 9216 on all data paths, VLAN 69 for internal storage
- Dual NIC CNodes use separate storage and data network fabrics
"""

        # ── Chat interface ────────────────────────────────────
        if "llm_chat_history" not in st.session_state:
            st.session_state["llm_chat_history"] = []

        for _msg in st.session_state["llm_chat_history"]:
            with st.chat_message(_msg["role"]):
                st.markdown(_msg["content"])

        if _prompt := st.chat_input("Ask about your cluster…"):
            st.session_state["llm_chat_history"].append({"role": "user", "content": _prompt})
            with st.chat_message("user"):
                st.markdown(_prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        _messages = [{"role": "system", "content": _build_llm_context()}]
                        _messages += st.session_state["llm_chat_history"]
                        _resp = requests.post(
                            f"{_ollama_host}/api/chat",
                            json={"model": _selected_model, "messages": _messages, "stream": False},
                            timeout=120
                        )
                        _answer = _resp.json()["message"]["content"]
                        st.markdown(_answer)
                        st.session_state["llm_chat_history"].append({"role": "assistant", "content": _answer})
                    except Exception as _e:
                        st.error(f"LLM error: {_e}")

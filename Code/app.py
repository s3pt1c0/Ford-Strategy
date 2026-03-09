import xml.etree.ElementTree as ET
from io import StringIO
import requests
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Ford PCM / ECM Decoder",
    page_icon="🚗",
    layout="wide"
)

# =========================
# MODULE MAP
# =========================
MODULE_INFO = {
    "020": ("4WAS/ARC/RASM", "4 Wheel Air Suspension / Automatic Ride Control / Rear Air Suspension Module"),
    "02A": ("EPB", "Electric Parking Brake"),
    "048": ("RAP", "Remote Anti-Theft / Personality Module"),
    "050": ("REM", "Rear Electronic Module"),
    "052": ("CTM/FEM/GEM", "Central Timer Module / Front Electronic Module / Generic Electronic Module"),
    "058": ("ECS/IABM", "Electronic Crash Sensor / Integrated Air Bag Module"),
    "059": ("FSSM", "Fire Suppression System Module"),
    "060": ("HEC/IC/VIC", "Hybrid Electronic Cluster / Instrument Cluster / Virtual Image Cluster"),
    "061": ("MC/OTC", "Message Center / Overhead Trip Computer"),
    "068": ("NAV", "Navigation Controller"),
    "070": ("LCM/SCIL", "Lighting Control Module / Steering Column Instrument Panel Lighting"),
    "071": ("HD_LVL", "Headlamp Leveling Module"),
    "090": ("CPM", "Cellular Phone Module"),
    "091": ("RESCU/VEMS", "Remote Emergency Satellite Cellular Unit Module / Vehicle Emergency Messaging System"),
    "098": ("EATC/RCC", "Electronic Automatic Temperature Control / Remote Climate Control"),
    "099": ("RATC", "Rear Air Temperature Control"),
    "0A6": ("PSM", "Passenger Front Seat Module"),
    "0B0": ("LPSDM", "Left Power Sliding Door Module"),
    "0B1": ("RPSDM", "Right Power Sliding Door Module"),
    "0C0": ("PATS", "Passive Anti-Theft System"),
    "0C1": ("CSM", "Security Module"),
    "0C3": ("SCLM", "Steering Column Locking Module"),
    "0CE": ("TBM", "Tracking and Blocking Module"),
    "00F": ("FFH/FOH", "Fuel Fired Coolant Heating Module / Fuel Operated Heater"),
    "013": ("NGSC", "Next Generation Speed Control Module"),
    "016": ("FIM/ICU/FIP", "Fuel Indication Module / Injector Control Unit / Fuel Injection Pump"),

    "701": ("GPSM", "Global Positioning System Module"),
    "706": ("IPMA", "Image Processing Module A"),
    "712": ("SCMG", "Seat Control Module G"),
    "713": ("SCMH", "Seat Control Module H"),
    "714": ("HSWM", "Heated Steering Wheel Module"),
    "716": ("GWM", "Gateway Module A"),
    "720": ("IPC", "Instrument Panel Control Module"),
    "721": ("VDM", "Vehicle Dynamics Module"),
    "723": ("BECMB", "Battery Energy Control Module B"),
    "724": ("SCCM", "Steering Column Control Module"),
    "726": ("BCM/GEM", "Body Control Module / Generic Electronic Module"),
    "727": ("ACM", "Audio Control Module"),
    "730": ("PSCM", "Power Steering Control Module"),
    "731": ("RFA", "Remote Function Actuator"),
    "733": ("HVAC", "Heating Ventilation Air Conditioning"),
    "734": ("HCM", "Headlamp Control Module"),
    "736": ("PAM", "Parking Aid Module"),
    "737": ("RCM", "Restraint Control Module"),
    "740": ("DDM", "Drivers Door Module"),
    "741": ("PDM", "Passengers Door Control Unit"),
    "744": ("DSM", "Driver's Seat Module"),
    "746": ("DCDC", "DC to DC Converter Control Module"),
    "751": ("RTM", "Remote Transceiver Module"),
    "754": ("TCU", "Telematic Control Unit"),
    "755": ("VSM", "Vehicle Security Module"),
    "757": ("TBC", "Trailer Brake Control Module"),
    "760": ("ABS", "Anti-Lock Brake / Traction Control Module"),
    "761": ("4X4M/TCCM", "4X4 Control Module / Transfer Case Control Module"),
    "764": ("CCM", "Cruise Control Module"),
    "765": ("OCS", "Occupant Classification System Module"),
    "766": ("PRB", "Power Running Board"),
    "771": ("RETM", "Rear Seat Entertainment Module"),
    "772": ("SRM", "Speech Recognition Module"),
    "774": ("RCU", "Audio Rear Control Unit"),
    "775": ("LTM", "Liftgate / Trunk Module"),
    "776": ("DCSM", "Driver/Dual Climate-Control Seat Module"),
    "777": ("PCSM2", "Passenger Climate-Control Seat Module 2 (rear)"),
    "782": ("SDARS", "Satellite Digital Audio Receiver System"),
    "783": ("DSP", "Digital Signal Processing Module"),
    "785": ("RHVAC", "Rear Heating Ventilation Air Conditioning"),
    "791": ("TRM", "Trailer Module"),
    "797": ("SASM", "Steering Angle Sensor Module"),

    "7A5": ("FCDIM", "Front Control/Display Interface Module"),
    "7A6": ("FDIM", "Front Display Interface Module"),
    "7A7": ("FCIM", "Front Controls Interface Module"),
    "7B1": ("IPMB", "Image Processing Module B"),
    "7B2": ("HUD", "Head Up Display"),
    "7B5": ("ILCM", "Interior Lighting Control Module"),
    "7B7": ("BCMB", "Body Control Module B"),
    "7C3": ("HCM2", "Headlamp Control Module 2(B)"),
    "7C4": ("SODL", "Side Obstacle Detection Control Module - Left"),
    "7C5": ("SECM", "Steering Effort Control Module"),
    "7C6": ("SODR", "Side Obstacle Detection Control Module - Right"),

    "7D0": ("APIM", "Accessory Protocol Interface Module"),
    "7D5": ("DACMC", "Digital Audio Control Module C"),

    "7E0": ("PCM", "Powertrain Control Module"),
    "7E1": ("TCM", "Transmission Control Module"),
    "7E2": ("CDIM", "Circuit Deactivation Ignition Module"),
    "7E3": ("AHCM", "Auxiliary Heater Control Module"),
    "7E5": ("AFCM/OBD_FICM", "Alternative Fuel Control Module / Fuel Injection Control Module"),
    "7E6": ("FICM", "Fuel Injection Control Module"),
    "7E7": ("ACCM/BECM", "Air Conditioning Control Module / Battery Energy Control Module"),
}


# =========================
# HELPERS
# =========================
def get_module_display(node_id: str):
    node_id = (node_id or "").strip().upper()
    return MODULE_INFO.get(node_id, ("", "Unknown Module"))


def decode_vin_year_local(vin: str) -> str:
    vin = (vin or "").strip().upper()
    if len(vin) != 17:
        return ""

    year_code = vin[9]
    year_map = {
        "A": 2010, "B": 2011, "C": 2012, "D": 2013, "E": 2014,
        "F": 2015, "G": 2016, "H": 2017, "J": 2018, "K": 2019,
        "L": 2020, "M": 2021, "N": 2022, "P": 2023, "R": 2024,
        "S": 2025, "T": 2026, "V": 2027, "W": 2028, "X": 2029,
        "Y": 2030,
        "1": 2001, "2": 2002, "3": 2003, "4": 2004, "5": 2005,
        "6": 2006, "7": 2007, "8": 2008, "9": 2009,
    }
    year = year_map.get(year_code, "")
    return str(year) if year else ""


@st.cache_data(show_spinner=False)
def decode_vin_with_nhtsa(vin: str) -> dict:
    vin = (vin or "").strip().upper()
    if len(vin) != 17:
        return {
            "year": "",
            "make": "",
            "model": "",
            "trim": "",
            "engine": "",
            "body": "",
            "drive": "",
            "plant": "",
            "error": "VIN must be 17 characters."
        }

    local_year = decode_vin_year_local(vin)
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
    if local_year:
        url += f"&modelyear={local_year}"

    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        payload = r.json()
        results = payload.get("Results", [])

        if not results:
            return {
                "year": local_year,
                "make": "",
                "model": "",
                "trim": "",
                "engine": "",
                "body": "",
                "drive": "",
                "plant": "",
                "error": "No results returned from VIN decoder."
            }

        item = results[0]

        year = (item.get("ModelYear") or local_year or "").strip()
        make = (item.get("Make") or "").strip()
        model = (item.get("Model") or "").strip()
        trim = (item.get("Trim") or "").strip()
        body = (item.get("BodyClass") or "").strip()
        drive = (item.get("DriveType") or "").strip()

        plant_parts = [
            (item.get("PlantCompanyName") or "").strip(),
            (item.get("PlantCity") or "").strip(),
            (item.get("PlantState") or "").strip(),
            (item.get("PlantCountry") or "").strip(),
        ]
        plant = ", ".join([p for p in plant_parts if p])

        engine_parts = []
        displacement_l = (item.get("DisplacementL") or "").strip()
        cylinders = (item.get("EngineCylinders") or "").strip()
        engine_model = (item.get("EngineModel") or "").strip()
        fuel = (item.get("FuelTypePrimary") or "").strip()

        if displacement_l:
            engine_parts.append(f"{displacement_l}L")
        if cylinders:
            engine_parts.append(f"V{cylinders}" if cylinders.isdigit() else cylinders)
        if engine_model:
            engine_parts.append(engine_model)
        if fuel:
            engine_parts.append(fuel)

        engine = " | ".join(engine_parts)

        error_code = (item.get("ErrorCode") or "").strip()
        error_text = (item.get("ErrorText") or "").strip()

        return {
            "year": year,
            "make": make,
            "model": model,
            "trim": trim,
            "engine": engine,
            "body": body,
            "drive": drive,
            "plant": plant,
            "error": error_text if error_code and error_code != "0" else ""
        }

    except Exception as e:
        return {
            "year": local_year,
            "make": "",
            "model": "",
            "trim": "",
            "engine": "",
            "body": "",
            "drive": "",
            "plant": "",
            "error": f"NHTSA decode failed: {e}"
        }


def parse_asbuilt(xml_text: str):
    root = ET.fromstring(xml_text)

    vin_el = root.find(".//VIN")
    vin = vin_el.text.strip() if vin_el is not None and vin_el.text else "N/A"

    all_modules = []
    pcm = None

    for node in root.iter("NODEID"):
        node_id = node.text.strip().upper() if node.text else ""

        def get(tag):
            el = node.find(tag)
            return el.text.strip() if el is not None and el.text else ""

        abbr, module_name = get_module_display(node_id)

        mod = {
            "id": node_id,
            "abbr": abbr,
            "module_name": module_name,
            "f110": get("F110"),
            "f111": get("F111"),
            "f113": get("F113"),
            "f188": get("F188"),
            "f18c": get("F18C"),
        }
        all_modules.append(mod)

        if node_id == "7E0":
            pcm = mod

    return {
        "vin": vin,
        "pcm": pcm,
        "all_modules": all_modules,
    }


def strategy_breakdown(strategy: str):
    if not strategy:
        return []
    parts = strategy.split("-")
    return parts if len(parts) == 3 else []


def make_vehicle_title(vin_info: dict) -> str:
    parts = [vin_info.get("year", ""), vin_info.get("make", ""), vin_info.get("model", "")]
    title = " ".join([p for p in parts if p]).strip()
    if vin_info.get("trim"):
        title = f"{title} {vin_info['trim']}".strip()
    return title


def modules_dataframe(modules: list[dict]) -> pd.DataFrame:
    rows = []
    for mod in modules:
        rows.append({
            "NODEID": mod["id"],
            "Acronym": mod["abbr"] or "",
            "Module Name": mod["module_name"],
            "F111 Hardware": mod["f111"] or "",
            "F113 Part Number": mod["f113"] or "",
            "F188 Strategy": mod["f188"] or "",
        })
    return pd.DataFrame(rows)


# =========================
# UI
# =========================
st.title("Ford PCM / ECM Decoder")
st.caption("Web version for GitHub / Streamlit — upload .ab file, decode VIN, inspect PCM/ECM and other modules.")

col_top1, col_top2 = st.columns([2, 1])
with col_top1:
    uploaded_file = st.file_uploader("Upload Ford AsBuilt file (.ab or .xml)", type=["ab", "xml"])
with col_top2:
    st.link_button("Open Motorcraft AsBuilt", "https://www.motorcraftservice.com/SetCountry?returnUrl=%2Fasbuilt")

st.info(
    "This web version does not automate Motorcraft, captcha, downloads, or browser control. "
    "Upload the .ab file after downloading it manually."
)

if uploaded_file is None:
    st.stop()

try:
    raw_bytes = uploaded_file.read()
    xml_text = raw_bytes.decode("utf-8", errors="ignore").strip()

    if not xml_text:
        st.error("The uploaded file is empty.")
        st.stop()

    parsed = parse_asbuilt(xml_text)

except ET.ParseError as e:
    st.error(f"Invalid XML: {e}")
    st.stop()
except Exception as e:
    st.error(f"Could not process file: {e}")
    st.stop()

vin = parsed["vin"]
pcm = parsed["pcm"]
all_modules = parsed["all_modules"]
vin_info = decode_vin_with_nhtsa(vin)

# =========================
# VEHICLE INFO
# =========================
vehicle_title = make_vehicle_title(vin_info)

st.subheader("Vehicle Info")
c1, c2, c3 = st.columns(3)
c1.metric("VIN", vin)
c2.metric("Vehicle", vehicle_title or "—")
c3.metric("Engine", vin_info.get("engine") or "—")

c4, c5, c6 = st.columns(3)
c4.metric("Body", vin_info.get("body") or "—")
c5.metric("Drive", vin_info.get("drive") or "—")
c6.metric("Plant", vin_info.get("plant") or "—")

if vin_info.get("error"):
    st.warning(vin_info["error"])

# =========================
# PCM / ECM
# =========================
st.subheader("PCM / ECM (7E0)")

if not pcm:
    st.error("7E0 (PCM/ECM) was not found in this file.")
else:
    pcm_abbr, pcm_name = get_module_display("7E0")
    st.markdown(f"**{pcm_abbr} — {pcm_name}**")

    p1, p2, p3 = st.columns(3)
    p1.text_input("F111 — Hardware Number", value=pcm.get("f111", ""), disabled=True)
    p2.text_input("F113 — Part Number", value=pcm.get("f113", ""), disabled=True)
    p3.text_input("F188 — Strategy", value=pcm.get("f188", ""), disabled=True)

    breakdown = strategy_breakdown(pcm.get("f188", ""))
    if breakdown:
        st.markdown("**Strategy Breakdown**")
        b1, b2, b3 = st.columns(3)
        b1.metric("Prefix", breakdown[0])
        b2.metric("Base", breakdown[1])
        b3.metric("Suffix / Rev", breakdown[2])

# =========================
# OTHER MODULES
# =========================
st.subheader("Other Modules Detected")

other_modules = [m for m in all_modules if m["id"] != "7E0"]
df = modules_dataframe(other_modules if other_modules else [])

search = st.text_input("Filter modules by NODEID, acronym, module name, hardware, part number, or strategy")

if not df.empty and search.strip():
    q = search.strip().lower()
    mask = df.apply(lambda row: any(q in str(v).lower() for v in row), axis=1)
    df = df[mask]

if df.empty:
    st.warning("No other modules found.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("Show detailed module cards"):
        for mod in other_modules:
            row_blob = " ".join([
                mod.get("id", ""),
                mod.get("abbr", ""),
                mod.get("module_name", ""),
                mod.get("f111", ""),
                mod.get("f113", ""),
                mod.get("f188", ""),
            ]).lower()

            if search.strip() and search.strip().lower() not in row_blob:
                continue

            title = f"{mod['id']}"
            if mod["abbr"]:
                title += f" — {mod['abbr']}"
            title += f" — {mod['module_name']}"

            with st.container(border=True):
                st.markdown(f"**{title}**")
                c1, c2, c3 = st.columns(3)
                c1.text_input("F111", value=mod.get("f111", ""), disabled=True, key=f"{mod['id']}_f111")
                c2.text_input("F113", value=mod.get("f113", ""), disabled=True, key=f"{mod['id']}_f113")
                c3.text_input("F188", value=mod.get("f188", ""), disabled=True, key=f"{mod['id']}_f188")

# =========================
# RAW XML
# =========================
with st.expander("Show raw XML"):
    st.code(xml_text[:50000], language="xml")

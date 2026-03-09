import os
import glob
import time
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

# =========================
# OPTIONAL DEPENDENCIES
# =========================
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WDM = True
except ImportError:
    HAS_WDM = False


# =========================
# UI COLORS
# =========================
BG_DARK = "#0a0e17"
CARD_BG = "#111827"
BORDER = "#1e293b"
FORD_BLUE = "#003478"
ACCENT = "#00A3E0"
TEXT_WHITE = "#e2e8f0"
TEXT_DIM = "#94a3b8"
TEXT_MUTED = "#475569"
GREEN = "#22c55e"
YELLOW = "#eab308"
RED_BG = "#1a0505"
RED_BORDER = "#7f1d1d"
RED_TEXT = "#fca5a5"

MOTORCRAFT_SETCOUNTRY = "https://www.motorcraftservice.com/SetCountry?returnUrl=%2Fasbuilt"


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
def center_window(win, width=780, height=700):
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


def get_downloads_folder() -> str:
    return str(Path.home() / "Downloads")


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

        mod = {
            "id": node_id,
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


# =========================
# SCROLLABLE FRAME
# =========================
class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.window_id, width=e.width)
        )

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


# =========================
# FORD BROWSER ASSIST
# =========================
class FordBrowserAssist:
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.driver = None
        self.wait = None

    def status(self, msg):
        if self.status_callback:
            self.status_callback(msg)

    def open_browser(self):
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        if HAS_WDM:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=opts)
        else:
            self.driver = webdriver.Chrome(options=opts)

        self.wait = WebDriverWait(self.driver, 15)
        self.driver.get(MOTORCRAFT_SETCOUNTRY)

    def try_fill_vin(self, vin: str) -> bool:
        if not self.driver:
            return False

        selectors = [
            (By.ID, "vin"),
            (By.ID, "VIN"),
            (By.NAME, "vin"),
            (By.NAME, "VIN"),
            (By.ID, "Ession_VIN"),
            (By.NAME, "Ession_VIN"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ]

        for by, value in selectors:
            try:
                elems = self.driver.find_elements(by, value)
                for elem in elems:
                    if elem.is_displayed() and elem.is_enabled():
                        try:
                            elem.clear()
                        except Exception:
                            pass
                        elem.send_keys(Keys.CONTROL, "a")
                        elem.send_keys(Keys.DELETE)
                        elem.send_keys(vin)
                        return True
            except Exception:
                continue

        return False

    def wait_for_asbuilt_and_fill(self, vin: str, timeout=300) -> bool:
        if not self.driver:
            return False

        start = time.time()

        while time.time() - start < timeout:
            try:
                url = (self.driver.current_url or "").lower()
            except Exception:
                break

            if "asbuilt" in url:
                self.status("AsBuilt page detected. Trying to fill VIN...")
                try:
                    if self.try_fill_vin(vin):
                        self.status("VIN inserted. Complete captcha and download the .ab file.")
                        return True
                except Exception:
                    pass

            time.sleep(1)

        return False

    def wait_for_download(self, download_dir: str, started_at: float, timeout=600):
        self.status(f"Watching Downloads: {download_dir}")
        end_time = time.time() + timeout
        seen_partial = False

        while time.time() < end_time:
            partials = glob.glob(os.path.join(download_dir, "*.crdownload")) + glob.glob(
                os.path.join(download_dir, "*.tmp")
            )
            if partials and not seen_partial:
                self.status("Download in progress...")
                seen_partial = True

            candidates = []
            for pattern in ("*.ab", "*.AB", "*"):
                for path in glob.glob(os.path.join(download_dir, pattern)):
                    if path.endswith(".crdownload") or path.endswith(".tmp"):
                        continue
                    try:
                        mtime = os.path.getmtime(path)
                        if mtime >= started_at:
                            candidates.append((mtime, path))
                    except Exception:
                        continue

            candidates.sort(reverse=True)

            for _, path in candidates:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(4000)
                    if "<AS_BUILT_DATA>" in content:
                        return path
                except Exception:
                    continue

            time.sleep(1)

        return None

    def close(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass


# =========================
# MAIN APP
# =========================
class FordPCMDecoder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ford PCM / ECM Decoder")
        self.configure(bg=BG_DARK)

        self.state("zoomed")
        self.minsize(720, 620)

        self.parsed_data = None
        self.last_ab_content = None
        self.browser_assist_running = False

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=BG_DARK)
        container.pack(fill="both", expand=True)

        self.scrollable = ScrollableFrame(container, bg=BG_DARK)
        self.scrollable.pack(fill="both", expand=True)

        self.inner = tk.Frame(self.scrollable.inner, bg=BG_DARK)
        self.inner.pack(fill="x", padx=20, pady=18)

        self._build_header()
        self._build_controls()
        self._build_results_area()

    def _build_header(self):
        header = tk.Frame(self.inner, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 14))

        badge = tk.Label(
            header,
            text=" 7E0 ",
            font=("Consolas", 14, "bold"),
            bg=FORD_BLUE,
            fg="white",
            padx=10,
            pady=6
        )
        badge.pack(side="left", padx=(0, 12))

        title_box = tk.Frame(header, bg=BG_DARK)
        title_box.pack(side="left")

        tk.Label(
            title_box,
            text="Ford PCM / ECM Decoder",
            font=("Segoe UI", 20, "bold"),
            bg=BG_DARK,
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="VIN browser assist + local .ab loader + VIN decode By Mangual",
            font=("Consolas", 8),
            bg=BG_DARK,
            fg=TEXT_DIM
        ).pack(anchor="w")

    def _build_controls(self):
        frame = tk.Frame(
            self.inner,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=18,
            pady=16
        )
        frame.pack(fill="x", pady=(0, 14))

        vin_row = tk.Frame(frame, bg=CARD_BG)
        vin_row.pack(fill="x")

        tk.Label(
            vin_row,
            text="VIN",
            font=("Consolas", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_DIM
        ).pack(side="left", padx=(0, 10))

        self.vin_entry = tk.Entry(
            vin_row,
            font=("Consolas", 15, "bold"),
            bg="#0d1520",
            fg="white",
            insertbackground="white",
            relief="flat",
            highlightbackground=BORDER,
            highlightthickness=1,
            highlightcolor=ACCENT,
            width=22
        )
        self.vin_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        self.vin_entry.bind("<Return>", lambda e: self._start_browser_assist())

        self.lookup_btn = tk.Button(
            vin_row,
            text="Search Ford",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT,
            fg="white",
            relief="flat",
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._start_browser_assist
        )
        self.lookup_btn.pack(side="left")

        self.status_label = tk.Label(
            frame,
            text="",
            font=("Segoe UI", 10),
            bg=CARD_BG,
            fg=TEXT_DIM,
            anchor="w",
            justify="left"
        )
        self.status_label.pack(fill="x", pady=(8, 0))

        if HAS_SELENIUM:
            dep_msg = "✓ Selenium detected — browser assist mode enabled"
            dep_color = GREEN
        else:
            dep_msg = "⚠ Selenium not installed — only manual browse mode available"
            dep_color = YELLOW

        tk.Label(
            frame,
            text=dep_msg,
            font=("Consolas", 8),
            bg=CARD_BG,
            fg=dep_color,
            anchor="w"
        ).pack(fill="x", pady=(4, 0))

        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=(12, 12))

        btn_row = tk.Frame(frame, bg=CARD_BG)
        btn_row.pack(fill="x")

        tk.Button(
            btn_row,
            text="📂 Browse .ab",
            font=("Segoe UI", 9, "bold"),
            bg=BORDER,
            fg=TEXT_WHITE,
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._browse_file
        ).pack(side="left")

        tk.Button(
            btn_row,
            text="🌐 Open Ford Website",
            font=("Segoe UI", 9, "bold"),
            bg=BORDER,
            fg=TEXT_WHITE,
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._open_website
        ).pack(side="left", padx=(8, 0))

        self.save_frame = tk.Frame(btn_row, bg=CARD_BG)
        self.save_btn = tk.Button(
            self.save_frame,
            text="💾 Save .ab",
            font=("Segoe UI", 9, "bold"),
            bg="#1a2332",
            fg=GREEN,
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._save_ab
        )
        self.save_btn.pack(side="right")

        if not HAS_SELENIUM:
            tk.Label(
                frame,
                text="Install for browser assist:\npython -m pip install selenium webdriver-manager requests",
                font=("Consolas", 8),
                bg=CARD_BG,
                fg=TEXT_MUTED,
                justify="left",
                anchor="w"
            ).pack(fill="x", pady=(10, 0))
        else:
            tk.Label(
                frame,
                text=(
                    "Flow:\n"
                    "1) App opens Chrome\n"
                    "2) You select country/language\n"
                    "3) App tries to insert VIN on /asbuilt\n"
                    "4) You solve captcha and download\n"
                    "5) App auto-loads the .ab"
                ),
                font=("Consolas", 8),
                bg=CARD_BG,
                fg=TEXT_MUTED,
                justify="left",
                anchor="w"
            ).pack(fill="x", pady=(10, 0))

    def _build_results_area(self):
        self.results_frame = tk.Frame(self.inner, bg=BG_DARK)
        self.results_frame.pack(fill="x")
        self._show_empty()

    def _show_empty(self):
        for w in self.results_frame.winfo_children():
            w.destroy()

        empty = tk.Frame(
            self.results_frame,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=20,
            pady=18
        )
        empty.pack(fill="x")

        tk.Label(
            empty,
            text="Enter a VIN to launch Ford browser assist, or browse a local .ab file.",
            font=("Segoe UI", 11),
            bg=CARD_BG,
            fg=TEXT_MUTED
        ).pack()

    def _open_website(self):
        webbrowser.open(MOTORCRAFT_SETCOUNTRY)

    def _set_status(self, msg, color=ACCENT):
        self.status_label.config(text=msg, fg=color)

    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def _get_module_display(self, node_id):
        node_id = (node_id or "").upper().strip()
        info = MODULE_INFO.get(node_id)
        if info:
            return info
        return "", "Unknown Module"

    def _show_ford_steps_popup(self):
        steps = (
            "Ford AsBuilt Download Steps\n\n"
            "1. Select your country and click Submit.\n"
            "2. Confirm the VIN, enter the captcha, and click Submit.\n"
            "3. On the vehicle information page, click Download.\n\n"
            "After the .ab file is downloaded, the app will try to load it automatically."
        )

        return messagebox.askokcancel(
            "Ford Download Instructions",
            steps
        )

    def _start_browser_assist(self):
        vin = self.vin_entry.get().strip().upper()

        if not vin:
            self._set_status("Enter a VIN number.", YELLOW)
            return

        if len(vin) != 17:
            self._set_status(f"Invalid VIN length: {len(vin)}. Must be 17.", RED_TEXT)
            return

        if not HAS_SELENIUM:
            self._open_website()
            self._set_status(
                "Selenium is not installed. Opened Ford website. Use Browse .ab after download.",
                YELLOW
            )
            return

        if not self._show_ford_steps_popup():
            self._set_status("Ford browser assist cancelled.", YELLOW)
            return

        if self.browser_assist_running:
            self._set_status("Browser assist is already running.", YELLOW)
            return

        self.browser_assist_running = True
        self.lookup_btn.config(state="disabled", text="Waiting...")
        self.save_frame.pack_forget()

        def worker():
            assist = FordBrowserAssist(
                status_callback=lambda msg: self.after(0, self._set_status, msg, ACCENT)
            )
            try:
                downloads_dir = get_downloads_folder()
                started_at = time.time()

                self.after(0, self._set_status, "Opening Chrome...", ACCENT)
                assist.open_browser()

                self.after(
                    0,
                    self._set_status,
                    "Chrome opened. Select country/language and press submit.",
                    ACCENT
                )

                filled = assist.wait_for_asbuilt_and_fill(vin, timeout=300)
                if not filled:
                    self.after(
                        0,
                        self._show_error,
                        "Could not detect the VIN field on the AsBuilt page.\n"
                        "You can still type the VIN manually in the browser and continue."
                    )

                file_path = assist.wait_for_download(downloads_dir, started_at, timeout=600)
                if not file_path:
                    self.after(
                        0,
                        self._show_error,
                        "No new .ab file was detected in Downloads.\n"
                        "Download it manually and then use Browse .ab."
                    )
                    return

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                self.last_ab_content = content
                parsed = parse_asbuilt(content)

                if not parsed["pcm"]:
                    self.after(0, self._show_error, "7E0 (PCM/ECM) was not found in the downloaded file.")
                    return

                self.parsed_data = parsed
                self.after(0, self._render_results)
                self.after(0, lambda: self.save_frame.pack(side="right"))
                self.after(
                    0,
                    self._set_status,
                    f"✓ Downloaded and loaded automatically: {os.path.basename(file_path)}",
                    GREEN
                )

            except ET.ParseError as e:
                self.after(0, self._show_error, f"XML parse error: {e}")
            except Exception as e:
                self.after(0, self._show_error, f"{e}")
            finally:
                try:
                    assist.close()
                except Exception:
                    pass
                self.browser_assist_running = False
                self.after(0, lambda: self.lookup_btn.config(state="normal", text="Search Ford"))

        threading.Thread(target=worker, daemon=True).start()

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select AsBuilt File",
            filetypes=[
                ("AsBuilt files", "*.ab"),
                ("XML files", "*.xml"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            self.last_ab_content = content
            parsed = parse_asbuilt(content)

            if not parsed["pcm"]:
                self._show_error("7E0 (PCM/ECM) was not found in this file.")
                return

            self.parsed_data = parsed
            self._render_results()
            self.save_frame.pack(side="right")
            self._set_status(f"✓ Loaded: {os.path.basename(path)}", GREEN)

        except ET.ParseError as e:
            self._show_error(f"XML parse error: {e}")
        except Exception as e:
            self._show_error(f"Error loading file: {e}")

    def _save_ab(self):
        if not self.last_ab_content:
            return

        vin = "UNKNOWN"
        if self.parsed_data:
            vin = self.parsed_data.get("vin", "UNKNOWN")

        path = filedialog.asksaveasfilename(
            title="Save AsBuilt File",
            defaultextension=".ab",
            initialfile=f"{vin}.ab",
            filetypes=[("AsBuilt files", "*.ab"), ("All files", "*.*")]
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.last_ab_content)

        self._set_status(f"✓ Saved: {os.path.basename(path)}", GREEN)

    def _show_error(self, msg):
        for w in self.results_frame.winfo_children():
            w.destroy()

        self._set_status("✗ Error", RED_TEXT)

        err = tk.Frame(
            self.results_frame,
            bg=RED_BG,
            highlightbackground=RED_BORDER,
            highlightthickness=1,
            padx=16,
            pady=12
        )
        err.pack(fill="x", pady=(0, 10))

        tk.Label(
            err,
            text=msg,
            font=("Segoe UI", 11),
            bg=RED_BG,
            fg=RED_TEXT,
            wraplength=680,
            justify="left"
        ).pack()

    def _build_vehicle_info_card(self, vin_info):
        card = tk.Frame(
            self.results_frame,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=16,
            pady=14
        )
        card.pack(fill="x", pady=(0, 12))

        tk.Label(
            card,
            text="VEHICLE INFO (VIN DECODE)",
            font=("Consolas", 9, "bold"),
            bg=CARD_BG,
            fg=TEXT_DIM
        ).pack(anchor="w", pady=(0, 10))

        def row(label, value):
            line = tk.Frame(card, bg=CARD_BG)
            line.pack(fill="x", pady=2)

            tk.Label(
                line,
                text=label,
                font=("Consolas", 9, "bold"),
                bg="#1a2332",
                fg=ACCENT,
                padx=6,
                pady=2,
                width=10,
                anchor="w"
            ).pack(side="left")

            tk.Label(
                line,
                text=value if value else "—",
                font=("Segoe UI", 10, "bold"),
                bg=CARD_BG,
                fg=TEXT_WHITE if value else TEXT_MUTED,
                anchor="w"
            ).pack(side="left", padx=(10, 0))

        year_make_model = " ".join(
            [x for x in [vin_info.get("year", ""), vin_info.get("make", ""), vin_info.get("model", "")] if x]
        ).strip()

        if vin_info.get("trim"):
            year_make_model = f"{year_make_model} {vin_info['trim']}".strip()

        row("Vehicle", year_make_model)
        row("Engine", vin_info.get("engine", ""))
        row("Body", vin_info.get("body", ""))
        row("Drive", vin_info.get("drive", ""))
        row("Plant", vin_info.get("plant", ""))

        if vin_info.get("error"):
            tk.Label(
                card,
                text=f"Note: {vin_info['error']}",
                font=("Segoe UI", 9),
                bg=CARD_BG,
                fg=YELLOW,
                wraplength=650,
                justify="left"
            ).pack(anchor="w", pady=(8, 0))

    def _render_results(self):
        for w in self.results_frame.winfo_children():
            w.destroy()

        data = self.parsed_data
        if not data:
            return

        vin_card = tk.Frame(
            self.results_frame,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=16,
            pady=12
        )
        vin_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            vin_card,
            text="VIN",
            font=("Consolas", 9, "bold"),
            bg=CARD_BG,
            fg=TEXT_DIM
        ).pack(side="left", padx=(0, 14))

        tk.Label(
            vin_card,
            text=data["vin"],
            font=("Consolas", 14, "bold"),
            bg=CARD_BG,
            fg="white"
        ).pack(side="left")

        tk.Button(
            vin_card,
            text="Copy",
            font=("Segoe UI", 8),
            bg=BORDER,
            fg=TEXT_WHITE,
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self._copy(data["vin"])
        ).pack(side="right")

        vin_info = decode_vin_with_nhtsa(data["vin"])
        self._build_vehicle_info_card(vin_info)
        self._build_pcm_card(data["pcm"])

        if data["pcm"].get("f188"):
            self._build_breakdown(data["pcm"]["f188"])

        others = [m for m in data["all_modules"] if m["id"] != "7E0"]
        if others:
            self._build_other_modules(others)

    def _build_pcm_card(self, pcm):
        card = tk.Frame(
            self.results_frame,
            bg=CARD_BG,
            highlightbackground=ACCENT,
            highlightthickness=2,
            padx=18,
            pady=16
        )
        card.pack(fill="x", pady=(0, 12))

        top = tk.Frame(card, bg=CARD_BG)
        top.pack(fill="x", pady=(0, 12))

        abbr, name = self._get_module_display("7E0")

        tk.Label(
            top,
            text="7E0",
            font=("Consolas", 18, "bold"),
            bg=CARD_BG,
            fg=ACCENT
        ).pack(side="left")

        tk.Label(
            top,
            text=f" {abbr} ",
            font=("Consolas", 9, "bold"),
            bg="#1a2332",
            fg="white",
            padx=8,
            pady=3
        ).pack(side="left", padx=(10, 8))

        tk.Label(
            top,
            text=name,
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_WHITE
        ).pack(side="left")

        tk.Button(
            top,
            text="Copy All",
            font=("Segoe UI", 8),
            bg=BORDER,
            fg=TEXT_WHITE,
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self._copy(
                f"Node ID: 7E0\n"
                f"Module: {abbr} - {name}\n"
                f"Hardware (F111): {pcm.get('f111', '')}\n"
                f"Part Number (F113): {pcm.get('f113', '')}\n"
                f"Strategy (F188): {pcm.get('f188', '')}"
            )
        ).pack(side="right")

        self._field(card, "F111", "Hardware Number", pcm.get("f111", ""))
        self._field(card, "F113", "Part Number", pcm.get("f113", ""))
        self._field(card, "F188", "Strategy", pcm.get("f188", ""), large=True)

    def _field(self, parent, did, label, value, large=False):
        bg = "#0d1520" if large else "#0c1018"
        border = ACCENT if large else BORDER
        font_size = 18 if large else 14

        frame = tk.Frame(
            parent,
            bg=bg,
            highlightbackground=border,
            highlightthickness=1,
            padx=14,
            pady=10
        )
        frame.pack(fill="x", pady=(0, 8))

        top = tk.Frame(frame, bg=bg)
        top.pack(fill="x")

        tk.Label(
            top,
            text=did,
            font=("Consolas", 9, "bold"),
            bg=ACCENT if large else "#1a2332",
            fg="white" if large else ACCENT,
            padx=6,
            pady=1
        ).pack(side="left")

        tk.Label(
            top,
            text=label,
            font=("Segoe UI", 9),
            bg=bg,
            fg=TEXT_DIM
        ).pack(side="left", padx=(10, 0))

        tk.Button(
            top,
            text="📋",
            font=("Segoe UI", 8),
            bg=bg,
            fg=TEXT_DIM,
            relief="flat",
            cursor="hand2",
            bd=0,
            command=lambda v=value: self._copy(v)
        ).pack(side="right")

        tk.Label(
            frame,
            text=value if value else "— not found —",
            font=("Consolas", font_size, "bold"),
            bg=bg,
            fg="white" if value else TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(6, 0))

    def _build_breakdown(self, strategy):
        parts = strategy.split("-")
        if len(parts) != 3:
            return

        card = tk.Frame(
            self.results_frame,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=18,
            pady=14
        )
        card.pack(fill="x", pady=(0, 12))

        tk.Label(
            card,
            text="STRATEGY BREAKDOWN",
            font=("Consolas", 9, "bold"),
            bg=CARD_BG,
            fg=TEXT_DIM
        ).pack(anchor="w", pady=(0, 10))

        cols = tk.Frame(card, bg=CARD_BG)
        cols.pack(fill="x")

        for i in range(3):
            cols.columnconfigure(i, weight=1)

        labels = ["PREFIX", "BASE", "SUFFIX / REV"]
        colors = [ACCENT, "white", GREEN]

        for i, (lbl, part, color) in enumerate(zip(labels, parts, colors)):
            cell = tk.Frame(
                cols,
                bg="#0d1520",
                padx=12,
                pady=8,
                highlightbackground=BORDER,
                highlightthickness=1
            )
            cell.grid(row=0, column=i, sticky="nsew", padx=4)

            tk.Label(
                cell,
                text=lbl,
                font=("Consolas", 8),
                bg="#0d1520",
                fg=TEXT_DIM
            ).pack()

            tk.Label(
                cell,
                text=part,
                font=("Consolas", 14, "bold"),
                bg="#0d1520",
                fg=color
            ).pack(pady=(4, 0))

    def _build_other_modules(self, modules):
        title = tk.Frame(self.results_frame, bg=BG_DARK)
        title.pack(fill="x", pady=(4, 8))

        tk.Label(
            title,
            text="OTHER MODULES DETECTED",
            font=("Consolas", 10, "bold"),
            bg=BG_DARK,
            fg=TEXT_DIM
        ).pack(side="left")

        tk.Label(
            title,
            text=f"  {len(modules)}  ",
            font=("Consolas", 9),
            bg="#1a2332",
            fg=TEXT_DIM
        ).pack(side="left", padx=(8, 0))

        for mod in modules:
            self._mod_row(mod)

    def _mod_row(self, mod):
        row = tk.Frame(
            self.results_frame,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=14,
            pady=10
        )
        row.pack(fill="x", pady=(0, 4))

        expanded = tk.BooleanVar(value=False)
        detail = tk.Frame(row, bg=CARD_BG)

        abbr, module_name = self._get_module_display(mod.get("id", ""))

        def toggle():
            if expanded.get():
                detail.pack_forget()
                expanded.set(False)
                arrow.config(text="▶")
            else:
                detail.pack(fill="x", pady=(8, 0))
                expanded.set(True)
                arrow.config(text="▼")

        top = tk.Frame(row, bg=CARD_BG)
        top.pack(fill="x")

        arrow = tk.Label(
            top,
            text="▶",
            font=("Consolas", 8),
            bg=CARD_BG,
            fg=TEXT_MUTED,
            cursor="hand2"
        )
        arrow.pack(side="left", padx=(0, 8))
        arrow.bind("<Button-1>", lambda e: toggle())

        id_label = tk.Label(
            top,
            text=mod.get("id", ""),
            font=("Consolas", 12, "bold"),
            bg=CARD_BG,
            fg=ACCENT,
            cursor="hand2"
        )
        id_label.pack(side="left")
        id_label.bind("<Button-1>", lambda e: toggle())

        if abbr:
            badge = tk.Label(
                top,
                text=f"  {abbr}  ",
                font=("Consolas", 9, "bold"),
                bg="#1a2332",
                fg="white"
            )
            badge.pack(side="left", padx=(10, 8))
            badge.bind("<Button-1>", lambda e: toggle())

        name_label = tk.Label(
            top,
            text=module_name,
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_WHITE,
            cursor="hand2"
        )
        name_label.pack(side="left")
        name_label.bind("<Button-1>", lambda e: toggle())

        preview = mod.get("f188") or mod.get("f113") or mod.get("f111") or ""
        if preview:
            tk.Label(
                top,
                text=preview,
                font=("Consolas", 9),
                bg=CARD_BG,
                fg=TEXT_MUTED
            ).pack(side="right")

        meta = tk.Frame(
            detail,
            bg="#0c1018",
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=10,
            pady=8
        )
        meta.pack(fill="x", pady=(0, 8))

        tk.Label(
            meta,
            text=f"NODEID: {mod.get('id', '')}",
            font=("Consolas", 9, "bold"),
            bg="#0c1018",
            fg=ACCENT
        ).pack(anchor="w")

        if abbr:
            tk.Label(
                meta,
                text=f"Acronym: {abbr}",
                font=("Segoe UI", 9),
                bg="#0c1018",
                fg=TEXT_WHITE
            ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            meta,
            text=f"Module Name: {module_name}",
            font=("Segoe UI", 9),
            bg="#0c1018",
            fg=TEXT_WHITE
        ).pack(anchor="w", pady=(2, 0))

        for did, label, value in [
            ("F111", "Hardware", mod.get("f111", "")),
            ("F113", "Part Number", mod.get("f113", "")),
            ("F188", "Strategy", mod.get("f188", "")),
        ]:
            if value:
                line = tk.Frame(detail, bg=CARD_BG)
                line.pack(fill="x", pady=2)

                tk.Label(
                    line,
                    text=did,
                    font=("Consolas", 8, "bold"),
                    bg="#1a2332",
                    fg=ACCENT,
                    padx=4
                ).pack(side="left")

                tk.Label(
                    line,
                    text=label,
                    font=("Segoe UI", 8),
                    bg=CARD_BG,
                    fg=TEXT_DIM
                ).pack(side="left", padx=(8, 0))

                tk.Label(
                    line,
                    text=value,
                    font=("Consolas", 10, "bold"),
                    bg=CARD_BG,
                    fg=TEXT_WHITE
                ).pack(side="left", padx=(12, 0))

                tk.Button(
                    line,
                    text="📋",
                    font=("Segoe UI", 7),
                    bg=CARD_BG,
                    fg=TEXT_DIM,
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda v=value: self._copy(v)
                ).pack(side="right")


def main():
    app = FordPCMDecoder()
    app.mainloop()


if __name__ == "__main__":
    main()
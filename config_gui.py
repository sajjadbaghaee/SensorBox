#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils import load_config, save_config

def f2float(s, default=0.0):
    try:
        return float(s)
    except Exception:
        return default

def save_changes():
    # ---- Offsets ----
    cfg_offsets = config.setdefault("offsets", {
        "BME680": {"temperature": 0.0, "humidity": 0.0, "pressure": 0.0, "gas": 0.0},
        "VEML7700": {"lux": 0.0},
        "SOUND": {"dB": 0.0}
    })
    cfg_offsets["BME680"]["temperature"] = f2float(entry_off_temp.get())
    cfg_offsets["BME680"]["humidity"]    = f2float(entry_off_hum.get())
    cfg_offsets["BME680"]["pressure"]    = f2float(entry_off_press.get())
    cfg_offsets["BME680"]["gas"]         = f2float(entry_off_gas.get())
    cfg_offsets["VEML7700"]["lux"]       = f2float(entry_off_lux.get())
    cfg_offsets["SOUND"]["dB"]           = f2float(entry_off_db.get())

    # ---- Intervals ----
    config["intervals"]["BME680"]     = f2float(entry_bme.get(), 45)
    config["intervals"]["VEML7700"]   = f2float(entry_veml.get(), 10)
    config["intervals"]["SOUND"]      = f2float(entry_sound.get(), 6)
    config["intervals"]["IP_REFRESH"] = f2float(entry_iprefresh.get(), 300)
    config["intervals"]["IamAlive"]   = f2float(entry_iamalive.get(), 3600)

    # ---- MQTT core ----
    config["mqtt"]["host"]         = entry_host.get().strip()
    config["mqtt"]["port"]         = int(f2float(entry_port.get(), 1883))
    config["mqtt"]["topic"]        = entry_topic.get().strip()
    config["mqtt"]["config_topic"] = entry_config_topic.get().strip()

    # ---- MQTT auth ----
    config["mqtt"]["username"] = entry_username.get().strip()
    config["mqtt"]["password"] = entry_password.get()

    # ---- MQTT TLS ----
    config["mqtt"]["use_tls"]      = bool(var_use_tls.get())
    config["mqtt"]["ca_cert"]      = entry_ca_cert.get().strip()
    config["mqtt"]["insecure_tls"] = bool(var_insecure_tls.get())

    # ---- Device ----
    config["device"]["nodeId"] = entry_nodeId.get().strip()

    # ---- Sensor IDs ----
    cfg_sensor = config.setdefault("sensorIds", {})
    cfg_sensor["temp_avg"]       = entries_sensor["temp_avg"].get().strip()
    cfg_sensor["temp_min"]       = entries_sensor["temp_min"].get().strip()
    cfg_sensor["temp_max"]       = entries_sensor["temp_max"].get().strip()

    cfg_sensor["hum_avg"]        = entries_sensor["hum_avg"].get().strip()
    cfg_sensor["hum_min"]        = entries_sensor["hum_min"].get().strip()
    cfg_sensor["hum_max"]        = entries_sensor["hum_max"].get().strip()

    cfg_sensor["press_avg"]      = entries_sensor["press_avg"].get().strip()
    cfg_sensor["press_min"]      = entries_sensor["press_min"].get().strip()
    cfg_sensor["press_max"]      = entries_sensor["press_max"].get().strip()

    cfg_sensor["gas_avg"]        = entries_sensor["gas_avg"].get().strip()
    cfg_sensor["gas_min"]        = entries_sensor["gas_min"].get().strip()
    cfg_sensor["gas_max"]        = entries_sensor["gas_max"].get().strip()

    cfg_sensor["aq_avg"]         = entries_sensor["aq_avg"].get().strip()
    cfg_sensor["aq_min"]         = entries_sensor["aq_min"].get().strip()
    cfg_sensor["aq_max"]         = entries_sensor["aq_max"].get().strip()

    cfg_sensor["aq_label_avg"]   = entries_sensor["aq_label_avg"].get().strip()
    cfg_sensor["aq_label_min"]   = entries_sensor["aq_label_min"].get().strip()
    cfg_sensor["aq_label_max"]   = entries_sensor["aq_label_max"].get().strip()

    cfg_sensor["lux_avg"]        = entries_sensor["lux_avg"].get().strip()
    cfg_sensor["lux_min"]        = entries_sensor["lux_min"].get().strip()
    cfg_sensor["lux_max"]        = entries_sensor["lux_max"].get().strip()

    cfg_sensor["sound_avg"]      = entries_sensor["sound_avg"].get().strip()
    cfg_sensor["sound_min"]      = entries_sensor["sound_min"].get().strip()
    cfg_sensor["sound_max"]      = entries_sensor["sound_max"].get().strip()

    cfg_sensor["ip_msg"]         = entries_sensor["ip_msg"].get().strip()
    cfg_sensor["mac_msg"]        = entries_sensor["mac_msg"].get().strip()
    cfg_sensor["alive_msg"]      = entries_sensor["alive_msg"].get().strip()

    save_config(config, reboot=True)
    messagebox.showinfo(
        "Config Saved",
        "Configuration updated successfully!\nThe system will reboot."
    )

def toggle_password():
    entry_password.config(show="" if var_show_pw.get() else "*")

def browse_ca():
    path = filedialog.askopenfilename(
        title="Select CA Certificate",
        filetypes=[("Certificate files", "*.crt *.pem *.der *.cer"), ("All files", "*.*")]
    )
    if path:
        entry_ca_cert.delete(0, tk.END)
        entry_ca_cert.insert(0, path)

# ---- Load config ----
config = load_config()

# Guarantee sensorIds exists in RAM so GUI doesn't break on first boot
sensorIds_cfg = config.setdefault("sensorIds", {
    "temp_avg": "",
    "temp_min": "",
    "temp_max": "",
    "hum_avg": "",
    "hum_min": "",
    "hum_max": "",
    "press_avg": "",
    "press_min": "",
    "press_max": "",
    "gas_avg": "",
    "gas_min": "",
    "gas_max": "",
    "aq_avg": "",
    "aq_min": "",
    "aq_max": "",
    "aq_label_avg": "",
    "aq_label_min": "",
    "aq_label_max": "",
    "lux_avg": "",
    "lux_min": "",
    "lux_max": "",
    "sound_avg": "",
    "sound_min": "",
    "sound_max": "",
    "ip_msg": "",
    "mac_msg": "",
    "alive_msg": ""
})

# ---- Window / scroll container ----
root = tk.Tk()
root.title("SensorBox Config")
root.geometry("1120x850")

container = ttk.Frame(root)
canvas = tk.Canvas(container, highlightthickness=0)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
hbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
scrollable = ttk.Frame(canvas)

scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set, xscrollcommand=hbar.set)

container.pack(fill="both", expand=True)
canvas.pack(side="left", fill="both", expand=True)
hbar.pack(side="bottom", fill="x")
scrollbar.pack(side="right", fill="y")

# ---- Styling ----
style = ttk.Style()
style.configure("TLabel", font=("Arial", 10), padding=2)
style.configure("TEntry", padding=2)
style.configure("TButton", font=("Arial", 11, "bold"), padding=6)
style.configure("TLabelframe", padding=10)
style.configure("TLabelframe.Label", font=("Arial", 11, "bold"))

# ---- Two-column layout ----
page = ttk.Frame(scrollable)
page.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
page.grid_columnconfigure(0, weight=1)  # left col
page.grid_columnconfigure(1, weight=1)  # right col

left_col  = ttk.Frame(page)
right_col = ttk.Frame(page)

left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

left_col.grid_columnconfigure(0, weight=1)
right_col.grid_columnconfigure(0, weight=1)

# =========================
# LEFT COLUMN
# =========================

# Device Settings (now at the TOP of left column)
frame_device = ttk.LabelFrame(left_col, text="Device Settings")
frame_device.pack(fill="x", expand=True, pady=6)

ttk.Label(frame_device, text="Node ID").grid(row=0, column=0, sticky="w")
entry_nodeId = ttk.Entry(frame_device, width=28)
entry_nodeId.insert(0, config["device"]["nodeId"])
entry_nodeId.grid(row=0, column=1, padx=6, pady=3, sticky="we")
frame_device.grid_columnconfigure(1, weight=1)

# MQTT Settings
frame_mqtt = ttk.LabelFrame(left_col, text="MQTT Settings")
frame_mqtt.pack(fill="x", expand=True, pady=6)

ttk.Label(frame_mqtt, text="Host").grid(row=0, column=0, sticky="w")
entry_host = ttk.Entry(frame_mqtt, width=28)
entry_host.insert(0, config["mqtt"]["host"])
entry_host.grid(row=0, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_mqtt, text="Port").grid(row=0, column=2, sticky="w")
entry_port = ttk.Entry(frame_mqtt, width=8)
entry_port.insert(0, config["mqtt"]["port"])
entry_port.grid(row=0, column=3, padx=6, pady=3, sticky="w")

ttk.Label(frame_mqtt, text="Topic").grid(row=1, column=0, sticky="w")
entry_topic = ttk.Entry(frame_mqtt, width=28)
entry_topic.insert(0, config["mqtt"].get("topic", "sensors"))
entry_topic.grid(row=1, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_mqtt, text="Config Topic").grid(row=1, column=2, sticky="w")
entry_config_topic = ttk.Entry(frame_mqtt, width=22)
entry_config_topic.insert(0, config["mqtt"].get("config_topic", ""))
entry_config_topic.grid(row=1, column=3, padx=6, pady=3, sticky="we")

frame_mqtt.grid_columnconfigure(1, weight=1)
frame_mqtt.grid_columnconfigure(3, weight=1)

# MQTT Authentication
frame_auth = ttk.LabelFrame(left_col, text="MQTT Authentication")
frame_auth.pack(fill="x", expand=True, pady=6)

ttk.Label(frame_auth, text="Username").grid(row=0, column=0, sticky="w")
entry_username = ttk.Entry(frame_auth, width=20)
entry_username.insert(0, config["mqtt"].get("username", ""))
entry_username.grid(row=0, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_auth, text="Password").grid(row=0, column=2, sticky="w")
entry_password = ttk.Entry(frame_auth, width=20, show="*")
entry_password.insert(0, config["mqtt"].get("password", ""))
entry_password.grid(row=0, column=3, padx=6, pady=3, sticky="we")

var_show_pw = tk.BooleanVar(value=False)
chk_show_pw = ttk.Checkbutton(frame_auth, text="Show", variable=var_show_pw, command=toggle_password)
chk_show_pw.grid(row=0, column=4, padx=6, pady=3, sticky="w")

for c in (1, 3):
    frame_auth.grid_columnconfigure(c, weight=1)

# TLS
frame_tls = ttk.LabelFrame(left_col, text="TLS (optional)")
frame_tls.pack(fill="x", expand=True, pady=6)

var_use_tls = tk.BooleanVar(value=bool(config["mqtt"].get("use_tls", False)))
chk_tls = ttk.Checkbutton(frame_tls, text="Use TLS", variable=var_use_tls)
chk_tls.grid(row=0, column=0, columnspan=4, sticky="w", padx=2, pady=3)

var_insecure_tls = tk.BooleanVar(value=bool(config["mqtt"].get("insecure_tls", False)))
chk_insecure = ttk.Checkbutton(frame_tls, text="Allow insecure / self-signed", variable=var_insecure_tls)
chk_insecure.grid(row=1, column=0, columnspan=4, sticky="w", padx=2, pady=3)

ttk.Label(frame_tls, text="CA Certificate").grid(row=2, column=0, sticky="w", padx=2)
entry_ca_cert = ttk.Entry(frame_tls, width=38)
entry_ca_cert.insert(0, config["mqtt"].get("ca_cert", ""))
entry_ca_cert.grid(row=2, column=1, columnspan=2, padx=6, pady=3, sticky="we")

btn_browse = ttk.Button(frame_tls, text="Browse...", command=browse_ca)
btn_browse.grid(row=2, column=3, padx=6, pady=3, sticky="w")

frame_tls.grid_columnconfigure(1, weight=1)
frame_tls.grid_columnconfigure(2, weight=1)

# Offsets
frame_off = ttk.LabelFrame(left_col, text="Offsets (additive)")
frame_off.pack(fill="x", expand=True, pady=6)

ttk.Label(frame_off, text="Temperature (°C)").grid(row=0, column=0, sticky="w")
entry_off_temp = ttk.Entry(frame_off, width=10)
entry_off_temp.insert(0, config.get("offsets", {}).get("BME680", {}).get("temperature", 0.0))
entry_off_temp.grid(row=0, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_off, text="Humidity (%RH)").grid(row=0, column=2, sticky="w")
entry_off_hum = ttk.Entry(frame_off, width=10)
entry_off_hum.insert(0, config.get("offsets", {}).get("BME680", {}).get("humidity", 0.0))
entry_off_hum.grid(row=0, column=3, padx=6, pady=3, sticky="we")

ttk.Label(frame_off, text="Pressure (hPa)").grid(row=1, column=0, sticky="w")
entry_off_press = ttk.Entry(frame_off, width=10)
entry_off_press.insert(0, config.get("offsets", {}).get("BME680", {}).get("pressure", 0.0))
entry_off_press.grid(row=1, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_off, text="Gas (Ω)").grid(row=1, column=2, sticky="w")
entry_off_gas = ttk.Entry(frame_off, width=10)
entry_off_gas.insert(0, config.get("offsets", {}).get("BME680", {}).get("gas", 0.0))
entry_off_gas.grid(row=1, column=3, padx=6, pady=3, sticky="we")

ttk.Label(frame_off, text="Light (lux)").grid(row=2, column=0, sticky="w")
entry_off_lux = ttk.Entry(frame_off, width=10)
entry_off_lux.insert(0, config.get("offsets", {}).get("VEML7700", {}).get("lux", 0.0))
entry_off_lux.grid(row=2, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_off, text="Sound (dB)").grid(row=2, column=2, sticky="w")
entry_off_db = ttk.Entry(frame_off, width=10)
entry_off_db.insert(0, config.get("offsets", {}).get("SOUND", {}).get("dB", 0.0))
entry_off_db.grid(row=2, column=3, padx=6, pady=3, sticky="we")

for c in (1, 3):
    frame_off.grid_columnconfigure(c, weight=1)

# Intervals
frame_int = ttk.LabelFrame(left_col, text="Intervals (seconds)")
frame_int.pack(fill="x", expand=True, pady=6)

ttk.Label(frame_int, text="BME680").grid(row=0, column=0, sticky="w")
entry_bme = ttk.Entry(frame_int, width=8)
entry_bme.insert(0, config["intervals"]["BME680"])
entry_bme.grid(row=0, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_int, text="VEML7700").grid(row=0, column=2, sticky="w")
entry_veml = ttk.Entry(frame_int, width=8)
entry_veml.insert(0, config["intervals"]["VEML7700"])
entry_veml.grid(row=0, column=3, padx=6, pady=3, sticky="we")

ttk.Label(frame_int, text="SOUND").grid(row=0, column=4, sticky="w")
entry_sound = ttk.Entry(frame_int, width=8)
entry_sound.insert(0, config["intervals"]["SOUND"])
entry_sound.grid(row=0, column=5, padx=6, pady=3, sticky="we")

ttk.Label(frame_int, text="IP Refresh").grid(row=1, column=0, sticky="w")
entry_iprefresh = ttk.Entry(frame_int, width=8)
entry_iprefresh.insert(0, config["intervals"]["IP_REFRESH"])
entry_iprefresh.grid(row=1, column=1, padx=6, pady=3, sticky="we")

ttk.Label(frame_int, text="I am Alive").grid(row=1, column=2, sticky="w")
entry_iamalive = ttk.Entry(frame_int, width=8)
entry_iamalive.insert(0, config["intervals"]["IamAlive"])
entry_iamalive.grid(row=1, column=3, padx=6, pady=3, sticky="we")

for c in (1, 3, 5):
    frame_int.grid_columnconfigure(c, weight=1)

# Save button
save_bar = ttk.Frame(left_col)
save_bar.pack(fill="x", expand=True, pady=(10, 20))
save_bar.grid_columnconfigure(0, weight=1)
ttk.Button(save_bar, text="Save & Reboot", command=save_changes).grid(row=0, column=0, sticky="e")

# =========================
# RIGHT COLUMN
# =========================

# Sensor IDs (right column only now)
frame_ids = ttk.LabelFrame(right_col, text="Sensor IDs")
frame_ids.pack(fill="x", expand=True, pady=6)

entries_sensor = {}

def make_sensor_row(row, label_text, key):
    ttk.Label(frame_ids, text=label_text).grid(row=row, column=0, sticky="w")
    e = ttk.Entry(frame_ids, width=40)
    e.insert(0, sensorIds_cfg.get(key, ""))
    e.grid(row=row, column=1, padx=6, pady=2, sticky="we")
    entries_sensor[key] = e

row_i = 0
for label, key in [
    ("Temp avg", "temp_avg"),
    ("Temp min", "temp_min"),
    ("Temp max", "temp_max"),
    ("Hum avg", "hum_avg"),
    ("Hum min", "hum_min"),
    ("Hum max", "hum_max"),
    ("Press avg", "press_avg"),
    ("Press min", "press_min"),
    ("Press max", "press_max"),
    ("Gas avg", "gas_avg"),
    ("Gas min", "gas_min"),
    ("Gas max", "gas_max"),
    ("AQ avg", "aq_avg"),
    ("AQ min", "aq_min"),
    ("AQ max", "aq_max"),
    ("AQ label avg", "aq_label_avg"),
    ("AQ label min", "aq_label_min"),
    ("AQ label max", "aq_label_max"),
    ("Lux avg", "lux_avg"),
    ("Lux min", "lux_min"),
    ("Lux max", "lux_max"),
    ("Sound avg", "sound_avg"),
    ("Sound min", "sound_min"),
    ("Sound max", "sound_max"),
    ("IP msg", "ip_msg"),
    ("MAC msg", "mac_msg"),
    ("Alive msg", "alive_msg"),
]:
    make_sensor_row(row_i, label, key)
    row_i += 1

frame_ids.grid_columnconfigure(1, weight=1)

root.mainloop()

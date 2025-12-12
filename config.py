# config.py
DEFAULTS = {
    "intervals": {
        "BME680": 45,
        "VEML7700": 10,
        "SOUND": 6,
        "IP_REFRESH": 300,
        "IamAlive": 3600
    },
    "mqtt": {
        "host": "0.0.0.0",
        "port": 1886,
        "topic": "topic",
        "config_topic": "toipc/commands",
        "username": "",          # <-- set if your broker requires auth
        "password": "",          # <-- set if your broker requires auth
        "use_tls": True,         # optional
        "ca_cert": "",           # optional: path to CA file (e.g., "/etc/ssl/certs/ca-certificates.crt")
        "insecure_tls": False    # optional: allow self-signed (not recommended for production)
    },
    "device": {
        "nodeId": "node1"
    },
    "buffer": {
        "maxlen": 1000
    }
}


# Per-sensor measurement offsets 
DEFAULTS["offsets"] = {
    "BME680": {
        "temperature": 0.0,
        "humidity": 0.0,
        "pressure": 0.0,
        "gas": 0.0
    },
    "VEML7700": {
        "lux": 0.0
    },
    "SOUND": {
        "dB": 0.0
    }
}

# ---------------------------------------------------------------------------
# Editable sensor IDs (moved here from payload_builder)
# ---------------------------------------------------------------------------
DEFAULTS["sensorIds"] = {
    # Temperature
    "temp_avg": "8adf6950-dc5c-40ba-aaa1-b0f1186fad20",
    "temp_min": "269a691c-29d9-4d2c-b251-793c36644b80",
    "temp_max": "60a23b17-d87e-42d3-be9a-23e4ffc3de60",

    # Humidity
    "hum_avg": "eb165dad-a828-4f2b-8f24-4144e2d5a2ae",
    "hum_min": "64e6760b-74f4-4073-808a-9dc4bff07d9a",
    "hum_max": "764f78e8-ea8f-4737-abcc-e3ea67111135",

    # Pressure
    "press_avg": "9a6dbf01-9831-4281-8909-0b452ef6ff7b",
    "press_min": "14472184-1d7b-4ab2-a392-7c624ac7454c",
    "press_max": "d9e53ae1-4c52-4bb7-b815-d752715c308f",

    # Gas
    "gas_avg": "c684834e-a9c0-471c-b9dd-703474426dc8",
    "gas_min": "a44b7881-fd56-43bc-b04b-1f2d3d4bd1f1",
    "gas_max": "be880eaf-72de-4990-b565-14f57542beb1",

    # Air Quality numeric
    "aq_avg": "1ea50264-9ed0-41ec-ab99-13b91feae61a",
    "aq_min": "2f0fc77d-975f-445b-a3ab-655f2c7aef0d",
    "aq_max": "dbf246db-8daf-44d6-a54c-8b4327f22720",

    # Air Quality labels (string)
    "aq_label_avg": "df1d17e0-70fd-4615-bab5-9f4e7c136b5d",
    "aq_label_min": "3a5acd7e-58f0-41d6-8c35-c0d73a362e2a",
    "aq_label_max": "5d2c3b0d-d843-4a4b-bc60-1cd3a57d4916",

    # Light
    "lux_avg": "400f7c9c-4648-4d68-9623-6ddba017c739",
    "lux_min": "080fbc9d-7a0a-420e-b1e4-36603386b6b0",
    "lux_max": "f2b6af8e-d051-4819-a4b2-302bfcbb3e9d",

    # Sound
    "sound_avg": "e1b5fa13-3e00-4a34-93c7-0e2c57564d1c",
    "sound_min": "60a6932f-25ac-4702-ba19-a461eccd8557",
    "sound_max": "bb3f059d-130b-41d4-94d8-e8c951350e83",

    # System messages
    "ip_msg":   "62fca2aa205c550094bca93f",
    "mac_msg":  "63089b5b205c5513f43719c6",
    "alive_msg": "ebfaf8fc-f984-4abf-8e69-5fbf97923939"
}

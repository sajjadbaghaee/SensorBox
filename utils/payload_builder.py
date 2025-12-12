# utils/payload_builder.py

import json

from datetime import datetime, timezone

def get_utc_timestamp():
    #return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    #return datetime.now(timezone.utc).astimezone().isoformat()
    return int(datetime.now(timezone.utc).timestamp())


def build_bme_payload(nodeId, bme_stats, ip, myMac, aq_scores, aq_labels, sensorIds):
    """
    nodeId      : string (config["device"]["nodeId"])
    bme_stats   : {
        "temperature": {"avg":..., "min":..., "max":...},
        "humidity":    {"avg":..., "min":..., "max":...},
        "pressure":    {"avg":..., "min":..., "max":...},
        "gas":         {"avg":..., "min":..., "max":...}
    }
    ip          : current IP address string (kept for parity with your old signature)
    myMac       : MAC address string
    aq_scores   : {"avg":..., "min":..., "max":...}  # numeric AQ scores from gas
    aq_labels   : {"avg":"Good","min":"Okay","max":"Bad"}  # text labels
    sensorIds   : config["sensorIds"] dict with all UUIDs
    """

    s = sensorIds  # just shorter alias for readability
    gdt = get_utc_timestamp()

    payload = {
        "dataType": "SensorData",
        "data": [
            # Temperature
            {"nodeId": nodeId, "sensorType": "Temperature", "sensorId": s["temp_avg"], "value": bme_stats["temperature"]["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Temperature", "sensorId": s["temp_min"], "value": bme_stats["temperature"]["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Temperature", "sensorId": s["temp_max"], "value": bme_stats["temperature"]["max"], "generatedDate": gdt},

            # Humidity
            {"nodeId": nodeId, "sensorType": "Humidity", "sensorId": s["hum_avg"], "value": bme_stats["humidity"]["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Humidity", "sensorId": s["hum_min"], "value": bme_stats["humidity"]["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Humidity", "sensorId": s["hum_max"], "value": bme_stats["humidity"]["max"], "generatedDate": gdt},

            # Pressure
            {"nodeId": nodeId, "sensorType": "Pressure", "sensorId": s["press_avg"], "value": bme_stats["pressure"]["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Pressure", "sensorId": s["press_min"], "value": bme_stats["pressure"]["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Pressure", "sensorId": s["press_max"], "value": bme_stats["pressure"]["max"], "generatedDate": gdt},

            # Gas (raw BME680)
            {"nodeId": nodeId, "sensorType": "Gas", "sensorId": s["gas_avg"], "value": bme_stats["gas"]["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Gas", "sensorId": s["gas_min"], "value": bme_stats["gas"]["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Gas", "sensorId": s["gas_max"], "value": bme_stats["gas"]["max"], "generatedDate": gdt},

            # AirQuality numeric
            {"nodeId": nodeId, "sensorType": "AirQuality", "sensorId": s["aq_avg"], "value": aq_scores["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "AirQuality", "sensorId": s["aq_min"], "value": aq_scores["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "AirQuality", "sensorId": s["aq_max"], "value": aq_scores["max"]},

            # AirQuality labels (Message type)
            {"nodeId": nodeId, "sensorType": "Message", "sensorId": s["aq_label_avg"], "value": aq_labels["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Message", "sensorId": s["aq_label_min"], "value": aq_labels["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Message", "sensorId": s["aq_label_max"], "value": aq_labels["max"], "generatedDate": gdt},
        ]
    }
    return json.dumps(payload)


def build_veml_payload(nodeId, veml_stats, ip, myMac, sensorIds):
    """
    veml_stats: {
        "lux": {"avg":..., "min":..., "max":...}
    }
    ip, myMac kept for consistency with old signature.
    """

    s = sensorIds
    gdt = get_utc_timestamp()

    payload = {
        "dataType": "SensorData",
        "data": [
            {"nodeId": nodeId, "sensorType": "Light", "sensorId": s["lux_avg"], "value": veml_stats["lux"]["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Light", "sensorId": s["lux_min"], "value": veml_stats["lux"]["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Light", "sensorId": s["lux_max"], "value": veml_stats["lux"]["max"], "generatedDate": gdt},
        ]
    }
    return json.dumps(payload)


def build_sound_payload(nodeId, sound_stats, ip, myMac, sensorIds):
    """
    sound_stats: {
        "dB": {"avg":..., "min":..., "max":...}
    }
    """

    s = sensorIds
    gdt = get_utc_timestamp()

    payload = {
        "dataType": "SensorData",
        "data": [
            {"nodeId": nodeId, "sensorType": "Sound", "sensorId": s["sound_avg"], "value": sound_stats["dB"]["avg"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Sound", "sensorId": s["sound_min"], "value": sound_stats["dB"]["min"], "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Sound", "sensorId": s["sound_max"], "value": sound_stats["dB"]["max"], "generatedDate": gdt},
        ]
    }
    return json.dumps(payload)


def build_IPMAC_payload(nodeId, ip, myMac, sensorIds):
    """
    Send network identity info.
    """

    s = sensorIds
    gdt = get_utc_timestamp()

    payload = {
        "dataType": "SensorData",
        "data": [
            {"nodeId": nodeId, "sensorType": "Message", "sensorId": s["ip_msg"], "value": ip, "generatedDate": gdt},
            {"nodeId": nodeId, "sensorType": "Message", "sensorId": s["mac_msg"], "value": myMac, "generatedDate": gdt},
        ]
    }
    return json.dumps(payload)


def build_IamAlive_payload(nodeId, sensorIds):
    """
    Heartbeat / health message.
    """

    s = sensorIds
    gdt = get_utc_timestamp()

    payload = {
        "dataType": "SensorData",
        "data": [
            {"nodeId": nodeId, "sensorType": "Message", "sensorId": s["alive_msg"], "value": "I am Alive", "generatedDate": gdt},
        ]
    }
    return json.dumps(payload)

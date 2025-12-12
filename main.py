#!/usr/bin/env python3
import time
import board
import busio
from collections import deque

from sensors import BME680Sensor, VEML7700Sensor, SoundSensor
from network import setup_mqtt, flush_buffer, start_watchdog   # <<-- UPDATED
from utils import (
    get_ip_address,
    get_mac_address,
    gas_to_air_quality_fixed,
    air_quality_label,
    load_config,
    init_stats,
    update_stats,
    finalize_stats,
)
from utils.payload_builder import (
    build_bme_payload,
    build_veml_payload,
    build_sound_payload,
    build_IPMAC_payload,
    build_IamAlive_payload,
)

def main():
    # Load runtime configuration (merged with DEFAULTS in config.py)
    config = load_config()

    # Grab sensorIds from config (these are now editable via GUI and stored in config["sensorIds"])
    sensorIds = config.get("sensorIds", {})

    # Init I2C & sensors
    i2c = busio.I2C(board.SCL, board.SDA)
    bme = BME680Sensor(i2c)
    veml = VEML7700Sensor(i2c)
    sound = SoundSensor(i2c)

    # MQTT setup
    mqtt_host = config["mqtt"]["host"]
    mqtt_port = config["mqtt"]["port"]
    client = setup_mqtt(mqtt_host, mqtt_port, config=config)

    # --- NEW: start watchdog thread (topic == nodeId) ---
    start_watchdog(client, config)

    buffer = deque(maxlen=int(config["buffer"]["maxlen"]))

    # Device identity
    myMac = get_mac_address()
    ip = get_ip_address()
    prev_ip = ip  # track last known IP to detect changes
    print(f"MAC: {myMac}, Initial IP: {ip}")

    # Send initial IP + MAC immediately
    buffer.append(build_IPMAC_payload(config["device"]["nodeId"], ip, myMac, sensorIds))

    # Initialize timers (monotonic timestamps)
    last_bme = 0
    last_veml = 0
    last_sound = 0
    last_ip_refresh = 0
    last_IamAlive = 0

    # Rolling stats accumulators for avg/min/max per channel
    stats_bme = init_stats(["temperature", "humidity", "pressure", "gas"])
    stats_veml = init_stats(["lux"])
    stats_sound = init_stats(["dB"])

    print("Starting sensor loop with avg/min/max statistics...")

    while True:
        now = time.monotonic()

        # Read current intervals from config
        intervals = config["intervals"]
        BME680_INTERVAL      = float(intervals.get("BME680", 45))
        VEML7700_INTERVAL    = float(intervals.get("VEML7700", 10))
        SOUND_INTERVAL       = float(intervals.get("SOUND", 6))
        IP_REFRESH_INTERVAL  = float(intervals.get("IP_REFRESH", 300))
        IAMALIVE_INTERVAL    = float(intervals.get("IamAlive", 3600))

        nodeId = config["device"]["nodeId"]
        MQTT_TOPIC = config["mqtt"]["topic"]

        # === Read sensors every loop and update rolling stats ===
        offsets = config.get("offsets", {})
        bme_off   = offsets.get("BME680", {})
        veml_off  = offsets.get("VEML7700", {})
        sound_off = offsets.get("SOUND", {})

        # BME680 read + apply offsets
        bme_vals = bme.read()
        for k in ("temperature", "humidity", "pressure", "gas"):
            if k in bme_vals:
                bme_vals[k] = bme_vals[k] + float(bme_off.get(k, 0.0))
        update_stats(stats_bme, bme_vals)

        # VEML7700 read + apply offset
        veml_vals = veml.read()
        if "lux" in veml_vals:
            veml_vals["lux"] = veml_vals["lux"] + float(veml_off.get("lux", 0.0))
        update_stats(stats_veml, veml_vals)

        # Sound read + apply offset
        sound_vals = sound.read()
        if "dB" in sound_vals:
            sound_vals["dB"] = sound_vals["dB"] + float(sound_off.get("dB", 0.0))
        update_stats(stats_sound, sound_vals)

        # === Refresh IP and detect changes ===
        if now - last_ip_refresh >= IP_REFRESH_INTERVAL:
            ip = get_ip_address()
            if ip != prev_ip:
                print(f"IP changed! Old={prev_ip}, New={ip}")
                prev_ip = ip
                buffer.append(build_IPMAC_payload(nodeId, ip, myMac, sensorIds))
            last_ip_refresh = now

        # === I am Alive message ===
        if now - last_IamAlive >= IAMALIVE_INTERVAL:
            buffer.append(build_IamAlive_payload(nodeId, sensorIds))
            last_IamAlive = now

        # === Periodic BME680 publish ===
        if now - last_bme >= BME680_INTERVAL:
            final_bme = finalize_stats(stats_bme)

            # Convert gas values to AQ score + label for avg/min/max
            aq_scores = {}
            aq_labels = {}
            for key in ["avg", "min", "max"]:
                gas_val = final_bme["gas"][key]
                if gas_val is not None:
                    score = gas_to_air_quality_fixed(gas_val)
                    aq_scores[key] = score
                    aq_labels[key] = air_quality_label(score)
                else:
                    aq_scores[key] = None
                    aq_labels[key] = "Unknown"

            buffer.append(
                build_bme_payload(
                    nodeId,
                    final_bme,
                    ip,
                    myMac,
                    aq_scores,
                    aq_labels,
                    sensorIds
                )
            )

            # reset rolling stats for next window
            stats_bme = init_stats(["temperature", "humidity", "pressure", "gas"])
            last_bme = now

        # === Periodic VEML7700 publish ===
        if now - last_veml >= VEML7700_INTERVAL:
            buffer.append(
                build_veml_payload(
                    nodeId,
                    finalize_stats(stats_veml),
                    ip,
                    myMac,
                    sensorIds
                )
            )
            stats_veml = init_stats(["lux"])
            last_veml = now

        # === Periodic Sound publish ===
        if now - last_sound >= SOUND_INTERVAL:
            buffer.append(
                build_sound_payload(
                    nodeId,
                    finalize_stats(stats_sound),
                    ip,
                    myMac,
                    sensorIds
                )
            )
            stats_sound = init_stats(["dB"])
            last_sound = now

        # Try to publish whatever is in buffer
        flush_buffer(client, buffer, MQTT_TOPIC)

        # tiny sleep to avoid 100% CPU
        time.sleep(0.1)


if __name__ == "__main__":
    main()
    
    

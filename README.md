# SensorBox – Modular IoT Environmental Sensing Platform

## Overview
SensorBox is a modular IoT sensing platform designed for **indoor environmental monitoring** and **research-oriented deployments**.  
It is built around **Raspberry Pi–based nodes** with multiple sensors and supports **buffered data transmission**, **MQTT communication**, and **robust operation under intermittent connectivity**.

The system is suitable for **smart buildings**, **living labs**, **digital twins**, and **AoI-aware sensing experiments**.


GitHub Repository:  
👉 **https://github.com/sajjadbaghaee/SensorBox**



## Key Features
- Modular sensor architecture (plug-and-play)
- MQTT-based communication (TLS-supported)
- Local buffering and delayed flush when connectivity is restored
- Epoch and ISO-8601 timestamping at sampling time
- Designed for long-running unattended operation
- Field-tested in real indoor environments

## Supported Sensors
- **BME680** – Temperature, Humidity, Pressure, Gas/Air Quality
- **VEML7700** – Ambient Light
- **Sound Sensor** – Noise level monitoring
- Extensible to additional I²C / analog sensors

## System Architecture
- **Edge Node:** Raspberry Pi (RPi 3/4/Zero)
- **Sensors:** I²C / Analog
- **Transport:** MQTT over TCP (TLS optional)
- **Backend:** Any MQTT-compatible IoT platform

## Repository Structure
```
.
├── main.py                 # Main execution loop
├── sensors/                # Sensor drivers
├── network/                # MQTT and connectivity handling
├── utils/                  # Payloads, timestamps, buffering
├── config/                 # Runtime configuration
└── docs/                   # Deployment notes
```

## Installation
```bash
git clone https://github.com/sajjadbaghaee/SensorBox.git
cd sensorbox
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration
All runtime parameters are defined in the configuration file:
- Sensor enable/disable
- Sampling intervals
- MQTT broker settings
- Node identifiers

## Running the Node
```bash
python main.py
```

The node will:
1. Sample sensors
2. Timestamp data locally
3. Buffer data if offline
4. Publish once connectivity is available

## Use Cases
- Smart indoor environment monitoring
- Noise-aware digital twins
- HVAC analytics and control support
- Research on Age of Information (AoI)
- Living lab deployments

## Research Context
SensorBox has been used in:
- University living labs
- Noise-reducing digital twin experiments
- AoI-aware IoT communication research


## Contact
For research collaboration or deployment support, feel free to get in touch.

<p align="center">
  <strong> 🔥📘💻 More Codes and Tutorials are available at:</strong><br>
  <a href="https://github.com/sajjadbaghaee">
    <img src="https://img.shields.io/badge/GitHub-sajjadbaghaee-blue?logo=github">
  </a>
</p>

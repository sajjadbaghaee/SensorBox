# network/mqtt_handler.py

import os
import socket
import platform
import logging
from datetime import datetime
import ssl
import json
import ipaddress
import time
import threading
import subprocess

import paho.mqtt.client as mqtt

_current_config = None  # reference to config dict

# -------- Watchdog state --------
_last_echo_time = None
_last_ping_id = None
_network_bad_since = None
_watchdog_lock = threading.Lock()

# -------- Defaults for watchdog behaviour --------
DEFAULT_WATCHDOG_INTERVAL = 30.0           # seconds between pings
DEFAULT_WATCHDOG_TIMEOUT = 90.0            # if no echo for this long ? suspect problem
DEFAULT_MAX_RECONNECT_TRIES = 3
DEFAULT_NETWORK_BAD_REBOOT_DELAY = 300.0   # network can be bad this long before reboot
DEFAULT_PING_TARGET = "192.168.1.1"            # override via config["watchdog"]["ping_target"]


# -------- Small helpers --------
def _mask_secret(s: str) -> str:
    if not s:
        return "<empty>"
    if len(s) <= 4:
        return "*" * len(s)
    return s[0] + "*" * (len(s) - 2) + s[-1]


def _stat_file(path: str) -> str:
    if not path:
        return "n/a"
    try:
        st = os.stat(path)
        return f"ok, size={st.st_size}B"
    except Exception as e:
        return f"missing/err: {e}"


def _rc_text(rc: int) -> str:
    mapping = {
        0: "Connection Accepted",
        1: "Incorrect protocol version",
        2: "Invalid client identifier",
        3: "Server unavailable",
        4: "Bad username or password",
        5: "Not authorised",
    }
    return mapping.get(rc, f"Unknown rc={rc}")


def _check_network(ping_target: str) -> bool:
    """Simple ping-based network check."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ping_target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[NET] ping error: {e}")
        return False

# -------- MQTT callbacks --------
def on_connect(client, userdata, flags, rc):
    print(f"? on_connect rc={rc} ({_rc_text(rc)})")

    cfg = userdata.get("config", {}) if isinstance(userdata, dict) else {}
    mqtt_cfg = cfg.get("mqtt", {})
    cfg_topic = mqtt_cfg.get("config_topic")
    node_id   = cfg.get("device", {}).get("nodeId")

    # Subscribe to config topic (remote config updates)
    if rc == 0:
        if cfg_topic:
            client.subscribe(cfg_topic)
            print(f"?? Subscribed to config topic: {cfg_topic}")
        # Subscribe to nodeId topic for watchdog + remote control
        if node_id:
            client.subscribe(node_id)
            print(f"?? Subscribed to node control topic: {node_id}")

        # Initialize echo time so we don't trigger immediately
        global _last_echo_time
        with _watchdog_lock:
            _last_echo_time = time.time()
    else:
        print("? Connect failed, see rc above.")


def on_message(client, userdata, msg):
    """Handle config updates on config_topic and watchdog/commands on nodeId topic."""
    global _current_config, _last_echo_time

    cfg = userdata.get("config", {}) if isinstance(userdata, dict) else {}
    mqtt_cfg = cfg.get("mqtt", {})
    cfg_topic = mqtt_cfg.get("config_topic")
    node_id   = cfg.get("device", {}).get("nodeId")

    try:
        payload = msg.payload.decode("utf-8", errors="replace")
    except Exception:
        payload = ""

    print(f"?? on_message topic={msg.topic} len={len(payload)}")

    # -------- 1) CONFIG UPDATE messages ----------
    if cfg_topic and msg.topic == cfg_topic:
        try:
            new_cfg = json.loads(payload)
            print("??? Received new config:", new_cfg)
            _current_config.update(new_cfg)
            from utils.config_manager import save_config
            save_config(_current_config, reboot=True)
        except json.JSONDecodeError:
            print("?? Message was not valid JSON; ignoring.")
        except Exception as e:
            print(f"?? Config update failed: {e}")
        return

    # -------- 2) NODE CONTROL / WATCHDOG messages on nodeId topic ----------
    if node_id and msg.topic == node_id:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            print("?? Node control payload not JSON; ignoring.")
            return

        msg_type = data.get("type")

        # 2a) Watchdog echo
        if msg_type == "watchdog":
            ping_id = data.get("id")
            with _watchdog_lock:
                global _last_ping_id
                if ping_id == _last_ping_id:
                    _last_echo_time = time.time()
                    # print(f"[WATCHDOG] Echo received for ping_id={ping_id}")
            return

        # 2b) Remote command, e.g. reboot
        if msg_type == "command":
            cmd = data.get("cmd")
            if cmd == "reboot":
                print("[CMD] Remote reboot command received, rebooting Raspberry Pi.")
                os.system("sudo reboot")
                time.sleep(5)
            # extend here for other commands if needed
        return

    # -------- other topics (if any) ----------
    # currently you don't subscribe to others, so nothing here
    return


def on_disconnect(client, userdata, rc):
    print(f"? on_disconnect rc={rc}")


# -------------------- main API --------------------

def setup_mqtt(
    host="broker.local",
    port=8883,
    keepalive=60,
    config=None,
    enable_debug_log=True,
    wait_conn_timeout=10,
    tls_probe=False,            # kept but disabled by default to avoid long blocking
):
    """
    Create MQTT client with TLS/auth based on config and start loop.
    """
    global _current_config
    _current_config = config or {}
    mqtt_cfg = _current_config.get("mqtt", {})

    username     = mqtt_cfg.get("username", "")
    password     = mqtt_cfg.get("password", "")
    use_tls      = bool(mqtt_cfg.get("use_tls", False))
    ca_cert      = mqtt_cfg.get("ca_cert") or None
    client_cert  = mqtt_cfg.get("client_cert") or None
    client_key   = mqtt_cfg.get("client_key") or None
    insecure_tls = bool(mqtt_cfg.get("insecure_tls", False))

    # -------- Debug dump --------
    print("\n===== MQTT DEBUG DUMP =====")
    print(f"Time:             {datetime.now()}")
    print(f"Host/Port:        {host}:{port}")
    print(f"Username:         {username or '<empty>'}")
    print(f"Password (mask):  {_mask_secret(password)}")
    print(f"Use TLS:          {use_tls}")
    print(f"CA file:          {ca_cert} ({_stat_file(ca_cert)})")
    print(f"Client cert:      {client_cert or 'n/a'} ({_stat_file(client_cert) if client_cert else 'n/a'})")
    print(f"Client key:       {client_key or 'n/a'} ({_stat_file(client_key) if client_key else 'n/a'})")
    print(f"Insecure TLS:     {insecure_tls}")
    print(f"Keepalive:        {keepalive}s")
    print(f"Python:           {platform.python_version()} on {platform.platform()}")
    print(f"OpenSSL:          {ssl.OPENSSL_VERSION}")

    # DNS/host resolution
    try:
        res = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        addrs = sorted({r[4][0] for r in res})
        print(f"DNS/AddrInfo:     {host} -> {addrs}")
    except Exception as e:
        print(f"DNS/AddrInfo:     FAILED: {e}")

    # IP vs hostname hint
    try:
        ipaddress.ip_address(host)
        if not insecure_tls:
            print("?? Using raw IP for TLS; ensure this IP is present in the broker certificate SANs.")
    except ValueError:
        print("?? Using hostname; ensure it matches a SAN in the broker certificate.")

    # Create client
    kwargs = dict(userdata={"config": _current_config}, protocol=mqtt.MQTTv311)
    if hasattr(mqtt, "CallbackAPIVersion"):
        kwargs["callback_api_version"] = mqtt.CallbackAPIVersion.VERSION1
    client = mqtt.Client(**kwargs)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    if enable_debug_log:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
        client.enable_logger()

    if username:
        client.username_pw_set(username, password or "")

    # TLS setup
    if use_tls:
        if not ca_cert:
            raise ValueError("TLS requested but 'ca_cert' path is missing in config.mqtt.ca_cert")
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = not insecure_tls
        ctx.load_verify_locations(cafile=ca_cert)
        if client_cert and client_key:
            ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
        client.tls_set_context(ctx)
        client.tls_insecure_set(bool(insecure_tls))

        print("TLS Context:")
        try:
            mv = ctx.minimum_version.name
        except Exception:
            mv = str(ctx.minimum_version)
        print(f"  min_version:    {mv}")
        print(f"  check_hostname: {ctx.check_hostname}")
        print(f"  verify_mode:    {ctx.verify_mode} (2=require)")

        # Optional one-shot probe (disabled by default)
        if tls_probe:
            try:
                print("TLS probe: opening socket & performing handshake!")
                with socket.create_connection((host, port), timeout=5) as s:
                    with ctx.wrap_socket(s, server_hostname=(host if ctx.check_hostname else None)) as ss:
                        vers = ss.version()
                        ciph = ss.cipher()
                        peer = ss.getpeercert()
                        print(f"  negotiated:     TLS={vers}, cipher={ciph}")
                        sans = None
                        if peer:
                            for k, v in peer.items():
                                if k == "subjectAltName":
                                    sans = v
                                    break
                        print(f"  peer SANs:      {sans if sans else '<none reported>'}")
            except Exception as e:
                print(f"  TLS probe FAILED: {repr(e)}")

    # Backoff for reconnects (useful if Wi-Fi blips)
    client.reconnect_delay_set(min_delay=1, max_delay=60)

    # Connect and start network thread
    print("Connecting (async)!")
    client.connect_async(host, int(port), keepalive=keepalive)
    client.loop_start()

    print("===== END MQTT DEBUG DUMP =====\n")
    return client


def flush_buffer(client, buffer, topic, qos=1, retain=False):
    """
    Publish oldest buffered message to the data topic.
    """
    if not buffer:
        return
    if not client.is_connected():
        print("?? Not connected yet; will retry later!")
        return
    try:
        message = buffer[0]
        info = client.publish(topic, message, qos=qos, retain=retain)
        if getattr(info, "rc", 0) == mqtt.MQTT_ERR_SUCCESS:
            print(f"?? Sent to {topic}: {message!r} (qos={qos}, retain={retain})")
            buffer.popleft()
        else:
            print(f"?? Publish RC={info.rc}; will retry!")
    except Exception as e:
        print(f"? MQTT publish error: {e}")
        

# -------------------- WATCHDOG LOGIC --------------------

def _watchdog_loop(client, config):
    """
    Background thread:
      - publish watchdog on nodeId topic
      - expect echo (because we subscribe to nodeId)
      - if no echo + reconnect + network bad for long ? reboot
    """
    global _last_ping_id, _last_echo_time, _network_bad_since

    node_id = config.get("device", {}).get("nodeId")
    if not node_id:
        print("[WATCHDOG] No device.nodeId in config; watchdog disabled.")
        return

    wd_conf = config.get("watchdog", {})
    WATCHDOG_INTERVAL = float(wd_conf.get("interval", DEFAULT_WATCHDOG_INTERVAL))
    WATCHDOG_TIMEOUT = float(wd_conf.get("timeout", DEFAULT_WATCHDOG_TIMEOUT))
    MAX_RECONNECT_TRIES = int(wd_conf.get("max_reconnect_tries", DEFAULT_MAX_RECONNECT_TRIES))
    NETWORK_BAD_REBOOT_DELAY = float(wd_conf.get("network_bad_reboot_delay", DEFAULT_NETWORK_BAD_REBOOT_DELAY))
    PING_TARGET = wd_conf.get("ping_target", DEFAULT_PING_TARGET)

    reconnect_attempts = 0

    print(f"[WATCHDOG] Started. interval={WATCHDOG_INTERVAL}s, timeout={WATCHDOG_TIMEOUT}s, "
          f"ping_target={PING_TARGET}")

    while True:
        # 1) Send watchdog ping
        ping_id = int(time.time() * 1000)  # ms timestamp as id
        payload = json.dumps({
            "type": "watchdog",
            "id": ping_id,
            "ts": time.time(),
            "node_id": node_id,
        })

        with _watchdog_lock:
            _last_ping_id = ping_id
            if _last_echo_time is None:
                _last_echo_time = time.time()

        try:
            client.publish(node_id, payload, qos=1)
            # print(f"[WATCHDOG] Sent ping_id={ping_id} on topic={node_id}")
        except Exception as e:
            print(f"[WATCHDOG] Publish error: {e}")

        time.sleep(WATCHDOG_INTERVAL)

        # 2) Check echo age
        now = time.time()
        with _watchdog_lock:
            elapsed = now - (_last_echo_time or now)

        if elapsed > WATCHDOG_TIMEOUT:
            print(f"[WATCHDOG] No echo for {elapsed:.1f}s ? checking MQTT + network")

            # 2a) Try MQTT reconnect
            try:
                client.reconnect()
                reconnect_attempts += 1
                print(f"[WATCHDOG] Reconnect attempt {reconnect_attempts}")
            except Exception as e:
                print(f"[WATCHDOG] Reconnect failed: {e}")
                reconnect_attempts += 1

            # 2b) Check network
            net_ok = _check_network(PING_TARGET)
            if net_ok:
                print("[NET] Network OK, so likely broker/topic issue. Not rebooting yet.")
                _network_bad_since = None
            else:
                if _network_bad_since is None:
                    _network_bad_since = time.time()
                    print("[NET] Network appears DOWN, starting bad timer...")
                else:
                    bad_duration = now - _network_bad_since
                    print(f"[NET] Network down for {bad_duration:.1f}s")

                    if (bad_duration > NETWORK_BAD_REBOOT_DELAY and
                            reconnect_attempts >= MAX_RECONNECT_TRIES):
                        print("[WATCHDOG] Long network+MQTT failure. REBOOTING RASPBERRY PI.")
                        os.system("sudo reboot")
                        time.sleep(10)
                        break
        else:
            # healthy again
            reconnect_attempts = 0
            _network_bad_since = None

def start_watchdog(client, config):
    """
    Public API: call from main.py after setup_mqtt().
    """
    t = threading.Thread(target=_watchdog_loop, args=(client, config), daemon=True)
    t.start()

# network/mqtt_handler.py

import os
import socket
import platform
import logging
from datetime import datetime
import ssl, json, ipaddress, time
import paho.mqtt.client as mqtt

_current_config = None  # reference to config dict

# --- robust Paho version detection ---
try:
    from importlib.metadata import version as _pkg_version  # Python 3.8+
    _PAHO_VERSION = _pkg_version("paho-mqtt")
except Exception:
    # Fallback for unusual installs / old environments
    _PAHO_VERSION = getattr(mqtt, "__version__", "unknown")


# -------------------- helpers --------------------

def _mask_secret(s: str) -> str:
    if not s:
        return "<empty>"
    if len(s) <= 2:
        return s[0] + "*"*(len(s)-1)
    return s[0] + "*"*(len(s)-2) + s[-1]

def _stat_file(path: str) -> str:
    if not path:
        return "n/a"
    try:
        st = os.stat(path)
        perms = oct(st.st_mode & 0o777)
        ts = datetime.fromtimestamp(st.st_mtime)
        return f"exists, size={st.st_size}B, perms={perms}, mtime={ts}"
    except FileNotFoundError:
        return "MISSING"
    except Exception as e:
        return f"ERROR: {e}"

def _rc_text(rc: int) -> str:
    return {
        0: "Success",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier",
        3: "Connection refused - server unavailable",
        4: "Connection refused - bad username or password",
        5: "Connection refused - not authorised",
    }.get(rc, f"Unknown ({rc})")


# -------------------- callbacks --------------------

def on_connect(client, userdata, flags, rc):
    print(f"? on_connect rc={rc} ({_rc_text(rc)})")
    if rc == 0:
        cfg = userdata.get("config", {}) if isinstance(userdata, dict) else {}
        mqtt_cfg = cfg.get("mqtt", {})
        cfg_topic = mqtt_cfg.get("config_topic")
        if cfg_topic:
            client.subscribe(cfg_topic)
            print(f"?? Subscribed to config topic: {cfg_topic}")
    else:
        print("? Connect failed, see rc above.")

def on_message(client, userdata, msg):
    global _current_config
    try:
        payload = msg.payload.decode("utf-8", errors="replace")
        print(f"?? on_message topic={msg.topic} len={len(payload)}")
        new_cfg = json.loads(payload)
        print("??? Received new config:", new_cfg)
        _current_config.update(new_cfg)
        from utils.config_manager import save_config
        save_config(_current_config, reboot=True)
    except json.JSONDecodeError:
        print("?? Message was not valid JSON; ignoring.")
    except Exception as e:
        print(f"?? Config update failed: {e}")

def on_disconnect(client, userdata, rc):
    print(f"?? on_disconnect rc={rc} (0=clean). Loop will attempt reconnects.")


# -------------------- main API --------------------

def setup_mqtt(
    host="broker.local",
    port=8883,
    keepalive=60,
    config=None,
    enable_debug_log=True,
    wait_conn_timeout=10,
    tls_probe=True,             # set False to skip the pre-handshake probe
):
    """
    host: use a hostname that matches the server cert SAN (e.g., 'broker.local').
          If you use an IP, make sure that IP is listed in the cert SANs.
    """
    global _current_config
    _current_config = config or {}
    mqtt_cfg = _current_config.get("mqtt", {})

    username     = mqtt_cfg.get("username", "")
    password     = mqtt_cfg.get("password", "")
    use_tls      = bool(mqtt_cfg.get("use_tls", True))
    ca_cert      = mqtt_cfg.get("ca_cert") or None
    client_cert  = mqtt_cfg.get("client_cert") or None
    client_key   = mqtt_cfg.get("client_key") or None
    insecure_tls = bool(mqtt_cfg.get("insecure_tls", False))
    
    # -------- Debug dump --------
    print("\n===== MQTT DEBUG DUMP =====")
    print(f"Time:             {datetime.now()}")
    print(f"Host/Port:        {host}:{port}")
    print(f"Username:         {username or '<empty>'}")
    print(f"Password:         {_mask_secret(password)}")
    print(f"Password:         {password}")
    print(f"Use TLS:          {use_tls}")
    print(f"CA file:          {ca_cert} ({_stat_file(ca_cert)})")
    print(f"Client cert:      {client_cert or 'n/a'} ({_stat_file(client_cert) if client_cert else 'n/a'})")
    print(f"Client key:       {client_key or 'n/a'} ({_stat_file(client_key) if client_key else 'n/a'})")
    print(f"Insecure TLS:     {insecure_tls}")
    print(f"Keepalive:        {keepalive}s")
    print(f"Python:           {platform.python_version()} on {platform.platform()}")
    print(f"Paho:             {_PAHO_VERSION}")
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
            print("?? Using raw IP; ensure this IP is present in the broker certificate SANs.")
    except ValueError:
        print("?? Using hostname; ensure it matches a SAN in the broker certificate.")

    # Create client (Paho v1 callback API)
    kwargs = dict(userdata={"config": _current_config}, protocol=mqtt.MQTTv311)
    if hasattr(mqtt, "CallbackAPIVersion"):
        kwargs["callback_api_version"] = mqtt.CallbackAPIVersion.VERSION1
    client = mqtt.Client(**kwargs)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    if enable_debug_log:
        # Ensure root logger is at DEBUG once; Paho uses logging module
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
        client.enable_logger()

    if username:
        client.username_pw_set(username, password or "")

    # TLS setup
    ctx = None
    if use_tls:
        if not ca_cert:
            raise ValueError("TLS requested but 'ca_cert' path is missing in config.")
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = not insecure_tls
        ctx.load_verify_locations(cafile=ca_cert)
        if client_cert and client_key:
            ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)  # mTLS, if you use port 8884
        client.tls_set_context(ctx)
        client.tls_insecure_set(bool(insecure_tls))
        #client.tls_insecure_set(True)

        print("TLS Context:")
        try:
            mv = ctx.minimum_version.name  # Py3.11+
        except Exception:
            mv = str(ctx.minimum_version)
        print(f"  min_version:    {mv}")
        print(f"  check_hostname: {ctx.check_hostname}")
        print(f"  verify_mode:    {ctx.verify_mode} (2=require)")

        # Optional one-shot TLS probe (preflight handshake)
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

    # Wait until actually connected (or timeout)
    deadline = time.time() + max(0, wait_conn_timeout)
    while time.time() < deadline and not client.is_connected():
        time.sleep(0.1)

    print(f"is_connected:     {client.is_connected()}")
    print("===== END MQTT DEBUG DUMP =====\n")
    return client


def flush_buffer(client, buffer, topic, qos=1, retain=False):
    if not buffer:
        return
    if not client.is_connected():
        print("?? Not connected yet; will retry later!")
        return
    try:
        message = buffer[0]
        info = client.publish(topic, message, qos=qos, retain=retain)
        # info.rc == MQTT_ERR_SUCCESS (0) means it was queued successfully
        if getattr(info, "rc", 0) == mqtt.MQTT_ERR_SUCCESS:
            print(f"?? Sent to {topic}: {message!r} (qos={qos}, retain={retain})")
            buffer.popleft()
            #buffer.pop(0) if hasattr(buffer, "pop") else buffer.popleft()
        else:
            print(f"?? Publish RC={info.rc}; will retry!")
    except Exception as e:
        print(f"? MQTT publish error: {e}")

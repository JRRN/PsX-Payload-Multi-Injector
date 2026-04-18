import ipaddress


def validate_endpoint(ip_text, port_text):
    ip = (ip_text or "").strip()
    port_raw = (port_text or "").strip()

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return None, None, "error_invalid_ip"

    try:
        port = int(port_raw)
    except Exception:
        return None, None, "error_invalid_port"

    if port < 1 or port > 65535:
        return None, None, "error_invalid_port"

    return ip, port, None

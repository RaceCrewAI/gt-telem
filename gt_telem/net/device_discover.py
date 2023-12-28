import socket
from typing import Optional, Tuple


def _get_host_type(buffer: str) -> str:
    for line in buffer.split("\n"):
        if line.startswith("HTTP"):
            code = int(line.split()[1])
        elif line:
            key, value = map(str.strip, line.split(":", 1))
            if key == "host-type":
                ps_type = value
                break
    return ps_type + " STANDBY" if code == 620 else ps_type


def get_ps_ip_type() -> tuple[str | None, str | None]:
    """
    Discovers the PlayStation IP address and host type using device discovery protocol.

    Returns:
    Tuple[Optional[str], Optional[str]]: A tuple containing the PlayStation IP address and host type.
    """
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    skt.settimeout(1)

    query = b"SRCH * HTTP/1.1\ndevice-discovery-protocol-version:00030010"

    skt.sendto(query, ("<broadcast>", 9302))
    try:
        packet, addr = skt.recvfrom(1024)
    except socket.timeout:
        return None, None

    ps_type = _get_host_type(packet.decode("utf-8"))
    host_ip = addr[0]

    return host_ip, ps_type

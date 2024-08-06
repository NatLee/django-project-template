from typing import Optional
from ipaddress import ip_address, ip_network

def is_valid_ip(ip: str) -> bool:
    try:
        ip_address(ip)
        return True
    except ValueError:
        return False

def is_private_ip(ip: str) -> bool:
    private_networks = [
        ip_network('10.0.0.0/8'),
        ip_network('172.16.0.0/12'),
        ip_network('192.168.0.0/16'),
        ip_network('fc00::/7'),
    ]
    ip_addr = ip_address(ip)
    return any(ip_addr in network for network in private_networks)

def get_client_ip(request) -> Optional[str]:
    ip_headers = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP',
        'HTTP_CLIENT_IP',
        'REMOTE_ADDR',
        'X_REAL_IP',
        'X_FORWARDED_FOR',
    ]
    for header in ip_headers:
        ip_list = request.META.get(header, '').split(',')
        for ip in ip_list:
            ip = ip.strip()
            if is_valid_ip(ip) and not is_private_ip(ip):
                return ip
    
    return None
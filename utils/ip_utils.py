

# utils/ip_utils.py
"""
IP address utilities for getting real IP and geolocation
"""
import requests
import logging
from functools import lru_cache
from ipaddress import ip_address, ip_network

logger = logging.getLogger(__name__)

# Private IP ranges
PRIVATE_IP_RANGES = [
    ip_network('10.0.0.0/8'),
    ip_network('172.16.0.0/12'),
    ip_network('192.168.0.0/16'),
    ip_network('127.0.0.0/8'),
    ip_network('::1/128'),
    ip_network('fc00::/7'),
    ip_network('fe80::/10')
]


def get_real_ip(request):
    """
    Get the real IP address from the request, handling proxies
    
    Args:
        request: Flask request object
        
    Returns:
        str: Real IP address or None
    """
    # Check for proxy headers in order of preference
    headers_to_check = [
        'X-Real-Ip',
        'X-Forwarded-For',
        'X-Client-Ip',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',    # Akamai and Cloudflare
        'X-Original-Forwarded-For'
    ]
    
    for header in headers_to_check:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For can contain multiple IPs
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            
            # Validate IP
            try:
                parsed_ip = ip_address(ip)
                # Skip private IPs
                if not any(parsed_ip in range for range in PRIVATE_IP_RANGES):
                    return str(parsed_ip)
            except ValueError:
                continue
    
    # Fallback to remote_addr
    return request.remote_addr


@lru_cache(maxsize=1000)
def get_geolocation(ip_address):
    """
    Get geolocation information for an IP address
    Uses ip-api.com free service (limited to 45 requests per minute)
    
    Args:
        ip_address: IP address string
        
    Returns:
        dict: Geolocation information
    """
    try:
        # Skip geolocation for private IPs
        parsed_ip = ip_address(ip_address)
        if any(parsed_ip in range for range in PRIVATE_IP_RANGES):
            return {'country': 'Local', 'city': 'Private Network'}
        
        # Make API request
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            timeout=2,
            params={'fields': 'country,countryCode,city,regionName,lat,lon'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('countryCode', 'UN'),
                    'country_name': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon')
                }
    except Exception as e:
        logger.warning(f"Failed to get geolocation for {ip_address}: {str(e)}")
    
    return {'country': 'UN', 'city': 'Unknown'}


def is_valid_ip(ip_string):
    """
    Check if a string is a valid IP address
    
    Args:
        ip_string: String to validate
        
    Returns:
        bool: True if valid IP, False otherwise
    """
    try:
        ip_address(ip_string)
        return True
    except ValueError:
        return False


def anonymize_ip(ip_string):
    """
    Anonymize IP address for privacy (zero out last octet)
    
    Args:
        ip_string: IP address to anonymize
        
    Returns:
        str: Anonymized IP address
    """
    try:
        ip = ip_address(ip_string)
        if ip.version == 4:
            # Zero out last octet
            parts = str(ip).split('.')
            parts[-1] = '0'
            return '.'.join(parts)
        else:
            # For IPv6, zero out last 64 bits
            return str(ip_network(f"{ip}/64", strict=False).network_address)
    except ValueError:
        return "0.0.0.0"
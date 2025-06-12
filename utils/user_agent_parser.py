# utils/user_agent_parser.py
"""
User agent parsing utilities
"""
from user_agents import parse


def parse_user_agent(user_agent_string):
    """
    Parse user agent string and extract relevant information
    
    Args:
        user_agent_string: Raw user agent string
        
    Returns:
        dict: Parsed user agent information
    """
    try:
        user_agent = parse(user_agent_string)
        
        # Determine device type
        if user_agent.is_mobile:
            device_type = 'mobile'
        elif user_agent.is_tablet:
            device_type = 'tablet'
        elif user_agent.is_pc:
            device_type = 'desktop'
        else:
            device_type = 'unknown'
        
        return {
            'browser': user_agent.browser.family[:50] if user_agent.browser.family else 'Unknown',
            'browser_version': user_agent.browser.version_string[:20] if user_agent.browser.version_string else None,
            'os': user_agent.os.family[:50] if user_agent.os.family else 'Unknown',
            'os_version': user_agent.os.version_string[:20] if user_agent.os.version_string else None,
            'device_type': device_type,
            'is_bot': user_agent.is_bot
        }
    except Exception:
        return {
            'browser': 'Unknown',
            'browser_version': None,
            'os': 'Unknown',
            'os_version': None,
            'device_type': 'unknown',
            'is_bot': False
        }


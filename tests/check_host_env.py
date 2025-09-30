#!/usr/bin/env python3
"""
Script to check if environment variables are accessible from the host
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_host_env():
    """
    Check if environment variables are accessible from the host
    """
    print("Checking environment variables from host...")
    print("=" * 50)
    
    # List of environment variables we're interested in
    env_vars = [
        'TAVILY_API_KEY',
        'FIRECRAWL_API_KEY',
        'OPENROUTER_API_KEY',
        'OPENROUTER_MODEL',
        'OLLAMA_HOST',
        'OLLAMA_MODEL',
        'REDIS_HOST',
        'REDIS_PORT',
        'N8N_HOST',
        'N8N_PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask the value for security (show only first 4 and last 4 characters)
            if len(value) > 8:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
            else:
                masked_value = '*' * len(value)
            print(f"✓ {var}: {masked_value}")
        else:
            print(f"✗ {var}: NOT SET")
    
    print("\n" + "=" * 50)
    print("All environment variables from .env file:")
    print("=" * 50)
    
    # Load and display all variables from .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if value:
                        # Mask the value for security
                        if len(value) > 8:
                            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
                        else:
                            masked_value = '*' * len(value)
                        print(f"{key}: {masked_value}")
                    else:
                        print(f"{key}: (empty)")

if __name__ == "__main__":
    check_host_env()
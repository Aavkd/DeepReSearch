#!/usr/bin/env python3
"""
Script to check if required environment variables are set
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Required environment variables
required_vars = [
    'TAVILY_API_KEY',
    'FIRECRAWL_API_KEY',
    'OPENROUTER_API_KEY',
    'OPENROUTER_MODEL',
    'OLLAMA_HOST',
    'OLLAMA_MODEL'
]

# Optional environment variables
optional_vars = [
    'BRAVE_API_KEY',
    'SEARCHAPI_IO_KEY',
    'N8N_HOST',
    'N8N_PORT',
    'N8N_ENCRYPTION_KEY',
    'REDIS_HOST',
    'REDIS_PORT',
    'POSTGRES_HOST',
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD'
]

def check_env_vars():
    """
    Check if environment variables are set
    """
    print("Checking required environment variables...")
    print("=" * 50)
    
    all_good = True
    
    # Check required variables
    for var in required_vars:
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
            all_good = False
    
    print("\nChecking optional environment variables...")
    print("=" * 50)
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            # Mask the value for security
            if len(value) > 8:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
            else:
                masked_value = '*' * len(value)
            print(f"✓ {var}: {masked_value}")
        else:
            print(f"○ {var}: NOT SET (optional)")
    
    print("\n" + "=" * 50)
    if all_good:
        print("All required environment variables are set!")
    else:
        print("Some required environment variables are missing!")
        print("Please check your .env file.")
    
    return all_good

def show_docker_env():
    """
    Show how to check environment variables in Docker containers
    """
    print("\nTo check environment variables in the n8n container, run:")
    print("docker-compose exec n8n printenv")
    
    print("\nTo check specific variables:")
    print("docker-compose exec n8n printenv | grep API_KEY")

if __name__ == "__main__":
    check_env_vars()
    show_docker_env()
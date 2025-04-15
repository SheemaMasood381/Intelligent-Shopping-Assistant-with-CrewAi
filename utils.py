import os
from dotenv import load_dotenv

# Load environment variables from the .env file
def load_environment_variables():
    load_dotenv(".env")

# Get API key securely from environment variables
def get_api_key(key_name):
    value = os.getenv(key_name)
    if value is None:
        raise ValueError(f"API key {key_name} is not set in the environment variables.")
    return value

# Function to check if the environment variables are set correctly
def check_environment_variables(required_keys):
    for key in required_keys:
        if not os.getenv(key):
            raise EnvironmentError(f"Required environment variable '{key}' is missing.")
    print("All required environment variables are loaded correctly.")

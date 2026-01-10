import os

def load_env(env_path=".env"):
    """
    Simple .env loader to avoid dependency on python-dotenv.
    """
    if not os.path.exists(env_path):
        # Try looking in parent dirs
        if os.path.exists(os.path.join("..", env_path)):
             env_path = os.path.join("..", env_path)
        else:
             print(f"⚠️  .env file not found at {env_path}")
             return
    
    print(f"🔧 Loading environment from {env_path}...")
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip()
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    os.environ[key.strip()] = value
                    # Mask value in log
                    print(f"  - Set {key.strip()}")
    except Exception as e:
        print(f"❌ Error loading .env: {e}")

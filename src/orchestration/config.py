import yaml
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "configs/system_rules.yaml"):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Loads the YAML configuration file.
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML config: {e}")

    def get_config(self) -> Dict[str, Any]:
        return self._config

    def get_llm_api_key(self) -> str:
        """
        Retrieves the Groq API Key from environment variables.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
             # Fallback or error - for now validation might be loose or strict depending on needs
             # In a strict pipeline, we might raise an error.
             print("Warning: GROQ_API_KEY not found in environment variables.")
        return api_key

# Global instance or factory
def load_global_config():
    # Adjust path relative to project root if needed
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_path, "configs", "system_rules.yaml")
    return ConfigLoader(config_path).get_config()

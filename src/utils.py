import yaml
from pathlib import Path
from typing import Any, Dict, TypedDict
from logger import logger  # Import the logger

class ConfigDict(TypedDict):
    project_root: Path
    input_folder: str
    output_folder: str
    input_folder_path: Path
    output_folder_path: Path

def get_project_root() -> Path:
    """
    Returns the root directory of the project by going up one level from the 'src' folder.

    Returns:
        Path: The root directory of the project.
    """
    project_root = Path(__file__).resolve().parent.parent
    logger.info(f"Project root determined: {project_root}")
    return project_root

def validate_config(config: Dict[str, Any]) -> None:
    """Ensure required keys exist in the config."""
    required_keys = ["input_folder", "output_folder"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required key '{key}' in config.yaml")
        else: logger.info("YAML configuration loaded successfully.")

def load_yaml_config(project_root: Path) -> Dict[str, Any]:
    """
    Loads a YAML configuration file from the specified folder.

    Args:
        yaml_folder_path (Path): The directory containing the 'config.yaml' file.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed YAML configuration.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        yaml.YAMLError: If there's an issue parsing the YAML file.
    """
    
    yaml_file_path = project_root / "config.yaml"

    if not yaml_file_path.exists():
        logger.error(f"Configuration file not found: {yaml_file_path}")
        raise FileNotFoundError(f"Configuration file not found: {yaml_file_path}")

    try:

        with yaml_file_path.open("r", encoding="utf-8") as file:
            # Load YAML
            config = yaml.safe_load(file) or {}

            # Apply validation before returning config
            validate_config(config)

            return config
    except yaml.YAMLError as e:
        logger.exception("Error parsing YAML file.")
        raise ValueError(f"Error parsing YAML file: {e}") from e

def get_config() -> ConfigDict:
    """
    Retrieves the project configuration, including the root directory and YAML settings.

    Returns:
        ConfigDict: A structured dictionary containing project settings.
    """

    logger.info("Loading project configuration...")

    project_root = get_project_root()
    config = load_yaml_config(project_root = project_root)

    # Generate output dict
    config_dict = {
        **config,
        "project_root": project_root,
        "input_folder_path": project_root / config["input_folder"],
        "output_folder_path": project_root / config["output_folder"]
    }

    return config_dict

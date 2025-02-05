import yaml
from pathlib import Path
from typing import Any, Dict
from logger import logger  # Import the logger

def get_project_root() -> Path:
    """
    Returns the root directory of the project by going up one level from the 'src' folder.

    Returns:
        Path: The root directory of the project.
    """
    project_root = Path(__file__).resolve().parent.parent
    logger.info(f"Project root determined: {project_root}")
    return project_root

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
        config_dict = {}
        config_dict["project_root"] = project_root

        with yaml_file_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
            logger.info("YAML configuration loaded successfully.")
            config_dict.update(config)

            return config_dict
    except yaml.YAMLError as e:
        logger.exception("Error parsing YAML file.")
        raise ValueError(f"Error parsing YAML file: {e}") from e

def get_config() -> Dict[str, Any]:
    """
    Retrieves the project configuration, including the root directory and YAML settings.

    Returns:
        Dict[str, Any]: A dictionary containing project settings.
    """
    logger.info("Loading project configuration...")
    config_dict = load_yaml_config(project_root = get_project_root())
    

    return config_dict

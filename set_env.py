"""
Environment and settings configuration module.
Handles loading .env variables and accessing settings.yaml configuration.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import yaml


def load_env_variables():
    """
    Load environment variables from .env file.

    This function loads machine-specific paths that vary depending on
    where the program is run.

    Returns:
        dict: Dictionary containing the loaded environment variables
    """
    # Load .env file from the project root
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)

    # Return the loaded variables as a dictionary
    return {
        'BOX_ATI_BASE_PATH': os.getenv('BOX_ATI_BASE_PATH', ''),
        'PROJECT_BASE_PATH': os.getenv('PROJECT_BASE_PATH', '')
    }


class Settings:
    """
    Wrapper class for accessing settings.yaml configuration.

    This class loads the YAML configuration and provides easy access to
    application settings that don't vary by machine.

    Usage:
        settings = Settings()
        db_path = settings.get('database.filename')
        email = settings.get('email.send_on_behalf')
    """

    def __init__(self):
        """Initialize and load the settings.yaml file."""
        settings_path = Path(__file__).parent / 'settings.yaml'
        with open(settings_path, 'r') as f:
            self._settings = yaml.safe_load(f)

        # Load environment variables
        self._env = load_env_variables()

    def get(self, key_path, default=None):
        """
        Get a configuration value using dot notation.

        Args:
            key_path (str): Dot-separated path to the setting (e.g., 'database.filename')
            default: Default value if the key is not found

        Returns:
            The configuration value or default if not found

        Example:
            settings.get('database.filename')
            settings.get('email.send_on_behalf')
            settings.get('box_paths.email_template')
        """
        keys = key_path.split('.')
        value = self._settings

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_full_path(self, path_type, key_path):
        """
        Get a full path by combining base path from .env with relative path from settings.yaml.

        Args:
            path_type (str): Either 'box' or 'project' to indicate which base path to use
            key_path (str): Dot-separated path to the relative path in settings.yaml

        Returns:
            str: Full constructed path

        Example:
            settings.get_full_path('box', 'box_paths.email_template')
            settings.get_full_path('project', 'project_paths.temp_pdf')
        """
        if path_type == 'box':
            base_path = self._env.get('BOX_ATI_BASE_PATH', '')
        elif path_type == 'project':
            base_path = self._env.get('PROJECT_BASE_PATH', '')
        else:
            raise ValueError(f"Invalid path_type: {path_type}. Must be 'box' or 'project'")

        relative_path = self.get(key_path, '')
        return os.path.join(base_path, relative_path)

    @property
    def all_settings(self):
        """Return all settings as a dictionary."""
        return self._settings

    @property
    def env_vars(self):
        """Return all environment variables as a dictionary."""
        return self._env


# Create a singleton instance for easy import
settings = Settings()


# Convenience functions for common paths
def get_database_path():
    """Get the database file path."""
    return settings.get('database.filename')


def get_box_path(relative_key):
    """
    Get a full Box path.

    Args:
        relative_key (str): Key from box_paths section (e.g., 'email_template')

    Returns:
        str: Full path to the Box resource
    """
    return settings.get_full_path('box', f'box_paths.{relative_key}')


def get_project_path(relative_key):
    """
    Get a full project path.

    Args:
        relative_key (str): Key from project_paths section (e.g., 'temp_pdf')

    Returns:
        str: Full path to the project resource
    """
    return settings.get_full_path('project', f'project_paths.{relative_key}')


if __name__ == '__main__':
    # Test the configuration loading
    print("Environment Variables:")
    print(f"  BOX_ATI_BASE_PATH: {settings.env_vars['BOX_ATI_BASE_PATH']}")
    print(f"  PROJECT_BASE_PATH: {settings.env_vars['PROJECT_BASE_PATH']}")
    print()
    print("Sample Settings:")
    print(f"  Database: {get_database_path()}")
    print(f"  Send on behalf email: {settings.get('email.send_on_behalf')}")
    print()
    print("Sample Full Paths:")
    print(f"  Box email template: {get_box_path('email_template')}")
    print(f"  Project temp PDF: {get_project_path('temp_pdf')}")
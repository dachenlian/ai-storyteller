import importlib.util
import os


# Helper function to check if a module can be imported
def _is_module_available(module_name: str) -> bool:
    """Checks if a Python module is available for import."""
    spec = importlib.util.find_spec(module_name)
    return spec is not None


def _get_from_colab(key_name: str) -> str | None:
    """Tries to get the specified environment variable from Google Colab userdata."""
    if not _is_module_available("google.colab"):
        return None

    from google.colab import userdata  # type: ignore

    return userdata.get(key_name)


def _get_from_kaggle(key_name: str) -> str | None:
    """Tries to get the specified environment variable from Kaggle secrets."""
    if not _is_module_available("kaggle_secrets"):
        return None

    try:
        from kaggle_secrets import UserSecretsClient  # type: ignore

        user_secrets = UserSecretsClient()
        return user_secrets.get_secret(key_name)
    except Exception:  # Catch potential errors from get_secret itself
        return None


def _get_from_env(key_name: str) -> str | None:
    """Tries to get the specified environment variable from environment variables (optionally using python-dotenv)."""
    if _is_module_available("dotenv"):
        from dotenv import load_dotenv  # type: ignore

        # Load .env file, overriding existing environment variables if present
        load_dotenv(override=True)
    # Always try os.getenv, as dotenv just loads vars into the environment
    return os.getenv(key_name)


def get_env_var(key_name: str) -> str:
    """
    Retrieves the specified environment variable from various sources in order of preference:
    1. Google Colab userdata
    2. Kaggle secrets
    3. Environment variables (optionally loaded from .env file)

    Raises:
        ValueError: If the specified environment variable cannot be found in any source.

    Returns:
        The found environment variable value.
    """
    # Define the order of strategies to try
    strategies = [
        _get_from_colab,
        _get_from_kaggle,
        _get_from_env,
    ]

    env_value: str | None = None
    for strategy in strategies:
        try:
            key = strategy(key_name)  # Call the strategy function
            if key:  # Check if key is not None and not an empty string
                env_value = key
                print(f"Found {key_name} using strategy: {strategy.__name__}")
                break  # Key found, stop searching
        except Exception:
            # Log or print a warning if needed, e.g., about Kaggle get_secret failure
            # print(f"Warning: Strategy {strategy.__name__} failed: {e}")
            continue  # Try the next strategy

    if env_value is None:
        raise ValueError(  # Using ValueError might be more semantically correct than ImportError
            f"{key_name} not found. Please set it in Colab/Kaggle secrets "
            "or as an environment variable (e.g., in a .env file)."
        )

    return env_value

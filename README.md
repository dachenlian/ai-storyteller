# ai-storyteller

# AI Storyteller

[Brief description of your project]

## Prerequisites

* **uv:** The fast Python package installer and resolver. Install it [here](https://docs.astral.sh/uv/getting-started/installation/).

## Installation and Setup

1. **Clone the Repository (with Submodules):**

    It's crucial to clone the repository along with its Git submodules, which contain necessary external components. Use the `--recurse-submodules` flag:

    ```bash
    git clone --recurse-submodules https://github.com/dachenlian/ai-storyteller.git 
    cd ai-storyteller
    ```

    * **If you already cloned without submodules:** Navigate into the repository directory and run:

        ```bash
        git submodule update --init --recursive
        ```

2. **Install Dependencies using `uv`:**

    `uv` will install the required Python packages based on `pyproject.toml` (and potentially `requirements.txt`). Make sure your submodules are checked out (Step 1) before running this. If any submodules *are* Python packages specified via a local path in `pyproject.toml`, `uv` will handle their installation from that local path.

    ```bash
    # Ensure you are in the project root directory (ai_storyteller/)
    # Make sure your virtual environment is active

    # Install dependencies specified in pyproject.toml / requirements.txt
    uv pip sync # Use this if you have a requirements.lock or pyproject.toml with pinned versions
    # OR if using requirements files:
    # uv pip install -r requirements.txt
    # OR if installing directly from pyproject.toml without lock file:
    # uv pip install .
    ```

    *(Choose the `uv` command that best fits your dependency management strategy - `uv pip sync` is common if using lock files generated by `uv pip compile`)*

    * **Note:** If a submodule *is* a Python package but *not* listed as a local path dependency in `pyproject.toml`, you might need to install it explicitly after updating submodules:

        ```bash
        # Example: Only run if needed and documented for your specific setup
        # uv pip install -e ./vendor/my-submodule-package
        ```

3. **Set Up Environment Variables:**

    The application requires API keys and potentially other configuration settings stored in environment variables.

    * Copy the example environment file:

        ```bash
        cp .env.example .env
        ```

    * Edit the `.env` file and fill in your actual API keys and any other required values (e.g., `GEMINI_API_KEY`, `OPENAI_API_KEY`, etc.).
    * **Important:** The `.env` file contains sensitive information and should **never** be committed to Git. Ensure `.env` is listed in your `.gitignore` file.

## Running the Application

Once installation is complete and your `.env` file is configured:

```bash
# Ensure your virtual environment is active
uv run python src/ai_storyteller/main.py

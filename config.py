import os
import json
from pathlib import Path
import sys
from dotenv import load_dotenv
import argparse

load_dotenv()


def get_claude_config_path() -> Path | None:
    """Get the Claude config directory based on platform."""
    if sys.platform == "win32":
        path = Path(Path.home(), "AppData", "Roaming", "Claude")
    elif sys.platform == "darwin":
        path = Path(Path.home(), "Library", "Application Support", "Claude")
    elif sys.platform.startswith("linux"):
        path = Path(
            os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"), "Claude"
        )
    else:
        return None

    if path.exists():
        return path
    return None


def get_python_path():
    return sys.executable


def generate_config(api_key: str | None = None):
    module_dir = Path(__file__).resolve().parent
    server_path = module_dir / "server.py"
    python_path = get_python_path()

    final_api_key = api_key or os.environ.get("GROQ_API_KEY")
    if not final_api_key:
        print("Error: Groq API key is required.")
        print("Please either:")
        print("  1. Pass the API key using --api-key argument, or")
        print("  2. Set the GROQ_API_KEY environment variable, or")
        print("  3. Add GROQ_API_KEY to your .env file")
        sys.exit(1)

    config = {
        "mcpServers": {
            "Groq": {
                "command": python_path,
                "args": [
                    str(server_path),
                ],
                "env": {
                    "GROQ_API_KEY": final_api_key,
                    # Optional: Add any other env vars needed
                    "BASE_OUTPUT_PATH": str(Path.home() / "Desktop"),  # Default output path
                },
            }
        }
    }

    return config


def update_antigravity_config(api_key: str):
    """Update Antigravity CLI configuration file if the application directory exists."""
    antigravity_dir = Path(Path.home(), ".gemini", "antigravity-cli")
    if not antigravity_dir.exists():
        return

    mcp_json_path = antigravity_dir / "mcp.json"
    
    module_dir = Path(__file__).resolve().parent
    server_path = module_dir / "server.py"
    python_path = get_python_path()
    
    # Read existing config or initialize
    if mcp_json_path.exists():
        try:
            with open(mcp_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to read Antigravity config: {e}. Reinitializing...")
            data = {}
    else:
        data = {}

    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        data["mcpServers"] = {}

    # Update groq-mcp configuration
    data["mcpServers"]["groq-mcp"] = {
        "command": python_path,
        "args": [str(server_path)],
        "cwd": str(module_dir),
        "env": {
            "GROQ_API_KEY": api_key,
            "BASE_OUTPUT_PATH": str(Path.home() / "Desktop"),
        }
    }

    try:
        with open(mcp_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully updated Antigravity config at {mcp_json_path}")
    except Exception as e:
        print(f"Warning: Failed to write Antigravity config: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Groq MCP server config for Claude")
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print config to screen instead of writing to file",
    )
    parser.add_argument(
        "--api-key",
        help="Groq API key (alternatively, set GROQ_API_KEY environment variable)",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        help="Custom path to Claude config directory",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        help="Custom path for output files (default: ~/Desktop)",
    )
    args = parser.parse_args()

    # Get API key to pass to config generator and Antigravity updater
    final_api_key = args.api_key or os.environ.get("GROQ_API_KEY")
    config = generate_config(args.api_key)

    if args.print:
        print(json.dumps(config, indent=2))
    else:
        claude_path = args.config_path if args.config_path else get_claude_config_path()
        if claude_path is not None:
            claude_path.mkdir(parents=True, exist_ok=True)
            config_file = claude_path / "claude_desktop_config.json"
            print(f"Writing config to {config_file}")
            try:
                # Merge into existing Claude config if it exists
                if config_file.exists():
                    with open(config_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                else:
                    existing = {}
                
                if "mcpServers" not in existing or not isinstance(existing["mcpServers"], dict):
                    existing["mcpServers"] = {}
                
                existing["mcpServers"].update(config["mcpServers"])
                
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(existing, f, indent=2)
                print(f"Successfully updated Claude config at {config_file}")
            except Exception as e:
                print(f"Warning: Failed to write Claude config: {e}")
        else:
            print("Could not find Claude config path automatically.")

        # Also update Antigravity config if available
        if final_api_key:
            update_antigravity_config(final_api_key)
 
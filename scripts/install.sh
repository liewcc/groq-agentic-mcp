#!/bin/bash
uv run mcp install server.py --with python-dotenv --with rapidfuzz --with sounddevice --with soundfile --with-editable . -f .env

# Run config.py to update Claude and Antigravity configs
echo "Updating configuration files (Claude Desktop & Antigravity)..."
uv run python config.py
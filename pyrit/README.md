# pyrit-demo

This directory contains a sample PyRIT implementation to run a red teaming and prompt attack against an LLM endpoint.

## Quickstart

```bash
# Create a new virtual env
python3 -m venv .venv

# Activate virtual env
source .venv/bin/activate

# Install packages
pip install pyrit dotenv pyyaml

# Option 1: Run red team scan via CLI
python gandalf-attack.py

# Option 2: Run script using VS Code
# View gandalf-attack.py in VS Code and launch with F5
```

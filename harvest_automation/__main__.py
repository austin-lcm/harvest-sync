"""
Allow `python -m harvest_automation` as a convenience wrapper around the Typer
CLI defined in harvest_automation.cli:app
"""
from .cli import app

if __name__ == "__main__":  # pragma: no cover
    app()
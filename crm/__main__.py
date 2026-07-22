"""Punto de entrada: `python -m crm <texto>`."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())

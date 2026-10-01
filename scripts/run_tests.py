#!/usr/bin/env python3
"""Run all unit and integration tests using pytest."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Execute test suite."""
    project_root = Path(__file__).resolve().parent.parent
    cmd = [sys.executable, "-m", "pytest", "-v"]
    print(f"Running test suite from {project_root}...")
    result = subprocess.run(cmd, cwd=project_root)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

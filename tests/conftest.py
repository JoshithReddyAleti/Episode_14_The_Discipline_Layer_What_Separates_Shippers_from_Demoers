"""Test fixtures and configuration."""
import sys
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

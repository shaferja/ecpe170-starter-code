"""Plot saved Case A baseline evidence."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from plotting import main

if __name__ == "__main__":
    main("A")

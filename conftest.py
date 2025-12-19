# conftest.py (project root)
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# add src/ to Python path
sys.path.insert(0, str(SRC))

# add project root to Python path
sys.path.insert(0, str(ROOT))

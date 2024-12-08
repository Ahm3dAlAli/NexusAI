import sys
import os
from pathlib import Path

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

# Now import from evaluate directory
from evaluate.main import main

if __name__ == "__main__":
    main()

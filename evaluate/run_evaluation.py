# evaluate/run_evaluation.py
import sys
import os
from pathlib import Path

def setup_python_path():
    # Get the absolute path of the project root directory (one level up from this script)
    root_dir = Path(__file__).resolve().parent.parent
    # Add the project root to Python path so we can import from other directories
    sys.path.insert(0, str(root_dir))

def main():
    setup_python_path()
    # Now we can import from the evaluate directory
    from evaluate.main import main as evaluate_main
    evaluate_main()

if __name__ == "__main__":
    main()
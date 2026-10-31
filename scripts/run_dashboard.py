import subprocess
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    app_path = BASE_DIR / "dashboard" / "app.py"
    print(f"Launching Streamlit Dashboard from {app_path} ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8501", "--server.headless", "true"])

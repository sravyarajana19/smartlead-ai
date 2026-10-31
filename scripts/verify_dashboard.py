import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dashboard.components.data_loader import load_all_dashboard_data


def main():
    print("Verifying Streamlit Dashboard Data Loader...")
    data = load_all_dashboard_data()
    for table, df in data.items():
        print(f"  * {table:<22}: {len(df):>7,} rows")

    print("\nVerifying Dashboard page files exist and are well-formed...")
    pages_dir = BASE_DIR / "dashboard" / "pages"
    page_files = sorted(list(pages_dir.glob("*.py")))
    assert len(page_files) == 12, f"Expected 12 pages, found {len(page_files)}"

    for pf in page_files:
        with open(pf, "r", encoding="utf-8") as f:
            code = f.read()
        compile(code, str(pf), "exec")
        print(f"  [OK] {pf.name}")

    print("\nAll 12 Streamlit dashboard pages compiled and verified successfully!")


if __name__ == "__main__":
    main()

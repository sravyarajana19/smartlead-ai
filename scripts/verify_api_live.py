import time
import threading
import sys
from pathlib import Path
import urllib.request
import json
import uvicorn

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def test_endpoint(url: str, name: str):
    req = urllib.request.urlopen(url, timeout=5)
    data = json.loads(req.read().decode("utf-8"))
    print(f"[{req.status}] {name}: Success!")
    return data


def main():
    print("Launching FastAPI server in test thread...")
    thread = ServerThread()
    thread.daemon = True
    thread.start()

    time.sleep(2)

    try:
        health = test_endpoint("http://127.0.0.1:8000/health", "Health Check")
        assert health["status"] == "healthy"

        metrics = test_endpoint("http://127.0.0.1:8000/api/dashboard/metrics", "Dashboard Metrics")
        assert metrics["total_leads"] == 20000
        print(f"  * Total Leads: {metrics['total_leads']:,}")
        print(f"  * Conversion Rate: {metrics['conversion_rate']}%")
        print(f"  * Won Revenue: ${metrics['won_revenue']:,.2f}")

        exceptions = test_endpoint("http://127.0.0.1:8000/api/exceptions", "Exception Records")
        assert exceptions["total_anomalies"] == 50
        print(f"  * Total Detected Anomalies: {exceptions['total_anomalies']}")

        rules = test_endpoint("http://127.0.0.1:8000/api/scoring/rules", "Scoring Rules")
        assert len(rules) > 0

        print("\nAll live REST API endpoints verified successfully!")
    finally:
        thread.stop()


if __name__ == "__main__":
    main()

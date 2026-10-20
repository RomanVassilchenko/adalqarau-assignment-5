"""Check the loopback test deployment returns the exact expected CSV."""

import time
import urllib.error
import urllib.request
from pathlib import Path


def main():
    expected = Path("/app/testdata/expected-yearly-summary.csv").read_bytes()
    request = urllib.request.Request("http://127.0.0.1:18081/summary.csv")
    for attempt in range(20):
        try:
            with urllib.request.urlopen(request, timeout=1) as response:
                actual = response.read()
            break
        except (OSError, urllib.error.URLError):
            if attempt == 19:
                raise
            time.sleep(0.5)
    if actual != expected:
        raise SystemExit("deployed summary does not match expected CSV")
    print("HTTP smoke check passed: deployed summary matches expected CSV")


if __name__ == "__main__":
    main()

import json
from pathlib import Path
from src.read_sheet import get_request_for_days_away

OUT = Path("pending_request.json")

def main():
    req = get_request_for_days_away(days_away=3)

    if not req:
        OUT.write_text(json.dumps({"found": False}, indent=2))
        print("No request found for day+3.")
        return

    OUT.write_text(json.dumps({"found": True, "request": req}, indent=2))
    print("Prefetched booking:", req)

if __name__ == "__main__":
    main()

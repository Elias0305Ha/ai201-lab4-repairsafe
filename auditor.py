import json
import os
from datetime import datetime, timezone
from config import LOG_FILE


def log_interaction(question: str, tier: str, response: str) -> None:
    """
    Append a structured record of this interaction to the audit log (JSONL).
    """

    # --- 1. Make sure the logs/ folder exists before writing ---
    log_dir = os.path.dirname(LOG_FILE)   # "logs" from "logs/audit.jsonl"
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # --- 2. Build the record (one dict = one log line) ---
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tier": tier,
        "question": question[:300],
        "response_preview": response[:200],
    }

    # --- 3. Append it as a single line of JSON ---
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    # --- 4. Print a one-line summary to the terminal ---
    print(f"[{tier}] {question[:60]}...")
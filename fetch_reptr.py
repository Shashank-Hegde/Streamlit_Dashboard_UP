import requests
import csv
import json
import time
import re
from pathlib import Path

URL = "https://prod.o-health.in/api/v2/admin/getCompleteReport"
OUTPUT_CSV = "report_v2_Balrampur_jan16_feb2.csv"

TIMEOUT = 20
SLEEP_BETWEEN = 0.25
RETRIES = 2

LIST_RAW = """
6636-7916
"""

def parse_ids(raw: str):
    ids, seen = [], set()
    tokens = re.split(r"[,\s]+", raw.strip())
    dash = r"[-–—]"

    for tok in tokens:
        if not tok:
            continue
        # Range like 11-1135 (supports hyphen/en/em dashes)
        if re.fullmatch(rf"\d+{dash}\d+", tok):
            a_s, b_s = re.split(dash, tok)
            a, b = int(a_s), int(b_s)
            if a > b:
                a, b = b, a
            # sanity cap to avoid gigantic expansions by mistake
            if b - a > 500_000:
                print(f"⚠️ Skipping suspiciously large range: {tok}")
                continue
            for n in range(a, b + 1):
                if n not in seen:
                    seen.add(n)
                    ids.append(n)
            continue
        # Standalone integer
        if re.fullmatch(r"\d+", tok):
            n = int(tok)
            if n not in seen:
                seen.add(n)
                ids.append(n)
            continue
        # else ignore tokens with letters/mixed content
    return ids

REPORT_IDS = parse_ids(LIST_RAW)

HEADERS = {
    "Content-Type": "application/json",
    # add auth headers here if your dev server requires them, e.g.:
    # "Authorization": "Bearer <TOKEN>"
}

def _post(payload):
    r = requests.post(URL, json=payload, headers=HEADERS, timeout=TIMEOUT)
    # raise for 4xx/5xx so we trigger retries/fallback
    r.raise_for_status()
    return r

def fetch_report(assessment_id: int):
    """
    Primary:      {'assessment_id': id}  <-- v2 expects this (works in Postman)
    Compatibility: if it fails, retry once with {'reportId': id}
    """
    last_err = None
    # try with assessment_id first
    for attempt in range(1, RETRIES + 1):
        try:
            r = _post({"assessment_id": assessment_id})
            return r.json()
        except requests.RequestException as e:
            last_err = e
            if attempt < RETRIES:
                time.sleep(0.5)
            else:
                # fallback exactly once with legacy key
                try:
                    r2 = _post({"reportId": assessment_id})
                    return r2.json()
                except requests.RequestException as e2:
                    # print server message bodies if available
                    resp_text = ""
                    if hasattr(e, "response") and e.response is not None:
                        try:
                            resp_text = e.response.text
                        except Exception:
                            pass
                    resp_text2 = ""
                    if hasattr(e2, "response") and e2.response is not None:
                        try:
                            resp_text2 = e2.response.text
                        except Exception:
                            pass
                    print(f"❌ Skipped id {assessment_id}: primary error={e}; resp={resp_text[:300]}")
                    print(f"   ↳ Fallback error={e2}; resp={resp_text2[:300]}")
                    return None

def main():
    print(f"Total unique report IDs to fetch: {len(REPORT_IDS)}")
    file_exists = Path(OUTPUT_CSV).exists()
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["report_json"])
        for idx, assessment_id in enumerate(REPORT_IDS, 1):
            data = fetch_report(assessment_id)
            if data is not None:
                writer.writerow([json.dumps(data, ensure_ascii=False)])
                print(f"✅ Saved id {assessment_id}  ({idx}/{len(REPORT_IDS)})")
            time.sleep(SLEEP_BETWEEN)

if __name__ == "__main__":
    main()

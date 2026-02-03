import pandas as pd
import json

INPUT_CSV  = "rpt_field_v2_Balrampur_jan16_feb2_with_specialist.csv"
OUTPUT_CSV = "repore_v2_Balrampur_jan16_feb2_with_specialist_and_assoc.csv"

def parse_list_cell(cell):
    """Parse a CSV cell into a list of strings. Supports JSON list or comma-separated text."""
    if cell is None or (isinstance(cell, float) and pd.isna(cell)):
        return []
    s = str(cell).strip()
    if not s:
        return []
    # Try JSON list
    try:
        v = json.loads(s)
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        # if somehow a single string stored as JSON
        if isinstance(v, str) and v.strip():
            return [v.strip()]
    except Exception:
        pass

    # Fallback: comma-separated
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        return [p for p in parts if p]
    return [s]

def normalize(x: str) -> str:
    return str(x).strip().lower()

def to_json_list_str(lst):
    """Store back as JSON string list (or empty string for null)."""
    if not lst:
        return ""
    return json.dumps(lst, ensure_ascii=False)

def main():
    df = pd.read_csv(INPUT_CSV, dtype=str)

    if "symptoms" not in df.columns or "initial_symptom" not in df.columns:
        raise ValueError("CSV must contain columns: symptoms, initial_symptom")

    associated_col = []

    for _, row in df.iterrows():
        symptoms = parse_list_cell(row.get("symptoms"))
        initial = parse_list_cell(row.get("initial_symptom"))

        # Rule: if initial_symptom is null/empty -> associated_symptom must be null
        if not initial:
            associated_col.append("")
            continue

        # Compute set difference (symptoms - initial_symptom)
        init_set = {normalize(x) for x in initial}
        assoc = [x for x in symptoms if normalize(x) not in init_set]

        # If both are same or nothing left -> null
        associated_col.append(to_json_list_str(assoc))

    df["associated_symptom"] = associated_col
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved: {OUTPUT_CSV} | rows: {len(df)}")

if __name__ == "__main__":
    main()

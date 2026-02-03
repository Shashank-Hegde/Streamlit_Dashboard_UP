import pandas as pd
import json

INPUT_CSV  = "report_v2_Balrampur_jan16_feb2.csv"
OUTPUT_CSV = "rpt_field_v2_Balrampur_jan16_feb2.csv"

def safe_json_loads(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        try:
            s2 = s.encode("utf-8", "ignore").decode("unicode_escape")
            return json.loads(s2)
        except Exception:
            return None

def first_non_null(*vals):
    for v in vals:
        if v is not None and v != "":
            return v
    return None

df = pd.read_csv(INPUT_CSV, header=None, dtype=str)
col0 = df.columns[0]

rows = []
for raw in df[col0].tolist():
    obj = safe_json_loads(raw)
    if not isinstance(obj, dict):
        continue

    if obj.get("hospital_id") != 6:
        continue

    final_report = obj.get("final_report", {}) or {}
    additional_info = final_report.get("additional_info", {}) or {}

    lifestyle_factors = final_report.get("lifestyle_factors", "")

    age = first_non_null(
        obj.get("age"),
        additional_info.get("age")
    )

    gender = obj.get("gender", "")   # 👈 gender extracted here

    def to_json_str(v):
        return "" if v is None else json.dumps(v, ensure_ascii=False)

    rows.append({
        "raw_json": raw,
        "lifestyle_factors": lifestyle_factors,
        "age": age if age is not None else "",
        "gender": gender,             # 👈 added column
        "symptoms": to_json_str(final_report.get("symptoms")),
        "symptom_duration": to_json_str(final_report.get("symptom_duration")),
        "initial_symptom": to_json_str(final_report.get("initial_symptom")),
    })

out = pd.DataFrame(rows, columns=[
    "raw_json",
    "lifestyle_factors",
    "age",
    "gender",
    "symptoms",
    "symptom_duration",
    "initial_symptom",
])

out.to_csv(OUTPUT_CSV, index=False)

print(f"Saved: {OUTPUT_CSV} | rows: {len(out)}")
print("\nGender distribution:")
print(out["gender"].value_counts(dropna=False))

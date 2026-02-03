import json
import pandas as pd
from collections import Counter, defaultdict
import numpy as np

# ---------------- CONFIG ----------------
INPUT_CSV = "repore_v2_Balrampur_jan16_feb2_with_specialist.csv"

# Columns expected:
# raw_json, lifestyle_factors, age, gender, symptoms, symptom_duration, initial_symptom, suggested_specialist

# ---------------- HELPERS ----------------
def parse_jsonish(cell):
    """Parse list/dict stored as JSON string; if plain string, return it; if empty -> None."""
    if cell is None or (isinstance(cell, float) and pd.isna(cell)):
        return None
    s = str(cell).strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s

def as_list(x):
    """Normalize values into a list of strings when possible."""
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i).strip() for i in x if str(i).strip()]
    if isinstance(x, dict):
        return [str(k).strip() for k in x.keys() if str(k).strip()]
    s = str(x).strip()
    if not s:
        return []
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        parts = [p for p in parts if p]
        if parts:
            return parts
    return [s]

def normalize_symptom(s):
    """Light normalization (lowercase + trim)."""
    return str(s).strip().lower()

def safe_int(x):
    try:
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return None
        s = str(x).strip()
        if not s:
            return None
        return int(float(s))
    except Exception:
        return None

def compute_associated(symptoms_list, initial_list):
    """
    associated_symptom = symptoms - initial_symptom
    Rules:
      - if initial_symptom is null/empty => associated is null (return [])
      - if both are same / subtraction empty => return []
    """
    if not initial_list:
        return []
    init_set = {normalize_symptom(x) for x in initial_list if str(x).strip()}
    assoc = [s for s in symptoms_list if normalize_symptom(s) not in init_set]
    return assoc

# ---------------- MAIN ----------------
def main():
    df = pd.read_csv(INPUT_CSV, dtype=str)

    # Counters
    symptoms_freq = Counter()
    initial_symptoms_freq = Counter()
    associated_symptoms_freq = Counter()
    specialists_freq = Counter()
    gender_freq = Counter()
    ages = []

    # Symptom duration mapping: symptom -> Counter(duration_string)
    symptom_duration_map = defaultdict(Counter)

    # Associated symptom duration mapping
    associated_duration_map = defaultdict(Counter)

    for _, row in df.iterrows():
        # ---- Symptoms frequency ----
        symptoms = as_list(parse_jsonish(row.get("symptoms")))
        symptoms_norm = [normalize_symptom(s) for s in symptoms]
        symptoms_freq.update([s for s in symptoms_norm if s])

        # ---- Initial symptoms frequency ----
        init_sym = as_list(parse_jsonish(row.get("initial_symptom")))
        init_norm = [normalize_symptom(s) for s in init_sym]
        initial_symptoms_freq.update([s for s in init_norm if s])

        # ---- Associated symptoms (computed) ----
        assoc_sym = compute_associated(symptoms, init_sym)
        assoc_norm = [normalize_symptom(s) for s in assoc_sym]
        associated_symptoms_freq.update([s for s in assoc_norm if s])

        # ---- Symptom duration mapping ----
        sd = parse_jsonish(row.get("symptom_duration"))
        if isinstance(sd, dict):
            for k, v in sd.items():
                sym = normalize_symptom(k)
                dur = str(v).strip()
                if sym and dur:
                    symptom_duration_map[sym].update([dur])

            # ---- Associated duration mapping (only for associated symptoms) ----
            assoc_set = set(assoc_norm)
            for k, v in sd.items():
                sym = normalize_symptom(k)
                dur = str(v).strip()
                if sym in assoc_set and dur:
                    associated_duration_map[sym].update([dur])

        # ---- Specialists frequency ----
        spec_raw = row.get("suggested_specialist")
        specialist = str(spec_raw).strip() if pd.notna(spec_raw) else ""
        if specialist:
            specialists_freq.update([specialist])

        # ---- Gender frequency ----
        gender_raw = row.get("gender")
        gender = str(gender_raw).strip() if pd.notna(gender_raw) else ""
        if not gender:
            gender = "(missing)"
        gender_freq.update([gender])

        # ---- Age stats ----
        age = safe_int(row.get("age"))
        if age is not None:
            ages.append(age)

    # ---------------- PRINTS ----------------
    print("\n==================== STATS ====================\n")

    # 1) symptoms frequency
    print("1) Symptoms frequency (top 50):")
    for sym, cnt in symptoms_freq.most_common(50):
        print(f"  {sym}: {cnt}")
    print(f"\n  Total unique symptoms: {len(symptoms_freq)}\n")

    # 2) symptoms and durations
    print("2) Symptoms and durations (top 30 symptoms; top 5 durations each):")
    sym_by_dur = sorted(symptom_duration_map.items(), key=lambda kv: sum(kv[1].values()), reverse=True)
    for sym, dur_counter in sym_by_dur[:30]:
        total = sum(dur_counter.values())
        top_durs = ", ".join([f"{d}({c})" for d, c in dur_counter.most_common(5)])
        print(f"  {sym}: total={total} | {top_durs}")
    if not sym_by_dur:
        print("  (No per-symptom duration dicts found in symptom_duration column.)")
    print()

    # 3) specialists frequency
    print("3) Specialists frequency:")
    for sp, cnt in specialists_freq.most_common():
        print(f"  {sp}: {cnt}")
    if not specialists_freq:
        print("  (No suggested_specialist values found.)")
    print()

    # 4) age statistics
    print("4) Age statistics:")
    if ages:
        ages_arr = np.array(ages, dtype=float)
        print(f"  Count: {len(ages)}")
        print(f"  Min: {int(np.min(ages_arr))}")
        print(f"  Max: {int(np.max(ages_arr))}")
        print(f"  Mean: {np.mean(ages_arr):.2f}")
        print(f"  Median: {np.median(ages_arr):.2f}")
        bins = [(0,12),(13,17),(18,29),(30,44),(45,59),(60,74),(75,120)]
        bucket_counts = {}
        for lo, hi in bins:
            bucket_counts[f"{lo}-{hi}"] = int(((ages_arr >= lo) & (ages_arr <= hi)).sum())
        print("  Buckets:")
        for k, v in bucket_counts.items():
            print(f"    {k}: {v}")
    else:
        print("  (No ages found.)")
    print()

    # 5) gender frequency
    print("5) Gender frequency:")
    for g, cnt in gender_freq.most_common():
        print(f"  {g}: {cnt}")
    print()

    # 6) initial symptoms frequency
    print("6) Initial symptoms frequency (top 50):")
    for sym, cnt in initial_symptoms_freq.most_common(50):
        print(f"  {sym}: {cnt}")
    print(f"\n  Total unique initial symptoms: {len(initial_symptoms_freq)}\n")

    # 7) associated symptoms frequency (NEW)
    print("7) Associated symptoms frequency (top 50):")
    for sym, cnt in associated_symptoms_freq.most_common(50):
        print(f"  {sym}: {cnt}")
    print(f"\n  Total unique associated symptoms: {len(associated_symptoms_freq)}\n")

    # 8) associated symptoms durations (NEW)
    print("8) Associated symptoms and durations (top 30; top 5 durations each):")
    assoc_by_dur = sorted(associated_duration_map.items(), key=lambda kv: sum(kv[1].values()), reverse=True)
    for sym, dur_counter in assoc_by_dur[:30]:
        total = sum(dur_counter.values())
        top_durs = ", ".join([f"{d}({c})" for d, c in dur_counter.most_common(5)])
        print(f"  {sym}: total={total} | {top_durs}")
    if not assoc_by_dur:
        print("  (No associated symptom duration pairs found in symptom_duration dicts.)")
    print()

    print("==================== DONE =====================\n")


if __name__ == "__main__":
    main()

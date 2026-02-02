import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="O-Health | Triage Insights Dashboard",
    page_icon="🩺",
    layout="wide",
)

# ---------------- DATA (FROM YOUR STATS) ----------------
symptoms_freq = {
    "fever": 50, "headache": 47, "stomach pain": 42, "weakness": 39, "kidney issue": 37,
    "insomnia": 30, "head pain": 29, "cough": 28, "vomiting": 26, "dizziness": 25,
    "cold": 24, "shortness of breath": 23, "nausea": 22, "chest pain": 21,
    "high blood pressure": 20, "leg pain": 18, "chills": 17, "balance problem": 17,
    "operation": 17, "anxiety": 17, "back pain": 15, "stress": 15, "gas": 14,
    "body pain": 14, "animal bite": 14, "hand pain": 13, "urine issue": 13,
    "loss of appetite": 12, "bloating": 11, "confusion": 11, "knee pain": 11,
    "swelling": 11, "injury": 10, "diabetes": 10, "tooth pain": 10, "infection": 9,
    "itching": 9, "runny nose": 8, "increased appetite": 8, "sore throat": 8,
    "neck pain": 8, "rash": 8, "arthritis": 7, "joint pain": 7, "sugar": 7,
    "fatigue": 7, "hand swelling": 6, "weight loss": 6, "tingling": 6, "fainting": 6
}
total_unique_symptoms = 191

# Symptom duration snippet you posted (only those present)
symptom_duration_map = {
    "kidney issue": {"2 years": 4, "96 years": 1, "4 years": 1, "2 days": 1, "3 months": 1},
    "cough": {"2 days": 2, "6 months": 2, "20 days": 1, "2 years": 1, "4 days": 1},
    "stomach pain": {"3 months": 3, "3 days": 1, "1 week": 1, "2 days": 1, "20 days": 1},
    "fever": {"3 months": 2, "6 months": 1, "4 days": 1, "2 days": 1, "25 years": 1},
    "headache": {"2 years": 2, "2 months": 1, "5 years": 1, "3 years": 1, "3 months": 1},
    "insomnia": {"8 months": 2, "3 years": 2, "4 years": 1, "17 years": 1},
    "back pain": {"4 years": 1, "8 years": 1, "3 day": 1, "5 months": 1, "3 months": 1},
    "swelling": {"3 years": 1, "8 months": 1, "2 days": 1, "5 months": 1, "2 weeks": 1},
    "weakness": {"4 days": 2, "6 months": 1, "10 days": 1, "20 years": 1},
    "chest pain": {"8 days": 1, "for a week": 1, "6 months": 1, "7 days": 1, "7 months": 1},
    "cold": {"4 months": 2, "6 years": 1, "3 years": 1, "4 years": 1},
    "head pain": {"6 months": 1, "2 months": 1, "2 years": 1, "4 days": 1},
    "anxiety": {"4 years": 1, "2 years": 1, "5 years": 1, "6 months": 1},
    "diabetes": {"10 years": 1, "2 years": 1, "3 years": 1, "2 weeks": 1},
    "head hurts": {"26 years": 1, "4 years": 1, "4 months": 1},
    "confusion": {"3 days": 1, "2 years": 1, "14 years": 1},
    "shortness of breath": {"2 days": 1, "15 days": 1, "2 months": 1},
    "bloating": {"12 years": 1, "3 months": 1, "4 months": 1},
    "leg pain": {"4 months": 1, "5 months": 1, "1 month": 1},
    "tooth pain": {"3 years": 1, "4 days": 1, "3 months": 1},
    "infection": {"3 months": 2, "6 months": 1},
    "stomach hurts": {"4 days": 1, "1 day": 1},
    "gas": {"3 days": 1, "6 years": 1},
    "knee pain": {"4 days": 1, "3 days": 1},
    "tingling": {"2 months": 1, "3 years": 1},
    "urine issue": {"4 months": 1, "6 months": 1},
    "hand pain": {"4 months": 1, "6 months": 1},
    "rash": {"20 days": 1, "3 months": 1},
    "liver issue": {"5 years": 1},
    "arthritis": {"3 year": 1},
}

specialists_freq = {
    "General Medicine": 166, "Orthopedic specialist": 45, "Neurology": 40, "Nephrologist": 37,
    "Psychiatry": 32, "Gastroenterology": 32, "Dermatology": 28, "Pulmonology": 23,
    "Cardiology": 19, "Ophthalmologist": 17, "ENT": 15, "Dentist": 12, "General Surgery": 10,
    "Endocrinology": 8, "Urology": 8, "Hepatologist": 4, "Allergy & Immunology": 3,
    "Internal Medicine": 2, "Andrology": 1, "Gynecology": 1, "Neurosurgery": 1
}

age_buckets = {
    "0-12": 76, "13-17": 28, "18-29": 99, "30-44": 125, "45-59": 92, "60-74": 52, "75-120": 5
}

gender_freq_raw = {"F": 220, "M": 210, "(missing)": 73, "male": 1}

initial_symptoms_freq = {
    "kidney issue": 35, "headache": 31, "stomach pain": 27, "fever": 24, "cough": 22,
    "dizziness": 21, "swelling": 20, "insomnia": 19, "back pain": 18, "shortness of breath": 16,
    "high blood pressure": 15, "leg pain": 15, "animal bite": 15, "vomiting": 13, "weakness": 13,
    "chest pain": 13, "head pain": 11, "operation": 11, "gas": 10, "injury": 10, "cold": 10,
    "stress": 10, "urine issue": 10, "anxiety": 9, "hand pain": 9, "infection": 9, "itching": 9,
    "tooth pain": 9, "confusion": 8, "knee pain": 8, "nausea": 8, "diabetes": 8, "neck pain": 8,
    "rash": 8, "body pain": 6, "joint pain": 5, "arthritis": 5, "tingling": 5, "waist pain": 5,
    "ear pain": 5, "loss of appetite": 5, "sugar": 5, "head hurts": 5, "fainting": 5, "eye issue": 5,
    "skin issue": 5, "liver issue": 4, "nervousness": 4, "head injury": 4, "tremor": 4
}
total_unique_initial_symptoms = 192

# Summary stats
age_count = 477
age_min = 0
age_max = 95
age_mean = 33.58
age_median = 35.00

total_rows = 504  # from your run "Processing row 1 / 504"

# ---------------- NORMALIZATIONS ----------------
gender_freq = {}
for k, v in gender_freq_raw.items():
    kk = str(k).strip()
    if kk.lower() == "male":
        kk = "M"
    gender_freq[kk] = gender_freq.get(kk, 0) + int(v)

# ---------------- UTILS ----------------
def dict_to_df(d, col_key="label", col_val="count"):
    df = pd.DataFrame(list(d.items()), columns=[col_key, col_val])
    df = df.sort_values(col_val, ascending=False)
    return df

def top_item(d):
    if not d:
        return ("", 0)
    k = max(d, key=d.get)
    return (k, d[k])

# ---------------- HEADER ----------------
st.markdown(
    """
    <div style="padding:14px 18px;border-radius:14px;border:1px solid #eaeaea;">
      <h2 style="margin:0;">O-Health • Triage Insights</h2>
      <div style="margin-top:6px;color:#666;">
        Chief-complaint driven routing overview • Symptoms • Specialists • Age & Gender • Durations
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ---------------- KPI ROW ----------------
top_sym, top_sym_n = top_item(symptoms_freq)
top_init, top_init_n = top_item(initial_symptoms_freq)
top_spec, top_spec_n = top_item(specialists_freq)
missing_gender = gender_freq.get("(missing)", 0)
missing_gender_pct = (missing_gender / total_rows) * 100 if total_rows else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Rows", f"{total_rows}")
k2.metric("Unique Symptoms", f"{total_unique_symptoms}")
k3.metric("Top Symptom", f"{top_sym}", f"{top_sym_n}")
k4.metric("Top Specialist", f"{top_spec}", f"{top_spec_n}")
k5.metric("Missing Gender", f"{missing_gender}", f"{missing_gender_pct:.1f}%")

st.write("")

# ---------------- CONTROLS ----------------
c1, c2, c3 = st.columns([1.2, 1.2, 1.6])

with c1:
    view_mode = st.radio(
        "View",
        ["All Symptoms", "Initial Symptoms (Chief Complaints)"],
        horizontal=False
    )

with c2:
    top_n = st.slider("Top-N to show", min_value=10, max_value=50, value=20, step=5)

with c3:
    st.info(
        "Tip: Chief complaints are **more reliable for routing** than associated symptoms.\n"
        "Use the *Duration Explorer* to spot chronic vs acute patterns."
    )

# Choose dataset
if view_mode == "All Symptoms":
    df_sym = dict_to_df(symptoms_freq, "symptom", "count").head(top_n)
else:
    df_sym = dict_to_df(initial_symptoms_freq, "symptom", "count").head(top_n)

# ---------------- MAIN TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["📌 Symptoms", "🧭 Specialist Load", "👥 Demographics", "⏳ Duration Explorer"])

# ---- TAB 1: Symptoms ----
with tab1:
    left, right = st.columns([1.35, 1])

    with left:
        st.subheader("Symptom Frequency")
        fig = px.bar(
            df_sym.sort_values("count", ascending=True),
            x="count",
            y="symptom",
            orientation="h",
            text="count",
        )
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Quick Table")
        st.dataframe(df_sym, use_container_width=True, height=520)

# ---- TAB 2: Specialists ----
with tab2:
    df_spec = dict_to_df(specialists_freq, "specialist", "count")
    cA, cB = st.columns([1.35, 1])

    with cA:
        st.subheader("Specialist Frequency (Leaderboard)")
        fig = px.bar(
            df_spec.head(25).sort_values("count", ascending=True),
            x="count",
            y="specialist",
            orientation="h",
            text="count"
        )
        fig.update_layout(height=560, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with cB:
        st.subheader("Share of Total (Top 10)")
        df_pie = df_spec.head(10)
        fig = px.pie(df_pie, names="specialist", values="count", hole=0.45)
        fig.update_layout(height=560, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

# ---- TAB 3: Demographics ----
with tab3:
    d1, d2 = st.columns(2)

    with d1:
        st.subheader("Age Distribution (Buckets)")
        df_age = dict_to_df(age_buckets, "age_range", "count")
        fig = px.bar(df_age, x="age_range", y="count", text="count")
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Age Summary")
        st.write(
            f"""
            - Count: **{age_count}**
            - Range: **{age_min}–{age_max}**
            - Mean: **{age_mean}**
            - Median: **{age_median}**
            """
        )

    with d2:
        st.subheader("Gender Distribution")
        df_gender = dict_to_df(gender_freq, "gender", "count")
        fig = px.bar(df_gender, x="gender", y="count", text="count")
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Data Quality Note")
        st.warning(
            "Gender has missing entries. Consider enforcing gender confirmation at intake.\n"
            "Also normalize variants (e.g., `male` → `M`) at ingestion."
        )

# ---- TAB 4: Duration Explorer ----
with tab4:
    st.subheader("Explore Symptom Durations")
    st.caption("This is from the available per-symptom duration dicts in your stats snippet.")

    available_symptoms = sorted(symptom_duration_map.keys())
    picked = st.selectbox("Select symptom", available_symptoms, index=0)

    dur_dict = symptom_duration_map.get(picked, {})
    if not dur_dict:
        st.info("No duration data available for this symptom.")
    else:
        df_dur = dict_to_df(dur_dict, "duration", "count")
        cL, cR = st.columns([1.35, 1])

        with cL:
            fig = px.bar(
                df_dur.sort_values("count", ascending=True),
                x="count",
                y="duration",
                orientation="h",
                text="count"
            )
            fig.update_layout(height=480, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with cR:
            st.subheader("Duration Table")
            st.dataframe(df_dur, use_container_width=True, height=480)

st.markdown("---")
st.caption("Built for quick OPD/triage visibility • O-Health analytics view")

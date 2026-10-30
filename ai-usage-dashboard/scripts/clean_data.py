from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "AI_Usage_and_Impact_on_Students_and_Professionals.csv"
OUT = ROOT / "data" / "clean"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW)
log = []
before = len(df)
df = df.drop_duplicates().copy()
log.append(f"Removed {before - len(df)} exact duplicate rows; {len(df)} rows remain.")

def to_number(series):
    cleaned = series.astype("string").str.replace(r"[$,]", "", regex=True)
    cleaned = cleaned.str.replace(r"\b(?:yrs?|years?|hrs?|hours?)\b", "", regex=True, case=False)
    cleaned = cleaned.str.strip()
    return pd.to_numeric(cleaned, errors="coerce")

numeric_cols = [
    "Age", "Monthly_Income", "Monthly_AI_Cost", "AI_Usage_Hours_Per_Day",
    "Time_Saved_Hours_Per_Week", "Work_or_Study_Hours_Per_Day"
]
for col in numeric_cols:
    old_missing = df[col].isna().sum()
    df[col] = to_number(df[col])
    log.append(f"{col}: converted text values to numbers; missing after conversion: {df[col].isna().sum()}.")

# Standardise category labels.
def normalise_text(value):
    if pd.isna(value):
        return value
    return str(value).strip()

df["Gender"] = df["Gender"].map(normalise_text)
gender_map = {"m":"Male", "male":"Male", "f":"Female", "female":"Female",
              "other":"Other", "non-binary":"Non-binary", "non binary":"Non-binary"}
df["Gender"] = df["Gender"].map(lambda x: gender_map.get(str(x).strip().lower(), x) if pd.notna(x) else x)

df["Country"] = df["Country"].map(normalise_text)
country_map = {"u.k.":"United Kingdom", "uk":"United Kingdom",
               "united states of america":"United States"}
df["Country"] = df["Country"].map(lambda x: country_map.get(str(x).strip().lower(), str(x).strip().title()) if pd.notna(x) else x)

df["AI_Tool"] = df["AI_Tool"].map(normalise_text)
tool_map = {
    "chat gpt":"ChatGPT", "chatgpt":"ChatGPT", "chatgpt ":"ChatGPT",
    "copilot":"Microsoft Copilot", "gemini":"Google Gemini", "claude":"Claude"
}
df["AI_Tool"] = df["AI_Tool"].map(lambda x: tool_map.get(str(x).strip().lower(), str(x).strip()) if pd.notna(x) else x)

df["Education_Level"] = df["Education_Level"].map(normalise_text)
education_map = {
    "masters":"Master's", "ma/msc":"Master's", "master's degree":"Master's",
    "bachelors":"Bachelor's", "ba/bsc":"Bachelor's", "bachelor's degree":"Bachelor's",
    "ph.d.":"PhD", "ph.d":"PhD", "hs":"High School", "high school":"High School",
    "undergrad":"Undergraduate"
}
df["Education_Level"] = df["Education_Level"].map(lambda x: education_map.get(str(x).strip().lower(), str(x).strip()) if pd.notna(x) else x)

# Flag implausible values as missing, retaining the respondent row.
limits = {
    "Age": lambda s: s > 80,
    "AI_Usage_Hours_Per_Day": lambda s: s > 16,
    "Work_or_Study_Hours_Per_Day": lambda s: s > 16,
    "Monthly_Income": lambda s: s > 50000,
}
for col, condition in limits.items():
    mask = df[col].notna() & condition(df[col])
    log.append(f"{col}: set {int(mask.sum())} implausible value(s) to blank.")
    df.loc[mask, col] = pd.NA

df["Age_Group"] = pd.cut(
    df["Age"], bins=[15,20,25,35,50,float("inf")],
    labels=["16–20","21–25","26–35","36–50","51+"], include_lowest=True
).astype("string")
df["Usage_Band"] = pd.cut(
    df["AI_Usage_Hours_Per_Day"], bins=[-0.001,1,2,4,float("inf")],
    labels=["under 1 h","1–2 h","2–4 h","4 h+"], right=True
).astype("string")
df["Paid_User"] = df["Monthly_AI_Cost"].gt(0).map({True:"Paid", False:"Free"}).where(df["Monthly_AI_Cost"].notna(), "Not stated")
df["Income_Band"] = pd.cut(
    df["Monthly_Income"], bins=[-0.001,1000,3000,5000,10000,float("inf")],
    labels=["≤1,000","1,001–3,000","3,001–5,000","5,001–10,000",">10,000"]
).astype("string")

# Use consistent text values for chart labels; missing categories are shown as Not stated in the dashboard.
df.to_csv(OUT / "ai_usage_clean.csv", index=False)
df.to_json(OUT / "ai_usage_clean.json", orient="records", force_ascii=False, indent=2)
(ROOT / "cleaning_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
print("\n".join(log))
print(f"Final rows: {len(df)}; unique User_IDs: {df['User_ID'].nunique()}")

import pandas as pd
import os

os.makedirs(r'C:\Users\malsh\OneDrive\Desktop\Datawarehouse\source', exist_ok=True)
os.makedirs(r'C:\Users\malsh\OneDrive\Desktop\Datawarehouse\assest-dataset', exist_ok=True)

print("=" * 50)
print("LFB Data Filter Script")
print("=" * 50)

# ── FILTER INCIDENT FILE ──────────────────────────
print("\n📂 Reading Incident file... (may take 1-2 minutes)")

df_incident = pd.read_excel(
   r"C:\Users\malsh\OneDrive\Desktop\Datawarehouse\dataset\primary dataset\LFB Incident data from 2018 - 2023.xlsx"
)

print(f"✅ Total rows loaded: {len(df_incident)}")
print(f"✅ Columns found: {list(df_incident.columns)}")

# Filter to 2022 and 2023 only
df_incident_filtered = df_incident[
    df_incident['CalYear'].isin([2022, 2023])
]

print(f"✅ Rows after filter (2022-2023): {len(df_incident_filtered)}")

# Save filtered file
df_incident_filtered.to_excel(
    r"C:\Users\malsh\OneDrive\Desktop\Datawarehouse\source\LFB_Incidents_2022_2023.xlsx",
    index=False
)
print("✅ Saved: LFB_Incidents_2022_2023.xlsx")


# ── FILTER MOBILISATION FILE ──────────────────────
print("\n📂 Reading Mobilisation file... (may take 1-2 minutes)")

df_mob = pd.read_csv(
    r"C:\Users\malsh\OneDrive\Desktop\Datawarehouse\dataset\primary dataset\LFB Mobilisation data from 2021 - 2024.csv",
    encoding='latin-1',
    low_memory=False
)

print(f"✅ Total rows loaded: {len(df_mob)}")
print(f"✅ Columns found: {list(df_mob.columns)}")

# Extract year from date column
df_mob['Year'] = pd.to_datetime(
    df_mob['DateAndTimeMobilised'],
    dayfirst=True,
    errors='coerce'
).dt.year

# Filter to 2022 and 2023 only
df_mob_filtered = df_mob[
    df_mob['Year'].isin([2022, 2023])
]

print(f"✅ Rows after filter (2022-2023): {len(df_mob_filtered)}")

# Save filtered file
df_mob_filtered.to_csv(
    r"C:\Users\malsh\OneDrive\Desktop\Datawarehouse\source\LFB_Mobilisation_2022_2023.csv",
    index=False
)
print("✅ Saved: LFB_Mobilisation_2022_2023.csv")


# ── DONE ─────────────────────────────────────────
print("\n" + "=" * 50)
print("🎉 ALL DONE! Your filtered files are ready.")
print("=" * 50)
print("\nFiles saved in your LFB_Data folder:")
print("  1. LFB_Incidents_2022_2023.xlsx")
print("  2. LFB_Mobilisation_2022_2023.csv")
input("\nPress Enter to close...")

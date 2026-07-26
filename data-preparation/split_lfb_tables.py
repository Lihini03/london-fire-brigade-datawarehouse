import pandas as pd
import os

print("=" * 60)
print("LFB Data - Corrected Table Splitter")
print("=" * 60)

df = pd.read_excel(r'C:\Users\malsh\OneDrive\Desktop\Datawarehouse\source\LFB_Incidents_2022_2023.xlsx')
print(f"\n✅ Rows loaded: {len(df)}")

out = r'C:\Users\malsh\OneDrive\Desktop\Datawarehouse\source\db_source_tables'
os.makedirs(out, exist_ok=True)

borough_area_map = {
    'City of London':('Central','Inner'),'Barking and Dagenham':('East','Outer'),
    'Barnet':('North','Outer'),'Bexley':('Southeast','Outer'),
    'Brent':('West','Outer'),'Bromley':('Southeast','Outer'),
    'Camden':('Central','Inner'),'Croydon':('South','Outer'),
    'Ealing':('West','Outer'),'Enfield':('North','Outer'),
    'Greenwich':('Southeast','Inner'),'Hackney':('East','Inner'),
    'Hammersmith and Fulham':('West','Inner'),'Haringey':('North','Inner'),
    'Harrow':('West','Outer'),'Havering':('East','Outer'),
    'Hillingdon':('West','Outer'),'Hounslow':('West','Outer'),
    'Islington':('Central','Inner'),'Kensington and Chelsea':('Central','Inner'),
    'Kingston upon Thames':('South','Outer'),'Lambeth':('South','Inner'),
    'Lewisham':('Southeast','Inner'),'Merton':('South','Outer'),
    'Newham':('East','Inner'),'Redbridge':('East','Outer'),
    'Richmond upon Thames':('South','Outer'),'Southwark':('Central','Inner'),
    'Sutton':('South','Outer'),'Tower Hamlets':('East','Inner'),
    'Waltham Forest':('East','Outer'),'Wandsworth':('South','Inner'),
    'Westminster':('Central','Inner'),
}

# ── TABLE 1: BOROUGH ─────────────────────────────────────────
print("\n📋 Creating BOROUGH ...")
boroughs = df[['IncGeo_BoroughCode','IncGeo_BoroughName']].drop_duplicates(
    subset=['IncGeo_BoroughCode']).dropna(subset=['IncGeo_BoroughCode']).copy()
boroughs.columns = ['BoroughCode','BoroughName']
boroughs['Area'] = boroughs['BoroughName'].map(lambda x: borough_area_map.get(x,('Unknown','Unknown'))[0])
boroughs['Type'] = boroughs['BoroughName'].map(lambda x: borough_area_map.get(x,('Unknown','Unknown'))[1])
boroughs.to_excel(f"{out}\\BOROUGH.xlsx", index=False)
print(f"   ✅ BOROUGH.xlsx | Rows: {len(boroughs)}")

# ── TABLE 2: STATION (StationName as PK — no StationCode!) ───
print("\n📋 Creating STATION ...")
stations = df[['IncidentStationGround','IncGeo_BoroughCode','IncGeo_BoroughName']].drop_duplicates(
    subset=['IncidentStationGround']).dropna(subset=['IncidentStationGround']).copy()
stations.columns = ['StationName','BoroughCode','BoroughName']
stations['EffectiveFrom'] = '2022-01-01'
stations['EffectiveTo']   = '9999-12-31'
stations['IsCurrent']     = 'Y'
stations.to_excel(f"{out}\\STATION.xlsx", index=False)
print(f"   ✅ STATION.xlsx | Rows: {len(stations)}")

# ── TABLE 3: INCIDENT_TYPE ───────────────────────────────────
print("\n📋 Creating INCIDENT_TYPE ...")
inc_types = df[['IncidentGroup','StopCodeDescription','SpecialServiceType']].drop_duplicates().dropna(
    subset=['IncidentGroup']).copy()
inc_types.insert(0,'TypeCode',['TYP'+str(i+1).zfill(3) for i in range(len(inc_types))])
inc_types.to_excel(f"{out}\\INCIDENT_TYPE.xlsx", index=False)
print(f"   ✅ INCIDENT_TYPE.xlsx | Rows: {len(inc_types)}")

# ── TABLE 4: PROPERTY ────────────────────────────────────────
print("\n📋 Creating PROPERTY ...")
props = df[['PropertyCategory','PropertyType']].drop_duplicates().dropna(
    subset=['PropertyCategory']).copy()
props.insert(0,'PropertyCode',['PROP'+str(i+1).zfill(3) for i in range(len(props))])
props.to_excel(f"{out}\\PROPERTY.xlsx", index=False)
print(f"   ✅ PROPERTY.xlsx | Rows: {len(props)}")

# ── TABLE 5: INCIDENT (with TypeCode & PropertyCode FKs) ─────
print("\n📋 Creating INCIDENT ...")
df_inc = df.copy()

# Rename measure columns to match SQL table
df_inc = df_inc.rename(columns={
    'PumpMinutesRounded' : 'PumpHoursRoundUp',
    'Notional Cost (£)'  : 'Notional_Cost',
})

# Add TypeCode by matching IncidentGroup + StopCodeDescription
df_inc = df_inc.merge(
    inc_types[['TypeCode','IncidentGroup','StopCodeDescription']],
    on=['IncidentGroup','StopCodeDescription'],
    how='left'
)

# Add PropertyCode by matching PropertyCategory + PropertyType
df_inc = df_inc.merge(
    props[['PropertyCode','PropertyCategory','PropertyType']],
    on=['PropertyCategory','PropertyType'],
    how='left'
)

incident_cols = [
    'IncidentNumber','DateOfCall','TimeOfCall','HourOfCall','CalYear',
    'IncGeo_BoroughCode','IncidentStationGround','TypeCode','PropertyCode',
    'Latitude','Longitude','Easting_m','Northing_m',
    'Postcode_full','Postcode_district','AddressQualifier',
    'NumStationsWithPumpsAttending','NumPumpsAttending',
    'PumpHoursRoundUp','Notional_Cost','FRS',
    'FirstPumpArriving_AttendanceTime','FirstPumpArriving_DeployedFromStation',
]
incident_cols_exist = [c for c in incident_cols if c in df_inc.columns]
df_incident = df_inc[incident_cols_exist].drop_duplicates(subset=['IncidentNumber'])
df_incident.to_excel(f"{out}\\INCIDENT.xlsx", index=False)
print(f"   ✅ INCIDENT.xlsx | Rows: {len(df_incident)} | Cols: {len(df_incident.columns)}")
print(f"   ✅ Columns: {list(df_incident.columns)}")

# ── DONE ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ALL DONE! Load in this exact order into SQL Server:")
print("=" * 60)
print("""
  1. BOROUGH.xlsx       → Borough table
  2. STATION.xlsx       → Station table
  3. INCIDENT_TYPE.xlsx → IncidentType table
  4. PROPERTY.xlsx      → Property table
  5. INCIDENT.xlsx      → Incident table
  6. (Mobilisation CSV loaded separately in SSIS)
""")
input("Press Enter to close...")
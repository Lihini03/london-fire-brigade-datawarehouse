# 🚒 London Fire Brigade — Enterprise Data Warehouse & BI Platform

[![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?style=flat&logo=microsoft-sql-server&logoColor=white)](https://www.microsoft.com/sql-server)
[![SSIS](https://img.shields.io/badge/SSIS-ETL-blue?style=flat)](#)
[![SSAS](https://img.shields.io/badge/SSAS-OLAP%20Cube-blue?style=flat)](#)
[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=power-bi&logoColor=black)](https://powerbi.microsoft.com/)
[![Excel](https://img.shields.io/badge/Excel-PivotTables-217346?style=flat&logo=microsoft-excel&logoColor=white)](#)
[![Status](https://img.shields.io/badge/status-complete-brightgreen?style=flat)](#)

An end-to-end **Data Warehousing & Business Intelligence** solution built on real-world London Fire Brigade (LFB) emergency incident data (2022–2023). This project takes ~251,000 raw operational records through a full **star-schema dimensional model**, a **multi-source ETL pipeline**, an **SSAS OLAP cube**, and a suite of **interactive Power BI reports** — mirroring the architecture a public-safety or logistics analytics team would run in production.

> Built as part of the Data Warehousing & Business Intelligence module (IT3021) at SLIIT, this repository documents the full lifecycle: source analysis → staging → dimensional modelling → ETL → OLAP → BI reporting.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Repository Structure](#-repository-structure)
- [Data Sources](#-data-sources)
- [Dimensional Model](#-dimensional-model)
- [ETL Pipeline](#-etl-pipeline)
- [Accumulating Fact Pattern](#-accumulating-fact-pattern)
- [OLAP Cube (SSAS)](#-olap-cube-ssas)
- [Business Intelligence Reports (Power BI)](#-business-intelligence-reports-power-bi)
- [Key Engineering Decisions](#-key-engineering-decisions)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Author](#-author)

---

## 🔍 Overview

The **London Fire Brigade Incident Records** dataset was chosen as the source system because it reflects a genuine OLTP transactional workload — real emergency incidents, resource mobilisations, and response-time metrics across 33 London boroughs. This makes it an ideal candidate for demonstrating:

- Multi-source data integration (relational database + flat file)
- Dimensional modelling with Slowly Changing Dimensions (SCD Type 1 & 2)
- SSIS-based ETL with data quality remediation
- Accumulating fact tables for business-process tracking
- Multidimensional OLAP analysis (Roll-up, Drill-down, Slice, Dice, Pivot)
- Self-service BI reporting with drill-down and drill-through navigation

**Scale:** ~251,506 incident records · ~368,690 mobilisation records · 33 boroughs · 102 fire stations · 2 full years of data (2022–2023)

---

## 🏗 Architecture

The solution follows a standard **three-tier DW/BI architecture**, ensuring clean separation between operational, analytical, and reporting layers:

```
┌───────────────────────┐      ┌────────────────────────┐      ┌─────────────────────┐      ┌───────────────────────┐
│      SOURCE LAYER      │      │     STAGING LAYER       │      │   DATA WAREHOUSE     │      │  ANALYTICS & BI       │
│                        │      │                          │      │                       │      │                        │
│  LFB_SourceDB (SQL)    │─SSIS→│  LFB_Staging (SQL)      │─SSIS→│  LFB_DW (Star Schema) │─────▶│  SSAS Cube            │
│  • dbo.Incident        │      │  • StgIncident           │      │  • FactIncident        │      │  • Excel PivotTables  │
│                        │      │  • StgMobilisation       │      │  • DimDate             │      │                        │
│  Flat File (CSV)       │      │  • StgBorough            │      │  • DimBorough          │      │  Power BI             │
│  • Mobilisation.csv    │      │  • StgStation            │      │  • DimStation (SCD2)   │      │  • 4 interactive       │
│                        │      │  • StgIncidentType       │      │  • DimIncidentType     │      │    reports             │
│                        │      │  • StgProperty           │      │  • DimProperty         │      │                        │
└───────────────────────┘      └────────────────────────┘      └─────────────────────┘      └───────────────────────┘
                                                                          ▲
                                                                          │
                                                          LFB_Update_AccumulatingFact.dtsx
                                                          (updates completion timestamps)
```

**Design rationale:** Separating sources into a SQL Server database (Incident data) and a CSV flat file (Mobilisation data) deliberately demonstrates handling heterogeneous source types in a single ETL pipeline — a common real-world scenario where operational systems export data in different formats.

---

## 📁 Repository Structure

```
london-fire-brigade-datawarehouse/
│
├── data-preparation/            # Source dataset preparation & source-to-DB loading
├── DataProfiling/                # SSIS Data Profiling Task outputs & findings
├── LFB_EmergencyResponse_DWBI/   # Core SSIS project — staging & DW ETL packages
│   ├── LFB_Load_Staging.dtsx     #   Source → Staging (multi-source extraction)
│   ├── LFB_Load_DW.dtsx          #   Staging → Data Warehouse (dimensional load)
│   └── LFB_Update_AccumulatingFact.dtsx  # Accumulating fact completion update
├── LFB_SSAS/                     # SQL Server Analysis Services multidimensional cube
└── PowerBi/                      # Power BI Desktop reports (.pbix) & DAX measures
```

---

## 🗂 Data Sources

| Source | Type | Format | Content |
|---|---|---|---|
| **LFB_SourceDB** | Relational Database | SQL Server | Incident records, station data, borough data, incident types, property types |
| **LFB_Mobilisation_2022_2023** | Flat File | CSV | Fire appliance dispatch and response-time records |
| **Borough Reference Data** | Manually curated | Excel | Inner/Outer London geographic classification |

Two source types were deliberately used to demonstrate ETL handling of both **database** and **file-based** extraction within the same pipeline — the Incident data was loaded via OLE DB Source, and the Mobilisation data via SSIS Flat File Source with UTF-8 code page handling for special characters.

**Natural hierarchy in the source data:**
`Fire Station → London Borough → Greater London Region` — this hierarchy was built directly into the `DimStation → DimBorough` foreign key relationship to support drill-up/drill-down OLAP analysis.

---

## ⭐ Dimensional Model

A **Star Schema** was chosen over a Snowflake Schema for three reasons: fewer joins → better query performance, simpler navigation in the SSAS cube, and the source hierarchy (Station → Borough) is fully captured through foreign keys without additional normalisation.

**Grain:** One row per incident.

| Table | Type | Description |
|---|---|---|
| `FactIncident` | Fact | Central fact table — one row per emergency incident, with FKs to all five dimensions plus accumulating-fact columns |
| `DimDate` | Dimension | Pre-populated calendar dimension (2022–2023) with day/week/month/quarter/year attributes |
| `DimBorough` | Dimension (SCD Type 1) | 33 London boroughs with Inner/Outer London classification |
| `DimStation` | Dimension (**SCD Type 2**) | 102 fire stations — tracks historical borough reassignments over time |
| `DimIncidentType` | Dimension | Incident classification (Fire, False Alarm, Special Service) with stop-code detail |
| `DimProperty` | Dimension | Property category and type involved in each incident |

**Measures:** First Pump Attendance Time, Number of Pumps Attending, Number of Stations Attending, Pump Hours (Round Up), Notional Cost, and the derived Accumulating Fact metrics below.

### Why SCD Type 2 for `DimStation`?
Fire stations can be reassigned between boroughs following London boundary reviews. SCD Type 2 preserves this history: `EndDate IS NULL` always identifies the currently active version of a station, while expired versions retain the borough assignment that was correct *at the time the historical incident occurred* — critical for accurate historical reporting.

---

## ⚙️ ETL Pipeline

Built entirely in **SQL Server Integration Services (SSIS)** across two orchestrated packages:

### Package 1 — `LFB_Load_Staging.dtsx` (Source → Staging)
Extracts from both source types into staging tables with no transformation applied, preserving source fidelity. Each Data Flow Task has an **OnPreExecute event handler** that truncates its staging table first, preventing duplicate loads on re-runs.

### Package 2 — `LFB_Load_DW.dtsx` (Staging → Data Warehouse)
Executes in strict dependency order to satisfy foreign-key constraints:

| Order | Task | Loads Into | Why This Order |
|---|---|---|---|
| 1 | Transform & Load Borough Data | `DimBorough` | No dependencies |
| 2 | Transform & Load Station Data (SCD2) | `DimStation` | Requires `BoroughKey` |
| 3 | Transform & Load Incident Type Data | `DimIncidentType` | Must precede fact load |
| 4 | Transform & Load Property Data | `DimProperty` | Must precede fact load |
| 5 | Transform & Load Fact Incident | `FactIncident` | Requires all dimension surrogate keys |

The fact-load task chains **four Lookup transformations** (Station, Borough, IncidentType, Property) configured with **Full Cache** mode for performance and **Ignore Failure** error handling, so incidents that can't be matched to a dimension don't halt the entire load.

### Data Profiling → ETL Decisions
A dedicated `Data_Profiling.dtsx` package was run against every staging table *before* transformation logic was designed. Key findings directly shaped the ETL:

| Finding | Remediation |
|---|---|
| ~40% NULLs in `SpecialServiceType` | `REPLACENULL(..., "N/A")` in Derived Column |
| NULLs in attendance time & cost | `ISNULL(..., 0)` in source SQL |
| BOM encoding corruption on `IncidentNumber` | Column renamed via `sp_rename` |
| NULL borough codes | Filtered with `WHERE IS NOT NULL` |

This profile-first approach ensured transformation logic was driven by actual data quality issues rather than assumptions.

---

## 📈 Accumulating Fact Pattern

`FactIncident` implements an **accumulating snapshot fact table** to track an incident's lifecycle across two milestones:

| Column | Type | Set When |
|---|---|---|
| `accm_txn_create_time` | DATETIME | Incident loaded into DW (`GETDATE()`) |
| `accm_txn_complete_time` | DATETIME | Incident resolved — updated by a **separate SSIS package** |
| `txn_process_time_hours` | Computed | `DATEDIFF(HOUR, create_time, complete_time)` — auto-calculated by SQL Server |

A standalone package, **`LFB_Update_AccumulatingFact.dtsx`**, reads completion events from a staging table and calls `dbo.UpdateAccumulatingFact`, which resolves the natural key (`IncidentNumber`) and gracefully **ignores unmatched transaction IDs** rather than failing — a realistic pattern for late-arriving or partial completion feeds.

---

## 🧊 OLAP Cube (SSAS)

A **SQL Server Analysis Services Multidimensional cube** (`Cube_LFB_Incidents`) sits on top of `LFB_DW`, pre-aggregating the model for sub-second analytical queries from Excel and Power BI.

**Hierarchies implemented:**
- **Date Hierarchy:** `Year → Quarter → Month → Day`
- **Location Hierarchy:** `Greater London → Borough → Station`

**KPI:** An "Average Response Time" KPI benchmarks live response performance against a 300s/360s threshold using a `CASE`-based status expression.

**OLAP operations demonstrated via Excel PivotTables:**

| Operation | Demonstration |
|---|---|
| **Roll-Up** | Incident cost aggregated from Borough → Greater London total |
| **Drill-Down** | Incident counts expanded Year → Quarter → Month |
| **Slice** | Cube fixed to `IncidentGroup = Fire` across all boroughs |
| **Dice** | Cube fixed to `IncidentGroup = Fire AND Year = 2022` |
| **Pivot** | Axes rotated between Borough-centric and Incident-Type-centric views |

---

## 📊 Business Intelligence Reports (Power BI)

Four production-style reports were built in Power BI Desktop and published to the Power BI Service, backed by custom **DAX measures**:

```dax
Total Incidents      = COUNTROWS(FactIncident)
Avg Response Minutes = DIVIDE(AVERAGE(FactIncident[FirstPumpArriving_AttendanceTime]), 60, 0)
Total Cost           = SUM(FactIncident[Notional_Cost])
YoY Incident Change % = 
    VAR CurrentYear  = CALCULATE(COUNTROWS(FactIncident), DimDate[Year] = 2023)
    VAR PreviousYear = CALCULATE(COUNTROWS(FactIncident), DimDate[Year] = 2022)
    RETURN DIVIDE(CurrentYear - PreviousYear, PreviousYear, 0) * 100
```

| Report | Purpose |
|---|---|
| **Matrix Report** | Cross-tab of incidents & cost by Borough × Incident Type, with row/column subtotals |
| **Cascading Slicer Report** | Borough selection dynamically filters the Incident Type slicer via star-schema cross-filtering |
| **Drill-Down Report** | Interactive Year → Quarter → Month drill-down on chart visuals |
| **Drill-Through Report** | Right-click any borough to navigate to a dedicated Borough Detail page |

---

## 🎯 Key Engineering Decisions

- **Star over Snowflake schema** — prioritised query performance and cube simplicity at the scale required (120K+ facts)
- **SCD Type 2 only where history matters** (`DimStation`) — avoided unnecessary complexity on dimensions with no meaningful change history
- **Profile-before-transform** — data profiling ran *before* ETL design, so NULL-handling and cleansing logic was evidence-based
- **Full Cache + Ignore Failure lookups** — balances load performance against pipeline resilience for unmatched records
- **Separate package for accumulating fact updates** — decouples the "incident created" and "incident resolved" ETL cadences, reflecting how real operational completion feeds arrive asynchronously

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Source & Staging | SQL Server, CSV Flat Files |
| ETL | SQL Server Integration Services (SSIS) |
| Data Warehouse | SQL Server (Star Schema) |
| OLAP | SQL Server Analysis Services (SSAS Multidimensional) |
| Reporting | Power BI Desktop & Service, Excel PivotTables/PivotCharts |
| Version Control | Git & GitHub |

---

## 🚀 Getting Started

1. Restore/create the three databases: `LFB_SourceDB`, `LFB_Staging`, `LFB_DW` (DDL scripts included in `LFB_EmergencyResponse_DWBI/`)
2. Open `LFB_EmergencyResponse_DWBI/` in Visual Studio (SSIS project) and update connection managers to point to your local SQL Server instance
3. Run `LFB_Load_Staging.dtsx`, then `LFB_Load_DW.dtsx`, then `LFB_Update_AccumulatingFact.dtsx`
4. Deploy the cube in `LFB_SSAS/` to your Analysis Services instance
5. Open the reports in `PowerBi/` and point the data source to your `LFB_DW` instance

---

## 👤 Author

**B.L.L.N. Bowaththa (Lihini)**
Data Science Undergraduate, SLIIT
[LinkedIn](https://linkedin.com/in/lihini-b) · [GitHub](https://github.com/Lihini03)

---

<p align="center"><i>Built as part of IT3021 — Data Warehousing & Business Intelligence, SLIIT</i></p>

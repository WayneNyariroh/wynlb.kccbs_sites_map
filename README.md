# KCCB-ACTS Supported Health Facilities Mapper

An interactive health programme mapping and analytics project combining **facility location data, programme performance data, and geographic classifications** to provide a clearer view of supported health facilities, service delivery, and programme reach across Kenya.

The project brings several separate datasets together at facility level and presents the resulting information through an interactive Streamlit dashboard and geographic facility map.

## Project overview

Health programme information is often stored across separate datasets. Facility coordinates may exist in one source, programme indicators in another, and administrative or programme regions somewhere else.

Viewed separately, these datasets answer only part of the question.

This project combines them into a single analytical dataset that can answer questions such as:

- Where are supported health facilities located?
- How widely is programme support distributed across counties?
- How many clients are currently receiving antiretroviral therapy at supported facilities?
- How does treatment volume vary between programme regions?
- How many clients were newly initiated on treatment during each quarter?
- Where are HIV testing services being delivered?
- Which testing entry points account for the largest testing volumes?
- How many tests and positive results were recorded across programme regions?

The final output is an interactive application that connects **where services are delivered** with **what programme activity is occurring at those locations**.

---

## Project context

The analysis focuses on health facilities supported by **KCCB-ACTS** - where I served as a Data Manager at the time - during FY2023.

The underlying data came from different programme and health information sources and required substantial preparation before it could be analysed together.

Kenya Master Health Facility List and KenyaHMIS Public NDWH were used for the data sourcing. There were no convenient public APIs at the time in either, so most of the data was manual entry. This meant that part of the project involved manually assembling source data before cleaning, validating, restructuring, and joining it.

The final facility-level dataset for 2023 contains:

- **105 supported health facilities**
- **20 counties**
- **7 programme regions**
- facility coordinates
- county and sub-county information
- facility ownership
- quarterly ART treatment indicators
- quarterly new-treatment indicators

Additional datasets provide HIV testing totals, positive test results, and testing activity by service entry point.

---

## What I wanted to solve

A list of supported facilities can show programme presence, but it does not immediately show the geographic pattern of that support.

Programme performance tables can show treatment numbers, but they provide little geographic context.

This project connects those two perspectives.

Conceptually, the data pipeline is:

```text
Facility Master Data
        │
        │  Facility identifiers + coordinates
        ▼
Supported Facility Filter
        │
        ├──────────────┐
        │              │
        ▼              ▼
    KCCB-ACTS
ART Programme Data   Regional Classification
        │              │
        └──────┬───────┘
               │
               ▼
     Integrated Facility Dataset
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
 Interactive Map    Programme Analytics
       │                │
       └───────┬────────┘
               ▼
       Streamlit Dashboard
```

The result is a dataset where each supported facility can be associated with both its geographic location and its programme indicators.

---

## Data preparation

Most of the analytical work takes place before the dashboard is built.

### 1. Facility data preparation

The health facility master dataset was reduced to fields required for the analysis, including:

```text
MFL code
Facility name
County
Sub-county
Owner
Latitude
Longitude
Implementing partner
```

Facilities were then filtered to retain sites supported by KCCB-ACTS.

Duplicate and missing-value checks were performed before the resulting dataset was saved for further processing.

---

### 2. Programme data integration

Facility programme data included quarterly treatment indicators such as:

```text
TX_NEW 2023 Q1
TX_NEW 2023 Q2
TX_NEW 2023 Q3
TX_NEW 2023 Q4

TX_CURR 2023 Q1
TX_CURR 2023 Q2
TX_CURR 2023 Q3
TX_CURR 2023 Q4
```

The **MFL code** was used as the primary facility identifier when joining programme records to facility information.

Using an identifier rather than facility names reduces problems caused by differences in spelling, abbreviations, or naming conventions between datasets.

---

### 3. Geographic enrichment

A separate regional dataset was added to associate facilities with programme regions.

The resulting dataset connects:

```text
Facility
   ↓
MFL Code
   ↓
County / Sub-county
   ↓
Programme Region
   ↓
Coordinates
   ↓
Programme Indicators
```

Additional region assignments were completed where the regional source dataset did not contain all facilities.

---

### 4. Final analytical dataset

After cleaning and joining the sources, the final dataset contains 16 fields:

```text
mfl_code
facility_name
region
county
sub_county
owner
lat
lon

txnew2023Q1
txnew2023Q2
txnew2023Q3
txnew2023Q4

2023Q1
2023Q2
2023Q3
2023Q4
```

Each row represents one supported facility.

This dataset is stored at:

```text
processed_data/cleaned_data.xlsx
```

---

## Dashboard

The Streamlit application has two main analytical components.

### Interactive facility map

The map uses **Folium** and facility latitude and longitude coordinates to plot supported sites across Kenya.

Nearby facilities are grouped using marker clustering so that the map remains readable at different zoom levels.

Selecting a facility displays information including:

- facility name
- sub-county
- county
- ART clients currently receiving treatment

This makes it possible to move from national programme coverage to individual supported facilities.

---

### Programme analytics

The dashboard uses the integrated dataset to produce several programme views.

#### Current clients on treatment

The application aggregates the latest FY2023 treatment data across supported facilities.

At the end of the available FY2023 period, the dataset contains approximately:

**141,336 clients currently receiving ART**

across the 105 supported facilities.

---

#### New clients initiated on treatment

Quarterly `TX_NEW` indicators allow treatment initiation to be compared over time and between programme regions.

Across FY2023, the facility dataset records:

**4,081 new ART initiations**

including:

**627 new ART initiations in Q4**

---

#### Regional treatment distribution

Treatment totals are aggregated by programme region to show where the largest numbers of clients receiving ART are being supported.

This helps move the analysis beyond a simple count of facilities.

A region with fewer facilities may still account for a large treatment volume, while another region may contain many smaller facilities.

---

#### Supported facilities by county

Facility counts are grouped by county to show the geographic footprint of programme support.

The dataset contains supported facilities across:

**20 Kenyan counties**

This represents programme presence rather than a measure of population-level healthcare accessibility.

---

#### HIV testing activity

Separate testing datasets were incorporated to examine testing service delivery.

For the available August 2023 testing data:

```text
Tests performed:      8,078
Positive results:       282
```

Testing activity can also be examined by service entry point, including areas such as:

```text
PMTCT ANC
PMTCT maternity
Outpatient services
and other testing entry points
```

This adds another programme dimension beyond ART treatment totals.

---

## Tools used

### Python

Used for data preparation, transformation, aggregation, and application logic.

### pandas

Used extensively for:

- reading Excel and CSV files
- filtering facilities
- selecting variables
- checking duplicates
- checking missing data
- renaming columns
- joining datasets
- grouping data
- calculating programme totals
- preparing data for visualisation

### NumPy

Used for numerical aggregation and derived calculations.

### Streamlit

Used to turn the analysis into an interactive web application.

### Folium

Used to create the geographic facility map and interactive markers.

### Altair

Used for dashboard charts and programme visualisations.

### OpenPyXL

Used to read Excel workbooks within the Python workflow.

---

## Repository structure

```text
.
├── raw_data/
│   ├── regiondata.csv
│   ├── entry_point_tests.xlsx
│   └── tested_totals.xlsx
│
├── processed_data/
│   ├── cleaned_kccb_his_master_coordinates.xlsx
│   └── cleaned_data.xlsx
│
├── icons/
│   └── txregime.png
│
├── extra_styling/
│   └── style.css
│
├── .streamlit/
│   └── config.toml
│
├── kccbsites_mapper.py
├── requirements.txt
├── README.md
└── LICENCE.txt
```

The repository also contains a data-preparation notebook checkpoint documenting much of the cleaning, merging, and exploratory analysis used to create the processed dataset.

---

## Running the project locally

Clone the repository:

```bash
git clone <repository-url>
cd wynlb.kccbs_sites_map
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Start the Streamlit application:

```bash
streamlit run kccbsites_mapper.py
```

Streamlit will provide a local address, usually:

```text
http://localhost:8501
```

Open this address in a browser to access the dashboard.

---

## Data quality considerations

Combining administrative, geographic, and programme datasets introduced several data-quality issues that had to be handled explicitly.

### Facility identifiers

Facility names can differ between data sources, so MFL codes were used as the primary joining field wherever possible.

### Incomplete regional classifications

The regional dataset contained fewer records than the facility dataset. Missing programme regions were therefore reviewed and assigned using county information.

### Manual source extraction

Some source data had to be assembled manually because the original systems did not provide a convenient public API or analytical export. 

Manual extraction increases the possibility of transcription errors, so the datasets required additional cleaning and validation.

### Different analytical grains

Not every dataset operates at facility level.

The project therefore uses different levels of aggregation depending on the indicator:

```text
Facility level  → supported sites and ART indicators
County level    → geographic programme distribution
Region level    → aggregated programme performance
Entry point     → HIV testing activity
```

Recognising these different grains is necessary before datasets are joined or compared.

---

## Limitations

This project describes the facilities and programme indicators contained in the available FY2023 datasets. It should not be interpreted as a complete picture of healthcare availability or HIV service coverage across Kenya.

In particular:

- mapped facilities represent KCCB-ACTS-supported facilities rather than all health facilities
- facility counts do not measure population access to services
- geographic presence does not measure travel time or distance to care
- programme indicators represent the reporting periods available in the source data
- some source data was manually compiled
- the application currently uses static local datasets rather than a live programme data pipeline

A fuller assessment of geographic healthcare accessibility would require additional information such as population distribution, road networks, travel times, facility capacity, catchment areas, and facilities supported by other programmes.

---

## What this project demonstrates

This project is primarily a **data integration and analytical communication exercise**.

It demonstrates how separate operational datasets can be combined to create a more useful programme view:

```text
Programme data
        +
Facility data
        +
Geographic data
        ↓
Integrated analytical dataset
        ↓
Maps + indicators + regional comparisons
        ↓
Clearer programme visibility
```

The main value does not come from producing a map alone.

It comes from connecting facility geography with programme performance so that users can examine **where programme support exists, how that support is distributed, and what service activity is associated with the supported facilities**.

---

## Possible future improvements

The project could be extended by:

- replacing manually assembled datasets with automated data pipelines
- adding facility search
- introducing county and region filters
- adding year and quarter selectors
- calculating additional HIV programme indicators
- adding trend visualisations across reporting periods
- introducing downloadable filtered datasets
- validating coordinates against an authoritative facility registry
- incorporating GeoJSON county boundaries
- producing choropleth views of programme indicators
- adding population denominators where appropriate
- adding travel-time or accessibility analysis
- moving processed data into PostgreSQL or another analytical database
- deploying an automated refresh pipeline

These additions would turn the project from a static FY2023 analytical application into a reusable programme monitoring tool.

---

## Author
**Wayne Omondi**

Data analysis, data integration, visualisation, and application development.

The project was built during my time as a KCCB Data Manager to explore how the programme, facility, and geographic data can be combined to make operational health data easier to understand and use.

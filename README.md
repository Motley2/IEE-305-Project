# Earthquake Analytics System

## Team Members
-Jarom Hansen jkhanse7

-William Motley wmotley1

## Description
Earthquakes are destructive natural events, and if buildings and people are not ready, there will be more destruction and death. Our project seeks to mitigate these problems by providing civil engineers with data in an organized way, about the earthquakes in a region so they know the risks of earthquakes and know how much they need to protect the buildings they are building and renovating so destruction and death is minimized.

## Features
- Real-time API health checking with offline/online status indicator
- Interactive sidebar navigation with 10 earthquake analytics queries
- Responsive data tables with Pandas integration
- Type-safe database operations with SQLModel ORM
- Automatic database schema management
- CORS-enabled REST API for flexible frontend integration

## Technologies Used
- **SQLModel** - Modern ORM combining SQLAlchemy and Pydantic
- **SQLite3** - Lightweight relational database
- **FastAPI** - High-performance REST API framework
- **Streamlit** - Interactive web frontend
- **Pandas** - Data manipulation and analysis
- **Python 3.10+** - Programming language
- **Pydantic** - Data validation using Python type annotations
- **SQLAlchemy** - SQL toolkit and ORM

## Installation

**Option 1: Install all dependencies at once (Recommended)**

```bash
pip install -r requirements.txt
```

**Option 2: Install individual core packages**

```bash
pip install sqlmodel fastapi uvicorn streamlit pandas requests
```

The `requirements.txt` file contains the exact versions of all 51 packages used in this project, ensuring consistency across different machines.

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Steps

**Step 1: Create and activate virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
```

**Step 2: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 3: Start the backend server**

```bash
uvicorn backend.main:app --reload
```

The backend will run on `http://127.0.0.1:8000`

API documentation available at `http://127.0.0.1:8000/docs`

**Step 4: Start the frontend (in a new terminal)**

```bash
streamlit run frontend/frontend.py
```

The frontend will open at `http://localhost:8501`

## Usage

Once both the backend and frontend are running, choose any of the ten queries and fill out the fields that appear and then click the button. Once the button is pressed, the results for the query will show up on the page.

## API Documentation
- Query 1: Fetch earthquakes in a region.

        GET /regions/{region_id}/earthquakes 

- Query 2: Fetch the average number of earthquakes in a region.
      
         GET /regions/{region_id}/stats/avg-magnitude

- Query 3: Fetch the Earthquakes near a location.

         GET /analytics/nearby

- Query 4: Fetch the most seismically active regions.

         GET /analytics/regions/most-active

- Query 5: Fetch earthquakes that have a specific magnitude.

         GET/analytics/high-magnitude

- Query 6: Fetch regions that have a user specified minimum number of earthquakes.

         GET /analytics/regions/with-min-quakes

- Query 7: Fetch regions with above average seismic activity.

         GET /analytics/regions/above-average-activity

- Query 8: Fetch earthquakes that meet multiple criteria.

         GET /analytics/multi-criteria

- Query 9: Fetch earthquakes that happen in a specified population region.

         GET /analytics/high-population-regions

- Query 10: Fetch the risk summary of a region.

         GET /regions/{region_id}/risk-summary

## Database Schema
```SQL
Table 1: Region
CREATE TABLE Region (
     region_id INTEGER PRIMARY KEY,
     region_name TEXT NOT NULL,
     country TEXT NOT NULL,
     population INTEGER NOT NULL,
    );

Table 2: SeismicZone
CREATE TABLE SeismicZone (
     zone_id INTEGER PRIMARY KEY,
     zone_name TEXT NOT NULL,
     risk_level INTEGER NOT NULL,
    );

Table 3: Earthquake
CREATE TABLE Earthquake (
     Quake_id INTEGER PRIMARY KEY,
     datetime TEXT NOT NULL,
     magnitude REAL NOT NULL,
     depth_km REAL NOT NULL,
     latitude REAL NOT NULL,
     longitude REAL NOT NULL,
     place TEXT NOT NULL,
     region_id INTEGER NOT NULL,
     zone_id INTEGER NOT NULL,
     FOREIGN KEY (region_id) REFERENCES Region(region_id)
     FOREIGN KEY (zone_id) REFERENCES SeismicZone(zone_id)
    );
```

## Project Structure

```
IEE-305-Project/
├── .venv/                 # Virtual environment (auto-generated)
├── .gitignore             # Git ignore file for cache and env files
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── backend/               # FastAPI backend
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI application with 10 endpoints
│   ├── models.py          # SQLModel ORM models (Region, SeismicZone, Earthquake)
│   ├── database.py        # Database connection and session management
│   ├── queries.py         # 10 query functions for earthquake analytics
│   ├── schemas.py         # Pydantic response models
│   └── fetch_data.py      # USGS data fetching and database population
│
├── frontend/              # Streamlit web interface
│   └── frontend.py        # Main Streamlit application with 10 queries
│
├── database/              # Data storage
│   ├── earthquakes.db     # SQLite database (auto-created)
│   └── schema.sql         # Original SQL schema (reference)
│
└── docs/                  # Documentation and diagrams
    ├── proposal.md        # Project proposal
    ├── final_report.md    # Final project report
    ├── ER_Diagram.png     # Entity-Relationship diagram
    ├── relational_schema.png  # Database schema diagram
    └── query screenshots/ # Screenshots of all 10 queries from frontend and backend
```


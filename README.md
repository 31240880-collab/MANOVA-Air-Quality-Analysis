# Air Quality Intelligence & MANOVA Research Platform

A Streamlit dashboard built around the supplied Global Air Pollution Data CSV. It includes KPI cards, overall AQI distribution, pollutant-specific AQI indicator summaries, country comparisons, an exploratory MANOVA, a data-quality/governance audit, filtering, and CSV exports.

## Important research limitation

The bundled dataset contains overall AQI and pollutant-specific AQI indicators for CO, ozone, NO2 and PM2.5. It does **not** include raw pollutant concentrations, SO2, dates/timestamps, or monitoring-station identifiers. It is suitable for developing the dashboard and exploratory cross-sectional comparisons, but it does not directly support the original research question about measured PM2.5, NO2 and SO2 concentration variations across industrial corridors or seasons.

## Run on Windows (VS Code or Command Prompt)

1. Install Python 3.10 or newer.
2. Extract the project ZIP.
3. Open Command Prompt in the extracted `Air_Quality_Intelligence_Dashboard` folder.
4. Create a virtual environment (recommended):

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bat
   pip install -r requirements.txt
   ```

6. Start the app:

   ```bat
   streamlit run app.py
   ```

7. Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Included files

- `app.py` — Streamlit dashboard
- `requirements.txt` — Python dependencies
- `data/global_air_pollution_data.csv` — bundled source CSV

## Data governance reminders

- Retain the source file and its attribution/license information.
- Do not represent AQI indicator values as raw pollutant concentrations.
- The MANOVA tab is exploratory; inspect group sizes and assumptions before reporting results.

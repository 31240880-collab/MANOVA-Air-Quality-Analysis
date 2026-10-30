from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "global_air_pollution_data.csv"
POLLUTANTS = {
    "CO AQI": "co_aqi_value",
    "Ozone AQI": "ozone_aqi_value",
    "NO₂ AQI": "no2_aqi_value",
    "PM2.5 AQI": "pm25_aqi_value",
}
CATEGORY_COLORS = {
    "Good": "#20c997", "Moderate": "#f5c451", "Unhealthy for Sensitive Groups": "#ff9f43",
    "Unhealthy": "#ff5c7a", "Very Unhealthy": "#b197fc", "Hazardous": "#e03131"
}

st.set_page_config(page_title="Air Quality Intelligence | MANOVA Research", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(ellipse at 10% 0%, #142437 0%, #0b1220 44%, #080d17 100%); color: #edf3fc; }
[data-testid="stSidebar"] { background: #0d1726; border-right: 1px solid #25354a; }
.block-container { padding-top: 1.7rem; padding-bottom: 2.5rem; max-width: 1500px; }
.hero { padding: 1.5rem 1.7rem; border: 1px solid #2a4059; border-radius: 20px; background: linear-gradient(115deg, rgba(21,45,67,.96), rgba(16,27,45,.92)); margin-bottom: 1rem; }
.eyebrow { color: #5eead4; font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
.hero h1 { margin: .35rem 0 .45rem 0; color: #f4f7ff; font-size: clamp(1.7rem, 3vw, 2.6rem); letter-spacing: -.035em; }
.hero p { color: #b7c6d9; font-size: 1rem; margin: 0; max-width: 900px; }
.kpi { background: linear-gradient(145deg, rgba(23,39,59,.96), rgba(15,26,42,.96)); border: 1px solid #293c53; padding: 1rem 1.1rem; border-radius: 15px; min-height: 112px; }
.kpi-label { color: #a8bad0; font-size: .82rem; }
.kpi-value { color: #f4f7ff; font-size: 1.8rem; font-weight: 750; margin-top: .28rem; }
.kpi-note { color: #7f96b0; font-size: .76rem; margin-top: .1rem; }
.section-title { font-size: 1.15rem; font-weight: 700; color: #f0f5ff; margin: .5rem 0 .7rem 0; }
.note { padding: .9rem 1rem; border-radius: 12px; background: rgba(245,196,81,.09); border: 1px solid rgba(245,196,81,.35); color: #f6df9b; }
.info-note { padding: .9rem 1rem; border-radius: 12px; background: rgba(94,234,212,.07); border: 1px solid rgba(94,234,212,.24); color: #b9f7ee; }
[data-testid="stMetric"] { background: rgba(20,35,53,.7); border: 1px solid #263b52; padding: .8rem; border-radius: 13px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(file_bytes=None):
    if file_bytes is not None:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig")
    else:
        df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df.columns = [str(c).strip().lower().replace(" ", "_").replace(".", "") for c in df.columns]
    # Normalize the source's trailing tab in co_aqi_value and the decimal in pm2.5.
    rename = {}
    for c in df.columns:
        if c.startswith("co_aqi_value"):
            rename[c] = "co_aqi_value"
        elif c.startswith("pm2_5_aqi_value") or c.startswith("pm25_aqi_value") or c.startswith("pm25aqi_value"):
            rename[c] = "pm25_aqi_value"
        elif c.startswith("pm2_5_aqi_category") or c.startswith("pm25_aqi_category") or c.startswith("pm25aqi_category"):
            rename[c] = "pm25_aqi_category"
    df = df.rename(columns=rename)
    for col in ["country_name", "city_name", "aqi_category", "co_aqi_category", "ozone_aqi_category", "no2_aqi_category", "pm25_aqi_category"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    numeric = ["aqi_value", "co_aqi_value", "ozone_aqi_value", "no2_aqi_value", "pm25_aqi_value"]
    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

try:
    df_all = load_data()
except Exception as exc:
    st.error(f"Could not load the bundled dataset: {exc}")
    st.stop()

st.markdown("""
<div class="hero">
  <div class="eyebrow">Environmental analytics · Research workspace</div>
  <h1>Air Quality Intelligence &amp; MANOVA Research Platform</h1>
  <p>Explore global city-level Air Quality Index indicators, compare geographic patterns, inspect data quality, and run an exploratory multivariate group comparison.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌍 Workspace controls")
    st.caption("Dataset: Global Air Pollution Data · Kaggle")
    uploaded = st.file_uploader("Use another CSV (optional)", type=["csv"], help="Leave empty to use the dataset included with this project.")
    st.divider()
    st.markdown("#### Filters")
    countries = sorted(df_all["country_name"].dropna().unique().tolist())
    selected_countries = st.multiselect("Countries", countries, default=[] , help="Leave empty to include all countries.")
    categories = sorted(df_all["aqi_category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Overall AQI categories", categories, default=[])
    min_aqi, max_aqi = int(df_all["aqi_value"].min()), int(df_all["aqi_value"].max())
    aqi_range = st.slider("Overall AQI range", min_value=min_aqi, max_value=max_aqi, value=(min_aqi, max_aqi))
    st.divider()
    st.caption("Research note: this file contains AQI indicator values, not raw pollutant concentrations or dated station measurements.")

if uploaded is not None:
    try:
        df = load_data(uploaded.getvalue())
        data_source = f"Uploaded file: {uploaded.name}"
    except Exception as exc:
        st.error(f"Could not read uploaded CSV: {exc}")
        st.stop()
else:
    df = df_all.copy()
    data_source = "Bundled Kaggle dataset"

filtered = df.copy()
if selected_countries:
    filtered = filtered[filtered["country_name"].isin(selected_countries)]
if selected_categories:
    filtered = filtered[filtered["aqi_category"].isin(selected_categories)]
filtered = filtered[filtered["aqi_value"].between(aqi_range[0], aqi_range[1], inclusive="both")]

if filtered.empty:
    st.warning("No records match the selected filters. Adjust the sidebar selections.")
    st.stop()

n_rows = len(filtered)
n_countries = filtered["country_name"].nunique(dropna=True)
n_cities = filtered["city_name"].nunique(dropna=True)
mean_aqi = filtered["aqi_value"].mean()

k1, k2, k3, k4 = st.columns(4)
for col, label, value, note in [
    (k1, "Records in view", f"{n_rows:,}", "Rows after filters"),
    (k2, "Countries represented", f"{n_countries:,}", "Non-missing country labels"),
    (k3, "Cities represented", f"{n_cities:,}", "Non-missing city labels"),
    (k4, "Mean overall AQI", f"{mean_aqi:.1f}", f"Range {filtered.aqi_value.min():.0f}–{filtered.aqi_value.max():.0f}"),
]:
    with col:
        st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

st.write("")
st.markdown('<div class="info-note"><b>Data interpretation:</b> The available pollutant columns are AQI indicator values for CO, ozone, NO₂ and PM2.5. They are not measured concentrations. This dataset has no observation date, no station identifier and no SO₂ field; therefore it cannot directly answer the original time-series or PM2.5/NO₂/SO₂ concentration research question.</div>', unsafe_allow_html=True)

tab_overview, tab_compare, tab_quality, tab_data = st.tabs(["Overview", "Compare regions", "Data governance", "Data table"])

plot_template = "plotly_dark"
plot_bg = "rgba(0,0,0,0)"

with tab_overview:
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown('<div class="section-title">Overall AQI distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(filtered, x="aqi_value", color="aqi_category", nbins=35, marginal="box", opacity=.86,
                           color_discrete_map=CATEGORY_COLORS, template=plot_template,
                           labels={"aqi_value":"Overall AQI value", "aqi_category":"AQI category"})
        fig.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg, legend_title_text="AQI category", height=390, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('<div class="section-title">AQI category mix</div>', unsafe_allow_html=True)
        cat_counts = filtered["aqi_category"].fillna("Unknown").value_counts().rename_axis("Category").reset_index(name="Records")
        fig = px.pie(cat_counts, names="Category", values="Records", hole=.58, color="Category", color_discrete_map=CATEGORY_COLORS, template=plot_template)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg, height=390, margin=dict(l=5,r=5,t=20,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="section-title">Pollutant-specific AQI indicator summary</div>', unsafe_allow_html=True)
    available = {label: col for label, col in POLLUTANTS.items() if col in filtered.columns}
    summary_rows = []
    for label, col in available.items():
        s = filtered[col].dropna()
        summary_rows.append({"Indicator": label, "Mean": round(s.mean(), 2) if len(s) else np.nan, "Median": round(s.median(), 2) if len(s) else np.nan,
                             "90th percentile": round(s.quantile(.9), 2) if len(s) else np.nan, "Maximum": round(s.max(), 2) if len(s) else np.nan})
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

with tab_compare:
    st.markdown('<div class="section-title">Country comparison</div>', unsafe_allow_html=True)
    st.caption("Only countries with enough records are included. Since there are no dates, this is a cross-sectional comparison, not a trend over time.")
    min_n = st.slider("Minimum records per country", 1, 100, 10, key="min_n")
    country_summary = filtered.dropna(subset=["country_name"]).groupby("country_name", as_index=False).agg(
        records=("aqi_value", "size"), mean_aqi=("aqi_value", "mean"), median_aqi=("aqi_value", "median"),
        mean_pm25_aqi=("pm25_aqi_value", "mean"), mean_no2_aqi=("no2_aqi_value", "mean"))
    country_summary = country_summary[country_summary["records"] >= min_n].sort_values("mean_aqi", ascending=False)
    top_n = st.slider("Countries to display", 5, 30, 15, key="top_n")
    if country_summary.empty:
        st.info("No countries meet the minimum record count. Reduce the threshold.")
    else:
        top_summary = country_summary.head(top_n)
        fig = px.bar(top_summary.sort_values("mean_aqi"), x="mean_aqi", y="country_name", orientation="h", color="mean_aqi",
                     color_continuous_scale="Tealgrn", template=plot_template,
                     labels={"mean_aqi":"Mean overall AQI", "country_name":"Country"})
        fig.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg, height=max(400, top_n*27), coloraxis_showscale=False,
                          margin=dict(l=10,r=10,t=15,b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(country_summary.head(100).round(2), use_container_width=True, hide_index=True)
        st.download_button("Download country summary CSV", country_summary.to_csv(index=False).encode("utf-8"), "country_aqi_summary.csv", "text/csv")

with tab_quality:
    st.markdown('<div class="section-title">Data governance and quality audit</div>', unsafe_allow_html=True)
    quality = pd.DataFrame({
        "Check": ["Rows", "Columns", "Exact duplicate rows", "Missing country names", "Missing city names", "Missing overall AQI", "Date/time field", "Station identifier", "SO₂ field", "Raw concentration units"],
        "Result": [f"{len(df):,}", str(len(df.columns)), f"{int(df.duplicated().sum()):,}", f"{int(df['country_name'].isna().sum()):,}" if "country_name" in df else "Not available",
                   f"{int(df['city_name'].isna().sum()):,}" if "city_name" in df else "Not available", f"{int(df['aqi_value'].isna().sum()):,}" if "aqi_value" in df else "Not available",
                   "Not present", "Not present", "Not present", "Not present — AQI indicators only"]
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.markdown("#### Missingness by column")
    missing = df.isna().sum().rename("Missing values").reset_index().rename(columns={"index":"Column"})
    missing["Missing %"] = (missing["Missing values"] / max(len(df), 1) * 100).round(2)
    fig = px.bar(missing.sort_values("Missing %", ascending=True), x="Missing %", y="Column", orientation="h", template=plot_template, color="Missing %", color_continuous_scale="Teal")
    fig.update_layout(paper_bgcolor=plot_bg, plot_bgcolor=plot_bg, height=350, coloraxis_showscale=False, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Governance notes")
    st.markdown("- Keep the original downloaded CSV unchanged and record the source, access date, version and license in the project report.\n- Preserve a reproducible cleaning script; do not silently delete or impute missing country labels.\n- AQI indicators are derived index values, not pollutant concentrations.\n- There are no dates, so seasonal or temporal trends cannot be estimated from this file.\n- Avoid claiming measured industrial-corridor exposure or causal effects from this city-level dataset.")

with tab_data:
    st.markdown('<div class="section-title">Filtered records</div>', unsafe_allow_html=True)
    st.caption(f"Source: {data_source} · Showing up to 5,000 rows in the preview.")
    st.dataframe(filtered.head(5000), use_container_width=True, height=480)
    st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8-sig"), "filtered_global_air_pollution_data.csv", "text/csv")

st.divider()
st.caption("Research integrity: use this dataset for interface development and exploratory AQI-indicator comparisons. For final scientific claims about PM2.5, NO₂ and SO₂ concentrations across industrial corridors, acquire a verified concentration dataset with timestamps and station metadata.")

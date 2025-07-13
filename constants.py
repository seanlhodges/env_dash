# constants.py
from hilltoppy import Hilltop
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# --- Hilltop API Configuration ---
TRC_HILLTOP_BASE_URL = 'https://extranet.trc.govt.nz/getdata/' 
TRC_HILLTOP_HTS_FILE = 'boo.hts' # Or 'boo.hts' if that's the correct one
BASE = f"{TRC_HILLTOP_BASE_URL}{TRC_HILLTOP_HTS_FILE}"

DF_SITES = Hilltop(TRC_HILLTOP_BASE_URL, TRC_HILLTOP_HTS_FILE).get_site_list(location='LatLong').dropna()

# --- App Styling ---
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "56px",
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow-y": "auto",
}

CONTENT_STYLE = {
    "margin-left": "19rem", 
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "top": "56px", 
    "position": "relative",
}

# --- Navigation Topics ---
MAIN_TOPICS_WITH_SUB_TOPICS = {
    'Quick Reference': ['Taranaki Rainfall Summary', 
                        'River Flow Status', 
                        'Waiwhakaiho Egmont Village',
                        'Waiwhakaiho Report',
                        'Air Quality Report'],
    'Maps': [],
    'Datasets': [],
    'Charts': [],
    'Reports': [],
}

# --- Measurement Definitions for Maps/Datasets ---
# This will be populated dynamically in app.py after fetching site data
MEASUREMENTS_FOR_MAPS_AND_DATASETS = {} 

# --- Time Period Options for Dropdowns ---
TIME_PERIOD_OPTIONS_INCREMENTAL = [
    {'label': 'Last 24 Hours', 'value': '24hrs'},
    {'label': 'Last 48 Hours', 'value': '48hrs'},
    {'label': 'Last 72 Hours', 'value': '72hrs'},
    {'label': 'Last 1 Week', 'value': '1week'},
    {'label': 'Last 1 Month', 'value': '1month'},
]

TIME_PERIOD_OPTIONS_INSTANTANEOUS = [
    {'label': 'Latest Reading', 'value': 'latest'},
]

# --- Map Configuration ---
TARANAKI_MAP_CENTER = [-39.2, 174.2] # Approximate center of Taranaki
DEFAULT_MAP_ZOOM = 9

# --- Dummy Data for Hilltop Connection Errors (for robustness) ---
# Use these if fetch_site_list fails, so the app still loads
DUMMY_RAINFALL_SITES = [
    {'SiteName': 'Stratford (Rain)', 'Latitude': -39.333, 'Longitude': 174.283},
    {'SiteName': 'New Plymouth (Rain)', 'Latitude': -39.066, 'Longitude': 174.073},
    {'SiteName': 'Hawera (Rain)', 'Latitude': -39.599, 'Longitude': 174.281},
]
DUMMY_FLOW_SITES = [
    {'SiteName': 'Manganui River (Flow)', 'Latitude': -39.300, 'Longitude': 174.350},
    {'SiteName': 'Waingongoro River (Flow)', 'Latitude': -39.450, 'Longitude': 174.200},
]
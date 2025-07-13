# app.py

import dash
from dash import Input, Output, State, html, dcc, ctx, no_update
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# Import custom modules
from layout import serve_header_layout, serve_sidebar_layout, CONTENT_STYLE
from callbacks import register_callbacks
from hilltop_api import fetch_site_list, fetch_active_site_list,fetch_site_list_collection
from constants import MEASUREMENTS_FOR_MAPS_AND_DATASETS, DUMMY_RAINFALL_SITES, DUMMY_FLOW_SITES, DF_SITES, BASE

# --- Initialize Data (moved to app.py as it's part of app startup) ---
try:
    # stage_site_data = fetch_site_list(measurement="Stage")# [Water Level]")
    # flow_site_data = fetch_site_list(measurement="Flow")# [Water Level]")
    # rainfall_site_data = fetch_site_list(measurement="Rainfall")# [Rainfall]")
    # water_temperature_site_data = fetch_site_list(measurement="Water Temperature")# [Water temperature (Continuous)]")
    # air_temperature_site_data = fetch_site_list(measurement="Air Temperature (Continuous)")#[Air temperature (Continuous)]")
    
    stage_site_data = fetch_site_list_collection("WebRivers") # [Water Level]")
    flow_site_data = stage_site_data
    rainfall_site_data = fetch_site_list_collection("WebRainfall")# [Rainfall]")
    water_temperature_site_data = stage_site_data # [Water temperature (Continuous)]")
    air_temperature_site_data = fetch_site_list_collection("WebAirTemp") #[Air temperature (Continuous)]")

    # stage_site_data = fetch_active_site_list(BASE, "WebRivers", 60, DF_SITES) # [Water Level]")
    # flow_site_data = stage_site_data
    # rainfall_site_data = fetch_active_site_list(BASE, "WebRainfall", 60, DF_SITES)# [Rainfall]")
    # water_temperature_site_data = stage_site_data # [Water temperature (Continuous)]")
    # air_temperature_site_data = fetch_active_site_list(BASE, "WebAirTemp", 60, DF_SITES) #[Air temperature (Continuous)]")


    MEASUREMENTS_FOR_MAPS_AND_DATASETS.update({
        # "Rainfall (mm)": {
        #     "hilltop_measurement_name": "Rainfall",# [Rainfall]",
        #     "is_incremental": True,
        #     "sites": rainfall_site_data,
        #     "interval": "",
        #     "method": "",
        #     "measures": "Rainfall,Rainfall SCADA",
        # },
        "Hourly Rainfall (mm)": {
            "hilltop_measurement_name": "Rainfall",# [Rainfall]",
            "is_incremental": True,
            "sites": rainfall_site_data,
            "interval": "1 hour",
            "method": "Total",
            "measures": "Rainfall,Rainfall SCADA",
        },
        "Daily Rainfall (mm)": {
            "hilltop_measurement_name": "Rainfall",# [Rainfall]",
            "is_incremental": True,
            "sites": rainfall_site_data,
            "interval": "1 day",
            "method": "Total",
            "measures": "Rainfall,Rainfall SCADA",
        },
        "River Stage (m)": {
            "hilltop_measurement_name": "Stage",# [Water Level]",
            "is_incremental": False,
            "sites": stage_site_data,
            "interval": "",
            "method": "",
            "measures": "Stage",
        },
        "River Flow (m³/s)": {
            "hilltop_measurement_name": "Flow",# [Water Level]",
            "is_incremental": False,
            "sites": flow_site_data,
            "interval": "",
            "method": "",
            "measures": "Flow",
        },
        "Water Temperature (°C)": {
            "hilltop_measurement_name": "Water Temperature",# [Water temperature (Continuous)]",
            "is_incremental": False,
            "sites": water_temperature_site_data,
            "interval": "",
            "method": "",
            "measures": "Water Temperature (Continuous)",
        },
        "Air Temperature (°C)": {
            "hilltop_measurement_name": "Air Temperature",# [Air temperature (Continuous)]",
            "is_incremental": False,
            "sites": air_temperature_site_data,
            "interval": "",
            "method": "",
            "measures": "Air Temperature (Continuous)",
        }, # Add other measurements as needed
    })
    print("Successfully loaded site and measurement configurations.")
except Exception as e:
    print(f"Error loading site/measurement configurations: {e}. Using dummy data.")
    # Fallback to dummy data if Hilltop connection fails at startup
    MEASUREMENTS_FOR_MAPS_AND_DATASETS.update({
        "Rainfall (mm)": {
            "hilltop_measurement_name": "Rainfall [Rainfall]",
            "is_incremental": True,
            "sites": DUMMY_RAINFALL_SITES,
            "interval": "",
            "method": "",
            "measures": "Rainfall",
        },
        "River Flow (m³/s)": {
            "hilltop_measurement_name": "Flow",
            "is_incremental": False,
            "sites": DUMMY_FLOW_SITES,
            "interval": "",
            "method": "",
            "measures": "Flow",
        },
    })

# --- Dash App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# --- App Layout ---
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='hilltop-data-store'), # To cache fetched data for download
    serve_header_layout(),
    serve_sidebar_layout(),
    html.Div(id="page-content", style=CONTENT_STYLE), # Dynamic content area
    html.Div(id='current-page-path', style={'display': 'none'}) # Hidden div for current path
], fluid=True) # Use fluid=True for full width if desired

# Register all callbacks
register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
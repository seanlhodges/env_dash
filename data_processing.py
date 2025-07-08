# data_processing.py

import pandas as pd
from datetime import datetime, timedelta
import dash_leaflet as dl
import dash_leaflet.express as dlx

from hilltop_api import fetch_data # Your existing Hilltop API wrapper
from constants import (
    MEASUREMENTS_FOR_MAPS_AND_DATASETS, 
    TIME_PERIOD_OPTIONS_INCREMENTAL, TIME_PERIOD_OPTIONS_INSTANTANEOUS
)

# --- Helper to get data for Quick Reference Pages ---

def get_rainfall_summary_data():
    """Fetches and processes data for the Taranaki Rainfall Summary."""
    try:
        site = 'Manganui at Everett Park' # Example site, replace with dynamic logic
        measurement = 'Rainfall'
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()
        
        # Use fetch_data from hilltop_api with rainfall processing
        data_dict = fetch_data(site, measurement, start_date, end_date, process_as_rainfall=True)
        
        if data_dict and "hourly_totals" in data_dict:
            df = data_dict["hourly_totals"]
            df.columns = ['DateTime','Rainfall (mm)']
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            return df
        else:
            print(f"No hourly rainfall data for {site}.")
            return pd.DataFrame(columns=['DateTime','Rainfall (mm)'])
    except Exception as e:
        print(f"[DP-GET-RAINFALL-SUMMARY] Error in get_rainfall_summary_data: {e}")
        return pd.DataFrame(columns=['DateTime','Rainfall (mm)'])

def get_flow_status_data(sitename="Patea at Skinner Rd"):
    """Fetches and processes data for the River Flow Status quick reference page."""
    log_prefix = "[DP-GET-FLOW-STATUS-DATA]"
    flow_data = pd.DataFrame(columns=['DateTime', 'Flow (m³/s)'])
    latest_flow_value = 'N/A'
    flow_status_text = "Unavailable"

    try:
        site = sitename # Example site, replace with dynamic logic
        measurement = 'Flow'
        if site == "Waiwhakaiho at Egmont Village":
            mean_annual_flood = 337.319 # m3/s
        elif site == "Patea at Skinner Rd":
            mean_annual_flood = 158.318 # m3/s
        else:
            mean_annual_flood = 100.0
        start_date = (datetime.now() - timedelta(days=7)).isoformat() # Last 48 hrs for graph
        end_date = datetime.now().isoformat()
        
        data_dict = fetch_data(site, measurement, start_date, end_date, process_as_rainfall=False)
        
        if data_dict and "raw_data" in data_dict:
            df = data_dict["raw_data"]
            df = df[['time', 'Value']].rename(columns={'time': 'DateTime', 'Value': 'Flow (m³/s)'})
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            #df.set_index('DateTime', inplace=True)
            
            if not df.empty:
                flow_data = df
                latest_flow_value = flow_data['Flow (m³/s)'].iloc[-1] # Latest flow value
                if isinstance(latest_flow_value, (int, float)):
                    if latest_flow_value > mean_annual_flood: flow_status_text = "Greater than mean annual flood flow"
                    elif latest_flow_value < 5: flow_status_text = "Low"
                    else: flow_status_text = "Normal"
        
    except Exception as e:
        print(f"{log_prefix} Error in get_flow_status_data: {e}")

    print(f"{log_prefix} Flow data fetched for {site}: {len(flow_data)} records, latest value: {latest_flow_value}, status: {flow_status_text}")
    # Return the flow data, latest value, and status text
    return flow_data, latest_flow_value, flow_status_text, mean_annual_flood


# --- Helpers for Map Page ---

def get_map_time_period_options(selected_measurement):
    """Returns time period options based on measurement type."""
    if not selected_measurement:
        return [], None
    
    measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
    if measurement_info and measurement_info.get("is_incremental"):
        return TIME_PERIOD_OPTIONS_INCREMENTAL, '24hrs'
    else:
        return TIME_PERIOD_OPTIONS_INSTANTANEOUS, 'latest'

def process_map_data(selected_measurement, selected_time_period):
    """
    Fetches and processes data for map display markers.
    Returns a list of dl.CircleMarker components.
    """
    log_prefix = "[DP-PROCESS-MAP-DATA]"
    map_markers = []
    if not selected_measurement or not selected_time_period:
        return map_markers # Return empty if selections are incomplete

    measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
    if not measurement_info:
        return map_markers

    print(f"{log_prefix} Processing map data for {selected_measurement} in period {selected_time_period}")
    
    print(f"{log_prefix} Measurement info: {measurement_info}")
    
    hilltop_measurement_name = measurement_info["hilltop_measurement_name"]
    sites = measurement_info["sites"]
    is_incremental = measurement_info["is_incremental"]

    end_date = datetime.now()
    start_date = None
    
    if selected_time_period == 'latest':
        start_date = end_date - timedelta(hours=1) 
    elif selected_time_period == '24hrs':
        start_date = end_date - timedelta(days=1)
    elif selected_time_period == '48hrs':
        start_date = end_date - timedelta(days=2)
    elif selected_time_period == '72hrs':
        start_date = end_date - timedelta(days=3)
    elif selected_time_period == '1week':
        start_date = end_date - timedelta(weeks=1)
    elif selected_time_period == '1month':
        start_date = end_date - timedelta(days=30)

    if not start_date:
        return map_markers # Should not happen with valid `selected_time_period`

    for site in sites:
        site_name = site['SiteName']
        lat = site['Latitude']
        lon = site['Longitude']
        
        try:
            data_dict = fetch_data(
                site=site_name, 
                measurement=hilltop_measurement_name, 
                start_date=start_date.isoformat(), 
                end_date=end_date.isoformat()
            )
            data_series = data_dict["raw_data"]
            # Rename the value column to a generic 'Value' after flattening for easier access
            data_series = data_series[['time', 'Value']].rename(columns={'time': 'DateTime'})
            data_series['DateTime'] = pd.to_datetime(data_series['DateTime'])
            data_series.set_index('DateTime', inplace=True)
                
            if is_incremental:
                if data_series is not None and not data_series.empty:
                    value = data_series.iloc[:, 0].sum()
                else:
                    value = 0 
            else: # Instantaneous
                if data_series is not None and not data_series.empty:
                    value = data_series.iloc[-1, 0]
                else:
                    value = None
            
            if value is not None:
                color = 'green' # Default color
                # Adjust color based on measurement type and value (dummy thresholds)
                if selected_measurement == "Rainfall (mm)":
                    if value > 50: color = 'red'
                    elif value > 10: color = 'orange'
                elif selected_measurement == "River Flow (m³/s)":
                    if value > 10: color = 'red'
                    elif value > 3: color = 'orange'
                # Add more conditions for other measurements as needed
               
                popup_content = f"<b>{site_name}</b><br>{selected_measurement}: {value:.1f}"
                if is_incremental:
                    popup_content += f" ({selected_time_period} total)"
                else:
                    popup_content += f" (Latest)"

                map_markers.append(
                    dl.CircleMarker(
                        center=[lat, lon],
                        radius=8,
                        color=color,
                        fillColor=color,
                        fillOpacity=0.8,
                        children=[dl.Popup(content=popup_content)]
                    )
                )
            else: # No data for the site/period
                 map_markers.append(
                    dl.CircleMarker(
                        center=[lat, lon],
                        radius=4, 
                        color='grey',
                        fillColor='grey',
                        fillOpacity=0.5,
                        children=[dl.Popup(content=f"<b>{site_name}</b><br>No data for {selected_measurement} in selected period.")]
                    )
                )

        except Exception as e:
            print(f"{log_prefix} Error fetching data for {site_name}: {e}")
            map_markers.append(
                dl.Marker(
                    position=[lat, lon],
                    children=[dl.Popup(content=f"<b>{site_name}</b><br>Error fetching data: {e}")]
                )
            )
    return map_markers

# --- Helpers for Dataset Page ---

def get_dataset_site_options(selected_measurement):
    """Returns site options for the dataset dropdown based on measurement type."""
    log_prefix = "[DP-GET-DATASET-SITE-OPTIONS]"
    if not selected_measurement:
        return [], []
    print(f"{log_prefix} Fetching site options for measurement: {selected_measurement}")    
    measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
    print(f"{log_prefix} Measurement info: {MEASUREMENTS_FOR_MAPS_AND_DATASETS}")
    if measurement_info:
        sites = measurement_info.get("sites", [])
        options = [{'label': s['SiteName'], 'value': s['SiteName']} for s in sites]
        return options, []
    return [], []

def get_dataset_data_for_display(selected_measurement, selected_sites, start_date, end_date):
    """
    Fetches and combines raw data for the dataset display.
    Returns combined_df and a boolean indicating if data was found.
    """
    log_prefix = "[DP-GET-DATASET-FOR-DISPLAY]"
    all_site_data = []

    measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
    if not measurement_info:
        return pd.DataFrame(), False # Return empty df and False if measurement is invalid

    hilltop_measurement_name = measurement_info["hilltop_measurement_name"]
    
    for site_name in selected_sites:
        try:
            site_info = next((s for s in measurement_info["sites"] if s['SiteName'] == site_name), None)
            if not site_info:
                print(f"{log_prefix} Warning: Site '{site_name}' not found in measurement info for {selected_measurement}.")
                continue

            data_dict = fetch_data(
                site=site_name,
                measurement=hilltop_measurement_name, 
                start_date=start_date, 
                end_date=end_date
            )
            df = data_dict["raw_data"]
            # Ensure consistent column naming after fetch_data processing
            df = df[['time', 'Value']].rename(columns={'time': 'DateTime'})
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            
            if df is not None and not df.empty:
                df.columns = ['DateTime', 'Value'] # Explicitly name columns
                df['Site'] = site_name
                df['Measurement'] = selected_measurement
                all_site_data.append(df) # Append the processed DataFrame
            else:
                print(f"{log_prefix} No data for {site_name} - {hilltop_measurement_name} for period {start_date} to {end_date}")

        except Exception as e:
            print(f"{log_prefix} Error fetching data for site {site_name} in dataset: {e}")
            
    if not all_site_data:
        return pd.DataFrame(), False

    combined_df = pd.concat(all_site_data, ignore_index=True)
    return combined_df, True
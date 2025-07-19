# data_processing.py

import pandas as pd
from datetime import datetime, timedelta
import dash_leaflet as dl
import dash_leaflet.express as dlx
from urllib.parse import quote

from hilltop_api import (fetch_data,
                         fetch_measurement_list,
                         fetch_data_table_for_custom_collection)
from constants import (
    MEASUREMENTS_FOR_MAPS_AND_DATASETS, 
    TIME_PERIOD_OPTIONS_INCREMENTAL, 
    TIME_PERIOD_OPTIONS_INSTANTANEOUS
)


# Chose whether to see all the print statements
verbose=False # Default is False

# --- Helper to get data for Quick Reference Pages ---

def get_rainfall_summary_data(sitename='Manganui at Everett Park'):
    """Fetches and processes data for the Taranaki Rainfall Summary."""
    try:
        site = sitename # Example site, replace with dynamic logic
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
            if verbose:
                print(f"No hourly rainfall data for {site}.")
            return pd.DataFrame(columns=['DateTime','Rainfall (mm)'])
    except Exception as e:
        if verbose:
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
        if verbose:
            print(f"{log_prefix} Error in get_flow_status_data: {e}")

    if verbose:
        print(f"{log_prefix} Flow data fetched for {site}: {len(flow_data)} records, latest value: {latest_flow_value}, status: {flow_status_text}")
    # Return the flow data, latest value, and status text
    return flow_data, latest_flow_value, flow_status_text, mean_annual_flood


# --- Helpers for Map Page ---

def get_map_time_period_options(selected_measurement):
    """Returns time period options based on measurement type."""
    if not selected_measurement:
        return [], None
    
    measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
    # if measurement_info and measurement_info.get("is_incremental"):
    #     return TIME_PERIOD_OPTIONS_INCREMENTAL, '24hrs'
    # else:
    return TIME_PERIOD_OPTIONS_INSTANTANEOUS, 'latest'

# def x_process_map_data(selected_measurement, selected_time_period):
#     """
#     Fetches and processes data for map display markers.
#     Returns a list of dl.CircleMarker components.
#     """
#     log_prefix = "[DP-PROCESS-MAP-DATA]"
#     map_markers = []
#     if not selected_measurement or not selected_time_period:
#         return map_markers # Return empty if selections are incomplete

#     measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
#     if not measurement_info:
#         return map_markers

#     print(f"{log_prefix} Processing map data for {selected_measurement} in period {selected_time_period}")
    
#     print(f"{log_prefix} Measurement info: {measurement_info}")
    
#     hilltop_measurement_name = measurement_info["hilltop_measurement_name"]
#     sites = measurement_info["sites"]
#     is_incremental = measurement_info["is_incremental"]

#     print(f"{log_prefix} Using sites: {sites}")
#     print(f"{log_prefix} Using measurement: {hilltop_measurement_name}")
    
#     end_date = datetime.now()
#     start_date = None
    
#     if selected_time_period == 'latest':
#         start_date = end_date - timedelta(hours=1) 
#     elif selected_time_period == '24hrs':
#         start_date = end_date - timedelta(days=1)
#     elif selected_time_period == '48hrs':
#         start_date = end_date - timedelta(days=2)
#     elif selected_time_period == '72hrs':
#         start_date = end_date - timedelta(days=3)
#     elif selected_time_period == '1week':
#         start_date = end_date - timedelta(weeks=1)
#     elif selected_time_period == '1month':
#         start_date = end_date - timedelta(days=30)

#     if not start_date:
#         return map_markers # Should not happen with valid `selected_time_period`

#     for site in sites:
#         site_name = site['SiteName']
#         lat = site['Latitude']
#         lon = site['Longitude']
        
#         try:
#             data_dict = fetch_data(
#                 site=site_name, 
#                 measurement=hilltop_measurement_name, 
#                 start_date=start_date.isoformat(), 
#                 end_date=end_date.isoformat()
#             )
#             data_series = data_dict["raw_data"]
#             # Rename the value column to a generic 'Value' after flattening for easier access
#             data_series = data_series[['time', 'Value']].rename(columns={'time': 'DateTime'})
#             data_series['DateTime'] = pd.to_datetime(data_series['DateTime'])
#             data_series.set_index('DateTime', inplace=True)
                
#             if is_incremental:
#                 if data_series is not None and not data_series.empty:
#                     value = data_series.iloc[:, 0].sum()
#                 else:
#                     value = 0 
#             else: # Instantaneous
#                 if data_series is not None and not data_series.empty:
#                     value = data_series.iloc[-1, 0]
#                 else:
#                     value = None
            
#             if value is not None:
#                 color = 'green' # Default color
#                 # Adjust color based on measurement type and value (dummy thresholds)
#                 if selected_measurement == "Rainfall (mm)":
#                     if value > 50: color = 'red'
#                     elif value > 10: color = 'orange'
#                 elif selected_measurement == "River Flow (m³/s)":
#                     if value > 10: color = 'red'
#                     elif value > 3: color = 'orange'
#                 # Add more conditions for other measurements as needed
               
#                 popup_content = f"<b>{site_name}</b><br>{selected_measurement}: {value:.1f}"
#                 if is_incremental:
#                     popup_content += f" ({selected_time_period} total)"
#                 else:
#                     popup_content += f" (Latest)"

#                 map_markers.append(
#                     dl.CircleMarker(
#                         center=[lat, lon],
#                         radius=8,
#                         color=color,
#                         fillColor=color,
#                         fillOpacity=0.8,
#                         children=[dl.Popup(content=popup_content)]
#                     )
#                 )
#             else: # No data for the site/period
#                  map_markers.append(
#                     dl.CircleMarker(
#                         center=[lat, lon],
#                         radius=4, 
#                         color='grey',
#                         fillColor='grey',
#                         fillOpacity=0.5,
#                         children=[dl.Popup(content=f"<b>{site_name}</b><br>No data for {selected_measurement} in selected period.")]
#                     )
#                 )

#         except Exception as e:
#             print(f"{log_prefix} Error fetching data for {site_name}: {e}")
#             map_markers.append(
#                 dl.Marker(
#                     position=[lat, lon],
#                     children=[dl.Popup(content=f"<b>{site_name}</b><br>Error fetching data: {e}")]
#                 )
#             )
#     return map_markers

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

    # print(f"{log_prefix} Processing map data for {selected_measurement} in period {selected_time_period}")
    
    # print(f"{log_prefix} Measurement info: {measurement_info}")
    
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

    # Extract SiteName and recently measured sensor value into a new dictionary
    if selected_measurement== "Rainfall (mm)":
        sensor_dict = {
            site['SiteName']: {
                'value': site['Rainfall (mm)'],
                'lat': site['Latitude'],
                'long': site['Longitude']
            }
            for site in sites
        }
    elif selected_measurement == "River Stage (m)":
        sensor_dict = {
            site['SiteName']: {
                'value': site['Stage (m)'],
                'lat': site['Latitude'],
                'long': site['Longitude']
            }
            for site in sites
        }
    elif selected_measurement == "Water Temperature (°C)":
        sensor_dict = {
            site['SiteName']: {
                'value': site['Water Temperature (°C)'],
                'lat': site['Latitude'],
                'long': site['Longitude']
            }
            for site in sites
        }
    elif selected_measurement == "Air Temperature (°C)":
        sensor_dict = {
            site['SiteName']: {
                'value': site['Air Temperature (°C)'],
                'lat': site['Latitude'],
                'long': site['Longitude']
            }
            for site in sites
        }
    elif selected_measurement == "River Flow (m³/s)":
        # Assuming 'Flow (m³/sec)' is the key for river flow values
        sensor_dict = {
            site['SiteName']: {
                'value': site['Flow (m³/sec)'],
                'lat': site['Latitude'],
                'long': site['Longitude']
            }
            for site in sites
        }

    for site_name, values in sensor_dict.items():
        value = values['value']
        lat = values['lat']
        lon = values['long']
        
        if value is not None:
            color = 'green' # Default color
            # Adjust color based on measurement type and value (dummy thresholds)
            if selected_measurement == "Rainfall (mm)":
                if value > 50: color = 'red'
                elif value > 10: color = 'orange'
            elif selected_measurement == "River Flow (m³/s)":
                if value > 100: color = 'red'
                elif value > 50: color = 'orange'
            elif selected_measurement == "Water Temperature (°C)":
                if value > 25: color = 'red'
                elif value > 15: color = 'orange'
            elif selected_measurement == "Air Temperature (°C)":
                if value > 24: color = 'red'
                elif value > 10: color = 'orange'
            elif selected_measurement == "River Stage (m)":
                if value > 7: color = 'red'
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

    return map_markers

# def process_map_data_2(selected_measurement, selected_time_period):
#     """
#     Fetches and processes data for map display markers.
#     Returns a list of dl.CircleMarker components.
#     """
#     log_prefix = "[DP-PROCESS-MAP-DATA-2]"
#     map_markers = []
#     if not selected_measurement or not selected_time_period:
#         return map_markers # Return empty if selections are incomplete

#     measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
#     if not measurement_info:
#         return map_markers

#     if verbose:
#         print(f"{log_prefix} Processing map data for {selected_measurement} in period {selected_time_period}")
    
#     if verbose:
#         print(f"{log_prefix} Measurement info: {measurement_info}")
    
#     hilltop_measurement_name = measurement_info["hilltop_measurement_name"]
#     sites = measurement_info["sites"]
#     measurements = measurement_info["measures"]
#     method =measurement_info["method"]
#     interval = measurement_info["interval"]
#     is_incremental = measurement_info["is_incremental"]

#     end_date = datetime.now()
#     start_date = datetime.now() - timedelta(days=2)

#     result = ','.join(sites['SiteName'])
#     sitenames = quote(result)
#     if verbose:
#         print(f"{log_prefix}: Site list: {sitenames}")
#     measurements = quote(measurements)
#     df = fetch_data_table_for_custom_collection(sitenames,
#                                                 measurements,
#                                                 from_date=start_date,
#                                                 to_date=end_date,
#                                                 method=method,
#                                                 interval=interval)
    
#     if verbose:
#         print(f"{log_prefix}: Measurement name -> {hilltop_measurement_name}")
    
#     if hilltop_measurement_name=="Rainfall":
#         df['M1'] = df['M1'].combine_first(df['M2'])
#         df = df[["SiteName","Time","M1"]]
    
#     df_most_recent = df.groupby('SiteName').last(numeric_only=False)['M1']
    
#     if verbose:
#         print(f"{log_prefix}: Dataframe [df_most_recent]:\n{df_most_recent.head()}")
          
#     if not start_date:
#         return map_markers # Should not happen with valid `selected_time_period`

#     # join Sites with the most recent value for each requested measurement for that site
#     sites = pd.merge(sites, df_most_recent, on='SiteName', how='left') #.dropna()
#     if verbose:
#         print(f"{log_prefix}: Dataframe [sites]:\n{sites.head()}")
    
#     # Extract SiteName and most recent sensor value into a new dictionary
#     sites_dict = sites.to_dict(orient='records')
#     if verbose:
#         print(f"{log_prefix}: Site dict contents:\n{sites_dict}")

#     for item in sites_dict:
#         site_name =item["SiteName"]
#         value = item["M1"]
#         lat = item["Latitude"]
#         lon = item["Longitude"]
        
#         if value is not None:
#             color = 'green' # Default color
#             # Adjust color based on measurement type and value (dummy thresholds)
#             if selected_measurement == "Rainfall (mm)":
#                 if value > 50: color = 'red'
#                 elif value > 10: color = 'orange'
#             elif selected_measurement == "River Flow (m³/s)":
#                 if value > 100: color = 'red'
#                 elif value > 50: color = 'orange'
#             elif selected_measurement == "Water Temperature (°C)":
#                 if value > 25: color = 'red'
#                 elif value > 15: color = 'orange'
#             elif selected_measurement == "Air Temperature (°C)":
#                 if value > 24: color = 'red'
#                 elif value > 10: color = 'orange'
#             elif selected_measurement == "River Stage (m)":
#                 if value > 7: color = 'red'
#                 elif value > 3: color = 'orange'
#             # Add more conditions for other measurements as needed
            
#             popup_content = f"<b>{site_name}</b><br>{selected_measurement}: {value:.1f}"
#             # if is_incremental:
#             #     popup_content += f" ({selected_time_period} total)"
#             # else:
#             #     popup_content += f" (Latest)"
#             popup_content += f" (Latest)"
#             map_markers.append(
#                 dl.CircleMarker(
#                     center=[lat, lon],
#                     radius=8,
#                     color=color,
#                     fillColor=color,
#                     fillOpacity=0.8,
#                     children=[dl.Popup(content=popup_content)]
#                 )
#             )
#         else: # No data for the site/period
#                 map_markers.append(
#                 dl.CircleMarker(
#                     center=[lat, lon],
#                     radius=4, 
#                     color='grey',
#                     fillColor='grey',
#                     fillOpacity=0.5,
#                     children=[dl.Popup(content=f"<b>{site_name}</b><br>No data for {selected_measurement} in selected period.")]
#                 )
#             )

#     return map_markers

# data_processing.py

# ... (rest of your code)

def process_map_data_2(selected_measurement, selected_time_period):
    """
    Fetches and processes data for map display markers.
    Returns a list of dl.CircleMarker components.
    """
    verbose=True
    log_prefix = "[DP-PROCESS-MAP-DATA-2]"
    map_markers = []
    if not selected_measurement or not selected_time_period:
        if verbose: print(f"{log_prefix} Incomplete selection: {selected_measurement}, {selected_time_period}. Returning empty markers.")
        return map_markers

    measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
    if not measurement_info:
        if verbose: print(f"{log_prefix} No measurement info for: {selected_measurement}. Returning empty markers.")
        return map_markers

    if verbose:
        print(f"\n{log_prefix} --- START PROCESSING FOR: {selected_measurement} ({selected_time_period}) ---")
        print(f"{log_prefix} Initial Measurement info sites type: {type(measurement_info['sites'])}")
    
    hilltop_measurement_name = measurement_info["hilltop_measurement_name"]
    # CRITICAL: Create a COPY of the sites DataFrame to ensure it's clean for each merge.
    # This might be the culprit if 'sites' was somehow being modified in place or retaining columns
    sites_base_df = measurement_info["sites"].copy() # <--- ADDED .copy() HERE
    
    measurements_str = measurement_info["measures"]
    method = measurement_info["method"]
    interval = measurement_info["interval"]
    is_incremental = measurement_info["is_incremental"]

    end_date = datetime.now()
    start_date = datetime.now() - timedelta(days=2) # This is a fixed window for all requests

    result = ','.join(sites_base_df['SiteName'])
    sitenames_quoted = quote(result)
    measurements_quoted = quote(measurements_str)
    
    if verbose:
        print(f"{log_prefix}: Requesting data for sites: {sites_base_df['SiteName'].tolist()}")
        print(f"{log_prefix}: Requesting data for measures: {measurements_str}")
        print(f"{log_prefix}: Using method: '{method}', interval: '{interval}'")
        print(f"{log_prefix}: Date range: {start_date.isoformat()} to {end_date.isoformat()}")

    df_fetched_raw = fetch_data_table_for_custom_collection(
        sitenames_quoted,
        measurements_quoted,
        from_date=start_date,
        to_date=end_date,
        method=method,
        interval=interval
    )
    
    if df_fetched_raw.empty:
        if verbose: print(f"{log_prefix}: No raw data fetched for {selected_measurement}. Returning empty markers.")
        return map_markers

    if verbose:
        print(f"{log_prefix}: Raw fetched data columns: {df_fetched_raw.columns.tolist()}")
        print(f"{log_prefix}: Raw fetched data head:\n{df_fetched_raw.head()}")
    
    # Standardize 'M1' if 'M2' contains the primary data for Rainfall as per app.py logic
    if hilltop_measurement_name == "Rainfall": # Based on app.py, Rainfall uses M1 or M2
        if 'M2' in df_fetched_raw.columns:
            df_fetched_raw['M1'] = df_fetched_raw['M1'].combine_first(df_fetched_raw['M2'])
            if verbose: print(f"{log_prefix}: Combined M1 and M2 for Rainfall.")
        df_processed = df_fetched_raw[["SiteName", "Time", "M1"]]
    else:
        # For other measurements, assume M1 is the relevant column
        if 'M1' in df_fetched_raw.columns:
            df_processed = df_fetched_raw[["SiteName", "Time", "M1"]]
        else:
            if verbose: print(f"{log_prefix}: 'M1' column not found for {selected_measurement}. Available columns: {df_fetched_raw.columns.tolist()}")
            return map_markers # Cannot proceed without M1

    # Get the last valid reading for 'M1' for each site
    # This needs to handle potential NaNs correctly
    # Get the last valid reading for 'M1' for each site
    # This revised apply directly selects the 'M1' value, resulting in a Series.
    # Then .dropna() removes any sites that had no valid 'M1' value.
    df_most_recent = df_processed.groupby('SiteName', group_keys=False)['M1'].apply(
        lambda x: x.loc[x.last_valid_index()] if x.last_valid_index() is not None else None
    ).dropna()

    # --- FIX STARTS HERE ---
    # Now, df_most_recent is a Series with SiteName as its index.
    # reset_index() will convert the Series into a DataFrame and promote the index ('SiteName') to a column.
    df_most_recent = df_most_recent.reset_index(name='M1') # Name the value column 'M1' after reset
    # --- FIX ENDS HERE ---

    if verbose:
        print(f"{log_prefix}: df_most_recent (after groupby, apply on M1, dropna, and reset_index):\n{df_most_recent.head()}")
        print(f"{log_prefix}: df_most_recent columns (after reset_index): {df_most_recent.columns.tolist()}")
          
    # Merge the base site information with the most recent sensor value
    # Now df_most_recent has 'SiteName' and 'M1' as columns.
    sites_with_data = pd.merge(sites_base_df, df_most_recent[['SiteName', 'M1']], on='SiteName', how='left')
        
    if verbose:
        print(f"{log_prefix}: Merged 'sites_with_data' DataFrame head:\n{sites_with_data.head()}")
        print(f"{log_prefix}: Merged 'sites_with_data' DataFrame columns:\n{sites_with_data.columns.tolist()}")
        # Check if _merge column shows issues like 'both' where it should be 'left_only' or vice versa
        # print(f"{log_prefix}: Merge indicator counts:\n{sites_with_data['_merge'].value_counts()}")
    
    sites_dict = sites_with_data.to_dict(orient='records')
    
    for item in sites_dict:
        site_name = item["SiteName"]
        value = item.get("M1") # Use .get() for safer access, returns None if not present
        lat = item["Latitude"]
        lon = item["Longitude"]
        
        if verbose: print(f"{log_prefix}: Processing site '{site_name}'. Raw value from merged DF: {value}")

        if pd.isna(value): # Explicitly check for NaN using pd.isna
            color = 'grey'
            radius = 4
            popup_content = f"<b>{site_name}</b><br>No recent data for {selected_measurement}."
            if verbose: print(f"{log_prefix}: Site '{site_name}': No data (NaN), using grey marker.")
        else:
            radius = 8
            color = 'green' # Default color
            
            # Your existing color logic
            if selected_measurement == "Hourly Rainfall (mm)" or selected_measurement == "Daily Rainfall (mm)":
                if value > 50: color = 'red'
                elif value > 10: color = 'orange'
            elif selected_measurement == "River Flow (m³/s)":
                if value > 100: color = 'red'
                elif value > 50: color = 'orange'
            elif selected_measurement == "Water Temperature (°C)":
                if value > 25: color = 'red'
                elif value > 15: color = 'orange'
            elif selected_measurement == "Air Temperature (°C)":
                if value > 24: color = 'red'
                elif value > 10: color = 'orange'
            elif selected_measurement == "River Stage (m)":
                if value > 7: color = 'red'
                elif value > 3: color = 'orange'
            
            popup_content = f"<b>{site_name}</b><br>{selected_measurement}: {value:.1f} (Latest)"
            if verbose: print(f"{log_prefix}: Site '{site_name}': Data {value:.1f}, color {color}.")

        map_markers.append(
            dl.CircleMarker(
                center=[lat, lon],
                radius=radius,
                color=color,
                fillColor=color,
                fillOpacity=0.8,
                children=[dl.Popup(content=popup_content)]
            )
        )
    
    if verbose: print(f"{log_prefix} --- END PROCESSING FOR: {selected_measurement} ---")
    return map_markers

# --- Helpers for Dataset Page ---

def get_dataset_site_options(selected_measurement):
    """Returns site options for the dataset dropdown based on measurement type."""
    log_prefix = "[DP-GET-DATASET-SITE-OPTIONS]"
    if not selected_measurement:
        return [], []
    if verbose:
        print(f"{log_prefix} Fetching site options for measurement: {selected_measurement}")    
    measurement_info = MEASUREMENTS_FOR_MAPS_AND_DATASETS.get(selected_measurement)
    if verbose:
        print(f"{log_prefix} Measurement info: {MEASUREMENTS_FOR_MAPS_AND_DATASETS}")
    if measurement_info:
        sites = measurement_info.get("sites", [])
        sites = sites.to_dict(orient='records')
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
    measurements = measurement_info["measures"]
    method =measurement_info["method"]
    interval = measurement_info["interval"]
    
    for site_name in selected_sites:
        try:
            site_info = next((s for s in measurement_info["sites"].to_dict(orient='records') if s['SiteName'] == site_name), None)
            # print(f"{log_prefix} {site_info}")
            
            if not site_info:
                if verbose:
                    print(f"{log_prefix} Warning: Site '{site_name}' not found in measurement info for {selected_measurement}.")
                continue

            df = fetch_data_table_for_custom_collection(site_name,
                                            measurements,
                                            from_date=start_date,
                                            to_date=end_date,
                                            method=method,
                                            interval=interval)
            
            if verbose:
                print(f"{log_prefix}: Dataframe [df] -> {df.head()}")
            
            # Ensure consistent column naming after fetch_data processing
            if df is not None and not df.empty:                
                df = df[['Time', 'M1']].rename(columns={'Time': 'DateTime', 'M1': "Value"})
                if verbose:
                    print(f"{log_prefix}: Dataframe [df] -> {df.head()}")
                # df['DateTime'] = pd.to_datetime(df['DateTime'])
                df['Measurement'] = selected_measurement
                df['SiteName'] = site_name
                if verbose:
                    print(f"{log_prefix}: Dataframe [df] -> {df.info()}")
                all_site_data.append(df) # Append the processed DataFrame
            else:
                if verbose:
                    print(f"{log_prefix} No data for {site_name} - {hilltop_measurement_name} for period {start_date} to {end_date}")

        except Exception as e:
            if verbose:
                print(f"{log_prefix} Error fetching data for site {site_name} in dataset: {e}")
            
    if not all_site_data:
        return pd.DataFrame(), False

    combined_df = pd.concat(all_site_data, ignore_index=True)
    return combined_df, True
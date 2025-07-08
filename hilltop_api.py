from hilltoppy import Hilltop
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
import pytz
from io import StringIO

# Create a connection to the TRC Hilltop server
SERVER_URL = "https://extranet.trc.govt.nz/getdata"
hts = "boo.hts"
url= f"{SERVER_URL}/{hts}"
ht = Hilltop(SERVER_URL,hts)
df_sites = ht.get_site_list(location='LatLong').dropna()

def fetch_site_list(measurement="Flow"):
    """Returns a list of dicts: [{name, lat, lon}]"""
    log_prefix = "[HT-API-FETCH-SITE-LIST]"
    sites_df = ht.get_site_list(location='LatLong', measurement=measurement)
    print(f"{log_prefix}: {type(sites_df)} Found {len(sites_df)} sites for measurement '{measurement}'")
    # Need to add measurement from and to dates check to this list
    #  to ensure sites are active for the measurement
    
    
    return sites_df.to_dict(orient="records")

def fetch_measurements(site):
    """Returns list of (name, units) tuples"""
    measurements_df = ht.get_measurement_list(site)
    # print(f"Found {len(measurements_df)} measurements for site {site}")
    # print(measurements_df.columns)
    return list(zip(measurements_df["MeasurementName"], measurements_df["Units"]))

def fetch_measurement_list(site):
    measurements_df = ht.get_measurement_list(site)
    measurements_df = measurements_df[["SiteName","MeasurementName", "Units", "From", "To"]]
    
    """Returns a DataFrame with measurement details for a site"""

    return measurements_df

def active_measurement(df,measurement="Flow"):
    """Returns the active measurements for a site"""
    log_prefix = "[HT-API-ACTIVE-MEASUREMENT]"
    df = df[df["MeasurementName"]=='Flow']
    df["To_Year"] =  df['To'].dt.year
    df = df[df["To_Year"]==df["To_Year"].max()]
    if not df.empty:
        return df
    else:
        print(f"{log_prefix} No active measurements found for {measurement} at site.")
        df = pd.DataFrame(columns=["SiteName", "MeasurementName", "Units", "From", "To"])
        return


def fetch_data(site, measurement, start_date, end_date, process_as_rainfall=False):
    """
    Returns a DataFrame with time series values.
    If process_as_rainfall is True, calculates hourly and daily totals for rainfall data.
    """
    log_prefix = "[HT-API-FETCH-DATA]"
    df = ht.get_data(site, measurement, start_date, end_date)
    
    if df is None or df.empty:
        print(f"[HT-API-FETCH-DATA] No data returned from Hilltop for {site}, {measurement} between {start_date} and {end_date}")
        return pd.DataFrame(columns=["time", "value"]) # Return empty DataFrame

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)  # flatten in case of multi-sensor
    # print(df.columns)  # Debug: print columns to understand structure
    # Rename the value column to a generic 'value' for consistency
    # Assuming the first column after index is the value column
    value_col_name = df.columns[0]
    print(f"{log_prefix} Processing data for {site} - {measurement}, value column: {value_col_name}")
    df = df.rename(columns={value_col_name: "value"})
    
    df = df.reset_index()
    df = df.rename(columns={"Time": "time"}) # Ensure 'Time' column is named 'time'

    # Ensure 'time' column is datetime and set as index for resampling
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')

    if process_as_rainfall: # Check if it's rainfall and aggregation is requested
        print(f"{log_prefix}  Processing {measurement} data for {site} as rainfall totals...")
        
        # Calculate hourly totals
        # .resample('H') groups data by hour. .sum() aggregates values within each hour.
        # .fillna(0) ensures hours with no rainfall get 0 instead of NaN.
        hourly_totals = df['Value'].resample('h').sum()#.rename('hourly_total_mm')
        print(hourly_totals.head(12))  # Debug: print first few hours to verify structure
        # Calculate daily totals
        # .resample('D') groups data by day. .sum() aggregates values within each day.
        daily_totals = df['Value'].resample('D').sum()#.rename('daily_total_mm')
        # print(daily_totals.head(12))  # Debug: print first few days to verify structure
        # Combine into a single DataFrame for return, or return separately as needed
        # For simplicity, let's return a DataFrame with original, hourly, and daily totals
        # Merging back to the original index is tricky for totals, better to return aggregated DFs
        # print(f"Hourly totals calculated: {hourly_totals.shape[0]} hours")
        # print(f"Daily totals calculated: {daily_totals.shape[0]} days") 
        # Option 1: Return a dictionary of DataFrames
        print(f"{log_prefix}  Returning dict with raw, hourly, and daily totals for {site} ({measurement})")
        return {
            "raw_data": df.reset_index(), # Original raw data with 'time' column
            "hourly_totals": hourly_totals.reset_index(),
            "daily_totals": daily_totals.reset_index()
        }
        
        # Option 2: Return just the aggregated data, or choose which one
        # For now, we will stick to Option 1 as it provides more flexibility for different quick reference pages.

    else:
        # For non-rainfall data or if aggregation is not requested, return the raw data
        print(f"{log_prefix} Returning raw data for {site} ({measurement}) with {df.shape[0]} rows")
        return {"raw_data": df.reset_index()}
    
    


def fetch_and_parse_hilltop_data(base_url=url,
                                 collection="WebRivers",
                                 minutes_ago=90):
    # Get NZ local time 90 minutes ago
    nz_tz = pytz.timezone("Pacific/Auckland")
    from_time = datetime.now(nz_tz) - timedelta(minutes=minutes_ago)
    from_str = from_time.strftime("%-d-%b-%Y %H:%M:%S")  # e.g., 7-Jul-2025 21:00:00

    # Build URL with query parameters
    params = {
        "service": "Hilltop",
        "request": "DataTable",
        "collection": collection,
        "from": from_str,
    }

    # Make the GET request
    response = requests.get(base_url, params=params)
    response.raise_for_status()

    xml_string = response.text
    return parse_hilltop_xml(xml_string)

def fetch_and_parse_recent_hilltop_data(base_url=url,
                                 collection="WebRivers"):
    # Get NZ local time 90 minutes ago
    # nz_tz = pytz.timezone("Pacific/Auckland")
    # from_time = datetime.now(nz_tz) - timedelta(minutes=minutes_ago)
    # from_str = from_time.strftime("%-d-%b-%Y %H:%M:%S")  # e.g., 7-Jul-2025 21:00:00

    # Build URL with query parameters
    params = {
        "service": "Hilltop",
        "request": "RecentDataTable",
        "collection": collection,
        # "from": from_str,
    }

    # Make the GET request
    response = requests.get(base_url, params=params)
    response.raise_for_status()

    xml_string = response.text
    return parse_hilltop_xml(xml_string)


def parse_hilltop_xml(xml_string):
    root = ET.parse(StringIO(xml_string)).getroot()

    # Step 1: Build mapping from ColumnName → "Measurement (Units)"
    column_map = {}
    for m in root.findall(".//Measurements"):
        column = m.findtext("ColumnName")
        name = m.findtext("Measurement")
        units = m.findtext("Units")
        if column:
            label = f"{name} ({units})" if units else name
            column_map[column] = label

    # Step 2: Parse Results
    records = []
    for result in root.findall(".//Results"):
        record = {
            "SiteName": result.findtext("SiteName"),
            "Time": result.findtext("Time"),
        }
        for col_key in column_map:
            record[column_map[col_key]] = result.findtext(col_key)
        records.append(record)

    df = pd.DataFrame(records)

    # Step 3: Type conversion
    df["Time"] = pd.to_datetime(df["Time"])
    for col in df.columns:
        if col not in ["SiteName", "Time"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def get_latest_by_site(df):
    """
    Given a DataFrame with 'SiteName' and 'Time', return the latest row for each SiteName.
    """
    log_prefix = "[HT-API-GET-LATEST-BY-SITE]"
    
    if "SiteName" not in df.columns or "Time" not in df.columns:
        raise ValueError(f"{log_prefix} DataFrame must include 'SiteName' and 'Time' columns.")

    # Ensure Time is datetime
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

    # Drop rows with missing times
    df = df.dropna(subset=["Time"])

    # Sort and get last row per SiteName
    latest_df = df.sort_values("Time").groupby("SiteName", as_index=False).tail(1)
    latest_df = latest_df.sort_values("SiteName") #.set_index('SiteName', inplace=True)
    
    
    return latest_df.reset_index(drop=True)


def fetch_active_site_list(base_url=url, 
                           collection="WebRivers", 
                           minutes_ago=60, 
                           df_sites=df_sites):
    """ 
    Fetches and parses Hilltop data, returning the latest readings for each site.
    The function merges the site data with the latest readings to provide a complete view.
    The `minutes_ago` parameter allows you to specify how far back to look for data    
    """
    df = fetch_and_parse_hilltop_data(base_url, collection, minutes_ago)
    df = get_latest_by_site(df)
    df = pd.merge(df, df_sites, on='SiteName', how='left')
    
    return df.to_dict(orient="records") #.set_index('SiteName', inplace=True)

def fetch_recent_active_site_list(base_url=url, 
                           collection="WebRivers", 
                           df_sites=df_sites):
    """ 
    Fetches and parses Hilltop data, returning the latest readings for each site.
    The function merges the site data with the latest readings to provide a complete view.
    The `minutes_ago` parameter allows you to specify how far back to look for data    
    """
    df = fetch_and_parse_recent_hilltop_data(base_url, collection)
    df = pd.merge(df, df_sites, on='SiteName', how='left')
    
    return df.to_dict(orient="records") #.set_index('SiteName', inplace=True)
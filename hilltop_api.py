from hilltoppy import Hilltop
import pandas as pd

# Create a connection to the TRC Hilltop server
SERVER_URL = "https://extranet.trc.govt.nz/getdata"
hts = "boo.hts"
ht = Hilltop(SERVER_URL,hts)

def fetch_site_list(measurement="Flow"):
    """Returns a list of dicts: [{name, lat, lon}]"""
    sites_df = ht.get_site_list(location='LatLong', measurement=measurement)
    return sites_df.to_dict(orient="records")

def fetch_measurements(site):
    """Returns list of (name, units) tuples"""
    measurements_df = ht.get_measurement_list(site)
    print(f"Found {len(measurements_df)} measurements for site {site}")
    print(measurements_df.columns)
    return list(zip(measurements_df["MeasurementName"], measurements_df["Units"]))

# def fetch_data(site, measurement, start_date, end_date):
#     """Returns a DataFrame with time series values"""
#     df = ht.get_data(site, measurement, start_date, end_date)
#     # print(df.columns)
#     if isinstance(df.columns, pd.MultiIndex):
#         df.columns = df.columns.get_level_values(0)  # flatten in case of multi-sensor
#     df = df.reset_index()

#     return df[["Time", "Value"]].rename(columns={"Time": "time", "Value": "value"}) 

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
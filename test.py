from hilltop_api import fetch_active_site_list, fetch_site_list, fetch_recent_active_site_list
import pandas as pd
from hilltoppy import Hilltop
from datetime import datetime, timedelta    

# --- Hilltop API Configuration ---
TRC_HILLTOP_BASE_URL = 'https://extranet.trc.govt.nz/getdata/' 
TRC_HILLTOP_HTS_FILE = 'default.hts' # Or 'boo.hts' if that's the correct one

base = f"{TRC_HILLTOP_BASE_URL}{TRC_HILLTOP_HTS_FILE}"

df_sites = Hilltop(TRC_HILLTOP_BASE_URL, TRC_HILLTOP_HTS_FILE).get_site_list(location='LatLong').dropna()

# Fetch and parse Hilltop data for the last 60 minutes
active_sites_df = fetch_active_site_list(base, "WebRivers", 60, df_sites)
print(active_sites_df[:10])
sites_df = fetch_site_list(measurement="Flow")
print(sites_df[:10])

# Fetch and parse recent Hilltop data for the last 60 minutes
active_sites_df = fetch_recent_active_site_list(base, "WebRivers", df_sites)
print(active_sites_df[:10])
sites_df = fetch_site_list(measurement="Flow")
print(sites_df[:10])
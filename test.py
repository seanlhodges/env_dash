from hilltop_api import (
    fetch_site_list_collection, 
    fetch_data_table_for_custom_collection, 
    fetch_active_site_list, 
    fetch_collection_list, 
    fetch_data)
import pandas as pd
from hilltoppy import Hilltop
from datetime import datetime, timedelta  
import requests  

# --- Hilltop API Configuration ---
TRC_HILLTOP_BASE_URL = 'https://extranet.trc.govt.nz/getdata/' 
TRC_HILLTOP_HTS_FILE = 'boo.hts' # Or 'boo.hts' if that's the correct one

base = f"{TRC_HILLTOP_BASE_URL}{TRC_HILLTOP_HTS_FILE}"

df_sites = Hilltop(TRC_HILLTOP_BASE_URL, TRC_HILLTOP_HTS_FILE).get_site_list(location='LatLong').dropna()
#print(df_sites.head())

# result = ','.join(df_sites['SiteName'])
# print(result)
# # Fetch and parse Hilltop data for the last 60 minutes
# active_sites_df = fetch_active_site_list(base, "WebRivers", 60, df_sites)
# print(active_sites_df[:10])
# sites_df = fetch_site_list(measurement="Flow")
# print(sites_df[:10])

# # Fetch and parse recent Hilltop data for the last 60 minutes
# active_sites_df = fetch_recent_active_site_list(base, "WebRivers", df_sites)
# print(active_sites_df[:10])
# sites_df = fetch_site_list(measurement="Flow")
# print(sites_df[:10])


def fetch_some_data(site, measurement, from_date=None, to_date=None):
    try:
        if from_date and to_date:
            df = fetch_data(
                site,
                measurement,
                from_date,
                to_date
            )
        else:
            df = fetch_active_site_list(base, "WebRivers", 60, df_sites)

        df["SiteName"] = site
        df["Measurement"] = measurement
        return df
    except Exception as e:
        print(f"Error fetching {site} - {measurement}: {e}")
        return None




# print(collections.head())
print("FETCH-CUSTOM-COLLECTION")
from urllib.parse import quote

collection = "WebRivers"
sitelist = fetch_site_list_collection(collection)
result = ','.join(sitelist['SiteName'])
#print(result)

# sites = quote("Waitotara at Rimunui Station,Waiwhakaiho at Egmont Village,Waiwhakaiho at Hillsborough,Whanganui at Mataimona Trig")
sites = quote(result)
measurements = quote("Stage")
df = fetch_data_table_for_custom_collection(sites,
                                            measurements,
                                            from_date='2025-07-01',
                                            to_date='2025-07-12',
                                            method='',
                                            interval='')

#df['Rainfall'] = df['M1'].combine_first(df['M2'])
print(df.head())


end_date = datetime.now()
start_date = datetime.now() - timedelta(days=2)

print(start_date)
print(end_date)

html.P("Suspension bridge on the Kurapete Walk at Everett Park Scenic Reserve. <b>Image</b>: Jaime Apolonio | Creative Commons"),
html.P(children=["Suspension bridge on the Kurapete Walk at Everett Park Scenic Reserve.",
                    html.B("Image:"),
                    html.I("Jaime Apolonio"),
                    " | ",
                    html.a("Creative Commons", 
                           href="https://creativecommons.org/licenses/by-nc/4.0/",
                           target="_blank")
    
])
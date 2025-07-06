from hilltoppy import Hilltop

# TRC hydrology endpoint
BASE_URL = "https://extranet.trc.govt.nz/getdata/"
hts = "boo.hts"
server = Hilltop(BASE_URL,hts)

def list_sites_with_coords(measurement='Flow [Water Level]'):
    """
    Retrieve all TRC hydrology sites that include lat/lon coordinates.
    Returns:
        DataFrame with SiteName, Latitude, Longitude
    """
    # df = server.get_site_list(location="LatLong", measurement=measurement)
    df = server.get_site_list(location="LatLong", collection="WebRivers")
    
    return df.dropna(subset=["Latitude", "Longitude"])

def list_measurements_for_site(site_name):
    """
    Get the list of available measurements (e.g., Flow, Water Level) for a given site.

    Args:
        site_name (str): Exact site name as listed in Hilltop

    Returns:
        DataFrame of measurement names
    """
    return server.get_measurement_list(sites=site_name)

def get_site_data(site_name, measurement, start, end):
    """
    Fetch time series data for a site and measurement between two datetimes.

    Args:
        site_name (str): Site name
        measurement (str): e.g., 'Flow' or 'Water Level'
        start (str): 'YYYY-MM-DD HH:MM:SS'
        end (str): 'YYYY-MM-DD HH:MM:SS'

    Returns:
        DataFrame indexed by datetime with a 'Value' column
    """
    return server.get_data(
        sites=site_name,
        measurements=measurement,
        from_date=start,
        to_date=end,
        agg_method=None,
        agg_interval=None
    )

if __name__ == "__main__":
    # List sites with coordinates
    df = list_sites_with_coords()
    print(df.head(20))    
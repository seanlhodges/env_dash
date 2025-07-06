def build_site_geojson(sites):
    features = []
    for site in sites:
        if site["Latitude"] is None or site["Longitude"] is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [site["Longitude"], site["Latitude"]]
            },
            "properties": {
                "name": site["SiteName"]
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }

# Readme.md

## About

Inspired by the portals of some other regional councils, this dashboard is a small attempt to replicate some of that capability within the dash framework. 

Google's Gemini AI has been use to build out the skeleton code, with further updates being added by the human part of this collaboration.

The main code is separated out into six files

- app.py: sets up the application
- callback.py: handles the application responses
- constants.py: global variables
- data_processing.py: a helper file that handles some of the heavy lifting in the app
- hilltop_api.py: handles all hilltop data extraction
- layout.py: lays out structure and content of the dash application

## Issues

1. Production of the mapped points for measurements still relies on individual calls to hilltop for data at each site - as a result, building the map takes too long. This needs to be replaced by a single call using ```DataTable``` or ```RecentDataTable```. These methods have been built and can be found in the ```hilltop_api.py``` file. This will make the map more responsive.

2. Charts and reports are yet to be built. The first report will likely be about the Jul 3rd, 2025 rainfall event

3. Rainfall is not well handled yet. I need to add some aggregation options to have hourly, and daily rainfall totals shown on maps and in tables.

4. And many more ...

## Important Considerations and Next Steps:

Note: these notes were created by Google Gemini AI. Any use of "I" or "I've" is the AI talking.

1. Initial MEASUREMENTS_FOR_MAPS_AND_DATASETS Population

I've moved the initial Hilltop calls for flow_site_data and rainfall_site_data into app.py before app.layout is defined. This ensures that MEASUREMENTS_FOR_MAPS_AND_DATASETS is populated with actual site data from Hilltop (or dummy data if Hilltop fails) at application startup. This dictionary is then imported and used by layout.py and data_processing.py.

2. Hilltop API Integration in data_processing.py

Ensure your hilltop_api.py has the fetch_data function that correctly handles both raw data and processed rainfall data (as discussed in the previous response).

The fetch_site_list and fetch_measurements from hilltop_api.py are used to populate MEASUREMENTS_FOR_MAPS_AND_DATASETS at startup.

3. Error Handling and Empty DataFrames

I've added more robust checks for empty or None DataFrames in data_processing.py to prevent errors in visualizations or tables if no data is returned from Hilltop.

4. Code Readability and Maintainability

Each file now has a clear purpose. If you need to change a layout, go to layout.py. If you need to fix data fetching logic, go to data_processing.py. This significantly reduces the cognitive load when working on specific features.

Imports: Be mindful of circular imports. The current structure (app imports layout and callbacks, callbacks imports layout and data_processing, data_processing imports hilltop_api and constants) should generally avoid circular dependencies.

5. Extendability

Adding New Quick Reference Pages: Add the page's name to MAIN_TOPICS_WITH_SUB_TOPICS, create a new serve_quick_reference_XYZ_layout() function in layout.py, and a corresponding get_XYZ_data() in data_processing.py (if it needs data). Then, add a new entry to the page_layouts dictionary in display_page in callbacks.py.

Adding New Measurement Types: Update MEASUREMENTS_FOR_MAPS_AND_DATASETS in constants.py and ensure your hilltop_api.py fetch_data can handle the new measurement. The map_page_layout and datasets_page_layout will automatically pick up new measurement types in their dropdowns.

Charts/Reports: These pages are currently placeholders. You can implement them with dedicated functions in layout.py and data_processing.py as you did for maps and datasets.

This modular approach makes your Dash application much cleaner, easier to navigate, and more scalable for future development.
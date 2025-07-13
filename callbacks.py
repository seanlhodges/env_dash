# callbacks.py
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd 
import io

from layout import (
    serve_header_layout, serve_sidebar_layout, serve_default_page_layout,
    serve_quick_reference_rainfall_summary_layout, serve_quick_reference_river_flow_status_layout, 
    serve_quick_reference_air_quality_report_layout,serve_quick_reference_waiwhakaiho_report_layout,
    serve_map_page_layout,serve_quick_reference_waiwhakaiho_egmont_village_layout,
    serve_datasets_page_layout, create_dataset_display,
    serve_charts_page_layout, serve_reports_page_layout
)
from data_processing import (
    get_map_time_period_options, process_map_data, process_map_data_2, 
    get_dataset_site_options, get_dataset_data_for_display,
    get_rainfall_summary_data, get_flow_status_data # NOW IMPORTED HERE
)
from constants import MEASUREMENTS_FOR_MAPS_AND_DATASETS 


def register_callbacks(app):
    """Registers all callbacks with the Dash app."""

    # Callback for Navbar Toggler
    @app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # Callback to update URL based on accordion button clicks
    @app.callback(
        Output('url', 'pathname'),
        Output('main-sidebar-accordion', 'active_item'),
        Input({'type': 'sidebar-sub-topic-button', 'index': dash.ALL}, 'n_clicks'),
        Input({'type': 'sidebar-main-topic-button', 'index': dash.ALL}, 'n_clicks'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def update_url_and_active_accordion(*args):
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        current_path = args[-1] 

        if 'sidebar-sub-topic-button' in button_id:
            button_data = eval(button_id)
            topic_and_sub_topic = button_data['index']
            
            main_topic_parts = topic_and_sub_topic.split('-')
            # Assuming 'Quick-Reference' is always the first two parts of the index
            main_topic_name = "-".join(main_topic_parts[:2]) 
            
            new_pathname = f"/{topic_and_sub_topic.lower()}"
            return new_pathname, f"accordion-item-{main_topic_name}"
            
        elif 'sidebar-main-topic-button' in button_id:
            button_data = eval(button_id)
            main_topic_name = button_data['index']
            new_pathname = f"/{main_topic_name.lower()}"
            return new_pathname, f"accordion-item-{main_topic_name}"
        
        return current_path, dash.no_update

    # Callback to update page content based on URL path (navigation)
    @app.callback(
        Output('page-content', 'children'),
        Output('current-page-path', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/quick-reference-taranaki-rainfall-summary':
            rainfall_data = get_rainfall_summary_data() # Fetch data here!
            return serve_quick_reference_rainfall_summary_layout(rainfall_data), pathname
        elif pathname == '/quick-reference-river-flow-status':
            flow_data, latest_flow_value, flow_status_text, mean_annual_flood = get_flow_status_data(sitename="Patea at Skinner Rd") # Fetch data here!
            return serve_quick_reference_river_flow_status_layout(flow_data, latest_flow_value, flow_status_text, mean_annual_flood), pathname
        elif pathname == '/quick-reference-waiwhakaiho-egmont-village':
            flow_data, latest_flow_value, flow_status_text, mean_annual_flood = get_flow_status_data(sitename="Waiwhakaiho at Egmont Village") # Fetch data here!
            return serve_quick_reference_waiwhakaiho_egmont_village_layout(flow_data, latest_flow_value, flow_status_text, mean_annual_flood), pathname
        elif pathname == '/quick-reference-waiwhakaiho-report':
           return serve_quick_reference_waiwhakaiho_report_layout(), pathname
        elif pathname == '/quick-reference-air-quality-report':
            return serve_quick_reference_air_quality_report_layout(), pathname
        elif pathname == '/maps':
            return serve_map_page_layout(), pathname
        elif pathname == '/datasets':
            return serve_datasets_page_layout(), pathname
        elif pathname == '/charts':
            return serve_charts_page_layout(), pathname
        elif pathname == '/reports':
            return serve_reports_page_layout(), pathname
        else:
            default_path = '/quick-reference-taranaki-rainfall-summary'
            return serve_default_page_layout(), default_path

    # --- Callbacks for Maps Page ---
    @app.callback(
        Output('map-time-period-dropdown', 'options'),
        Output('map-time-period-dropdown', 'value'),
        Input('map-measurement-dropdown', 'value'),
        # prevent_initial_call=True
    )
    def update_map_time_period_options(selected_measurement):
        return get_map_time_period_options(selected_measurement)


    @app.callback(
        Output("marker-layer", "children"),
        Input("map-measurement-dropdown", "value"),
        Input("map-time-period-dropdown", "value")
    )
    def update_map_markers(selected_measurement, selected_time_period):
        print(f"[DEBUG] Triggered with: {selected_measurement}, {selected_time_period}")
        if not selected_measurement or not selected_time_period:
            # Returning empty list clears existing markers
            return []

        markers = process_map_data_2(selected_measurement, selected_time_period)

        if not markers:
            # Optional: add a default marker or popup for "no data"
            print("[MAP] No markers returned.")
            return []

        return markers


    # --- Callbacks for Datasets Page ---    
    @app.callback(
        Output('dataset-site-dropdown', 'options'),
        Output('dataset-site-dropdown', 'value'),
        Input('dataset-measurement-dropdown', 'value')
    )
    def update_dataset_site_options(selected_measurement):
        return get_dataset_site_options(selected_measurement)

    @app.callback(
        Output('dataset-output-container', 'children'),
        Output('download-csv-btn', 'disabled'),
        Output('hilltop-data-store', 'data'),
        Input('load-dataset-btn', 'n_clicks'),
        State('dataset-measurement-dropdown', 'value'),
        State('dataset-date-range-picker', 'start_date'),
        State('dataset-date-range-picker', 'end_date'),
        State('dataset-site-dropdown', 'value'), # Move this to the correct position
        prevent_initial_call=True
    )
    def load_dataset(n_clicks, selected_measurement, start_date, end_date, selected_sites):
        if not n_clicks:
            raise dash.exceptions.PreventUpdate

        if not selected_measurement or not selected_sites or not start_date or not end_date:
            return (dbc.Alert("Please select all options to load data.", color="info"), True, None)

        if not MEASUREMENTS_FOR_MAPS_AND_DATASETS:
            return (dbc.Alert("Site and measurement data not loaded. Check Hilltop connection.", color="danger"), True, None)


        combined_df, data_found = get_dataset_data_for_display(
            selected_measurement, selected_sites, start_date, end_date
        )
        
        if not data_found:
            return (dbc.Alert("No data found for the selected criteria.", color="warning"), True, None)

        data_to_store = combined_df.to_json(date_format='iso', orient='split')

        return (create_dataset_display(combined_df, selected_measurement, selected_sites, start_date, end_date), 
                False, 
                data_to_store)

    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("download-csv-btn", "n_clicks"),
        State("hilltop-data-store", "data"),
        State("dataset-measurement-dropdown", "value"),
        prevent_initial_call=True,
    )
    def download_csv(n_clicks, stored_data, selected_measurement):
        if not n_clicks or not stored_data:
            raise dash.exceptions.PreventUpdate
        df = pd.read_json(io.StringIO(stored_data), orient='split')
        # df = pd.read_json(stored_data, orient='split')
        filename = f"{selected_measurement.replace(' ', '_').replace('(', '').replace(')', '')}_data.csv"
        print(f"Preparing to download {filename} with {len(df)} rows.")
        return dcc.send_data_frame(df.to_csv, filename=filename)
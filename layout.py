# layout.py

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_leaflet as dl
from datetime import datetime, timedelta # Still needed for DatePickerRange defaults

from constants import (
    SIDEBAR_STYLE, CONTENT_STYLE, MAIN_TOPICS_WITH_SUB_TOPICS,
    MEASUREMENTS_FOR_MAPS_AND_DATASETS, 
    # TIME_PERIOD_OPTIONS_INCREMENTAL, TIME_PERIOD_OPTIONS_INSTANTANEOUS, # These are not used directly here
    TARANAKI_MAP_CENTER, DEFAULT_MAP_ZOOM
)
# REMOVED: Imports from data_processing.py that shouldn't be here
# from data_processing import (
#     get_rainfall_summary_data, get_flow_status_data, 
#     get_map_data_for_display, get_dataset_data_for_display
# ) 

def serve_header_layout():
    """Returns the fixed header layout."""
    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="/assets/portal_logo_white_transparent_bkgd.png", height="30px"), width="auto", style={"position":"absolute","left":"10px"}), 
                            dbc.Col(dbc.NavbarBrand("Environmental Data Portal", className="ms-1")),
                        ],
                        align="left",
                        className="g-0",
                    ),
                    href="http://127.0.0.1:8050/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("About", href="http://127.0.0.1:8050/about-us/", target="_blank")),
                            dbc.NavItem(dbc.NavLink("Contact", href="http://127.0.0.1:8050/contact-us/", target="_blank")),
                        ],
                        className="ms-auto",
                        navbar=True,
                    ),
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ]
        ),
        color="primary",
        dark=True,
        fixed="top",
        className="mb-4"
    )

def serve_sidebar_layout():
    """Returns the sidebar layout with accordion navigation."""
    return html.Div(
        [
            html.H2("Navigation", className="display-6"),
            html.Hr(),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        html.Div([
                            dbc.Button(
                                sub_topic,
                                id={'type': 'sidebar-sub-topic-button', 'index': f"{topic.replace(' ', '-')}-{sub_topic.replace(' ', '-')}"},
                                className="mb-2",
                                style={"width": "100%", "text-align": "left"},
                                color="link"
                            ) for sub_topic in sub_topics
                        ]) if sub_topics else
                        dbc.Button(
                            topic,
                            id={'type': 'sidebar-main-topic-button', 'index': topic.replace(' ', '-')},
                            className="mb-2",
                            style={"width": "100%", "text-align": "left"},
                            color="primary" if topic in ["Maps", "Datasets"] else "link"
                        ),
                        title=topic, 
                        item_id=f"accordion-item-{topic.replace(' ', '-')}",
                    ) for topic, sub_topics in MAIN_TOPICS_WITH_SUB_TOPICS.items()
                ],
                id="main-sidebar-accordion",
                active_item="accordion-item-Quick-Reference",
                always_open=False,
            ),
        ],
        style=SIDEBAR_STYLE,
    )

def serve_default_page_layout():
    """Returns the welcome/default landing page layout."""
    default_path = '/quick-reference-taranaki-rainfall-summary'
    default_path = '/'
    return html.Div([
        html.Img(src='https://www.doc.govt.nz/thumbs/hero/contentassets/88ba5e1f554e4e7f871aadcaabbf875c/everett-park-scenic-reserve-walk1920.jpg',
                     style={
                            'width': '100%',
                            'height': '200px',
                            'padding':'0px',
                            'margin':'0px',
                            'object-fit': 'none' #contain
                            },),
        html.P(children=["Suspension bridge on the Kurapete Walk at Everett Park Scenic Reserve. ",
                    html.Br(),
                    "Source: ",
                    html.A("Department of Conservation", 
                           href="https://www.doc.govt.nz/parks-and-recreation/places-to-go/taranaki/places/everett-park-scenic-reserve/things-to-do/everett-park-scenic-reserve-walk/",
                           target="_blank"),
                    ".  ",
                    "Image attribution: ",
                    "Jaime Apolonio",
                    " | ",
                    html.A("Creative Commons", 
                           href="https://creativecommons.org/licenses/by-nc/4.0/",
                           target="_blank"),   
                    html.Br(),
                    ],
                     style={
                            'font-size':'0.8em'
                            },),
        html.P(""),
        html.H2("Environmental Data Portal"),
        html.P("Use the navigation on the left to explore selected environmental data for the Taranaki Region."),
        html.P(children=["This portal accesses environmental monitoring data collected in the Taranaki region. ",
                         "The sources of data used in this portal are from:",
                         html.Ul(),
                         html.Li("Councils"),
                         html.Li("Private weather stations"),
                         html.Li("NIWA"),]),
        html.P("We do make some of the data available for download but please refer to metadata for specific sources."),                 
        # dcc.Link("Go to Taranaki Rainfall Summary", href=default_path)
    ],style={'padding':'0px',
             'margin':'0px',}
    )

# Quick Reference Page Layouts - these now ACCEPT data as arguments
# They no longer fetch data themselves
def serve_quick_reference_rainfall_summary_layout(rainfall_data_df=None):
    """Returns the layout for the Taranaki Rainfall Summary quick reference page."""
    if rainfall_data_df is None or rainfall_data_df.empty:
        total_rainfall = "N/A"
        table_content = dbc.Alert("No rainfall data available for display.", color="warning")
        graph_figure = go.Figure(layout=go.Layout(title='No Data Available', xaxis_title='Date/Time', yaxis_title='Rainfall (mm)'))
    else:
        total_rainfall = f"{rainfall_data_df['Rainfall (mm)'].sum():.1f}"
        table_content = html.Div(dbc.Table.from_dataframe(rainfall_data_df.tail(100), striped=True, bordered=True, hover=True),
                                 style={'maxHeight': '300px', 'overflowY': 'auto'})
        graph_figure = go.Figure(data=[go.Bar(x=rainfall_data_df['DateTime'], y=rainfall_data_df['Rainfall (mm)'])],
                                 layout=go.Layout(title='Last 7 Days Rainfall',
                                                  xaxis_title='Date/Time',
                                                  yaxis_title='Rainfall (mm)',
                                                  margin=dict(t=50, b=50, l=50, r=50)))

    return html.Div([
        html.H3("Taranaki Rainfall Summary"),
        html.P("This page provides an overview of recent rainfall across key Taranaki sites."),
        dbc.Card(
            dbc.CardBody([
                html.H5("Recent Rainfall (Manganui at Everett Park)", className="card-title"),
                html.P(f"Total Rainfall: {total_rainfall} mm"),
                dcc.Graph(figure=graph_figure, style={'height': '350px'}),
                table_content
            ])
        )
    ])

def serve_quick_reference_river_flow_status_layout(flow_data_df=None, latest_flow=None, status_text="Unavailable", mean_annual_flood=None):
    """Returns the layout for the River Flow Status quick reference page."""
    if flow_data_df is None or flow_data_df.empty:
        latest_flow_display = "N/A"
        flow_graph_figure = go.Figure(layout=go.Layout(title='No Data Available', xaxis_title='Date/Time', yaxis_title='Flow (m³/s)'))
        table_content = dbc.Alert("No river flow data available for display.", color="warning")
    else:
        latest_flow_display = f"{latest_flow:.1f}" if isinstance(latest_flow, (int, float)) else str(latest_flow)
        flow_graph_figure = go.Figure(data=[go.Scatter(x=flow_data_df['DateTime'], y=flow_data_df['Flow (m³/s)'], mode='lines')],
                                     layout=go.Layout(title='Patea at Skinner Rd (Last 7 Days)',
                                                      xaxis_title='Date/Time',
                                                      yaxis_title='Flow (m³/s)',
                                                      margin=dict(t=50, b=50, l=50, r=50)))
        # Add a horizontal threshold line at y=10
        flow_graph_figure.add_hline(y=mean_annual_flood, line_width=2, line_dash="dash", line_color="red", annotation_text="Mean annual flood", annotation_position="top right")
        flow_graph_figure.add_hline(y=222.4, line_width=2, line_dash="dash", line_color="red", annotation_text="1:10 AEP", annotation_position="top right")

        table_content = html.Div(dbc.Table.from_dataframe(flow_data_df.tail(100), striped=True, bordered=True, hover=True),
                                 style={'maxHeight': '300px', 'overflowY': 'auto'})

    return html.Div([
        html.H3("River Flow Status"),
        html.P("Provides a quick overview of current river flow conditions in key Taranaki rivers."),
        dbc.Card(
            dbc.CardBody([
                html.H5("Patea at Skinner Rd - Latest Flow", className="card-title"),
                html.P(f"Current Flow: {latest_flow_display} m³/s", className="card-text"),
                html.P(f"Mean Annual Flood Flow: {mean_annual_flood} m³/s", className="card-text"),
                html.P(f"Status: {status_text}", className="card-text"),
                html.P("This section would include more details about historical averages, warning levels, etc."),
                dcc.Graph(figure=flow_graph_figure, style={'height': '350px'}),
                table_content
            ])
        )
    ])

def serve_quick_reference_waiwhakaiho_egmont_village_layout(flow_data_df=None, latest_flow=None, status_text="Unavailable", mean_annual_flood=None):
    """Returns the layout for the River Flow Status quick reference page."""
    if flow_data_df is None or flow_data_df.empty:
        latest_flow_display = "N/A"
        flow_graph_figure = go.Figure(layout=go.Layout(title='No Data Available', xaxis_title='Date/Time', yaxis_title='Flow (m³/s)'))
        table_content = dbc.Alert("No river flow data available for display.", color="warning")
    else:
        latest_flow_display = f"{latest_flow:.1f}" if isinstance(latest_flow, (int, float)) else str(latest_flow)
        flow_graph_figure = go.Figure(data=[go.Scatter(x=flow_data_df['DateTime'], y=flow_data_df['Flow (m³/s)'], mode='lines')],
                                     layout=go.Layout(title='Waiwhakaiho (Last 7 Days)',
                                                      xaxis_title='Date/Time',
                                                      yaxis_title='Flow (m³/s)',
                                                      margin=dict(t=50, b=50, l=50, r=50)))
        # Add a horizontal threshold line at y=10
        flow_graph_figure.add_hline(y=mean_annual_flood, line_width=2, line_dash="dash", line_color="red", annotation_text="Mean annual flood", annotation_position="top right")
        flow_graph_figure.add_hline(y=426.16, line_width=2, line_dash="dash", line_color="red", annotation_text="1:10 AEP", annotation_position="top right")

        table_content = html.Div(dbc.Table.from_dataframe(flow_data_df.tail(100), striped=True, bordered=True, hover=True),
                                 style={'maxHeight': '300px', 'overflowY': 'auto'})

    return html.Div([
        html.H3("River Flow Status"),
        html.P("Provides a quick overview of current river flow conditions in key Taranaki rivers."),
        dbc.Card(
            dbc.CardBody([
                html.H5("Waiwhakaiho at Egmont Village - Latest Flow", className="card-title"),
                html.P(f"Current Flow: {latest_flow_display} m³/s", className="card-text"),
                html.P(f"Mean Annual Flood Flow: {mean_annual_flood} m³/s", className="card-text"),
                html.P(f"Status: {status_text}", className="card-text"),
                html.P("This section would include more details about historical averages, warning levels, etc."),
                dcc.Graph(figure=flow_graph_figure, style={'height': '350px'}),
                table_content
            ])
        )
    ])


def serve_quick_reference_waiwhakaiho_report_layout():
    """Returns the layout for the Waiwhakaiho Report quick reference page."""
    return html.Div([
        html.H3("Waiwhakaiho Report"),
        html.P("Summary of Waiawhakaiho River data for the Taranaki region."),
        dbc.Alert("Data for river stage and flows is currently being integrated. Please check back later.", color="warning"),
        html.P("This page would eventually display graphs and tables of river stage and flow data, similar to the River Flow Status page."),
    ])

def serve_quick_reference_air_quality_report_layout():
    """Returns the layout for the Air Quality Report quick reference page."""
    return html.Div([
        html.H3("Air Quality Report"),
        html.P("Summary of recent air quality data for the Taranaki region."),
        dbc.Alert("Data for air quality is currently being integrated. Please check back later.", color="warning"),
        html.P("This page would eventually display graphs and tables of common air pollutants (e.g., PM10, PM2.5).")
    ])


def serve_map_page_layout():
    """Returns the layout for the Maps page."""
    measurement_options = [{'label': k, 'value': k} for k in MEASUREMENTS_FOR_MAPS_AND_DATASETS.keys()]
    
    return html.Div([
        html.H3("Environmental Data Maps"),
        
        dbc.Row([
            dbc.Col(
                dbc.FormFloating([
                    dcc.Dropdown(
                        id='map-measurement-dropdown',
                        options=measurement_options,
                        placeholder="Select a Measurement",
                        value=list(MEASUREMENTS_FOR_MAPS_AND_DATASETS.keys())[0] if MEASUREMENTS_FOR_MAPS_AND_DATASETS else None,
                        clearable=False
                    ),
                    dbc.Label("Measurement Type")
                ]),
                md=4
            ),
            dbc.Col(
                dbc.FormFloating([
                    dcc.Dropdown(
                        id='map-time-period-dropdown',
                        options=[],  # Set by callback
                        placeholder="Select Time Period",
                        clearable=False
                    ),
                    dbc.Label("Time Period")
                ]),
                md=4
            )
        ], className="mb-4"),
        
        dcc.Loading(
            id="loading-map",
            type="circle",
            children=[
                dl.Map(
                    id="leaflet-map",
                    center=TARANAKI_MAP_CENTER,
                    zoom=DEFAULT_MAP_ZOOM,
                    children=[
                        dl.TileLayer(),
                        dl.LayersControl([
                            dl.Overlay(
                                dl.LayerGroup(id="marker-layer"),
                                name="Sites",
                                checked=True
                            )
                        ])
                    ],
                    style={'width': '100%', 'height': '600px', 'margin': "auto", "display": "block"}
                )
            ]
        ),

        html.Hr(),
        html.P("Map legend goes here: e.g., Red = High, Orange = Medium, Green = Low")
    ])


def serve_datasets_page_layout():
    """Returns the layout for the Datasets page."""
    measurement_options = [{'label': k, 'value': k} for k in MEASUREMENTS_FOR_MAPS_AND_DATASETS.keys()]
    
    return html.Div([
        html.H3("Environmental Data Downloads"),
        dbc.Row([
            dbc.Col(
                dbc.FormFloating(
                    [
                        dcc.Dropdown(
                            id='dataset-measurement-dropdown',
                            options=measurement_options,
                            placeholder="Select a Measurement",
                            value=list(MEASUREMENTS_FOR_MAPS_AND_DATASETS.keys())[0] if MEASUREMENTS_FOR_MAPS_AND_DATASETS else None,
                            clearable=False
                        ),
                        dbc.Label("Measurement Type")
                    ]
                ),
                md=4
            ),
            dbc.Col(
                dbc.FormFloating(
                    [
                        dcc.Dropdown(
                            id='dataset-site-dropdown',
                            options=[], # Populated by callback
                            placeholder="Select Site(s)",
                            multi=True
                        ),
                        dbc.Label("Site(s)")
                    ]
                ),
                md=4
            ),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(
                html.Div([
                    dbc.Label("Select Date Range"),
                    dcc.DatePickerRange(
                        id='dataset-date-range-picker',
                        start_date=datetime.now() - timedelta(days=7),
                        end_date=datetime.now(),
                        display_format='YYYY-MM-DD',
                        clearable=True
                    )
                ], id='dataset-date-range-container'),
                md=6
            ),
            dbc.Col(
                dbc.Button("Load Dataset", id="load-dataset-btn", color="primary", className="mt-4"),
                md=3
            ),
            dbc.Col(
                dbc.Button("Download CSV", id="download-csv-btn", color="success", className="mt-4", 
                           disabled=True),
                md=3
            ),
            dcc.Download(id="download-dataframe-csv"),
        ], className="mb-4"),
        html.Div(id='dataset-output-container', children=[
            dbc.Alert("Select measurement, site(s), and date range, then click 'Load Dataset'.", color="info")
        ])
    ])

def create_dataset_display(combined_df, selected_measurement, selected_sites, start_date, end_date):
    """Generates the dataset display components (table and graph)."""
    table = dbc.Table.from_dataframe(combined_df.head(50), striped=True, bordered=True, hover=True, className="mt-3")
    return html.Div([
        html.H4(f"Data for {selected_measurement}"),
        html.P(f"Selected sites: {', '.join(selected_sites)}"),
        html.P(f"Date Range: {start_date} to {end_date}"),
        dbc.Alert(f"Displaying first {min(50, len(combined_df))} rows. Download CSV for full data.", color="info"),
        html.Div(table, style={'maxHeight': '400px', 'overflowY': 'auto'}),
        dcc.Graph(figure=go.Figure(data=go.Scatter(x=combined_df['DateTime'], y=combined_df['Value'], mode='lines', name='Data'),
                                   layout=go.Layout(title=f'Time Series for {selected_measurement}', 
                                                    xaxis_title='Date', yaxis_title='Value')))
    ])

def serve_charts_page_layout():
    """Returns the layout for the Charts page."""
    return html.Div([
        html.H3("Charts"),
        html.P("Explore various charts for different environmental parameters. Select options below."),
        html.P("This page will have controls to select measurements, sites, and time ranges for custom charts.")
    ])

def serve_reports_page_layout():
    """Returns the layout for the Reports page."""
    return html.Div([
        html.H3("Reports"),
        html.P("This section will contain detailed environmental reports, possibly generated on demand or as static documents."),
    ])
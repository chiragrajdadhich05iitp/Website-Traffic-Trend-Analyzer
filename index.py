
import dash
from dash import dcc, html, Input, Output  # Components for layout & interactivity
import pandas as pd
import plotly.express as px

sample_data = {
    "date": pd.date_range(start="2025-07-01", periods=30, freq="D").tolist() * 3,
    "page": ["Home", "Products", "Contact"] * 30,
    # Generate a simple sinusoidal pattern to simulate traffic fluctuation
    "visits": [abs(int(100 + 50 * pd.Series(range(90)).sin()[i])) for i in range(90)],
    "device": ["Desktop", "Mobile", "Tablet"] * 30,
    "location": ["India", "USA", "UK"] * 30
}

# Convert dictionary into a Pandas DataFrame for easier manipulation
df = pd.DataFrame(sample_data)

# ======================================================
# 3. INITIALIZE DASH APP
# ======================================================
# Dash apps are web servers that create interactive data visualizations.

app = dash.Dash(__name__)
app.title = "Website Traffic Trend Analyzer"  # Sets browser tab title

# ======================================================
# 4. LAYOUT OF DASHBOARD
# ======================================================
# The layout defines what users see: filters, charts, and headings.

app.layout = html.Div([
    # Dashboard title
    html.H1("Website Traffic Trend Analyzer", style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Filter section
    html.Div([
        html.Label("Select Device:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id="device_filter",
            options=[{"label": device, "value": device} for device in df["device"].unique()],
            value=None,
            placeholder="Filter by Device",
            multi=True  # Allows selection of multiple devices
        ),

        html.Br(),

        html.Label("Select Location:", style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id="location_filter",
            options=[{"label": location, "value": location} for location in df["location"].unique()],
            value=None,
            placeholder="Filter by Location",
            multi=True  # Allows selection of multiple locations
        ),
    ], style={"width": "40%", "display": "inline-block", "padding": "10px"}),

    html.Br(),

    # Charts section
    dcc.Graph(id="traffic_trend"),     # Line chart for daily visits
    dcc.Graph(id="top_pages"),         # Bar chart for top pages
    dcc.Graph(id="device_pie")         # Pie chart for device distribution
])

# ======================================================
# 5. CALLBACKS FOR INTERACTIVITY
# ======================================================
# Callbacks link inputs (filters) to outputs (charts). When a user changes filters,
# the charts update automatically.

@app.callback(
    [Output("traffic_trend", "figure"),
     Output("top_pages", "figure"),
     Output("device_pie", "figure")],
    [Input("device_filter", "value"),
     Input("location_filter", "value")]
)
def update_dashboard(selected_devices, selected_locations):
    """
    Filters the dataset based on selected devices and locations,
    then regenerates the three charts with filtered data.
    """

    # Make a copy of the main DataFrame to apply filters
    filtered_df = df.copy()

    # Apply device filter if selected
    if selected_devices:
        filtered_df = filtered_df[filtered_df["device"].isin(selected_devices)]

    # Apply location filter if selected
    if selected_locations:
        filtered_df = filtered_df[filtered_df["location"].isin(selected_locations)]

    # ------------------------------------------------------
    # Line Chart: Daily Website Visits
    # ------------------------------------------------------
    traffic_by_date = filtered_df.groupby("date")["visits"].sum().reset_index()
    fig_trend = px.line(traffic_by_date, x="date", y="visits",
                        title="Daily Website Visits",
                        markers=True)
    fig_trend.update_layout(xaxis_title="Date", yaxis_title="Visits")

    # ------------------------------------------------------
    # Bar Chart: Top Pages by Visits
    # ------------------------------------------------------
    top_pages = filtered_df.groupby("page")["visits"].sum().reset_index().sort_values(by="visits", ascending=False)
    fig_pages = px.bar(top_pages, x="page", y="visits",
                       title="Top Pages by Visits",
                       text="visits",
                       color="page")
    fig_pages.update_traces(texttemplate='%{text}', textposition='outside')
    fig_pages.update_layout(xaxis_title="Page", yaxis_title="Visits")

    # ------------------------------------------------------
    # Pie Chart: Device Traffic Distribution
    # ------------------------------------------------------
    device_data = filtered_df.groupby("device")["visits"].sum().reset_index()
    fig_device = px.pie(device_data, names="device", values="visits",
                        title="Traffic by Device",
                        hole=0.3)  # Creates a donut-style chart

    return fig_trend, fig_pages, fig_device

# ======================================================
# 6. RUN THE SERVER
# ======================================================
# When executed locally, this will start a development server at http://127.0.0.1:8050

if __name__ == "__main__":
    app.run_server(debug=True)

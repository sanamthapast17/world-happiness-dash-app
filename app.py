# Import required libraries
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('data/world-happiness-report-2021.csv')

# Preprocess the data
# Rename columns for better readability
df = df.rename(columns={
    'Country name': 'Country',
    'Regional indicator': 'Region',
    'Ladder score': 'Happiness',
    'Logged GDP per capita': 'GDP',
    'Social support': 'Social',
    'Healthy life expectancy': 'Health',
    'Freedom to make life choices': 'Freedom',
    'Generosity': 'Generosity',
    'Perceptions of corruption': 'Corruption'
})

# Create a list of regions for the dropdown
regions = df['Region'].unique()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("World Happiness Dashboard", className="text-center mb-4"), width=12)
    ]),

    # Introduction text
    dbc.Row([
        dbc.Col(html.P(
            "Explore happiness metrics across countries and regions. "
            "Use the interactive controls below to filter and visualize the data.",
            className="text-center mb-4"
        ), width=12)
    ]),

    # Controls row
    dbc.Row([
        # Region dropdown
        dbc.Col([
            html.Label("Select Region:", className="mb-2"),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': region, 'value': region} for region in regions],
                value=regions[0],
                clearable=False
            )
        ], md=3),

        # Metric dropdown
        dbc.Col([
            html.Label("Select Metric:", className="mb-2"),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'Happiness Score', 'value': 'Happiness'},
                    {'label': 'GDP per Capita', 'value': 'GDP'},
                    {'label': 'Social Support', 'value': 'Social'},
                    {'label': 'Healthy Life Expectancy', 'value': 'Health'},
                    {'label': 'Freedom', 'value': 'Freedom'},
                    {'label': 'Generosity', 'value': 'Generosity'},
                    {'label': 'Corruption', 'value': 'Corruption'}
                ],
                value='Happiness',
                clearable=False
            )
        ], md=3),

        # Number of countries slider
        dbc.Col([
            html.Label("Number of Countries to Display:", className="mb-2"),
            dcc.Slider(
                id='country-slider',
                min=5,
                max=20,
                step=1,
                value=10,
                marks={i: str(i) for i in range(5, 21, 5)}
            )
        ], md=3),

        # Color scale radio items
        dbc.Col([
            html.Label("Color Scale:", className="mb-2"),
            dcc.RadioItems(
                id='color-radio',
                options=[
                    {'label': 'Plasma', 'value': 'Plasma'},
                    {'label': 'Viridis', 'value': 'Viridis'},
                    {'label': 'Inferno', 'value': 'Inferno'}
                ],
                value='Plasma',
                inline=True
            )
        ], md=3)
    ], className="mb-4"),

    # Graphs row
    dbc.Row([
        # Bar chart
        dbc.Col(dcc.Graph(id='bar-chart'), md=6),

        # Scatter plot
        dbc.Col(dcc.Graph(id='scatter-plot'), md=6)
    ], className="mb-4"),

    # Second row of graphs
    dbc.Row([
        # Choropleth map
        dbc.Col(dcc.Graph(id='choropleth-map'), md=12)
    ]),

    # Correlation heatmap row
    dbc.Row([
        dbc.Col(dcc.Graph(id='correlation-heatmap'), md=12)
    ]),

    # Footer
    dbc.Row([
        dbc.Col(html.P(
            "Data Source: World Happiness Report 2021 | "
            "Dashboard created for COMP 4433 Project 2",
            className="text-center mt-4 text-muted"
        ), width=12)
    ])
], fluid=True)

# Callback for updating the bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('region-dropdown', 'value'),
     Input('metric-dropdown', 'value'),
     Input('country-slider', 'value'),
     Input('color-radio', 'value')]
)
def update_bar_chart(selected_region, selected_metric, n_countries, color_scale):
    # Filter data by region
    filtered_df = df[df['Region'] == selected_region]

    # Sort and select top countries
    filtered_df = filtered_df.sort_values(by=selected_metric, ascending=False).head(n_countries)

    # Create bar chart
    fig = px.bar(
        filtered_df,
        x='Country',
        y=selected_metric,
        color=selected_metric,
        color_continuous_scale=color_scale,
        title=f'Top {n_countries} Countries in {selected_region} by {selected_metric}'
    )

    # Update layout
    fig.update_layout(
        yaxis_title=selected_metric,
        xaxis_title='Country',
        coloraxis_showscale=False
    )

    return fig

# Callback for updating the scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('region-dropdown', 'value'),
     Input('metric-dropdown', 'value'),
     Input('color-radio', 'value')]
)
def update_scatter_plot(selected_region, selected_metric, color_scale):
    # Filter data by region
    filtered_df = df[df['Region'] == selected_region]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='GDP',
        y=selected_metric,
        color='Happiness',
        size='Happiness',
        hover_name='Country',
        color_continuous_scale=color_scale,
        title=f'GDP vs {selected_metric} in {selected_region} (Colored by Happiness)'
    )

    # Update layout
    fig.update_layout(
        yaxis_title=selected_metric,
        xaxis_title='GDP per Capita'
    )

    return fig

# Callback for updating the choropleth map
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('metric-dropdown', 'value'),
     Input('color-radio', 'value')]
)
def update_choropleth(selected_metric, color_scale):
    # Create choropleth map
    fig = px.choropleth(
        df,
        locations='Country',
        locationmode='country names',
        color=selected_metric,
        hover_name='Country',
        color_continuous_scale=color_scale,
        title=f'World Map of {selected_metric}'
    )

    # Update layout
    fig.update_layout(geo=dict(showframe=False, showcoastlines=False))

    return fig

# Callback for updating the correlation heatmap
@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_heatmap(selected_region):
    # Filter data by region
    filtered_df = df[df['Region'] == selected_region]

    # Select numeric columns
    numeric_cols = ['Happiness', 'GDP', 'Social', 'Health', 'Freedom', 'Generosity', 'Corruption']
    corr_matrix = filtered_df[numeric_cols].corr()

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=numeric_cols,
        y=numeric_cols,
        colorscale='Plasma',
        zmin=-1,
        zmax=1
    ))

    # Update layout
    fig.update_layout(
        title=f'Correlation Matrix of Happiness Factors in {selected_region}',
        xaxis_title='Metrics',
        yaxis_title='Metrics'
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

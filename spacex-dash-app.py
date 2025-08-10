# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# ----- APP LAYOUT -----
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown de sitios
    dcc.Dropdown(
        id='site-dropdown',
        options=([{'label': 'All Sites', 'value': 'ALL'}] +
                 [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]),
        value='ALL',
        clearable=False,
        placeholder='Select a Launch Site',
        style={'width': '60%', 'margin': '0 auto'}
    ),
    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),

    # TASK 3: RangeSlider de payload
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, max=max_payload, step=1000,
        marks={int(x): str(int(x)) for x in [min_payload, (min_payload+max_payload)/2, max_payload]},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ----- CALLBACKS -----

# TASK 2: Pie chart
# - ALL: éxitos por sitio
# - Específico: éxitos vs fallos en ese sitio
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Suma de éxitos (class=1) por sitio
        df_all = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df_all, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df_site['class'].value_counts().rename(index={1: 'Success', 0: 'Failure'}).reset_index()
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Success vs Failure for {selected_site}')
    return fig

# TASK 4: Scatter payload vs success (filtrado por sitio + rango de payload)
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                   (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=('Correlation between Payload and Success'
               if selected_site == 'ALL' else
               f'Payload vs Success for {selected_site}'),
        labels={'class': 'Success (1) / Failure (0)'},
        hover_data=['Launch Site']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
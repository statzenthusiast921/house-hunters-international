#Import packages
import pandas as pd
import numpy as np
import os
import plotly.express as px
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State



#Read in processed data from github
hhi_df = pd.read_csv('https://raw.githubusercontent.com/statzenthusiast921/house-hunters-international/main/data/data_w_lat_lon_v2.csv')

origin_city_choices = hhi_df['Origin'].unique()

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'color':'white',
    'backgroundColor': '#222222'

}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#626ffb',
    'color': 'white',
    'padding': '6px'
}



app = dash.Dash(__name__,assets_folder=os.path.join(os.curdir,"assets"))
server = app.server
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Welcome',value='tab-1',style=tab_style, selected_style=tab_selected_style,
        children = [
            dbc.Row([
                dbc.Col([
                  html.P('Test')  
                ])
            ])
        ]),
        dcc.Tab(label='Plot Everything',value='tab-2',style=tab_style, selected_style=tab_selected_style,
        children=[
            dbc.Row([
                dbc.Col([
                     dcc.Dropdown(
                        id='dropdown0',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_city_choices],
                        value=origin_city_choices[0]
                    ),
                    dcc.Graph(id='plot_everything')
                ],width=12),
            ])
        ])
     
    ])
])


#Plot Everything
@app.callback(
    Output('plot_everything','figure'),
    Input('dropdown0','value')
)
def plot_stuff(dd0):
    
    filtered = hhi_df[hhi_df['Origin']==dd0]

    fig = px.scatter_mapbox(
        filtered, 
        lat="lat_dest", lon="lon_dest", 
        hover_name="Destination", 
        #color_continuous_scale="balance",
        #color="per_gop",
        hover_data = {
            "Destination":True,
            "ep_title":True,
            "air_date":True,
            "lat_orig":False,
            "lon_orig":False,
        },
        labels={
            'Destination':'Destination',
            'Episode Title':'ep_title',
            'Air Date':'air_date'},
        #size = "gop_dem_total",
        zoom=3)
        #center = {"lat": 37.0902, "lon": -95.7129})
    
    fig.update_layout(mapbox_style="carto-positron",margin={"r":0,"t":0,"l":0,"b":0})

    return fig

    


# #Configure Reactivity for Tab Colors
# @app.callback(Output('tabs-content-inline', 'children'),
#               Input('tabs-styled-with-inline', 'value'))
# def render_content(tab):
#     if tab == 'tab-1':
#         return html.Div([
#             html.H3('Tab content 1')
#         ])
#     elif tab == 'tab-2':
#         return html.Div([
#             html.H3('Tab content 2')
#         ])



if __name__=='__main__':
	app.run_server()

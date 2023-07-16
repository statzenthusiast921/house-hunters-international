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
hhi_df = pd.read_csv('https://raw.githubusercontent.com/statzenthusiast921/house-hunters-international/main/data/data_w_lat_lon_v2.csv',encoding='latin-1')

country_counts = pd.DataFrame(hhi_df.groupby('MoveFromCountry').size()).reset_index()
country_counts.columns = ['MoveFromCountry', 'num_eps_to_filter']

hhi_df = hhi_df.merge(country_counts, on='MoveFromCountry', how='left')




origin_city_choices = hhi_df['MoveFromCity'].unique()
origin_country_choices = hhi_df['MoveFromCountry'].unique()

# Country --> City Dictionary
df_for_dict = hhi_df[['MoveFromCountry','MoveFromCity']]
df_for_dict = df_for_dict.drop_duplicates(subset='MoveFromCity',keep='first')
country_city_dict = df_for_dict.groupby('MoveFromCountry')['MoveFromCity'].apply(list).to_dict()
#country_city_dict_sorted = {l: sorted(m) for l, m in country_city_dict.items()}



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
        dcc.Tab(label='Countries',value='tab-2',style=tab_style, selected_style=tab_selected_style,
        children = [
            dbc.Row([
                dbc.Col([
                    dbc.Card(id='card_a')
                ],width=4),
                dbc.Col([
                    dbc.Card(id='card_b')
                ],width=4),
                dbc.Col([
                    dbc.Card(id='card_c')
                ],width=4),
            ]),
            dbc.Row([
                dcc.Dropdown(
                        id='dropdown_a',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_country_choices],
                        value=origin_country_choices[0]
                    ),
                dcc.Graph(id='map_origin_cities')

            ])
        ]),
        dcc.Tab(label='Origin',value='tab-3',style=tab_style, selected_style=tab_selected_style,
        children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card(id='card0')
                ],width=4),
                dbc.Col([
                    dbc.Card(id='card1')
                ],width=4),
                dbc.Col([
                    dbc.Card(id='card2')
                ],width=4),
            ]),
            dbc.Row([
                dbc.Col([
                     dcc.Dropdown(
                        id='dropdown0',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_country_choices],
                        value=origin_country_choices[0]
                    ),
                ],width=6),
                dbc.Col([
                     dcc.Dropdown(
                        id='dropdown1',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_city_choices],
                        value=origin_city_choices[0]
                    ),
                ],width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='map_dest_cities')
                ], width = 6),
                dbc.Col([
                    dcc.Graph(id='tree_map_dest_cities')
                ], width = 6),
            ])
        ])
     
    ])
])


#Configure Reactivity for Tab Colors
@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])

    
#Cards for Destination Map
@app.callback(
    Output('card_a','children'),
    Output('card_b','children'),
    Output('card_c','children'),
    Input('dropdown_a','value')
)

def info_about_destinations(dd_a):

    filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]
    filtered = filtered[filtered['num_eps_to_filter']>2]

    #Metric 1 --> # of episodes
    metric1 = filtered.shape[0]

    #Metric 2 --> avg distance (excluding 0 and NAs)
    remove0s = filtered[(filtered['distance_km']>0) & filtered['distance_km'].notnull()]
    metric2 = round(remove0s['distance_km'].mean(),2)

    #Metric 3 --> max distance
    metric3 = round(filtered['distance_km'].max(),2)


    card_a = dbc.Card([
        dbc.CardBody([
            html.P(f'# Episodes Leaving {dd_a}'),
            html.H5(f"{metric1} Episodes")
        ])
    ],
    style={'display': 'inline-block',
           'width': '100%',
           'text-align': 'center',
           'background-color': '#70747c',
           'color':'white',
           'fontWeight': 'bold',
           'fontSize':16},
    outline=True)

    card_b = dbc.Card([
        dbc.CardBody([
            html.P(f'Avg Distance Travelled from {dd_a}'),
            html.H5(f"{metric2}")
        ])
    ],
    style={'display': 'inline-block',
           'width': '100%',
           'text-align': 'center',
           'background-color': '#70747c',
           'color':'white',
           'fontWeight': 'bold',
           'fontSize':16},
    outline=True)

    card_c = dbc.Card([
        dbc.CardBody([
            html.P(f'Max Distance Travelled from {dd_a}'),
            html.H5(f"{metric3}")
        ])
    ],
    style={'display': 'inline-block',
           'width': '100%',
           'text-align': 'center',
           'background-color': '#70747c',
           'color':'white',
           'fontWeight': 'bold',
           'fontSize':16},
    outline=True)

    return card_a, card_b, card_c


#Plot Destination Cities from Origin
@app.callback(
    Output('map_origin_cities','figure'),
    Input('dropdown_a','value')
)
def plot_map_dest_cities(dd_a):
    
    filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]
    filtered = filtered[filtered['MoveToCountry']!=dd_a]

    city_counts = pd.DataFrame(filtered.groupby('Destination').size()).reset_index()
    city_counts.columns = ['Destination', 'DestCount']

    new_df = filtered.merge(city_counts, on='Destination', how='inner')



    fig = px.scatter_mapbox(
        new_df, 
        lat="lat_dest", lon="lon_dest", 
        hover_name="Destination", 
        #color_continuous_scale="balance",
        #color="per_gop",
        hover_data = {
            "Destination":True,
            "lat_orig":False,
            "lon_orig":False,
        },
        # labels={
        #     'Destination':'Destination'
        # },
        size = "DestCount",
        zoom=1)
        #center = {"lat": 37.0902, "lon": -95.7129})
    
    fig.update_layout(mapbox_style="carto-positron",margin={"r":0,"t":0,"l":0,"b":0})

    return fig


#Filter origin city choices by parent dropdown (origin country)
@app.callback(
    Output('dropdown1', 'options'), #--> filter cities
    Output('dropdown1', 'value'),
    Input('dropdown0', 'value') #--> choose country
)
def set_city_options(selected_origin_country):
    return [{'label': i, 'value': i} for i in country_city_dict[selected_origin_country]], country_city_dict[selected_origin_country][0]

    
#Cards for Destination Map
@app.callback(
    Output('card0','children'),
    Output('card1','children'),
    Output('card2','children'),
    Input('dropdown1','value')
)

def info_about_destinations(dd0):

    filtered = hhi_df[hhi_df['MoveFromCity']==dd0]

    #Metric 1 --> avg distance travelled
    remove0s = filtered[(filtered['distance_km']>0) & filtered['distance_km'].notnull()]
    metric1 = round(remove0s['distance_km'].mean(),2)

    #Metric 2 --> max distance travelled
    metric2 = round(filtered['distance_km'].max(),2)



    card0 = dbc.Card([
        dbc.CardBody([
            html.P(f'Avg Distance Travelled from {dd0}'),
            html.H5(f"{metric1} km")
        ])
    ],
    style={'display': 'inline-block',
           'width': '100%',
           'text-align': 'center',
           'background-color': '#70747c',
           'color':'white',
           'fontWeight': 'bold',
           'fontSize':16},
    outline=True)

    card1 = dbc.Card([
        dbc.CardBody([
            html.P(f'Max Distance Travelled'),
            html.H5(f"{metric2}")
        ])
    ],
    style={'display': 'inline-block',
           'width': '100%',
           'text-align': 'center',
           'background-color': '#70747c',
           'color':'white',
           'fontWeight': 'bold',
           'fontSize':16},
    outline=True)

    card2 = dbc.Card([
        dbc.CardBody([
            html.P('Card3'),
            html.H5("Metric 3")
        ])
    ],
    style={'display': 'inline-block',
           'width': '100%',
           'text-align': 'center',
           'background-color': '#70747c',
           'color':'white',
           'fontWeight': 'bold',
           'fontSize':16},
    outline=True)

    return card0, card1, card2


#Plot Destination Cities from Origin
@app.callback(
    Output('map_dest_cities','figure'),
    Input('dropdown1','value')
)
def plot_map_dest_cities(dd1):
    
    filtered = hhi_df[hhi_df['MoveFromCity']==dd1]

    fig = px.scatter_mapbox(
        filtered, 
        lat="lat_dest", lon="lon_dest", 
        hover_name="Destination", 
        #color_continuous_scale="balance",
        #color="per_gop",
        hover_data = {
            "Destination":True,
            #"ep_title":True,
            #"air_date":True,
            "lat_orig":False,
            "lon_orig":False,
        },
        labels={
            'Destination':'Destination'#,
            #'Episode Title':'ep_title',
        },
        #size = "gop_dem_total",
        zoom=1)
        #center = {"lat": 37.0902, "lon": -95.7129})
    
    fig.update_layout(mapbox_style="carto-positron",margin={"r":0,"t":0,"l":0,"b":0})

    return fig


#Plot Treemap Cities from Origin
@app.callback(
    Output('tree_map_dest_cities','figure'),
    Input('dropdown1','value')
)
def treemap_dest_cities(dd1):
    filtered = hhi_df[hhi_df['MoveFromCity']==dd1]

    tree_fig = px.treemap(
        filtered, 
        path = ['MoveToCity'],
        values = 'Destination Cities',
        template='plotly_dark',
        title=f'Destination Cities from {dd1}',
        color = 'MoveToCity',
        # color_discrete_map={
        #     'Crossed Kármán Line':'#626ffb', 
        #     'Elite Spacewalker':'#b064fc', 
        #     'Space Resident': '#ef563b',
        #     'Frequent Walker': '#f45498',
        #     'Frequent Flyer': '#ff94fc',
        #     'Elite Spaceflyer': '#a8f064',
        #     'Moonwalker': '#24cce6',
        #     'Memorial': '#ffa45c',
        #     'ISS Visitor': '#00cc96'
        # }   
    )

    tree_fig.update_traces(
        hovertemplate='Cities=%{value}'
    )


    return tree_fig




if __name__=='__main__':
	app.run_server()
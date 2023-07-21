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
#hhi_df = pd.read_csv('/Users/jonzimmerman/Desktop/Data Projects/House Hunters International/data/data_w_lat_lon_v2.csv',encoding='latin-1')

country_counts = pd.DataFrame(hhi_df.groupby('MoveFromCountry').size()).reset_index()
country_counts.columns = ['MoveFromCountry', 'num_eps_to_filter']

hhi_df = hhi_df.merge(country_counts, on='MoveFromCountry', how='left')
hhi_df['lon_orig'] = pd.to_numeric(hhi_df['lon_orig'],errors='coerce')

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
        dcc.Tab(label='Origins',value='tab-2',style=tab_style, selected_style=tab_selected_style,
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
        dcc.Tab(label='Destinations',value='tab-3',style=tab_style, selected_style=tab_selected_style,
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
                    dcc.Dropdown(
                        id='dropdown1',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_city_choices],
                        value=origin_city_choices[0]
                    ),
                ],width=12)
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

    
#------------------------ TAB #2: Origins ------------------------#
#Cards for Origin Map
@app.callback(
    Output('card_a','children'),
    Output('card_b','children'),
    Output('card_c','children'),
    Input('dropdown_a','value')
)

def info_about_origins(dd_a):

    filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]
    #filtered = filtered[filtered['MoveToCountry']!=dd_a]
    filtered = filtered[(filtered['Skip']=="Can get data") & (filtered['GeoCategory']=="All")]

    #filtered = filtered[filtered['num_eps_to_filter']>2]

    #Metric 1 --> # of episodes
    metric1 = filtered.shape[0]

    #Metric 2 --> avg distance travelling away
    remove0s = filtered[(filtered['distance_km']>0) & (filtered['distance_km'].notnull())]
    metric2 = round(remove0s['distance_km'].mean(),2)


    #use this for another plot
    # visit_country_counts = pd.DataFrame(filtered.groupby('MoveToCountry').size()).reset_index()
    # visit_country_counts.columns = ['MoveToCountry', 'Count']
    # most_pop_country = visit_country_counts.sort_values('Count', ascending=False).head(1)['MoveToCountry'].values[0]

    #Metric 3 --> max distance
    country_ref = filtered['distance_km'].max()
    metric3 = round(filtered['distance_km'].max(),2)
    max_dist_country = filtered[filtered['distance_km']==country_ref]['MoveToCountry'].values[0]


    card_a = dbc.Card([
        dbc.CardBody([
            html.P(f'# episodes leaving {dd_a}'),
            html.H5(f"{metric1} episodes")
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
            html.P(f'Average distance to travel'),
            html.H5(f"{metric2} km")
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
            html.P(f'Max distance to travel'),
            html.H5(f"{metric3} km to {max_dist_country}")
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


#Plot Origin Cities
@app.callback(
    Output('map_origin_cities','figure'),
    Input('dropdown_a','value')
)
def plot_map_origin_cities(dd_a):
    
    filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]
    filtered = filtered[(filtered['Skip']=="Can get data") & (filtered['GeoCategory']=="All")]
    #filtered = filtered[filtered['MoveToCountry']!=dd_a]

    city_counts = pd.DataFrame(filtered.groupby('Origin').size()).reset_index()
    city_counts.columns = ['Origin', 'OriginCount']

    new_df = filtered.merge(city_counts, on='Origin', how='inner')


    fig = px.scatter_mapbox(
        new_df, 
        lat="lat_orig", lon="lon_orig", 
        hover_name="Origin", 
        #color_continuous_scale="balance",
        #color="per_gop",
        hover_data = {
            "Origin":True,
            "OriginCount":True,
            "lat_orig":False,
            "lon_orig":False
        },
        labels={
            'OriginCount':'# Episodes',
            'Origin':'City'
        },
        size = "OriginCount",
        zoom=3)
        #center = {"lat": 37.0902, "lon": -95.7129})
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return fig

#------------------------ TAB #3: Destinations ------------------------#

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
    filtered = filtered[(filtered['Skip']=="Can get data") & (filtered['GeoCategory']=="All")]

    #Metric 1 --> # of episodes travelling to destination
    metric1 = filtered.shape[0]

    #Metric 2 --> avg distance travelled
    remove0s = filtered[(filtered['distance_km']>0) & filtered['distance_km'].notnull()]
    metric2 = round(remove0s['distance_km'].mean(),2)

    #Metric 3 --> max distance travelled
    country_ref = filtered['distance_km'].max()
    metric3 = round(filtered['distance_km'].max(),2)

    max_dist_city = filtered[filtered['distance_km']==country_ref]['Destination'].values[0]

    card0 = dbc.Card([
        dbc.CardBody([
            html.P(f'# episodes leaving from {dd0}'),
            html.H5(f"{metric1} episodes")
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
            html.P(f'Average distance to travel'),
            html.H5(f"{metric2} km")
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
            html.P(f'Max distance to travel'),
            html.H5(f"{metric3} km to {max_dist_city}")
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
    
    filtered = hhi_df[hhi_df['Origin']==dd1]
    filtered = filtered[(filtered['Skip']=="Can get data") & (filtered['GeoCategory']=="All")]

    city_counts = pd.DataFrame(filtered.groupby('Destination').size()).reset_index()
    city_counts.columns = ['Destination', 'DestinationCount']
    new_df = filtered.merge(city_counts, on='Destination', how='inner')
    new_df['Key'] = 'Destination'

    orig_lat = new_df['lat_orig'][0]
    orig_lon = new_df['lon_orig'][0]


    #Add a row of the origin as destination and color it differently
    new_row = {
        'index': 0, 'ep_summary': 'Text','air_date': '01-Jan-99','ep_nums':0,
        'ep_title':'Title','episode':0,'season':0,'year':0,
        'MoveFromCity':'text','MoveFromCountry':'text','MoveToCity':'text','MoveToCountry':'text',
        'NumBlanks':0,'Origin':'text',
        'Destination':dd1,
        'GeoCategory':'All','lat_orig':0,'lon_orig':0,
        'lat_dest':orig_lat,
        'lon_dest':orig_lon,
        'distance_km':0,'Skip': 'Can get data','DestinationCount': 1,
        'Key':'Origin'
    }
    new_df = new_df.append(new_row, ignore_index = True)

    fig = px.scatter_mapbox(
        new_df, 
        lat="lat_dest", lon="lon_dest", 
        hover_name="Destination", 
        #color_continuous_scale="balance",
        color="Key",
        hover_data = {
            "Destination":True,
            #"ep_title":True,
            #"air_date":True,
            "lat_dest":False,
            "lat_dest":False,
            "lon_dest":False,
            "Key":False
        },
        labels={
            'Destination':'City'#,
            #'Episode Title':'ep_title',
        },
        size = "DestinationCount",
        zoom=2,
        center = {"lat": orig_lat, "lon": orig_lon})
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False
    )

    return fig


# #Plot Treemap Cities from Origin
# @app.callback(
#     Output('tree_map_dest_cities','figure'),
#     Input('dropdown1','value')
# )
# def treemap_dest_cities(dd1):
#     filtered = hhi_df[hhi_df['MoveFromCity']==dd1]

#     tree_fig = px.treemap(
#         filtered, 
#         path = ['MoveToCity'],
#         values = 'Destination Cities',
#         template='plotly_dark',
#         title=f'Destination Cities from {dd1}',
#         color = 'MoveToCity',
#         # color_discrete_map={
#         #     'Crossed Kármán Line':'#626ffb', 
#         #     'Elite Spacewalker':'#b064fc', 
#         #     'Space Resident': '#ef563b',
#         #     'Frequent Walker': '#f45498',
#         #     'Frequent Flyer': '#ff94fc',
#         #     'Elite Spaceflyer': '#a8f064',
#         #     'Moonwalker': '#24cce6',
#         #     'Memorial': '#ffa45c',
#         #     'ISS Visitor': '#00cc96'
#         # }   
#     )

#     tree_fig.update_traces(
#         hovertemplate='Cities=%{value}'
#     )


#     return tree_fig




if __name__=='__main__':
	app.run_server()
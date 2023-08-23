#Import packages
import pandas as pd
import os
import plotly.express as px
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go



#Read in processed data from github
hhi_df = pd.read_csv('https://raw.githubusercontent.com/statzenthusiast921/house-hunters-international/main/data/data_w_lat_lon_v2.csv',encoding='latin-1')
hhi_df = hhi_df[
    (hhi_df['Skip']=="Can get data") & 
    (hhi_df['NumBlanks']==0) &
    (~hhi_df['Origin'].str.contains(', United States',na=False))
]

hhi_df['distance_mi'] = hhi_df['distance_km'] * 0.621371

country_counts = pd.DataFrame(hhi_df.groupby('MoveFromCountry').size()).reset_index()
country_counts.columns = ['MoveFromCountry', 'num_eps_to_filter']

hhi_df = hhi_df.merge(country_counts, on='MoveFromCountry', how='left')
hhi_df['lon_orig'] = pd.to_numeric(hhi_df['lon_orig'],errors='coerce')

origin_city_choices = hhi_df['MoveFromCity'].unique()
origin_country_choices = sorted(hhi_df['MoveFromCountry'].unique())
destination_country_choices = sorted(hhi_df['MoveToCountry'].unique())
year_choices = hhi_df['year'].unique()

# Country --> City Dictionary
df_for_dict = hhi_df[['MoveFromCountry','MoveFromCity']]
df_for_dict = df_for_dict.drop_duplicates(subset='MoveFromCity',keep='first')
country_city_dict = df_for_dict.groupby('MoveFromCountry')['MoveFromCity'].apply(list).to_dict()
#country_city_dict_sorted = {l: sorted(m) for l, m in country_city_dict.items()}

geo_world = pd.read_json('https://raw.githubusercontent.com/statzenthusiast921/COVID19_Project/main/custom.geo.json')
 
# country_conversion_dict = {
#     'Dominican Rep.': "Dominican Republic", 
#     'United States': 'United States of America', 
#     'Bolivia': 'Bolivia (Plurinational State of)', 
#     'Falkland Is.': 'Falkland Islands (Malvinas)', 
#     'Venezuela': 'Venezuela (Bolivarian Republic of)', 
#     'N. Cyprus': 'Cyprus', 
#     'Brunei': 'Brunei Darussalam', 
#     'Iran': 'Iran (Islamic Republic of)', 
#     'Korea': 'Republic of Korea', 
#     'Palestine': 'occupied Palestinian territory, including east Jerusalem', 
#     'Lao PDR': "Lao People's Democratic Republic", 
#     #'Taiwan', 
#     'Vietnam': 'Viet Nam', 
#     'Dem. Rep. Korea': "Democratic People's Republic of Korea", 
#     'Syria': 'Syrian Arab Republic', 
#     "Côte d'Ivoire": 'Côte d’Ivoire', 
#     'Central African Rep.': 'Central African Republic', 
#     'Dem. Rep. Congo': 'Democratic Republic of the Congo', 
#     'Eq. Guinea': 'Equatorial Guinea', 
#     #'W. Sahara', 
#     'S. Sudan': 'South Sudan', 
#     #'Somaliland', 
#     #'Swaziland', 
#     'Tanzania': 'United Republic of Tanzania', 
#     'Czech Rep.': 'Czechia', 
#     'United Kingdom': 'The United Kingdom', 
#     'Bosnia and Herz.': 'Bosnia and Herzegovina', 
#     'Kosovo': 'Kosovo[1]', 
#     'Russia': 'Russian Federation', 
#     'Moldova': 'Republic of Moldova', 
#     'Macedonia': 'North Macedonia', 
#     'Solomon Is.': 'Solomon Islands'
    
# }

#Instanciating necessary lists
found = []
missing = []
countries_geo = []

#For simpler access, setting "zone" as index in temporary dataframe
tmp = hhi_df.set_index('MoveToCountry')

#Looping over custom GeoJSON file
for country in geo_world['features']:
    
    #Country name detection
    country_name = country['properties']['name']
    
    #Eventual replacement with our transition dictionary
    #country_name = country_conversion_dict[country_name] if country_name in country_conversion_dict.keys() else country_name
    go_on = country_name in tmp.index
    
    
    #If country is in original dataset or transition dictionary
    if go_on:
        
        #Adding country to our "Matched/Found" countries list
        found.append(country_name)
        
        #Getting information from both GeoJSON file and dataframe
        geometry = country['geometry']
        
        #Adding 'id' information for further match between map and data
        countries_geo.append({
            'type':'Feature',
            'geometry': geometry,
            'id':country_name
        })
        
    #Else, adding the country to the missing countries list
    else:
        missing.append(country_name)
 
 #Displaying metrics
print(f'Countries found: {len(found)}')
print(f'Countries not found: {len(missing)}')
geo_world_ok = {'type':'FeatureCollection','features':countries_geo}


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
            html.Div([
                html.H1(dcc.Markdown('''**Welcome To My House Hunters International Dashboard!**''')),
                html.Br()
                   ]),   
                html.Div([
                    html.P(dcc.Markdown('''**What is the purpose of this dashboard?**''')),
                ],style={'text-decoration': 'underline'}),
                html.Div([
                    html.P("This dashboard attempts to answer several questions:"),
                    html.P("1.) Which cities/countries are people moving to?"),
                    html.P("2.) Which cities/countries are people moving from?"),
                    html.P("3.) How far are people travelling on average?"),
                    html.P("4.) Is there any discernible trend with the origins or destinations?")
                ]),
                html.Div([
                    html.P(dcc.Markdown('''**What data is being used for this analysis?**''')),
                ],style={'text-decoration': 'underline'}),   
                html.Div([
                       html.P("Data was gathered over the course of a month through two methods:"),
                       html.P(["1.) scraped from the link " ,html.A("here",href="https://thetvdb.com/series/house-hunters-international/allseasons/official"),' and then Name-Entity-Recognition (NER) was used to pull out geographical text.']),
                       html.P(["2.) Painstakingly recorded by watching as much HHI as I could.  I would mark down the origin and destination in an Excel file and then load the data into a Python script that analyzed the locations using the ", html.A('geopy',href='https://geopy.readthedocs.io/en/stable/')," and ", html.A('h3',href='https://pypi.org/project/h3/'),' libraries to extract the latitudes, longitudes, and distances (in km) in between origins and destinations.'])
                ]),
                html.Div([
                    html.P(dcc.Markdown('''**What are the limitations of this data?**''')),
                ],style={'text-decoration': 'underline'}),
                html.Div(
                    children=[
                       html.P(["Not all cities and countries were available. As much as I would love to sit down and watch every single episode of House Hunters International to fill in the gaps where the episode descriptions or episode titles were insufficient, I don't have that kind of time. The episodes with missing information were left out of the distance analyses."])
                    ]
                )
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
                dbc.RadioItems(
                        id='radio1',
                        options=[
                            {'label': ' Origins', 'value': 'Origins'},
                            {'label': ' Destinations', 'value': 'Destinations'}
                        ],
                        value='Origins',
                        labelStyle={'display': 'inline-block','text-align': 'left'}
                )
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Choose a country:')
                ],width = 2),
                dbc.Col([
                    dcc.Dropdown(
                            id='dropdown_a',
                            style={'color':'black'},
                            options=[{'label': i, 'value': i} for i in origin_country_choices],
                            value= 'Australia'
                    )
                ], width =10)
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='map_origin_dest_cities')
                ],width=6),
                dbc.Col([
                    dcc.Graph(id='bar_chart_countries')
                ],width=6),

            ])
        ]),
        dcc.Tab(label='Cities',value='tab-3',style=tab_style, selected_style=tab_selected_style,
        children=[
            dbc.Row([
                dbc.Col([
                    dbc.Label('Choose a country: ')
                ],width = 2),
                dbc.Col([
                     dcc.Dropdown(
                        id='dropdown0',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_country_choices],
                        #value=origin_country_choices[0]
                    ),
                ],width=10)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Choose a city: ')
                ],width = 2),
                dbc.Col([
                    dcc.Dropdown(
                        id='dropdown1',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_city_choices],
                        #value=origin_city_choices[0]
                    ),
                ],width=10)
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='map_dest_cities')
                ], width = 6),
                dbc.Col([
                    html.Div(id='routes_table')
                ], width = 6)
            ])
        ]),
        dcc.Tab(label='Trends',value='tab-4',style=tab_style, selected_style=tab_selected_style,
            children = [
                dbc.Row([
                    dbc.Col([
                        dcc.RangeSlider(
                            id='range_slider',
                            min=year_choices.min(),
                            max=year_choices.max(),
                            step=1,
                            value=[2008, 2019],
                            allowCross=False,
                            pushable=1,
                            tooltip={"placement": "bottom", "always_visible": True},
                            marks={
                                2006: '2006',
                                2009: '2009',
                                2012: '2012',
                                2015: '2015',
                                2018: '2018',
                                2021: '2021',
                                2023: '2023'
                            }
                        )
                    ],width = 12),
                    dbc.Col([
                        dbc.RadioItems(
                            id='radio2',
                            options=[
                                {'label': ' Origins', 'value': 'Origins'},
                                {'label': ' Destinations', 'value': 'Destinations'}
                            ],
                            value='Origins',
                            labelStyle={'display': 'inline-block','text-align': 'left'}
                        )
                    ],width = 6),
                    dbc.Col([
                        dcc.Dropdown(
                            id='dropdown2',
                            style={'color':'black'},
                            options=[{'label': i, 'value': i} for i in destination_country_choices],
                            value=destination_country_choices[0],
                            multi = True
                        )
                    ], width = 6)
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph('choropleth_map')
                    ],width = 6),
                    dbc.Col([  
                        dcc.Graph('line_chart_timeline')
                    ], width = 6)
                ])
            ]
        )

     
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
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content 4')
        ])

    
#------------------------ TAB #2: Origins ------------------------#

#Filter origin city choices by parent dropdown (origin country)
@app.callback(
    Output('dropdown0', 'options'), #--> filter cities
    Output('dropdown0', 'value'),
    Input('radio1', 'value') #--> choose country
)
def set_dd_options_from_radio_button(selected_radio_button_value):
        
        if selected_radio_button_value == 'Origins':
            options = [{'label': x, 'value': x} for x in origin_country_choices]
            value = origin_country_choices[0]
        else:
            options = [{'label': x, 'value': x} for x in destination_country_choices]
            #value = destination_country_choices[0]
            value = 'Portugal'
        
        return options, value

#Cards for Origin Map
@app.callback(
    Output('card_a','children'),
    Output('card_b','children'),
    Output('card_c','children'),
    Input('dropdown_a','value'),
    Input('radio1','value')
)

def info_about_origins(dd_a, radio_select):

    if 'Origins' in radio_select:

        filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]
    
        #Metric 1 --> # of episodes
        metric1 = filtered.shape[0]

        #Metric 2 --> avg distance travelling away
        remove0s = filtered[(filtered['distance_km']>0) & (filtered['distance_km'].notnull())]
        metric2 = int(remove0s['distance_km'].median())

        #Metric 3 --> max distance
        country_ref = filtered['distance_km'].max()
        metric3 = int(filtered['distance_km'].max())
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
                html.P(f'Median distance to travel'),
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
    else:

        filtered = hhi_df[hhi_df['MoveToCountry']==dd_a]
    
        #Metric 1 --> # of episodes
        metric1 = filtered.shape[0]

        #Metric 2 --> avg distance travelling away
        remove0s = filtered[(filtered['distance_km']>0) & (filtered['distance_km'].notnull())]
        metric2 = int(remove0s['distance_km'].median())

        #Metric 3 --> max distance
        country_ref = filtered['distance_km'].max()
        metric3 = int(filtered['distance_km'].max())
        max_dist_country = filtered[filtered['distance_km']==country_ref]['MoveFromCountry'].values[0]

        card_a = dbc.Card([
            dbc.CardBody([
                html.P(f'# episodes moving to {dd_a}'),
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
                html.P(f'Median distance to travel'),
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
                html.H5(f"{metric3} km from {max_dist_country}")
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

#Plot Origin/Destination Cities
@app.callback(
    Output('map_origin_dest_cities','figure'),
    Input('dropdown_a','value'),
    Input('radio1','value')
)
def plot_map_origin_dest_cities(dd_a, radio_select):

    if 'Origins' in radio_select:
    
        filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]

        city_counts = pd.DataFrame(filtered.groupby('Origin').size()).reset_index()
        city_counts.columns = ['Origin', 'OriginCount']

        new_df = filtered.merge(city_counts, on='Origin', how='inner')


        fig = px.scatter_mapbox(
            new_df, 
            lat="lat_orig", lon="lon_orig", 
            hover_name="Origin", 
            color_continuous_scale="viridis",
            color="OriginCount",
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
            opacity = 0.25,
            zoom=3)
        
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='black' 
        )
        fig.update_coloraxes(
            colorbar=dict(bgcolor='black'),
            colorbar_title_font_color='white',
            colorbar_tickfont_color='white'
        )

        return fig
    else:
        filtered = hhi_df[hhi_df['MoveToCountry']==dd_a]

        city_counts = pd.DataFrame(filtered.groupby('Destination').size()).reset_index()
        city_counts.columns = ['Destination', 'DestinationCount']

        new_df = filtered.merge(city_counts, on='Destination', how='inner')


        fig = px.scatter_mapbox(
            new_df, 
            lat="lat_dest", lon="lon_dest", 
            hover_name="Destination", 
            color_continuous_scale="viridis",
            color="DestinationCount",
            hover_data = {
                "Destination":True,
                "DestinationCount":True,
                "lat_dest":False,
                "lon_dest":False
            },
            labels={
                'DestinationCount':'# Episodes',
                'Destination':'City'
            },
            size = "DestinationCount",
            opacity = 0.25,
            zoom=3)
        
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='black' 
        )
        fig.update_coloraxes(
            colorbar=dict(bgcolor='black'),
            colorbar_title_font_color='white',
            colorbar_tickfont_color='white'
        )


        return fig

#Bar chart of origins and destination countries
@app.callback(
    Output('bar_chart_countries','figure'),
    Input('dropdown_a','value'),
    Input('radio1','value')
)
def plot_bar_chart(dd_a, radio_select):

    if 'Origins' in radio_select:
        filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]
        dest_countries = pd.DataFrame(filtered['MoveToCountry'].value_counts()).reset_index().head(10)
        dest_countries = dest_countries.rename(columns={
            dest_countries.columns[0]: "Country" ,
            dest_countries.columns[1]: "# Episodes" 
        })
    
        bar_chart = px.bar(
            dest_countries,
            x='Country', 
            y='# Episodes',
            template = 'plotly_dark',
            title= 'Where are they moving to? (Top 10)'

        )

        return bar_chart

    else:
        filtered = hhi_df[hhi_df['MoveToCountry']==dd_a]
        origin_countries = pd.DataFrame(filtered['MoveFromCountry'].value_counts()).reset_index().head(10)
        origin_countries = origin_countries.rename(columns={
            origin_countries.columns[0]: "Country" ,
            origin_countries.columns[1]: "# Episodes" 
        })
     
        bar_chart = px.bar(
            origin_countries,
            x='Country', 
            y='# Episodes',
            template = 'plotly_dark',
            title= 'Where are they moving from? (Top 10)'

        )

        return bar_chart

#----- Tab 3: Routes

#Filter origin city choices by parent dropdown (origin country)
@app.callback(
    Output('dropdown1', 'options'), #--> filter cities
    Output('dropdown1', 'value'),
    Input('dropdown0', 'value') #--> choose country
)
def set_city_options(selected_origin_country):
    return [{'label': i, 'value': i} for i in country_city_dict[selected_origin_country]], country_city_dict[selected_origin_country][0]

@app.callback(
    Output('map_dest_cities','figure'),
    Input('dropdown0','value'),
    Input('dropdown1','value')
)
def plot_map_of_routes(dd1,dd0):

    locations_list = [dd0, ', ', dd1]

    if 'United States' in locations_list:

        full_loc_name = dd0
        filtered = hhi_df[hhi_df['Origin']==full_loc_name]


        city_counts = pd.DataFrame(filtered.groupby('Destination').size()).reset_index()
        city_counts.columns = ['Destination', 'DestinationCount']
        new_df = filtered.merge(city_counts, on='Destination', how='inner')
        new_df['Legend'] = 'Destination'
        orig_lat = float(new_df['lat_orig'][0])
        orig_lon = float(new_df['lon_orig'][0])

        #Add a row of the origin as destination and color it differently
        new_row = {
            'index': 0, 'ep_summary': 'Text','air_date': '01-Jan-99','ep_nums':0,
            'ep_title':'Title','episode':0,'season':0,'year':0,
            'MoveFromCity':'text','MoveFromCountry':'text','MoveToCity':'text','MoveToCountry':'text',
            'NumBlanks':0,'Origin':'text',
            'Destination':full_loc_name,
            'GeoCategory':'All','lat_orig':0,'lon_orig':0,
            'lat_dest':orig_lat,
            'lon_dest':orig_lon,
            'distance_km':0,'Skip': 'Can get data','DestinationCount': 1,
            'Legend':'Origin'
        }
        new_df = new_df.append(new_row, ignore_index = True)

        fig = px.scatter_mapbox(
            new_df, 
            lat="lat_dest", lon="lon_dest", 
            hover_name="Destination", 
            color="Legend",
            hover_data = {
                "Destination":True,
                "lat_dest":False,
                "lat_dest":False,
                "lon_dest":False,
                "Legend":False
            },
            labels={
                'Destination':'City'
            },
            size = "DestinationCount",
            zoom=3,
            center = {"lat": orig_lat, "lon": orig_lon})
        
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0,"t":0,"l":0,"b":0},
            showlegend=True,
            paper_bgcolor='white' ,
            font_color="black",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(0,0,0,0)'

            )
        )

        for lon,lat in zip(new_df['lon_dest'][0:-1],new_df['lat_dest'][0:-1]):
                fig.add_trace(
                    go.Scattermapbox(
                        mode="lines", 
                        lon=[new_df['lon_dest'].iloc[-1],lon], 
                        lat=[new_df['lat_dest'].iloc[-1],lat],
                        line_color = 'black',
                        showlegend = False
                    )
                )
        return fig

    else:
        full_loc_name = "".join(locations_list)

        filtered = hhi_df[hhi_df['Origin']==full_loc_name]


        city_counts = pd.DataFrame(filtered.groupby('Destination').size()).reset_index()
        city_counts.columns = ['Destination', 'DestinationCount']
        new_df = filtered.merge(city_counts, on='Destination', how='inner')
        new_df['Legend'] = 'Destination'
        orig_lat = float(new_df['lat_orig'][0])
        orig_lon = float(new_df['lon_orig'][0])

        #Add a row of the origin as destination and color it differently
        new_row = {
            'index': 0, 'ep_summary': 'Text','air_date': '01-Jan-99','ep_nums':0,
            'ep_title':'Title','episode':0,'season':0,'year':0,
            'MoveFromCity':'text','MoveFromCountry':'text','MoveToCity':'text','MoveToCountry':'text',
            'NumBlanks':0,'Origin':'text',
            'Destination':full_loc_name,
            'GeoCategory':'All','lat_orig':0,'lon_orig':0,
            'lat_dest':orig_lat,
            'lon_dest':orig_lon,
            'distance_km':0,'Skip': 'Can get data','DestinationCount': 1,
            'Legend':'Origin'
        }
        new_df = new_df.append(new_row, ignore_index = True)

        fig = px.scatter_mapbox(
            new_df, 
            lat="lat_dest", lon="lon_dest", 
            hover_name="Destination", 
            color="Legend",
            hover_data = {
                "Destination":True,
                "lat_dest":False,
                "lat_dest":False,
                "lon_dest":False,
                "Legend":False
            },
            labels={
                'Destination':'City'
            },
            size = "DestinationCount",
            zoom=3,
            center = {"lat": orig_lat, "lon": orig_lon})
        
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0,"t":0,"l":0,"b":0},
            showlegend=True,
            paper_bgcolor='black',
            font_color="black",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(0,0,0,0)'
            )
        )

        for lon,lat in zip(new_df['lon_dest'][0:-1],new_df['lat_dest'][0:-1]):
                fig.add_trace(
                    go.Scattermapbox(
                        mode="lines", 
                        lon=[new_df['lon_dest'].iloc[-1],lon], 
                        lat=[new_df['lat_dest'].iloc[-1],lat],
                        line_color = 'black',
                        showlegend = False

                    )
                )

        return fig
#Table that displays destinations from origin city (selected)
@app.callback(
    Output('routes_table','children'),
    Input('dropdown0','value'),
    Input('dropdown1','value')
)
def table(dd1,dd0):
    locations_list = [dd0, ', ', dd1]

    if 'United States' in locations_list:
    
        full_loc_name = dd0
        #full_loc_name = 'San Diego, California'
        filtered = hhi_df[hhi_df['Origin']==full_loc_name]


        city_counts = pd.DataFrame(filtered.groupby('Destination').size()).reset_index()
        city_counts.columns = ['Destination', 'DestinationCount']
        new_df = filtered.merge(city_counts, on='Destination', how='inner')
        new_df = new_df[['Origin','Destination','DestinationCount','distance_km']]
        new_df = new_df.rename(columns={
                new_df.columns[2]: "# Episodes" ,
                new_df.columns[3]: "Distance" 
            })
        new_df['Distance'] = round(new_df['Distance'],1)
        new_df = new_df.drop_duplicates()
        new_df = new_df.sort_values(['# Episodes', 'Distance'], ascending=[False, False])


        return html.Div([
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in new_df.columns],
                style_data_conditional=[{
                    'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
                style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                #filter_action='native',
                style_data={'width': '125px', 'minWidth': '125px', 'maxWidth': '125px','overflow': 'hidden','textOverflow': 'ellipsis'},
                sort_action='native',sort_mode="multi",
                page_action="native", page_current= 0,page_size= 14,                     
                data=new_df.to_dict('records')
            )
        ])
    else:
        full_loc_name = "".join(locations_list)

        filtered = hhi_df[hhi_df['Origin']==full_loc_name]

        city_counts = pd.DataFrame(filtered.groupby('Destination').size()).reset_index()
        city_counts.columns = ['Destination', 'DestinationCount']
        new_df = filtered.merge(city_counts, on='Destination', how='inner')
        new_df = new_df[['Origin','Destination','DestinationCount','distance_km']]
        new_df = new_df.rename(columns={
                new_df.columns[2]: "# Episodes" ,
                new_df.columns[3]: "Distance" 
            })
        new_df['Distance'] = round(new_df['Distance'],1)

        new_df = new_df.drop_duplicates()
        new_df = new_df.sort_values(['# Episodes', 'Distance'], ascending=[False, False])

        return html.Div([
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in new_df.columns],
                style_data_conditional=[{
                    'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
                style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                #filter_action='native',
                style_data={'width': '125px', 'minWidth': '125px', 'maxWidth': '125px','overflow': 'hidden','textOverflow': 'ellipsis'},
                sort_action='native',sort_mode="multi",
                page_action="native", page_current= 0,page_size= 14,                     
                data=new_df.to_dict('records')
            )
        ])

#TAB #4: TRENDS#

#Filter dropdown options by radio button
@app.callback(
    Output('dropdown2', 'options'),
    Output('dropdown2', 'value'),
    Input('radio1', 'value')
)
def set_dd_options_from_radio_button2(selected_radio_button_value):
        
        if selected_radio_button_value == 'Origins':
            options = [{'label': x, 'value': x} for x in origin_country_choices]
            value = ['United States','Canada']
        else:
            options = [{'label': x, 'value': x} for x in destination_country_choices]
            value = ['United States','Canada']
        
        return options, value

#Choropleth map that shows which countries are travelled to in range of years
@app.callback(
    Output('choropleth_map','figure'),
    Input('range_slider','value'),
    Input('radio2','value')
)
def choropleth_map(range_slider_values,radio2):

    filtered = hhi_df[['year','MoveFromCountry','MoveToCountry']]

    #filtered = filtered[(filtered['year']>=2012) & (filtered['year']<=2015)]
    filtered = filtered[(filtered['year']>=range_slider_values[0]) & (filtered['year']<=range_slider_values[1])]

    map_df1 = filtered[['MoveToCountry']]
    map_df2 = filtered[['MoveFromCountry']]

    if 'Origins' in radio2:

        country_counts = pd.DataFrame(map_df1.groupby('MoveToCountry').size()).reset_index()
        country_counts.columns = ['Country', 'num_eps']

        choropleth_map1 = px.choropleth_mapbox(country_counts,
                                        geojson=geo_world_ok,
                                        locations='Country',
                                        color=country_counts['num_eps'],
                                        color_continuous_scale='ylorrd',
                                        range_color=(0, country_counts['num_eps'].max()),
                                        hover_name='Country',
                                        hover_data = {'num_eps':False,
                                                        'Country':False},
                                        mapbox_style = 'open-street-map',
                                        zoom=1,
                                        center={'lat':19,'lon':11},
                                        opacity=0.6)

        return choropleth_map1
    else:
        country_counts = pd.DataFrame(map_df2.groupby('MoveFromCountry').size()).reset_index()
        country_counts.columns = ['Country', 'num_eps']

        choropleth_map1 = px.choropleth_mapbox(country_counts,
                                        geojson=geo_world_ok,
                                        locations='Country',
                                        color=country_counts['num_eps'],
                                        color_continuous_scale='ylorrd',
                                        range_color=(0, country_counts['num_eps'].max()),
                                        hover_name='Country',
                                        hover_data = {'num_eps':False,
                                                        'Country':False},
                                        mapbox_style = 'open-street-map',
                                        zoom=1,
                                        center={'lat':19,'lon':11},
                                        opacity=0.6)

        return choropleth_map1

#Line chart timeline shows the # of episodes travelling to a country per year
@app.callback(
    Output('line_chart_timeline','figure'),
    Input('range_slider','value'),
    Input('radio2','value'),
    Input('dropdown2','value')

)
def line_chart_timeline(range_slider_values, radio2, dd2):

    filtered = hhi_df[['year','MoveFromCountry','MoveToCountry']]

    #filtered = filtered[(filtered['year']>=2010) & (filtered['year']<=2015)]
    filtered = filtered[(filtered['year']>=range_slider_values[0]) & (filtered['year']<=range_slider_values[1])]


    if 'Origins' in radio2:
        line_chart_df1 = filtered[['year','MoveFromCountry']]
        line_chart_df1 = line_chart_df1[line_chart_df1['MoveFromCountry'].isin(dd2)]

        year_country_counts = pd.DataFrame(line_chart_df1.groupby(['year','MoveFromCountry']).size()).reset_index()
        year_country_counts.columns = ['year', 'MoveFromCountry','Count']

        line_chart = px.line(
            year_country_counts, 
            x="year", 
            y="Count", 
            color='MoveFromCountry'
        )
        return line_chart
    else:
        line_chart_df2 = filtered[['year','MoveToCountry']]
        line_chart_df2 = line_chart_df2[line_chart_df2['MoveToCountry'].isin(dd2)]

        year_country_counts = pd.DataFrame(line_chart_df2.groupby(['year','MoveToCountry']).size()).reset_index()
        year_country_counts.columns = ['year', 'MoveToCountry','Count']

        line_chart = px.line(
            year_country_counts, 
            x="year", 
            y="Count", 
            color='MoveToCountry'
        )
        return line_chart

if __name__=='__main__':
	app.run_server()
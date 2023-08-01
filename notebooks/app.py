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
hhi_df = hhi_df[
    (hhi_df['Skip']=="Can get data") & 
    (hhi_df['NumBlanks']==0) &
    (~hhi_df['Origin'].str.contains(', United States',na=False))
]

#hhi_df = pd.read_csv('/Users/jonzimmerman/Desktop/Data Projects/House Hunters International/data/data_w_lat_lon_v2.csv',encoding='latin-1')

country_counts = pd.DataFrame(hhi_df.groupby('MoveFromCountry').size()).reset_index()
country_counts.columns = ['MoveFromCountry', 'num_eps_to_filter']

hhi_df = hhi_df.merge(country_counts, on='MoveFromCountry', how='left')
hhi_df['lon_orig'] = pd.to_numeric(hhi_df['lon_orig'],errors='coerce')

origin_city_choices = hhi_df['MoveFromCity'].unique()
origin_country_choices = sorted(hhi_df['MoveFromCountry'].unique())
destination_country_choices = sorted(hhi_df['MoveToCountry'].unique())

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
            html.Div([
                html.H1(dcc.Markdown('''**Welcome To My House Hunters International Dashboard!**''')),
                html.Br()
                   ]),   
                html.Div([
                    html.P(dcc.Markdown('''**What is the purpose of this dashboard?**''')),
                ],style={'text-decoration': 'underline'}),
                html.Div([
                    html.P("This dashboard attempts to answer several questions:"),
                    html.P("1.) blah blah 1?"),
                    html.P("2.) blah blah 2?"),
                    html.P("3.) blah blah 3?")
                ]),
                html.Div([
                    html.P(dcc.Markdown('''**What data is being used for this analysis?**''')),
                ],style={'text-decoration': 'underline'}),   
                html.Div([
                       html.P(["Data" ,html.A(" here ",href="https://www.ahrq.gov/sdoh/data-analytics/sdoh-data.html")])
                ]),
                html.Div([
                    html.P(dcc.Markdown('''**How was the data analyzed?**''')),
                ],style={'text-decoration': 'underline'}),
                html.Div([
                    html.P(children=['.sadfasdf'])
                ]),
                html.Div([
                    html.P(dcc.Markdown('''**What are the limitations of this data?**''')),
                ],style={'text-decoration': 'underline'}),
                html.Div(
                    children=[
                       html.P("Dsdfadsfdsf."),
                       html.P(["asdfladskfadsf"])
                    ]
                )
        ]),
        dcc.Tab(label='Origins/Destinations',value='tab-2',style=tab_style, selected_style=tab_selected_style,
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
                ),
                dcc.Dropdown(
                        id='dropdown_a',
                        style={'color':'black'},
                        options=[{'label': i, 'value': i} for i in origin_country_choices],
                        value='United States'
                )
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='map_origin_dest_cities')
                ],width=6),
                dbc.Col([
                    dcc.Graph(id='tree_map_countries')
                ],width=6),

            ])
        ]),
        dcc.Tab(label='Routes',value='tab-3',style=tab_style, selected_style=tab_selected_style,
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
                ], width = 6)
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
    else:

        filtered = hhi_df[hhi_df['MoveToCountry']==dd_a]
    
        #Metric 1 --> # of episodes
        metric1 = filtered.shape[0]

        #Metric 2 --> avg distance travelling away
        remove0s = filtered[(filtered['distance_km']>0) & (filtered['distance_km'].notnull())]
        metric2 = round(remove0s['distance_km'].mean(),2)

        #Metric 3 --> max distance
        country_ref = filtered['distance_km'].max()
        metric3 = round(filtered['distance_km'].max(),2)
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
            margin={"r":0,"t":0,"l":0,"b":0}
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
            margin={"r":0,"t":0,"l":0,"b":0}
        )

        return fig

#Plot Treemap of origins and destination countries
@app.callback(
    Output('tree_map_countries','figure'),
    Input('dropdown_a','value'),
    Input('radio1','value')
)
def plot_tree_map(dd_a, radio_select):

    def colour_map_creator(df, col):
        colour_map = {}
        for i in range(len(df[col])):
            colour_map[df[col][i]] = px.colors.qualitative.Plotly[i]
        return colour_map

    if 'Origins' in radio_select:
        filtered = hhi_df[hhi_df['MoveFromCountry']==dd_a]
        dest_countries = pd.DataFrame(filtered['MoveToCountry'].value_counts()).reset_index().head(10)
        dest_countries = dest_countries.rename(columns={
            dest_countries.columns[0]: "country" ,
            dest_countries.columns[1]: "count" 
        })
    
        tree_fig = px.treemap(
            dest_countries, 
            path = ['country'],
            values = 'count',
            template ='plotly_dark',
            title=f'Top 10 Destinations moving from {dd_a}',
            color = 'country',
            color_discrete_map = colour_map_creator(dest_countries,'country')
        )

        tree_fig.update_traces(
            hovertemplate='Count=%{value}'
        )

        return tree_fig

    else:
        filtered = hhi_df[hhi_df['MoveToCountry']==dd_a]
        origin_countries = pd.DataFrame(filtered['MoveFromCountry'].value_counts()).reset_index().head(10)
        origin_countries = origin_countries.rename(columns={
            origin_countries.columns[0]: "country" ,
            origin_countries.columns[1]: "count" 
        })
     
    
        tree_fig = px.treemap(
            origin_countries, 
            path = ['country'],
            values = 'count',
            template = 'plotly_dark',
            title=f'Top 10 Origins moved from to {dd_a}',

            color = 'country',
            color_discrete_map = colour_map_creator(origin_countries,'country')
        )

        tree_fig.update_traces(
            hovertemplate='Count=%{value}'
        )

        return tree_fig



if __name__=='__main__':
	app.run_server()
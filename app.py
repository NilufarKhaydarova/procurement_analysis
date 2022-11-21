
from distutils.command.config import dump_file
from turtle import color
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import bokeh
import wfdb
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import json


#data
df = pd.read_csv('data/dashboard_df.csv', sep = ',')

#columns
vendor_terr = df['vendor_terr'].unique()
contract_dat = pd.to_datetime(df['contract_dat'])

#dict
month_dict = {1: 'Январь', 2:'Февраль', 3:'Март', 4:'Апрель', 5:'Май', 6:'Июнь', 7:'Июль', 8:'Август', 9:'Сентябрь', 10:'Октябрь', 11:'Ноябрь', 12:'Декабрь'}
months =contract_dat.dt.month.unique()
months_names = [month_dict[elem] for elem in months]
year = contract_dat.dt.year.unique()
tovar_name = df['tovar_name'].unique()
regions = df['name'].unique()

#dashboard
app = Dash(external_stylesheets=[dbc.themes.LUX])

#sidebar
sidebar = html.Div(
    [
        dbc.Row(
            [
                html.H5('Filters',
                        style={'margin-top': '12px', 'margin-left': '18'})
                ],
            style={"height": "5vh"},
            className='bg-primary text-black font-italic'
            ),
        dbc.Row(
            [
                html.Div([
                    html.P('Regions',
                           style={'margin-top': '8px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                    dcc.Dropdown(id='my-cat-picker', multi=False, value='regions',
                                 options=[{'label': x, 'value': x}
                                          for x in regions],
                                 style={'width': '320px', 'color':'black'}
                                 ),
                    html.P('Months',
                           style={'margin-top': '16px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                    dcc.Dropdown(id='my-cont-picker', multi=False, value='months',
                                 options=[{'label': x, 'value': x}
                                          for x in months_names],
                                 style={'width': '320px', 'color': 'black'}
                                 ),
                    html.P('Tovar name',
                           style={'margin-top': '16px', 'margin-bottom': '4px'},
                           className='font-weight-bold'),
                    dcc.Dropdown(id='my-corr-picker', multi=True,
                                 value='tovar name',
                                 options=[{'label': x, 'value': x}
                                          for x in tovar_name],
                                 style={'width': '320px', 'color': 'black'}
                                 ),
                    html.Button(id='my-button', n_clicks=0, children='apply',
                                style={'margin-top': '16px'},
                                className='bg-dark text-white'),
                    html.Hr()
                    ]
                    )
                ],
            style={'height': '50vh', 'margin': '8px'}),
        dbc.Row(
            [
                html.P('Qoshimcha', className='font-weight-bold')
                ],
            style={"height": "45vh", 'margin': '8px'}
            )
        ]
    )


#content

content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([
                            html.P(id='bar-title', title='Top 10',
                                   className='font-weight-bold'),
                            dcc.Graph(id="bar-chart",
                                      className='pink', )]),
                        ]),
                dbc.Col(
                    [
                     html.Div([
                            html.P(id='bar-title-2', title = 'Tail 10',
                                   className='font-weight-bold'),
                            dcc.Graph(id="bar-chart-2",
                                      className='pink')])
                    ])
            ],
            style={'height': '50vh',
                   'margin-top': '16px', 'margin-left': '8px',
                   'margin-bottom': '8px', 'margin-right': '8px'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([
                            html.P('Map',
                                   className='font-weight-bold'),
                            dcc.Graph(id='corr-chart',
                                      className='pink')])
                        ])
                ],
            style={"height": "50vh", 'margin': '8px'})
        ]
    )




app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, className='bg-dark'),
                dbc.Col(content, width=9)
                ]
            ),
        ],
    fluid=True
    )

@app.callback(Output('bar-chart', 'figure'),
              Output('bar-title', 'children'),
              Input('my-button', 'n_clicks'),
              State('my-cat-picker', 'value'))
def update_bar(n_clicks, cat_pick):
    bar_df =df.groupby('tovar_name')['summa'].sum().sort_values(ascending=False).head(10)

    fig_bar = px.bar(df,
                     x=bar_df.values,
                     y=bar_df.index,
                     color=bar_df.values,
                     color_continuous_scale='ice', 
                     )

    fig_bar.update_layout(width=500,
                          height=340,
                          margin=dict(l=40, r=20, t=20, b=30),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          legend_title=None,
                          yaxis_title=None,
                          xaxis_title=None,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.02,
                              xanchor="right",
                              x=1
                              )
                          )
    fig_bar.update_coloraxes(showscale=False)

    title_bar = 'Top 10'

    return fig_bar, title_bar

@app.callback(Output('bar-chart-2', 'figure'),
              Output('bar-title-2', 'children'),
              Input('my-button', 'n_clicks'),
              State('my-cat-picker', 'value')                    
                )
def tail_10(n_clicks, cont_pick):
    bar_df =df.groupby('tovar_name')['summa'].sum().sort_values(ascending=False).tail(10)

    fig_bar = px.bar(df,
                     x=bar_df.values,
                     y=bar_df.index, color=bar_df.values,
                    color_continuous_scale='ice')

    fig_bar.update_layout(width=500,
                          height=340,
                          margin=dict(l=40, r=20, t=20, b=30),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          legend_title=None,
                          yaxis_title=None,
                          xaxis_title=None,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.02,
                              xanchor="right",
                              x=1
                              )
                          )

    title_bar = 'Tail 10'

    return fig_bar, title_bar

@app.callback(Output('corr-chart', 'figure'),
              Input('my-button', 'n_clicks'),
              State('my-corr-picker', 'value'))
def update_corr(n_clicks, corr_pick):
    df_corr = df[['tovar_name', 'summa', 'vendor_name', 'contract_dat', 'name']]
    corr = df_corr.corr('pearson')
    x = list(corr.columns)
    y = list(corr.index)
    z = corr.values

    fig_corr = ff.create_annotated_heatmap(
        z,
        x=x,
        y=y,
        annotation_text=np.around(z, decimals=2),
        hoverinfo='z',
        colorscale='ice'
    )

    fig_corr.update_layout(width=1040,
                           height=300,
                           margin=dict(l=40, r=20, t=20, b=20),
                           paper_bgcolor='rgba(0,0,0,0)'
                           )

    return fig_corr

    
#run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)

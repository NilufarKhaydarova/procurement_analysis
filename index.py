from calendar import monthrange
from re import X
from turtle import title
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
from decouple import config

#for plotting choropleth
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.graph_objs as go
import json
import geojson
import geoplot
import geopandas
import celery
from celery import Celery
from celery.schedules import crontab
from process import df
from callbacks import * 

#dashboard
app = dash.Dash(__name__, external_scripts=['https://cdn.plot.ly/plotly-geo-assets/1.0.0/plotly-geo-assets.js'], external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

#choropleth
with open('data/geo.json') as f:
    geo_data = json.load(f)


#define navbar
def Navbar():

    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Page 1", href="/page1")),
                dbc.NavItem(dbc.NavLink("Page 2", href="/page2")),
            ] ,
            brand="Multipage Dash App",
            brand_href="/page1",
            color="dark",
            dark=True,
        ), 
    ])

    return layout


#layout for 4 charts and 1 choropleth
app.layout = html.Div([
    html.Div([
        html.H1('DXMAP', style={'margin-top': '12px', 'margin-left': '18'})
    ]),
    html.Div([
        html.Div([
            html.Div([
                html.H3('Выберите регион'),
                dcc.Dropdown(
                    id='region_name',
                    options=[{'label': i, 'value': i} for i in df.region_name.unique()]
                ),
            ], style={'width': '16%', 'display': 'inline-block', 'margin-left': '16'}),

            html.Div([
                html.H3('Выберите месяц'),
                dcc.Dropdown(
                    id='month',
                    options=[{'label': i, 'value': i} for i in df['month'].unique()]
                ),
            
            ], style={'width': '16%', 'display': 'inline-block', 'margin-left': '16'}),

            html.Div([
                html.H3('Выберите год'),
                dcc.Dropdown(
                    id='year',
                    options=[{'label': i, 'value': i} for i in df.year.unique()],
                    value=2022
                ),
            ], style={'width': '16%', 'display': 'inline-block', 'margin-left': '16'}),

            html.Div([
                html.H3('Выберите товар'),
                dcc.Dropdown(
                    id='tovar_name',
                    options=[{'label': i, 'value': i} for i in df['tovar_name'].unique()],
                    value='Бензин автомобильный'
                ),
            ], style={'width': '16%', 'display': 'inline-block', 'margin-left': '16'}),

            html.Div([
                html.H3('Выберите биржу'),
                dcc.Dropdown(
                    id='etp_id',
                    options=[{'label': i, 'value': i} for i in df['etp_id'].unique()]
                ),
            ], style={'width': '16%', 'display': 'inline-block', 'margin-left': '16'}),

            html.Div([
                html.H3('Выберите тип'),
                dcc.Dropdown(
                    id='proc_id',
                    options=[{'label': i, 'value': i} for i in df.proc_id.unique()]
                ),
            ], style={'width': '16%', 'display': 'inline-block', 'margin-left': '16'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '16'}),

        html.Div([
            html.Div([
                dcc.Graph(id='top_10')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                dcc.Graph(id='price_10')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),

        html.Div([
            html.Div([
                dcc.Graph(id='bar_line_chart')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                dcc.Graph(id='bar_chart')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
    ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        html.Div([
            html.Div([
                dcc.Graph(id='map')
            ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'})])


@app.callback(  
    Output('top_10', 'figure'),
    [Input('month', 'value'),
    Input('year', 'value'),
    Input('etp_id', 'value'),
    Input('proc_id', 'value'),
    Input('region_name', 'value')])

def update_graph_1(x, y, z, a, b):
    if x:
        df1 = df[df['month'] == x]
    else:
        df1 = df
    if y:
        df1 = df1[df1['year'] == y]
    else:
        df1 = df1
    if z:
        df1 = df1[df1['etp_id'] == z]
    else:
        df1 = df1
    if a:
        df1 = df1[df1['proc_id'] == a]
    else:
        df1 = df1
    if b:
        df1 = df1[df1['region_name'] == b]
    else:
        df1 = df1
    df1 = df1.tovar_name.value_counts(ascending=False).head(10)
    fig = px.bar(df1, x=df1.index, y=df1.values, orientation='v', color=df1.values, color_continuous_scale='mint')
    fig.update_layout(
        title='Топ 10 товаров',
        xaxis_title='Цена',
        yaxis_title='Товар'
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig



#callback Chart 2
@app.callback(
    Output('price_10', 'figure'),
    [Input('year', 'value'),
    Input('month', 'value'),
    Input('year', 'value'),
    Input('etp_id', 'value'),
    Input('proc_id', 'value'),
    Input('region_name', 'value')])
def update_graph_2(x, y, z, a, b, c):
    dff = df[(df['month'] == x) & (df['year'] == y) & (df['etp_id'] == z) & (df['proc_id'] == a) & (df['region_name'] == b)]
    dff = dff.sort_values(by='tovar_price', ascending=False)
    dff = dff.head(10)
    fig = px.bar(dff, x='tovar_name', y='tovar_price', color='tovar_price')
    fig.update_layout(
        title='Топ 10 товаров',
        xaxis_title='Товар',
        yaxis_title='Цена',
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig
    


#callback Chart 3
@app.callback(
    Output('bar_line_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('year', 'value'),
    Input('region_name', 'value'),
    Input('month', 'value'),
    Input('etp_id', 'value'),
    Input('proc_id', 'value')])
def update_graph_3(x, y, z, a, b, c):
    #for tovar_name 'Моноблок' show its average price for each month and draw a line chart with trend
    chart_3 = df[df['tovar_name'] == x].groupby('month')['tovar_price'].mean()
    fig = px.bar(x=chart_3.index, y=chart_3.values,title=f'Средняя цена по месяцам - {x}', color_continuous_scale='mint', color=chart_3.values)
    fig.add_trace(go.Scatter(x=chart_3.index, y=chart_3.values, mode='lines', name='trend'))
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
    fig.update_xaxes(title_text='Месяц')
    fig.update_yaxes(title_text='Цена')
    return fig

#callback Chart 4
@app.callback(
    Output('bar_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('region_name', 'value'),
    Input('month', 'value'),
    Input('etp_id', 'value'),
    Input('proc_id', 'value')])

def update_graph_4(x, y, z, a, b):
    #take input from dropdown and show its average price for each region
    chart_4 = df[df['tovar_name'] == x].groupby('region_name')['tovar_price'].mean()
    fig = px.bar(x=chart_4.index, y=chart_4.values,color=chart_4.values, title=f'Средняя цена по регионам - {x}', color_continuous_scale='mint')
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    #fremove y x
    fig.update_xaxes(title_text='Регион')
    fig.update_yaxes(title_text='Цена')
    return fig

    #for tovar_name 'Моноблок' show its average price for each region and draw a bar chart
    chart_4 = df[df['tovar_name'] == input].groupby('name')['tovar_price'].mean()
    fig = px.bar(x=chart_4.index, y=chart_4.values, title='Средняя цена моноблока', color_continuous_scale='ice')
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

@app.callback(
    Output('map', 'figure'),
    [Input('tovar_name', 'value'),
    Input('month', 'value'), 
    Input('year', 'value'),
    Input('etp_id', 'value'),
    Input('proc_id', 'value')])

def graph_5(input, month, year, etp_id, proc_id):
    #choropleth map for counts 
    fig = px.choropleth_mapbox(df, geojson=geo_data, locations='vendor_terr', featureidkey='properties.vendor_terr', color='counts', color_continuous_scale="mint",
                            range_color=(df['counts'].min(), df['counts'].max()),               
                            mapbox_style="carto-positron", zoom=5, 
                            opacity=0.5, center={"lat": 41.377491, "lon": 64.585262},
                            labels={'contract_dat':'Date of contract'}, title='Количество продаж по регионам')                      
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(coloraxis_showscale=False)
    fig.update_geos(fitbounds="locations", visible=True)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True, port = 5050)



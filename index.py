import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
from decouple import config
import dash

#for plotting choropleth
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.graph_objs as go
import json
from callbacks import *
from process import df 


#dashboard
app = dash.Dash(__name__, external_scripts=['https://cdn.plot.ly/plotly-geo-assets/1.0.0/plotly-geo-assets.js'], external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'], use_pages=True)


#choropleth
with open('data/geo.json') as f:
    geo_data = json.load(f)

#pages layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

#top

#home page
app.layout = html.Div([
    html.Div([
        html.H1('DXMAP', style={'margin-top': '12px', 'margin-left': '18'})
    ]),
    #add button for downloading as pdf
    html.Div([
        html.Button('PDF', id='btn_pdf', 
        style={'margin-top': '12px', 'margin-right': '18', 'float': 'right'}), 
        dcc.Download(id="download-pdf")
    ]),
    html.Div([
        html.Div([
            html.Div([
                html.H3('Выберите регион'),
                dcc.Dropdown(
                    id='region_name',
                    options=[{'label': i, 'value': i} for i in df.region_name.unique()]
                ),
            ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18'}),

            html.Div([
                html.H3('Выберите месяц'),
                dcc.Dropdown(
                    id='month',
                    options=[{'label': i, 'value': i} for i in df['month'].unique()],
                    #last month
                    value=df['month'].unique()[-1]
                ),
            
            ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18'}),

            html.Div([
                html.H3('Выберите год'),
                dcc.Dropdown(
                    id='year',  
                    options=[{'label': i, 'value': i} for i in df.year.unique()],
                    value=2022
                ),
            ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18'}),

            html.Div([
                html.H3('Выберите биржу'),
                dcc.Dropdown(
                    id='etp_id',
                    options=[{'label': i, 'value': i} for i in df['etp_id'].unique()]
                ),
            ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18'}),

            html.Div([
                html.H3('Выберите тип'),
                dcc.Dropdown(
                    id='proc_id',
                    options=[{'label': i, 'value': i} for i in df.proc_id.unique()]
                ),
            ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'})
    ]),
        html.Div([
            html.Div([
                dcc.Graph(id='top_10')
            ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        #dropdown in the middle
        html.Div([
            html.H3('Выберите товар или услугу'),
            dcc.Dropdown(
                id='tovar_name',
                options=[{'label': i, 'value': i} for i in df['tovar_name'].unique()],
                value = 'Бензин автомобильный'
            ),      
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        #align text in the middle
    
        #dropdown to the left
        html.Div([
            html.H3('Выберите регион'),
            dcc.Dropdown(
                id='region_bar',
                options=[{'label': i, 'value': i} for i in df['region_name'].unique()],
                value = 'Город Ташкент'
            ), 
        ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18'}),
        #two dropdowns to the right
            html.Div([
                html.H3('Выберите месяц'),
                dcc.Dropdown(
                    id='month_bar',
                    options=[{'label': i, 'value': i} for i in df['month'].unique()],
                    #last month
                    value=df['month'].unique()[-1]
                ),
            ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18', 'float': 'right'}),
            html.Div([
                html.H3('Выберите квартал'),
                dcc.Dropdown(
                    id='quarter_bar',
                    options=[{'label': i, 'value': i} for i in df['quarter'].unique()]
                ),
            ], style={'width': '20%', 'display': 'inline-block', 'margin-left': '18', 'float': 'right'}),
        
        html.Div([
            html.Div([
                dcc.Graph(id='bar_line_chart')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                dcc.Graph(id='bar_chart')   
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),

        html.Div([
            html.H3('Выберите тип карты'),
            dcc.Dropdown( 
                id='map_type',
                options= ['По количеству покупателей', 'По сумме закупок', 'По количеству поставщиков', 'По количеству закупок'],
                value='По количеству покупателей'
        ), 
    ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),

        html.Div([
            html.Div([
                dcc.Graph(id='map')
            ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),

        dash.page_container
    ])

@app.callback(  
    Output('top_10', 'figure'),
    [Input('month', 'value'),
    Input('year', 'value'),
    Input('etp_id', 'value'),
    Input('proc_id', 'value'),
    Input('region_name', 'value')])

def update_graph_1(month, year, etp_id, proc_id, region_name):
    if month:
        df1 = df[df['month'] == month]
    else:
        df1 = df
    if year:
        df1 = df1[df1['year'] == year]
    else:
        df1 = df1
    if etp_id:
        df1 = df1[df1['etp_id'] == etp_id]
    else:
        df1 = df1
    if proc_id:
        df1 = df1[df1['proc_id'] == proc_id]
    else:
        df1 = df1
    if region_name:
        df1 = df1[df1['region_name'] == region_name]
    else:
        df1 = df1

    chart_1 = df1.tovar_name.value_counts(ascending=False).head(10)
    fig = px.bar(chart_1, x=chart_1.index, y=chart_1.values, orientation='v', color=chart_1.values, color_continuous_scale='mint')
    fig.update_layout(
        title='Топ 10 товаров',
        xaxis_title='Товар',
        yaxis_title='Количество закупок'
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

#callback Chart 3
@app.callback(
    Output('bar_line_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('region_bar', 'value')])
def update_graph_3(tovar_name, region_bar):
    if region_bar:
        df3 = df[df['region_name'] == region_bar]
    else:
        df3 = df
    if tovar_name:
        df3 = df3[df3['tovar_name'] == tovar_name]
    else:
        df3 = df3

    chart_3 = df3[df3['tovar_name'] == tovar_name].groupby('month')['tovar_price'].mean()
    fig = px.bar(x=chart_3.index, y=chart_3.values,title=f'Средняя цена по месяцам - {tovar_name}', color_continuous_scale='mint', color=chart_3.values)
    fig.add_trace(go.Scatter(x=chart_3.index, y=chart_3.values, mode='lines', name='trend'))
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
    fig.update_layout(xaxis_title='Месяц', yaxis_title='Цена')
    #remove legend
    fig.update_layout(showlegend=False)
    return fig



#callback Chart 4
@app.callback(
    Output('bar_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('month_bar', 'value'),
    Input('quarter_bar', 'value')])
def update_graph_4(tovar_name, month_bar, quarter_bar):
    if month_bar:
        df4 = df[df['month'] == month_bar]
    else:
        df4 = df
    if quarter_bar:
        df4 = df4[df4['quarter'] == quarter_bar]
    else:
        df4 = df4
    if tovar_name:
        df4 = df4[df4['tovar_name'] == tovar_name]
    else:
        df4 = df4

    chart_4 = df4.groupby('region_name')['tovar_price'].mean()
    fig = px.bar(x=chart_4.index, y=chart_4.values, title=f'Средняя цена по месяцам - {tovar_name}', color_continuous_scale='mint', color=chart_4.values)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
    fig.update_layout(xaxis_title='Месяц', yaxis_title='Цена')
    fig.update_layout(showlegend=False)
    return fig


@app.callback(
    Output('map', 'figure'),
    [Input('map_type', 'value')]
)
def graph_5(map_type):
    if map_type == 'По количеству покупателей':
        chart_5 = df.groupby('vendor_terr')['inn'].nunique().reset_index()
        set_color = 'inn'
    elif map_type == 'По сумме закупок':
        chart_5 = df.groupby('vendor_terr')['p_summa'].sum().reset_index()
        set_color = 'p_summa'
    elif map_type == 'По количеству закупок':
        chart_5 = df.groupby('vendor_terr')['lot_id'].count().reset_index()
        set_color = 'lot_id'
    else:
        chart_5 = df.groupby('vendor_terr')['vendor_inn'].nunique().reset_index()
        set_color = 'vendor_inn'

    #choropleth map for counts 
    fig = px.choropleth_mapbox(chart_5, geojson=geo_data, locations='vendor_terr', featureidkey='properties.vendor_terr', color=set_color, color_continuous_scale="mint",
                            #range color should change depending on the map type
                            range_color=(chart_5[set_color].min(), chart_5[set_color].max()),
                            mapbox_style="carto-positron", zoom=5, 
                            opacity=0.5, center={"lat": 41.377491, "lon": 64.585262},
                            labels={'contract_dat':'Date of contract'}, title='Количество продаж по регионам')                      
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(coloraxis_showscale=False)
    fig.update_geos(fitbounds="locations", visible=True)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port = 5050)



from calendar import monthrange
from re import X
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc

#for plotting choropleth
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.graph_objs as go
import json
import geojson
import geoplot
import geopandas
from sqlalchemy import create_engine

#dashboard
app = dash.Dash(__name__, external_scripts=['https://cdn.plot.ly/plotly-geo-assets/1.0.0/plotly-geo-assets.js'], external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

#connect to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/')
conn = engine.connect()

resultat_method = pd.read_sql_table('resultat_method', conn)
rel_db = pd.read_sql_table('resultat_method_specifications', conn)
specifications = pd.read_sql_table('specifications', conn)

#contract
contract = pd.read_sql_table('contract_info', conn)
contract = contract.drop_duplicates(subset='response_id', keep='last', inplace=True)
contract = contract[contract.state == 2]
contract = contract.drop_duplicates('lot_id')

#keep valid ones
resultat_method = resultat_method[resultat_method['lot_id'].isin(contract['lot_id'])]
resultat = resultat_method.merge(rel_db, left_on='id', right_on='resultat_method_id')
df = resultat.merge(specifications, left_on='specifications_id', right_on='id')


#process vendor data
terr_dict = {
    1703: 'Andijon viloyati',
    1706: 'Buxoro viloyati',
    1730: 'Farg\‘ona viloyati',
    1708: 'Jizzax viloyati',
    1735: 'Qoraqalpog\‘iston Respublikasi',
    1710: 'Qashqadaryo viloyati',
    1733: 'Xorazm viloyati',
    1714: 'Namangan viloyati',
    1712: 'Navoiy viloyati',
    1718: 'Samarqand viloyati',
    1724: 'Sirdaryo viloyati',
    1722: 'Surxondaryo viloyati',
    1726: 'Toshkent shahri',
    1727: 'Toshkent viloyati'
}
df['vendor_terr'] = df['vendor_terr'] + 1700000
df = df[df.vendor_terr != 1700000]
df.vendor_terr = df.vendor_terr[df.vendor_terr.id.astype(str).str.len() == 4]
df.vendor_terr = df.vendor_terr.astype(str)
df['region_name'] = df['vendor_terr'].map(terr_dict)





#data
df = pd.read_csv('data/dashboard_df.csv', sep=',')
df['contract_dat'] = pd.to_datetime(df['contract_dat'])
df['contract_dat'] = df['contract_dat'].dt.strftime('%Y-%m-%d')
df['contract_dat'] = pd.to_datetime(df['contract_dat'])

#columnss
vendor_terr = df['vendor_terr'].unique()
contract_dat = pd.to_datetime(df['contract_dat'])
month_dict = {1: 'Январь', 2:'Февраль', 3:'Март', 4:'Апрель', 5:'Май', 6:'Июнь', 7:'Июль', 8:'Август', 9:'Сентябрь', 10:'Октябрь', 11:'Ноябрь', 12:'Декабрь'}
months = contract_dat.dt.month.unique()
months_names = [month_dict[elem] for elem in months]

df['month'] = df['contract_dat'].dt.month
df['month'] = df['month'].apply(lambda x: month_dict[x])

df['year'] = df['contract_dat'].dt.year



#some preprocessing
counts = df.vendor_terr.value_counts()  
counts = counts.reset_index()

df['counts'] = df['vendor_terr'].map(counts.set_index('index')['vendor_terr'])

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
                    id='name',
                    options=[{'label': i, 'value': i} for i in df.name.unique()]
                ),
            ], style={'width': '16%', 'display': 'inline-block', 'margin-left': '16'}),

            html.Div([
                html.H3('Выберите месяц'),
                dcc.Dropdown(
                    id='month',
                    options=[{'label': i, 'value': i} for i in months_names]
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
                html.H3('Выберите поставщика'),
                dcc.Dropdown(
                    id='vendor_name',
                    options=[{'label': i, 'value': i} for i in df['vendor_name'].unique()]
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

#callback Chart 1
@app.callback(
    Output('top_10', 'figure'),
    [Input('tovar_name', 'value'),
    Input('month', 'value')])   

def update_graph_1(x, y):
    chart_1 = df.tovar_name.value_counts(ascending=False).head(10)
    fig = px.bar(y=chart_1.index, x=chart_1.values, color=chart_1.values, orientation='h', title='Самые востребованные товары', color_continuous_scale='mint')
    #scale remove
    fig.update_layout(coloraxis_showscale=False)
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

#callback Chart 2
@app.callback(
    Output('price_10', 'figure'),
    [Input('year', 'value'),
    Input('month', 'value')])
def update_graph_2(x, y):
    #the most sold products that are the most expensive top 10
    chart_2 = df.groupby('tovar_name')['tovar_price'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(y=chart_2.index, x=chart_2.values, orientation='h', title='Самые дорогие товары', color_continuous_scale='mint', color=chart_2.values)
    #scale remove
    fig.update_layout(coloraxis_showscale=False)
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(title_text='Цена')
    fig.update_yaxes(title_text='Товар')
    return fig



#callback Chart 3
@app.callback(
    Output('bar_line_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('year', 'value')])
def update_graph_3(x, y):
    #for tovar_name 'Моноблок' show its average price for each month and draw a line chart with trend
    chart_3 = df[df['tovar_name'] == x].groupby('month')['tovar_price'].mean()
    fig = px.bar(x=chart_3.index, y=chart_3.values,title=f'Средняя цена по месяцам - {x}', color_continuous_scale='mint', color=chart_3.values)
    fig.add_trace(go.Scatter(x=chart_3.index, y=chart_3.values, mode='lines', name='trend'))
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
    return fig

#callback Chart 4
@app.callback(
    Output('bar_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('name', 'value')])
def update_graph_4(x, y):
    #take input from dropdown and show its average price for each region
    chart_4 = df[df['tovar_name'] == x].groupby('name')['tovar_price'].mean()
    fig = px.bar(x=chart_4.index, y=chart_4.values,color=chart_4.values, title=f'Средняя цена по регионам - {x}', color_continuous_scale='mint')
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    #fremove y x
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
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
    Input('month', 'value')])
def update_graph_5(x, y):
    fig = px.choropleth_mapbox(df, geojson=geo_data, locations='id_y', featureidkey='properties.vendor_terr', color='counts', color_continuous_scale="mint",
                            range_color=(df['counts'].min(), df['counts'].max()),               
                            mapbox_style="carto-positron", zoom=5, 
                            opacity=0.5, center={"lat": 41.377491, "lon": 64.585262},
                            labels={'contract_dat':'Date of contract'}, title='Количество продаж по регионам')                      
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_geos(fitbounds="locations", visible=True)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port = 5050)



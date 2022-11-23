from calendar import monthrange
from re import X
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc

#for plotting choropleth
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.graph_objs as go
import json
import geojson
import geoplot
import geopandas

#dashboard
app = dash.Dash(__name__, external_scripts=['https://cdn.plot.ly/plotly-geo-assets/1.0.0/plotly-geo-assets.js'], external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

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

print(df.info())
print(df.head(1))

name = df['name'].unique()

#some preprocessing
counts = df.vendor_terr.value_counts()  
counts = counts.reset_index()

df['counts'] = df['vendor_terr'].map(counts.set_index('index')['vendor_terr'])

#choropleth
with open('data/geo.json') as f:
    geo_data = json.load(f)

#callback map
fig = px.choropleth_mapbox(df, geojson=geo_data, locations='id_y', featureidkey='properties.vendor_terr', color='counts', color_continuous_scale="icefire",
                            range_color=(df['counts'].min(), df['counts'].max()),               
                            mapbox_style="carto-positron", zoom=5, 
                            opacity=0.5, center={"lat": 41.377491, "lon": 64.585262},
                            labels={'contract_dat':'Date of contract'},
                            )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_geos(fitbounds="locations", visible=True)

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
                    id='vendor_terr',
                    options=[{'label': i, 'value': i} for i in name]
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                html.H3('Выберите месяц'),
                dcc.Dropdown(
                    id='month',
                    options=[{'label': i, 'value': i} for i in months_names]
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                html.H3('Выберите товар'),
                dcc.Dropdown(
                    id='tovar_name',
                    options=[{'label': i, 'value': i} for i in df['tovar_name'].unique()]
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                html.H3('Выберите биржу'),
                dcc.Dropdown(
                    id='etp_id',
                    options=[{'label': i, 'value': i} for i in df['etp_id'].unique()]
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'margin-left': '18'}),

        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        html.Div([
            html.Div([
                html.H3('Eng ko\'p sotiladigan tovarlar 10taligi'),
                dcc.Graph(id='top_10')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                html.H3('Eng qimmat tovarlar 10taligi'),
                dcc.Graph(id='price_10')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        html.Div([
            html.Div([
                html.H3('Monoblok oylar bo\'yicha narxi'),
                dcc.Graph(id='bar_line_chart')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                html.H3('Monoblok har bir viloyat bo\'yicha narxi'),
                dcc.Graph(id='bar_chart')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        html.Div([
            html.Div([
                html.H3('map'),
                dcc.Graph(id='map', figure=fig)
            ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),])])

#callback Chart 1
@app.callback(
    Output('top_10', 'figure'),
    [Input('tovar_name', 'value'),
    Input('month', 'value')])   

def update_graph(x, y):
    chart_1 = df.tovar_name.value_counts(ascending=False).head(10)
    fig = px.bar(y=chart_1.index, x=chart_1.values, color = chart_1.values, orientation='h', title='Количество контрактов', color_continuous_scale='icefire')
    #scale remove
    fig.update_layout(coloraxis_showscale=False)
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

#callback Chart 2
@app.callback(
    Output('price_10', 'figure'),
    [Input('tovar_name', 'value'),
    Input('month', 'value')])
def update_graph(x, y):
    #the most sold products that are the most expensive top 10
    chart_2 = df.groupby('tovar_name')['tovar_summa'].count().sort_values(ascending=False).head(10)
    fig = px.bar(y=chart_2.index, x=chart_2.values, color = chart_2.values, orientation='h', title='Количество контрактов', color_continuous_scale='icefire')
    #scale remove
    fig.update_layout(coloraxis_showscale=False)
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig



#callback Chart 3
@app.callback(
    Output('bar_line_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('vendor_terr', 'value')])
def update_graph(x, y):
    #for tovar_name 'Моноблок' show its average price for each month and draw a line chart with trend
    chart_3 = df[df['tovar_name'] == 'Моноблок'].groupby('month')['tovar_summa'].mean()
    fig = px.bar(x=chart_3.index, y=chart_3.values, title='Средняя цена моноблока по месяцам', color_continuous_scale='icefire')
    fig.add_trace(go.Scatter(x=chart_3.index, y=chart_3.values, mode='lines', name='trend'))
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

#callback Chart 4
@app.callback(
    Output('bar_chart', 'figure'),
    [Input('tovar_name', 'value'),
    Input('vendor_terr', 'value')])
def update_graph(x, y):
    #for tovar_name 'Моноблок' show its average price for each region and draw a bar chart
    chart_4 = df[df['tovar_name'] == 'Моноблок'].groupby('name')['tovar_summa'].mean()
    fig = px.bar(x=chart_4.index, y=chart_4.values, title='Средняя цена моноблока', color_continuous_scale='icefire')
    #white background
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port = 5050)



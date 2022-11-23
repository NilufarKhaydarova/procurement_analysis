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

#choropleth
with open('data/geo.json') as f:
    geo_data = json.load(f)

print(geo_data['features'][0].keys())

print(geo_data['features'][0]['geometry'].keys())

print(geo_data['features'][0]['geometry']['coordinates'][0][0])

chart_1 = df.groupby('tovar_name')['summa'].sum().sort_values(ascending=False).head(10)
print(chart_1)



#columnss
vendor_terr = df['vendor_terr'].unique()
contract_dat = pd.to_datetime(df['contract_dat'])
month_dict = {1: 'Январь', 2:'Февраль', 3:'Март', 4:'Апрель', 5:'Май', 6:'Июнь', 7:'Июль', 8:'Август', 9:'Сентябрь', 10:'Октябрь', 11:'Ноябрь', 12:'Декабрь'}
months = contract_dat.dt.month.unique()
months_names = [month_dict[elem] for elem in months]

name = df['name'].unique()

counts = df.vendor_terr.value_counts()  
counts = counts.reset_index()

df['counts'] = df['vendor_terr'].map(counts.set_index('index')['vendor_terr'])

#plot choropleth
fig = px.choropleth_mapbox(df, geojson=geo_data, locations='id_y', featureidkey='properties.vendor_terr', color='counts', color_continuous_scale="Viridis",
                            range_color=(df['counts'].min(), df['counts'].max()),               
                            mapbox_style="carto-positron", zoom=5, 
                            opacity=0.5, center={"lat": 41.377491, "lon": 64.585262},
                            labels={'contract_dat':'Date of contract'},
                            )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#layout
app.layout = html.Div([
    html.Div([
        html.H1('Dashboard', style={'margin-top': '12px', 'margin-left': '18'})
    ]),
    html.Div([
        html.Div([
            html.Div([
                html.H3('Выберите регион'),
                dcc.Dropdown(
                    id='vendor_terr',
                    options=[{'label': i, 'value': i} for i in name]
                ),
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                html.H3('Выберите месяц'),
                dcc.Dropdown(
                    id='month',
                    options=[{'label': i, 'value': i} for i in months_names]
                ),
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        html.Div([
            html.Div([
                html.H3('Количество контрактов'),
                dcc.Graph(id='contracts')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
            html.Div([
                html.H3('Сумма контрактов'),
                dcc.Graph(id='sum')
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '18'}),
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
        html.Div([
            html.H3('Карта'),
            dcc.Graph(id='map', figure=fig)
        ], style={'width': '100%', 'display': 'inline-block', 'margin-left': '18'}),
    ])
])

#callback
@app.callback(
    Output('contracts', 'figure'),
    [Input('vendor_terr', 'value'),

        Input('month', 'value')])   

def update_graph(vendor_terr, month):
    fig = px.bar(x=chart_1.index, y=chart_1.values, color = chart_1.values, orientation='h', title='Количество контрактов')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port = 5050)



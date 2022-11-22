from base64 import decode
from re import X
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd 
import numpy as np
import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import geoplot
import geopandas

#data
df = pd.read_csv('data/dashboard_df.csv', sep = ',')
df['contract_dat'] = pd.to_datetime(df['contract_dat'])

path = 'data/geo.json'
with open(path) as f:
    geo = json.load(f)

uzb_data = []
for i in range(len(geo['features'])):
    uzb_data.append(geo['features'][i]['properties']['name'])
    

#plot map
fig = go.Figure(go.Choroplethmapbox(geojson=geo, locations=uzb_data, z=df['contract_dat'].value_counts(), colorscale="Viridis", zmin=0, zmax=100, marker_opacity=0.5, marker_line_width=0))
fig.show()
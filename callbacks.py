#copy callbacks from index.py to callbacks.py

# Path: callbacks.py
# Compare this snippet from index.py:

'''
import dash
import pandas as pd
import numpy as np
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
from index import app
from process import df


#callback 1
@app.callback(
    Output('top_10', 'figure'),
    [Input('name', 'value'),
    Input('year', 'value'),
    Input('month', 'value'),
    Input('proc_id', 'value')])


def update_top_10(name, year, month, proc_id):
    #top 10 most demanded tovar_name
    df_top_10 = df[(df['region_name'] == name) & (df['year'] == year) & (df['month'] == month) & (df['proc_id'] == proc_id)].groupby('tovar_name').sum().sort_values(by='counts', ascending=False).head(10)
    df_top_10 = df_top_10.reset_index()
    fig = px.bar(df_top_10, x='tovar_name', y='counts', color='tovar_name', title='Топ 10 товаров')
    fig.update_layout(
        xaxis_title="Товар",
        yaxis_title="Количество",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )
    fig.update_xaxes(tickangle=45)
    #background color none
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(coloraxis_showscale=False)
    return fig




'''

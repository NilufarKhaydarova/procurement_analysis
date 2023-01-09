from process import df
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_table

dash.register_page(__name__)

layout = html.Div([
    html.H1('Таблица'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'scroll'},
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'minWidth': '0px', 'maxWidth': '180px',
            'width': '180px'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )
])

def update_table():
    df = df.value_counts(ascending=False)
    return df.to_dict('records')


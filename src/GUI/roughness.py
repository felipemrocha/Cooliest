
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from dash import dcc
from dash import html
import dash
#import dash_core_components as dcc
#import dash_html_components as html

def calculate_roughness(thickness):
    x = np.linspace(0, 1, 100)
    y = x * 0.5 + np.random.normal(0, 0.02, size=100)
    f = interp1d(x, y, kind='cubic')
    return f(thickness)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Surface Roughness vs. Thickness'),

     dcc.Slider(
        id='thickness-slider',
        min=0,
        max=1,
        step=0.01,
        value=0.5,
        marks={0: '0', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1: '1'}
    ),

    dcc.Graph(
        id='roughness-graph',
        figure={
            'data': [
                {'x': [], 'y': [], 'type': 'line'}
            ],
            'layout': {
                'xaxis': {'title': 'Thickness'},
                'yaxis': {'title': 'Surface Roughness'},
                'margin': {'l': 40, 'b': 40, 't': 10, 'r': 10},
                'height': 300
            }
        }
    )
])

@app.callback(
    dash.dependencies.Output('roughness-graph', 'figure'),
    [dash.dependencies.Input('thickness-slider', 'value')]
)
def update_figure(thickness):
    x = np.linspace(0, 1, 100)
    y = calculate_roughness(x)
    roughness = calculate_roughness(thickness)
    return {
        'data': [
            {'x': x, 'y': y, 'type': 'line'},
            {'x': [thickness], 'y': [roughness], 'mode': 'markers', 'marker': {'size': 10}}
        ],
        'layout': {
            'xaxis': {'title': 'Thickness'},
            'yaxis': {'title': 'Surface Roughness'},
            'margin': {'l': 40, 'b': 40, 't': 10, 'r': 10},
            'height': 300
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)

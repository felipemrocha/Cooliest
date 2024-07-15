import logging
from pathlib import Path
from functools import lru_cache

import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px

from src.model.calculate_chip_temp import calculate_parameters


logging.basicConfig(level=logging.DEBUG)


def airflow_cfm_to_m3s(airflow_cfm):
    return airflow_cfm * 0.00047194745


def swap_keys_values(a):
    return dict((v, k) for k, v in a.items())


# read in fan data TODO clean data better
current_dir = Path(__file__).parent
fan_data = pd.read_csv(
    current_dir / "../../data/model/fan_specifications_rack_fans.csv", index_col=0
)
fan_data = fan_data.loc[fan_data.index.dropna()]
airflow = pd.to_numeric(fan_data["Airflow (CFM)"], errors="coerce").dropna()
airflow = airflow_cfm_to_m3s(airflow)
fans = airflow.index
fan_data = fan_data.loc[fans]
fan_data["Airflow (m3/s)"] = airflow


# Define the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        dcc.Input(id="width-input", placeholder="Enter a width...", value=0.938),
        dcc.Input(id="height-input", placeholder="Enter a height...", value=0.04445),
        dcc.Input(
            id="length_in-input", placeholder="Enter a length in...", value=0.45086 / 3
        ),
        dcc.Input(
            id="length_out-input",
            placeholder="Enter a length out...",
            value=0.45086 / 3,
        ),
        dcc.Input(
            id="length_chip-input",
            placeholder="Enter a length chip...",
            value=0.45086 / 3,
        ),
        dcc.Input(id="T_in-input", placeholder="Enter a T_in...", value=291.15),
        dcc.Input(id="q_chip-input", placeholder="Enter a q_chip...", value=50),
        dcc.Input(
            id="fluid_name-input", placeholder="Enter a fluid_name...", value="air"
        ),
        dcc.Dropdown(
            id="V_dot-radio",
            options={a: a for a in fans.to_list()},
            multi=True,
            value=fans[0],
        ),
        # Create a div to hold the bar chart
        html.Div(id="bar-chart"),
    ]
)


@lru_cache(maxsize=32)
def _calculate_parameters_cached(
    width, height, l_in, l_chip, l_out, t_in, airflow, q_chip, fluid_name
):
    """Cache the results of the calculation for a given set of parameters"""
    t_chip, t_mid_chip, t_out = calculate_parameters(
        w=width,
        h=height,
        l_in=l_in,
        l_chip=l_chip,
        l_out=l_out,
        t_in=t_in,
        v_dot=airflow,
        q=q_chip,
        fluid_name=fluid_name,
    )
    return t_mid_chip - 273.15


# Define the callback to generate the bar chart
@app.callback(
    dash.dependencies.Output("bar-chart", "children"),
    [
        dash.dependencies.Input("width-input", "value"),
        dash.dependencies.Input("height-input", "value"),
        dash.dependencies.Input("length_in-input", "value"),
        dash.dependencies.Input("length_chip-input", "value"),
        dash.dependencies.Input("length_out-input", "value"),
        dash.dependencies.Input("T_in-input", "value"),
        dash.dependencies.Input("q_chip-input", "value"),
        dash.dependencies.Input("fluid_name-input", "value"),
        dash.dependencies.Input("V_dot-radio", "value"),
    ],
)
def update_bar_chart(
    width, height, l_in, l_out, l_chip, t_in, q_chip, fluid_name, fan_names
):
    width = float(width)
    height = float(height)
    l_in = float(l_in)
    l_out = float(l_out)
    l_chip = float(l_chip)
    t_in = float(t_in)
    q_chip = float(q_chip)

    wall_temps = {
        fan_name: _calculate_parameters_cached(
            airflow=airflow.loc[fan_name],
            width=width,
            height=height,
            l_in=l_in,
            l_out=l_out,
            l_chip=l_chip,
            t_in=t_in,
            q_chip=q_chip,
            fluid_name=fluid_name,
        )
        for fan_name in fan_names
    }

    wall_temps = pd.DataFrame(pd.Series(wall_temps), columns=["wall_temp"])
    # Create the bar chart using Plotly Express
    fig = px.bar(wall_temps)

    # Return the Plotly graph as a div
    return dcc.Graph(figure=fig)


def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()

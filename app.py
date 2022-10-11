import base64
import io

import numpy as np
import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from datetime import datetime
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc
from scipy.signal import argrelextrema

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

colors = {
    "graphBackground": "#f5f5f5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div([
    dcc.Upload(
        id="upload-data",
        children=html.Div([
            html.A("Select file")
        ]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px"
        }
    ),
    dcc.Graph(id="plot"),
    html.Div(id="output-data-upload")
])

def parse_content(contents):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

        df["interpolation"] = 0
        try:
            mins = argrelextrema(df["Adj Close"].values, np.less, order=3)
            maxs = argrelextrema(df["Adj Close"].values, np.greater, order=3)
        except Exception as e:
            print("here")
            print(e)

        prev_end = 0
        for (min_ind, max_ind) in zip(mins[0], maxs[0]):
            if min_ind != prev_end:
                xdata = list(range(prev_end, min_ind+1))
                if len(xdata) > 1:
                    ydata = df.iloc[prev_end:min_ind+1]["Adj Close"].values
                    with np.errstate(divide="ignore", invalid="ignore"):
                        z = np.polyfit(xdata, ydata, 3)
                        p = np.poly1d(z)
                        yfit = p(xdata)
                    for i, x in enumerate(xdata):
                        df.iat[x, df.columns.shape[0]-1] = yfit[i]
            if min_ind != max_ind:
                xdata = list(range(prev_end, min_ind + 1))
                if len(xdata) > 1:
                    ydata = df.iloc[prev_end:min_ind + 1]["Adj Close"].values
                    with np.errstate(divide="ignore", invalid="ignore"):
                        z = np.polyfit(xdata, ydata, 3)
                        p = np.poly1d(z)
                        yfit = p(xdata)
                    for i, x in enumerate(xdata):
                        df.iat[x, df.columns.shape[0]-1] = yfit[i]
                prev_end = max_ind

    except Exception as e:
        print(e)
        html.Div([
            "There was an exception processing file"
        ])
    return df
    # return html.Div([
    #     html.H5(filename),
    #     dash_table.DataTable(
    #         df.to_dict("records"),
    #         [{"name": i, "id": i} for i in df.columns]
    #     ),
    #
    #     html.Hr(),
    # ])

@app.callback(Output("plot", "figure"),
              [
                  Input("upload-data", "contents")
              ])
def update_graph(contents):
    # fig = {
    #     "layout": go.Layout(
    #         plot_bgcolor=colors["graphBackground"],
    #         paper_bgcolor=colors["graphBackground"])
    # }
    fig = px.line(template="plotly_dark")
    if contents:
        df = parse_content(contents)
        # df = df.set_index(df.columns[0])
        fig = px.line(df, x="Date", y=["Adj Close", "interpolation"], template="plotly_dark")

    return fig

# @app.callback(Output("output-data-upload", "children"),
#               Input("upload-data", "contents"),
#               State("upload-data", "filename"))
# def update_output(content, name):
#     if content is not None:
#         return [parse_content(content, name)]

if __name__ == "__main__":
    app.run_server(debug=True)
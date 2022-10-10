import base64
import io

import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from datetime import datetime
import plotly.express as px

app = dash.Dash(__name__)

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

def parse_content(contents, filename):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
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
                  Input("upload-data", "contents"),
                  Input("upload-data", "filename")
              ])
def update_graph(contents, filename):
    # fig = {
    #     "layout": go.Layout(
    #         plot_bgcolor=colors["graphBackground"],
    #         paper_bgcolor=colors["graphBackground"])
    # }
    fig = px.scatter()
    if contents:
        df = parse_content(contents, filename)
        # df = df.set_index(df.columns[0])
        fig = px.scatter(df, x="date", y="prices")

    return fig

# @app.callback(Output("output-data-upload", "children"),
#               Input("upload-data", "contents"),
#               State("upload-data", "filename"))
# def update_output(content, name):
#     if content is not None:
#         return [parse_content(content, name)]

if __name__ == "__main__":
    app.run_server(debug=True)
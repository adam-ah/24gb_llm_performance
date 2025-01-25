import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from dash import dash_table

csv_file_path = "data.csv"
df = pd.read_csv(csv_file_path)
average_row = df.iloc[:, 1:].mean()
average_row[df.columns[0]] = "Average"
df.loc["Average"] = average_row

def color_gradient(value):
    try:
        value = float(value)
        r = int(255 * (1 - value / 1))
        g = int(255 * (value / 1))
        return f"rgb({r}, {g}, 0)"
    except (ValueError, TypeError):
        return "white"

def format_dataframe(df):
    formatted_data = []
    for _, row in df.iterrows():
        row_data = {}
        for col in df.columns:
            if col != df.columns[0]  :
                value = row[col]
                row_data[col] = {
                    "value": value,
                    "style": {"backgroundColor": color_gradient(value), "color": "black"},
                }
            else:
                row_data[col] = {"value": row[col], "style": {"fontWeight": "bold"}}
        formatted_data.append(row_data)
    return formatted_data

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("24GB VRAM LLM Models Performance", style={"textAlign": "center", "marginBottom": "20px", "fontSize": "1.5em"}),
        html.Div(
            children=[
                dcc.RadioItems(
                    id="layout-switch",
                    options=[
                        {"label": "Tests as Rows", "value": "default"},
                        {"label": "Models as Rows", "value": "transpose"},
                    ],
                    value="default",
                    inline=True,
                    style={"marginBottom": "20px"},
                )
            ],
            style={"textAlign": "center"},
        ),
        html.Div(id="table-container"),
    ]
)

@app.callback(
    Output("table-container", "children"),
    [Input("layout-switch", "value")],
)
def update_table(layout):
    """Switch between default and transposed layouts."""
    if layout == "transpose":
        table_df = df.set_index(df.columns[0]).transpose().reset_index().rename(columns={"index": "Model"})
    else:
        table_df = df

    formatted_data = format_dataframe(table_df)

    return dash_table.DataTable(
        columns=[
            {"name": col, "id": col, "presentation": "markdown"}
            for col in table_df.columns
        ],
        data=[
            {col: f"{formatted_data[row][col]['value'] * 100:.2f}" 
             if j != 0 else formatted_data[row][col]['value'] 
             for j, col in enumerate(table_df.columns)}
            for row in range(len(formatted_data))
        ],
        style_data_conditional=[
            {
                "if": {"row_index": i, "column_id": col},
                **formatted_data[i][col]["style"],
            }
            for i in range(len(formatted_data))
            for j, col in enumerate(table_df.columns)
            if j != 0
        ],
        style_header={"backgroundColor": "black", "color": "white", "fontWeight": "bold", "textAlign": "left"},
        style_data={"textAlign": "right"},
        style_table={"overflowX": "auto", "margin": "0 auto"},
        style_cell_conditional=[
            {
                "if": {"column_id": table_df.columns[0]},
                "position": "sticky",
                "left": 0,
                "backgroundColor": "white",
                "zIndex": 1,
            }
        ],
    )

if __name__ == "__main__":
    app.run_server(debug=True)

import pandas as pd
import plotly.express as px

from dash import Dash, dcc, html, Input, Output


# =========================
# Load Data
# =========================


df = pd.read_csv( r'C:\Users\New Star Computer 25\DEPI_AI\src\Data Analysis\Dash.csv')

print(df.head())
print(df.columns)



app = Dash(__name__)

app.title = "Sales Dashboard"




app.layout = html.Div([

    # Title
    html.H1(
        "Sales Dashboard",
        style={
            "marginBottom": "15px"
        }
    ),

    # Label
    html.Label(
        "Select a value to show in the pie chart"
    ),

    # Dropdown
    dcc.Dropdown(
        id="value_dropdown",

        options=[
            {
                "label": "Sales",
                "value": "Sales"
            },
            {
                "label": "Unit",
                "value": "Unit"
            },
            {
                "label": "Profit",
                "value": "Profit"
            }
        ],

        value="Sales",

        clearable=True
    ),

    # Pie Chart
    dcc.Graph(
        id="pie_chart"
    )

])


@app.callback(
    Output("pie_chart", "figure"),
    Input("value_dropdown", "value")
)


def update_pie_chart(selected_value):

    # Group data by Area
    grouped_data = (
        df.groupby("Area")[selected_value]
        .sum()
        .reset_index()
    )

    # Create Pie Chart
    fig = px.pie(
    grouped_data,
    names="Area",
    values=selected_value,
    hole=0.4,
    title=f"Distribution of {selected_value} by Area",
    color="Area",
    color_discrete_sequence=[
        "#800020",
        "#C41E3A",
        "#F08080",
        "#E6A57A",
        "#D3D3D3"
    ]
    )

    # Show percentage inside the chart
    fig.update_traces(
        textposition="inside",
        textinfo="percent"
    )

    # Layout
    fig.update_layout(
        margin={
            "l": 20,
            "r": 20,
            "t": 60,
            "b": 20
        }
    )

    return fig




if __name__ == "__main__":
    app.run(debug=True)
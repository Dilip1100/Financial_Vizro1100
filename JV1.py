import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Load the data
df = pd.read_csv("DBT.csv", encoding="latin1")

# Sort data by Year and Quarter
df = df.sort_values(by=["YEAR_ID", "QTR_ID"], ascending=[False, False])

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define a grey theme
theme = {
    "background": "#2b2b2b",
    "card_background": "#3c3c3c",
    "text_color": "#ffffff",
    "border_color": "#555555",
    "dropdown_background": "#3c3c3c",
    "dropdown_hover": "#4d4d4d",
    "table_header_background": "#555555",
    "table_header_text": "#ffffff",
    "table_cell_background": "#3c3c3c",
    "table_cell_border": "#666666"
}

# Define the layout
app.layout = html.Div(
    style={"backgroundColor": theme["background"], "padding": "20px", "fontFamily": "Arial, sans-serif"},
    children=[
        html.H1("Financial Dashboard", style={"textAlign": "center", "color": theme["text_color"], "marginBottom": "30px"}),

        # Quarter Selector
        dcc.Slider(
            id='qtr_selector',
            min=df["QTR_ID"].min(),
            max=df["QTR_ID"].max(),
            value=df["QTR_ID"].min(),
            marks={str(qtr): str(qtr) for qtr in sorted(df["QTR_ID"].unique())},
            step=None
        ),

        # Toggle for Revenue & Total Loss
        dcc.RadioItems(
            id='metric_toggle',
            options=[
                {'label': 'Revenue', 'value': 'TOTALREVENUE'},
                {'label': 'Total Loss', 'value': 'TOTALLOSS'}
            ],
            value='TOTALREVENUE',
            style={"color": theme["text_color"], "margin": "20px"}
        ),

        html.Div(
            style={"display": "flex", "gap": "20px"},
            children=[
                # Horizontal Bar Chart
                html.Div(
                    dcc.Graph(id='bar_chart'),
                    style={"flex": "1"}
                ),
                
                # Pie Chart
                html.Div(
                    dcc.Graph(id='pie_chart'),
                    style={"flex": "1"}
                )
            ]
        ),

        # Year Checkbox Selector
        dcc.Checklist(
            id='year_selector',
            options=[{'label': str(year), 'value': year} for year in sorted(df["YEAR_ID"].unique(), reverse=True)],
            value=df["YEAR_ID"].unique().tolist(),
            inline=True,
            style={"color": theme["text_color"], "margin": "20px"}
        ),

        # Line Chart for Revenue and Loss Trend
        dcc.Graph(id='line_chart')
    ]
)

# Callbacks
@app.callback(
    [Output('bar_chart', 'figure'),
     Output('pie_chart', 'figure'),
     Output('line_chart', 'figure')],
    [Input('qtr_selector', 'value'),
     Input('metric_toggle', 'value'),
     Input('year_selector', 'value')]
)
def update_charts(selected_qtr, selected_metric, selected_years):
    filtered_df = df[(df["QTR_ID"] == selected_qtr) & (df["YEAR_ID"].isin(selected_years))]
    
    # Bar Chart
    top_customers = filtered_df.groupby("CUSTOMERNAME")[selected_metric].sum().nlargest(10).reset_index()
    bar_fig = px.bar(top_customers, y="CUSTOMERNAME", x=selected_metric, title=f'Top 10 Customers by {selected_metric}',
                      orientation='h', color=selected_metric, color_continuous_scale='blues')
    
    # Pie Chart
    top_countries = filtered_df.groupby("COUNTRY")[selected_metric].sum().nlargest(10).reset_index()
    pie_fig = px.pie(top_countries, values=selected_metric, names="COUNTRY", title=f'Top 10 Countries by {selected_metric}',
                      color_discrete_sequence=px.colors.sequential.Blues)
    
    # Line Chart
    trend_df = df[df["YEAR_ID"].isin(selected_years)].groupby(["QTR_ID"])[["TOTALREVENUE", "TOTALLOSS"]].sum().reset_index()
    line_fig = px.line(trend_df, x="QTR_ID", y=["TOTALREVENUE", "TOTALLOSS"], title="Revenue & Loss Trend by Quarter",
                        labels={"value": "Amount", "variable": "Metric"}, color_discrete_sequence=['#1f77b4', '#ff7f0e'])
    
    return bar_fig, pie_fig, line_fig

if __name__ == '__main__':
    app.run_server(debug=True)

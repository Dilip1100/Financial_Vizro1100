import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc

# ---- Load Data ----
df = pd.read_csv('https://github.com/Dilip1100/Financial_Vizro1100/blob/94d364e98061cd58f8b52224f33037aa7ca3ed5f/DV2.csv', encoding='latin1')
df.columns = [col.strip().replace("ï»¿", "") for col in df.columns]
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
df['Year'] = df['Date'].dt.year
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

# ---- App ----
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# ---- Theme ----
theme = {
    "background": "#2E2E2E",
    "text_color": "#FFFFFF",
    "chart_bg": "#3A3A3A",
    "bar_color": "#1f77b4",
    "pie_colors": px.colors.sequential.Plasma_r
}

dropdown_style = {
    "variant": "filled",
    "size": "sm",
    "radius": "md",
    "styles": {"dropdown": {"backgroundColor": "#1C1C1C", "color": "#FFF"}}
}

# ---- Layout ----
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    children=html.Div(style={"backgroundColor": theme["background"], "padding": "20px", "color": theme["text_color"]}, children=[

        html.H1("Car Retailer Sales Dashboard", style={"textAlign": "center"}),

        html.Div(style={"display": "flex", "justifyContent": "space-around", "marginBottom": "20px", "gap": "10px"}, children=[
            dmc.MultiSelect(
                id='salesperson_filter',
                data=[{'label': s, 'value': s} for s in sorted(df['Salesperson'].dropna().unique())],
                placeholder="Select Salesperson",
                searchable=True,
                clearable=True,
                style={"width": "280px"},
                **dropdown_style
            ),
            dmc.MultiSelect(
                id='car_make_filter',
                data=[{'label': m, 'value': m} for m in sorted(df['Car Make'].dropna().unique())],
                placeholder="Select Car Make",
                searchable=True,
                clearable=True,
                style={"width": "280px"},
                **dropdown_style
            ),
            dmc.MultiSelect(
                id='car_year_filter',
                data=[{'label': str(int(y)), 'value': str(int(y))} for y in sorted(df['Car Year'].dropna().unique())],
                placeholder="Select Car Year",
                searchable=True,
                clearable=True,
                style={"width": "180px"},
                **dropdown_style
            )
        ]),

        dcc.RadioItems(
            id='metric_toggle',
            options=[
                {'label': 'Sale Price', 'value': 'Sale Price'},
                {'label': 'Commission Earned', 'value': 'Commission Earned'}
            ],
            value='Sale Price',
            labelStyle={"display": "inline-block", "marginRight": "10px"},
            style={"textAlign": "center", "marginBottom": "20px"}
        ),

        html.Div(style={'display': 'flex', 'justify-content': 'space-between'}, children=[
            html.Div(id='bar_chart', style={'width': '48%', 'backgroundColor': theme['chart_bg']}),
            html.Div(id='pie_chart', style={'width': '48%', 'backgroundColor': theme['chart_bg']})
        ]),

        html.Div(id='trend_chart', style={'marginTop': '20px', 'backgroundColor': theme['chart_bg']})
    ])
)

# ---- Callback Logic ----
@app.callback(
    [Output('bar_chart', 'children'), Output('pie_chart', 'children'), Output('trend_chart', 'children')],
    [
        Input('salesperson_filter', 'value'),
        Input('car_make_filter', 'value'),
        Input('car_year_filter', 'value'),
        Input('metric_toggle', 'value')
    ]
)
def update_graph(salespeople, makes, years, selected_metric):
    filtered_df = df.copy()

    if salespeople:
        filtered_df = filtered_df[filtered_df['Salesperson'].isin(salespeople)]
    if makes:
        filtered_df = filtered_df[filtered_df['Car Make'].isin(makes)]
    if years:
        filtered_df = filtered_df[filtered_df['Car Year'].astype(str).isin(years)]

    # Bar Chart
    top_salespeople = filtered_df.groupby('Salesperson')[selected_metric].sum().nlargest(10).reset_index()
    bar_fig = px.bar(top_salespeople, y='Salesperson', x=selected_metric, orientation='h',
                     title=f'Top 10 Salespeople by {selected_metric}',
                     color_discrete_sequence=[theme['bar_color']],
                     template='plotly_dark')

    # Pie Chart (Donut Style)
    car_make_metric = filtered_df.groupby('Car Make')[selected_metric].sum().nlargest(10).reset_index()
    pie_fig = px.pie(car_make_metric, names='Car Make', values=selected_metric,
                     title=f'Top 10 Car Makes by {selected_metric}',
                     hole=0.3,
                     color_discrete_sequence=theme['pie_colors'],
                     template='plotly_dark')

    # Trend Line Chart by Quarter
    trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
    trend_fig = px.line(trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'],
                        markers=True, title='Sales and Commission Trend by Quarter',
                        labels={'value': 'Amount', 'Quarter': 'Quarter'},
                        template='plotly_dark')

    return dcc.Graph(figure=bar_fig), dcc.Graph(figure=pie_fig), dcc.Graph(figure=trend_fig)

# ---- Run Server ----
if __name__ == '__main__':
    app.run(debug=True)

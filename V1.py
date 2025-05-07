import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data
file_path = 'https://github.com/Dilip1100/Financial_Vizro1100/blob/0342b0328b64852877190a60523265bdb9ca4b4a/DBT.csv'
df = pd.read_csv(file_path, encoding='latin1')

# Ensure correct column names
expected_columns = ["CUSTOMERNAME", "COUNTRY", "YEAR_ID", "QTR_ID", "TOTALLOSS", "TOTALREVENUE", "PROFIT"]
df.columns = expected_columns

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Theme
theme = {
    "background": "#2E2E2E",
    "text_color": "#FFFFFF",
    "chart_bg": "#3A3A3A",
    "bar_color": "#1f77b4",
    "pie_colors": px.colors.qualitative.Set3
}

app.layout = html.Div(style={"backgroundColor": theme["background"], "padding": "20px", "color": theme["text_color"]}, children=[
    html.H1("DBT Data Visualization", style={"textAlign": "center", "color": theme["text_color"]}),
    
    # Year Checkbox Slicer
    dcc.Checklist(
        id='year_checkbox',
        options=[{'label': str(y), 'value': y} for y in sorted(df['YEAR_ID'].unique())],
        value=[df['YEAR_ID'].max()],
        inline=True,
        style={"textAlign": "center", "marginBottom": "20px", "color": theme["text_color"]}
    ),
    
    # Toggle switch for Revenue and Total Loss
    dcc.RadioItems(
        id='metric_toggle',
        options=[
            {'label': 'Total Revenue', 'value': 'TOTALREVENUE'},
            {'label': 'Total Loss', 'value': 'TOTALLOSS'}
        ],
        value='TOTALREVENUE',
        labelStyle={"display": "inline-block", "marginRight": "10px"},
        style={"textAlign": "center", "marginBottom": "20px"}
    ),
    
    html.Div(style={'display': 'flex', 'justify-content': 'space-between'}, children=[
        # Bar chart container (Left)
        html.Div(id='revenue_bar_chart', style={'width': '48%', 'backgroundColor': theme['chart_bg']}),
        
        # Pie chart container (Right)
        html.Div(id='revenue_pie_chart', style={'width': '48%', 'backgroundColor': theme['chart_bg']})
    ]),
    
    # Line Chart for Revenue and Loss Trend
    html.Div(id='revenue_loss_trend_chart', style={'marginTop': '20px', 'backgroundColor': theme['chart_bg']})
])

@app.callback(
    [Output('revenue_bar_chart', 'children'), Output('revenue_pie_chart', 'children'), Output('revenue_loss_trend_chart', 'children')],
    [Input('year_checkbox', 'value'), Input('metric_toggle', 'value')]
)
def update_graph(selected_years, selected_metric):
    filtered_df = df[df['YEAR_ID'].isin(selected_years)]
    
    # Get top 10 customers by selected metric
    top_customers = filtered_df.groupby('CUSTOMERNAME')[selected_metric].sum().nlargest(10).reset_index()
    fig_revenue_bar = px.bar(top_customers, y='CUSTOMERNAME', x=selected_metric, title=f'Top 10 Customers by {selected_metric}', 
                              labels={selected_metric: selected_metric},
                              orientation='h',
                              color_discrete_sequence=[theme['bar_color']], 
                              template='plotly_dark')
    
    # Pie chart for top 10 countries by selected metric
    country_metric = filtered_df.groupby('COUNTRY')[selected_metric].sum().nlargest(10).reset_index()
    fig_revenue_pie = px.pie(country_metric, names='COUNTRY', values=selected_metric, title=f'Top 10 Countries by {selected_metric}',
                              color_discrete_sequence=px.colors.qualitative.Set3)
    
    # Line chart for Revenue and Loss Trend using QTR_ID
    trend_df = filtered_df.groupby(['QTR_ID'])[['TOTALREVENUE', 'TOTALLOSS']].sum().reset_index()
    fig_trend = px.line(trend_df, x='QTR_ID', y=['TOTALREVENUE', 'TOTALLOSS'],
                         markers=True, title='Revenue & Loss Trend Over Quarters',
                         labels={'value': 'Amount', 'QTR_ID': 'Quarter'},
                         template='plotly_dark')
    
    return dcc.Graph(figure=fig_revenue_bar), dcc.Graph(figure=fig_revenue_pie), dcc.Graph(figure=fig_trend)

if __name__ == '__main__':
    app.run_server(debug=True)

from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from django_plotly_dash import DjangoDash

# Database connection details
DB_URL = "mssql+pyodbc://sa:Admin123!@127.0.0.1/INFDAT?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DB_URL)

# Fetch data from the database
def fetch_data(query):
    return pd.read_sql(query, engine)

# Fetch vendor sales data
sales_data_query = """
SELECT vendor_name, SUM(sales) as total_sales
FROM sales_table
GROUP BY vendor_name
"""
sales_data = fetch_data(sales_data_query)

# Fetch vendor information
vendor_info_query = """
SELECT vendor_id, vendor_name, contact_name, contact_email, contact_phone
FROM vendor_table
"""
vendor_info = fetch_data(vendor_info_query)

# Create a bar chart for sales trends
sales_trends_fig = px.bar(sales_data, x='vendor_name', y='total_sales', title='Sales Trends by Vendor')

# Create a table for vendor information
vendor_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in vendor_info.columns],
    data=vendor_info.to_dict('records'),
    page_size=10,
)

# Define the Dash app
app = DjangoDash('VendorDashboard')
app.layout = html.Div([
    html.H1("Vendor Dashboard"),
    dcc.Graph(figure=sales_trends_fig),
    html.H2("Vendor Information"),
    vendor_table,
])
import random
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='Sales Dashboard', page_icon=':bar_chart', layout='wide')


st.title('Sales Dashboard')

with st.sidebar:
    st.header('Configurations')
    uploaded_file = st.file_uploader('Choose a file')
    
if uploaded_file is None:
    st.info('Upload a file through config')
    st.stop()
    
    
@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)
    return df

df = load_data(uploaded_file)
all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

with st.expander('Data Preview'):
    st.dataframe(
        df,
        column_config={'Year': st.column_config.NumberColumn(format='%d')}
    )
    
def plot_metric(label, value, prefix='', suffix='', show_graph=False, color_graph='', text_color='', num_color=''):
    fig = go.Figure()
    
    fig.add_trace(
        go.Indicator(
            value = value,
            gauge={'axis': {'visible': False}},
            number={
                'prefix': prefix,
                'suffix': suffix,
               'font': {'size': 22, 'color': num_color},
            },
            title={
                'text': label,
                'font': {'size': 20,'color':text_color}
            }
        )
    )
    
    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo='skip',
                fill='tozeroy',
                fillcolor=color_graph,
                line={
                    'color': color_graph
                }
            )
        )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        margin = dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor='white',
        height=200
    )
    
    st.plotly_chart(fig, use_container_width=True)
    

def plot_gauge(
    indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound
):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode='gauge+number',
            domain={'x':[0,1], 'y':[0,1]},
            number={
                'suffix': indicator_suffix,
                'font.size': 26
            },
            gauge={
                'axis': {'range': [0, max_bound], 'tickwidth': 1},
                'bar': {'color': indicator_color}
            },
            title={
                'text': indicator_title,
                'font': {'size': 28},
            }
        )
    )
    fig.update_layout(
        height=200,
        margin=dict(l=10,r=10,b=10,pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_top_right():
    sales_data = duckdb.sql(
        f''' 
            WITH sales_data AS (
                UNPIVOT (
                    SELECT
                        Scenario,
                        business_unit,
                        {','.join(all_months)}
                        from df
                        WHERE Year = '2023'
                        AND ACCOUNT = 'Sales'
                )
                ON {','.join(all_months)}
                INTO 
                    NAME month
                    VALUE sales
            ),
            
            aggregated_sales AS (
                SELECT
                    Scenario,
                    business_unit,
                    SUM(sales) AS sales
                FROM sales_data
                GROUP BY Scenario, business_unit
            )
            SELECT * FROM aggregated_sales
        '''
    ).df()
    
    fig = px.bar(
        sales_data,
        x='business_unit',
        y='sales',
        color='Scenario',
        barmode='group',
        text_auto='.2s',
        title='Sales for some year 2023',
        height=400
    )
    fig.update_traces(
        textfont_size=12, textangle=0, textposition='outside', cliponaxis=False
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_bottom_left():
    sales_data = duckdb.sql(
        f''' 
            WITH sales_data AS (
                SELECT
                Scenario,{','.join(all_months)}
                FROM df
                WHERE Year = '2023'
                AND Account = 'Sales'
                AND business_unit='Software'
            )
            UNPIVOT sales_data
            ON {','.join(all_months)}
            INTO
                NAME month
                VALUE sales
        '''
    ).df()
    
    fig = px.line(
        sales_data,
        x='month',
        y='sales',
        color='Scenario',
        markers=True,
        title='Motn budget 2023',
        text='sales'
    )
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)
    
def plot_bottom_right():
    sales_data = duckdb.sql(
        f''' 
           WITH sales_data AS (
               UNPIVOT (
                   SELECT
                        Account, Year, {','.join([f'ABS({month}) AS {month}' for month in all_months])}
                        FROM df
                        WHERE Scenario='Actuals'
                        AND ACCOUNT !='Sales'
               )
               ON {','.join(all_months)}
               INTO
                NAME year
                VALUE sales
           ),
           
           aggregated_sales AS (
               SELECT
                    Account,
                    Year,
                    SUM(sales) AS sales
               FROM sales_data
               GROUP BY Account, Year
           )
           SELECT * FROM aggregated_sales
        '''
    ).df()
    
    fig = px.bar(
        sales_data,
        x='Year',
        y='sales',
        color='Account',
        title='Yearly sales 2023',
    )
    st.plotly_chart(fig, use_container_width=True)


top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)

with top_left_column:
    column1, column2, column3, column4 = st.columns(4)
    
    with column1:
        plot_metric(
            'Total Accounts Receivable',
            6621280,
            prefix='$',
            suffix='',
            show_graph=True,
            color_graph='rgba(0, 104, 201, 0.2)',
            text_color='black',
            num_color='rgba(0, 104, 201, 0.6)'
        )
        plot_gauge(1.86, '#0000ff', '%', 'In Stock', 31)
    with column2:
        plot_metric(
            'Total Accounts Payable',
            1630270,
            prefix='$',
            suffix='',
            show_graph=True,
            color_graph='rgba(255, 43, 43, 0.2)',
            text_color='black',
            num_color='rgba(255, 0, 0, 0.6)'
        )
        plot_gauge(10, '#ff8700', 'days', 'In Stock', 31)
    with column3:
        plot_metric('Equity Ratio', 75.38, prefix='', suffix='%', show_graph=False, text_color='white', num_color='white')
        plot_gauge(7, '#ff2b2b', 'days', 'Out Stock', 31)
        
    with column4:
        plot_metric('Debt Equity', 1.10, prefix='', suffix='%', show_graph=False, text_color='white', num_color='white')
        plot_gauge(28, '#29b0d9', 'days', 'Delay', 31)
        
with top_right_column:
    plot_top_right()
    
with bottom_left_column:
    plot_bottom_left()
    
with bottom_right_column:
    plot_bottom_right()

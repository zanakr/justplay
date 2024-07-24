import os
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Function to capitalize the first letter of a string for display purposes
def capitalize_first_letter(s):
    return s[0].upper() + s[1:] if s else s

# Function for the first page (Installs Data Exploration)
def installs_data_exploration():
    # Load the dataset
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(current_dir, '../data/processed/installs.csv')

    # Create combined column for channel, campaign, and creative
    df['channel_campaign_creative'] = df['channel'] + ' | ' + df['campaign'] + ' | ' + df['creative']

    # Streamlit App
    st.title('Installs Data Exploration')

    # Sidebar for selecting x and y axes
    st.sidebar.header('User Input Features')

    # Select dimension for x-axis
    x_axis_options = ['countryName', 'adGroupName', 'trackerName', 'limitAdTracking', 
                      'os_name', 'device', 'channel', 'campaign', 'creative', 
                      'channel_campaign_creative']
    x_axis_display_options = [capitalize_first_letter(option) for option in x_axis_options]
    x_axis_display = st.sidebar.selectbox('Select X-axis dimension', x_axis_display_options)
    x_axis = x_axis_options[x_axis_display_options.index(x_axis_display)]

    # Plot distribution based on selected dimension
    st.subheader(f'Distribution by {x_axis_display}')

    plot_data = df[x_axis].value_counts().reset_index()
    plot_data.columns = [x_axis_display, 'count']

    fig = px.bar(plot_data, 
                 x=x_axis_display, y='count', 
                 labels={x_axis_display: x_axis_display, 'count': 'Number of Installations'},
                 title=f'Installations by {x_axis_display}')
    st.plotly_chart(fig)

    # Filtered Data
    st.header('Filtered Data by Country')
    country = st.selectbox('Select Country', sorted(df['countryName'].unique()))
    filtered_df = df[df['countryName'] == country]

    st.write(f'Data for {country}')
    st.write(filtered_df)

    # Display summary statistics for filtered data
    st.subheader('Summary Statistics for Filtered Data')
    st.write(filtered_df.describe(include='all'))

    # Allow downloading of filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(label='Download Filtered Data as CSV', data=csv, file_name=f'{country}_installs.csv', mime='text/csv')

# Function for the second page (Revenue Data Exploration)
def revenue_data_exploration():
    # Load data
    data = pd.read_csv('../data/processed/revenue.csv')

    # Rename columns
    data = data.rename(columns={
        'userId': 'Number of Users',
        'amount': 'Revenue Amount'
    })

    # Title
    st.title("Revenue Data Exploration")

    # Sidebar for selecting x and y axes
    st.sidebar.header('User Input Features')

    # Interactive plot options
    x_axis_options = ['countryName', 'platform', 'source', 'network', 'adUnitFormat', 'packageName', 'adUnitName']
    x_axis_display_options = [capitalize_first_letter(option) for option in x_axis_options]
    x_axis_display = st.sidebar.selectbox("Select X-axis dimension", x_axis_display_options)
    x_axis = x_axis_options[x_axis_display_options.index(x_axis_display)]

    # Header for the plots
    st.header(f'Distribution by {x_axis_display}')

    # Prepare data for plotting
    plot_data_users = data.groupby(x_axis)['Number of Users'].nunique().reset_index()
    plot_data_users.columns = [x_axis_display, 'Number of Users']
    plot_data_users = plot_data_users.sort_values(by='Number of Users', ascending=False)

    plot_data_revenue = data.groupby(x_axis)['Revenue Amount'].sum().reset_index()
    plot_data_revenue.columns = [x_axis_display, 'Revenue Amount']
    plot_data_revenue = plot_data_revenue.set_index(x_axis_display).reindex(plot_data_users[x_axis_display]).reset_index()

    # Create plots with ordered values
    fig_users = px.bar(plot_data_users, x=x_axis_display, y='Number of Users', 
                       title=f'Number of Users by {x_axis_display}',
                       category_orders={x_axis_display: plot_data_users[x_axis_display].tolist()})

    fig_revenue = px.bar(plot_data_revenue, x=x_axis_display, y='Revenue Amount', 
                         title=f'Revenue Amount by {x_axis_display}',
                         category_orders={x_axis_display: plot_data_users[x_axis_display].tolist()})

    # Display plots
    st.plotly_chart(fig_users)
    st.plotly_chart(fig_revenue)

# Function for the third page (Ad Spend Installs Data Exploration)
def ad_spend_installs_exploration():
    # Load the datasets
    ad_spend_df = pd.read_csv('../data/processed/ad_spend_installs.csv')
    ad_spend_df_without_outliers = pd.read_csv('../data/processed/ad_spend_installs_without_outliers.csv')

    # Calculate additional metrics for both datasets
    for df in [ad_spend_df, ad_spend_df_without_outliers]:
        df['Cost per Install (CPI)'] = df['cost'] / df['installs']
        df['Install Rate'] = df['installs'] / df['network_impressions']
        df['Click-through Rate (CTR)'] = df['network_clicks'] / df['network_impressions']
        df['Conversion Rate'] = df['installs'] / df['network_clicks']
        df.replace([float('inf'), -float('inf')], 0, inplace=True)
        df['channel_campaign_creative'] = df['channel'] + ' | ' + df['campaign'] + ' | ' + df['creative']

    # Streamlit app
    st.title('Ad Spend Installs Data Exploration')

    # Sidebar for selecting the dataset
    dataset_option = st.sidebar.radio(
        'Select Dataset',
        ('Original Dataset', 'Dataset Without Outliers')
    )

    # Select the appropriate dataframe based on the user input
    if dataset_option == 'Original Dataset':
        selected_df = ad_spend_df
    else:
        selected_df = ad_spend_df_without_outliers

    # Sidebar for selecting x and y axes
    st.sidebar.header('User Input Features')

    # Dropdown for selecting the y-axis
    y_axis = st.sidebar.selectbox(
        'Select Y-axis metric',
        ['network_clicks', 'network_impressions', 'network_installs', 'network_installs_diff', 'installs', 'cost', 
         'Cost per Install (CPI)', 'Install Rate', 'Click-through Rate (CTR)', 'Conversion Rate']
    )

    # Dropdown for selecting the x-axis
    x_axis = st.sidebar.selectbox(
        'Select X-axis dimension',
        ['country_name', 'os_name', 'channel', 'campaign', 'creative', 'channel_campaign_creative']
    )

    # Filtered dataframe based on the selected columns
    filtered_df = selected_df[[x_axis, y_axis]]

    # Plotting
    fig = px.bar(filtered_df, x=x_axis, y=y_axis, color=x_axis, title=f'{y_axis} by {x_axis}')
    st.plotly_chart(fig)

# Function for the main page (JustPlay Ad Performance Metrics Dashboard)
def ad_performance_metrics_dashboard():
    # Load the dataset
    ad_performance_metrics_per_channel = pd.read_csv('../data/processed/ad_performance_metrics_per_channel.csv')

    # Fill NaN and infinity values with zero
    ad_performance_metrics_per_channel = ad_performance_metrics_per_channel.fillna(0)
    ad_performance_metrics_per_channel = ad_performance_metrics_per_channel.replace([float('inf'), float('-inf')], 0)

    # Calculate metrics
    total_revenue = ad_performance_metrics_per_channel['revenue_2024_01_01'].sum()
    total_users = ad_performance_metrics_per_channel['installs/users_2024_01_01'].sum()
    total_events = ad_performance_metrics_per_channel['events_2024_01_01'].sum()
    total_installs = ad_performance_metrics_per_channel['installs'].sum()
    total_network_installs = ad_performance_metrics_per_channel['network_installs'].sum()
    total_installs_on_date = ad_performance_metrics_per_channel['installs/users_2024_01_01'].sum() 
    total_impressions = ad_performance_metrics_per_channel['network_impressions'].sum()
    total_clicks = ad_performance_metrics_per_channel['network_clicks'].sum()
    total_cost = ad_performance_metrics_per_channel['cost'].sum()

    cpi = total_cost / total_installs if total_installs != 0 else 0
    cpc = total_cost / total_clicks if total_clicks != 0 else 0
    ctr = (total_clicks / total_impressions) * 100 if total_impressions != 0 else 0
    conversion_rate = (total_network_installs / total_clicks) * 100 if total_clicks != 0 else 0
    install_rate = (total_network_installs / total_impressions) * 100 if total_impressions != 0 else 0
    rpi = total_revenue / total_installs if total_installs != 0 else 0
    roas = total_revenue / total_cost if total_cost != 0 else 0
    arpu = total_revenue / total_users if total_users != 0 else 0
    roi = ((total_revenue - total_cost) / total_cost) * 100 if total_cost != 0 else 0

    # Streamlit App
    st.title("Ad Performance Metrics Dashboard")

    st.header("Key Metrics")
    st.metric("Total Revenue on 01.01.2024", f"${total_revenue:,.2f}")
    st.metric("Total Installs on 01.01.2024", f"{total_installs_on_date:,}")
    st.metric("Total Events on 01.01.2024", f"{total_events:,}")
    st.metric("Total Installs", f"{total_installs:,}")
    st.metric("Total Network Installs", f"{total_network_installs:,}")
    st.metric("Total Impressions", f"{total_impressions:,}")
    st.metric("Total Clicks", f"{total_clicks:,}")
    st.metric("Cost per Install (CPI)", f"${cpi:.2f}")
    st.metric("Cost per Click (CPC)", f"${cpc:.2f}")
    st.metric("Click Through Rate (CTR)", f"{ctr:.2f}%")
    st.metric("Conversion Rate", f"{conversion_rate:.2f}%")
    st.metric("Install Rate", f"{install_rate:.2f}%")
    st.metric("Revenue per Install (RPI)", f"${rpi:.2f}")
    st.metric("Return on Ad Spend (ROAS)", f"{roas:.2f}")
    st.metric("Average Revenue per User (ARPU)", f"${arpu:.2f}")
    st.metric("Return on Investment (ROI)", f"{roi:.2f}%")

    st.header("Visualizations")

    # Metric filter
    metric_options = {
        'Revenue on 01.01.2024': 'revenue_2024_01_01',
        'Installs on 01.01.2024': 'installs/users_2024_01_01',
        'Events on 01.01.2024': 'events_2024_01_01',
        'Installs': 'installs',
        'Network Installs': 'network_installs',
        'Network Impressions': 'network_impressions',
        'Network Clicks': 'network_clicks',
        'Cost': 'cost'
    }

    selected_metric = st.selectbox("Select Metric to Display per Channel", options=list(metric_options.keys()))

    # Display selected metric per channel
    st.subheader(f"{selected_metric} per Channel")
    fig = px.bar(ad_performance_metrics_per_channel, x='channel', y=metric_options[selected_metric],
                 title=f'{selected_metric} per Channel')
    st.plotly_chart(fig)

    # Relationship between cost and installs
    st.subheader("Relationship between Cost and Installs")
    fig = px.scatter(ad_performance_metrics_per_channel, x='cost', y='installs', title='Cost vs. Installs', opacity=0.5)
    st.plotly_chart(fig)

    # Relationship between network impressions and installs
    st.subheader("Relationship between Network Impressions and Installs")
    fig = px.scatter(ad_performance_metrics_per_channel, x='network_impressions', y='installs', title='Network Impressions vs. Installs', opacity=0.5)
    st.plotly_chart(fig)

# Main app
def main():
    with st.sidebar:
        selected = option_menu("JustPlay Case Study", ["Ad Performance Metrics Dashboard", "Installs Data Exploration", "Revenue Data Exploration", "Ad Spend Installs Data Exploration"],
                               icons=["info-circle", "bar-chart", "graph-up", "database"], menu_icon="house", default_index=0)

    if selected == "Ad Performance Metrics Dashboard":
        ad_performance_metrics_dashboard()
    elif selected == "Installs Data Exploration":
        installs_data_exploration()
    elif selected == "Revenue Data Exploration":
        revenue_data_exploration()
    elif selected == "Ad Spend Installs Data Exploration":
        ad_spend_installs_exploration()

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:17:19 2023

@author: SemanurSancar
"""

import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static


from functions import monthly_wind_generation

# Set page configuration
st.set_page_config(layout="wide")

# Main function to display the Streamlit app
def main():
    # CSS style to center-align the title
    st.markdown("""
    <style>
    .title {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("<h1 class='title'>Coordinate Based Monthly Wind Generation</h1>", unsafe_allow_html=True)

    # Input fields for latitude, longitude, and peak power
    lat = st.number_input('Latitude:', min_value=0.0, max_value=90.0, value=37.019148, step=0.00000001, format="%.8f")
    lon = st.number_input('Longitude:', min_value=0.0, max_value=180.0, value=36.116237, step=0.00000001, format="%.8f")
    height = st.number_input('Height [m]:', min_value=10, value=80, step=1, format="%i")
    swept_area = st.number_input('Swept Area [m^2]:', min_value=10.0, value=300.0, step=1.0)

    # Button to get average generation
    if st.button('Get Average Generation'):
        try:
            # Call the function to fill empty coordinates
            table, user_note = monthly_wind_generation(lat, lon, height, swept_area)

            # Custom CSS to center-align table headers
            custom_css = """
            <style>
            th {
                text-align: center;
            }
            table {
                border-collapse: separate;
                border-spacing: 0;
                border-radius: 10px;
                overflow: hidden;
            }
            td, th {
                border: 1px solid #dddddd;
                padding: 8px;
            }
            </style>
            """
            st.write(custom_css, unsafe_allow_html=True)

            # Split the screen into two columns for the table and chart
            col1, col2 = st.columns(2)

            # Render the table using HTML and CSS in the first column
            with col1:
                st.subheader('Wind Generation Data')
                st.write(table.to_html(index=False, escape=False), unsafe_allow_html=True)
                st.write(user_note)

                # Render the map below the table and chart
                st.subheader('Wind Generation Location')
                m = folium.Map(location=[lat, lon], zoom_start=5, width='95%')
                folium.Marker([lat, lon]).add_to(m)
                folium_static(m)

            # Create the line chart using Streamlit's st.line_chart function in the second column
            with col2:
                st.subheader('Wind Generation Chart')
                fig = go.Figure()

                # Add bar chart for average generation
                fig.add_trace(
                    go.Bar(x=table['Months'], y=table[f'E{height}m [kWh]'], name='Average Generation [kWh]'),
                )

                # # Add scatter plot for max. generation capacity
                # fig.add_trace(
                #     go.Scatter(x=table['Months'], y=table['Max. Generation Capacity [kWh]'], name='Max. Generation Capacity [kWh]', mode='markers', marker=dict(color='red')),
                # )

                y_max = max(table[f'E{height}m [kWh]'])  # Find the maximum value in the table
                y_axis_margin = y_max * 0.1  # Add a 10% margin to the y-axis

                fig.update_layout(
                    xaxis_title='Months',
                    yaxis=dict(title='Wind Generation [kWh]', range=[0, y_max + y_axis_margin]),
                    legend=dict(orientation='h', x=0, y=-0.2),  # Move legend to the bottom with horizontal orientation
                    height=570,
                    xaxis=dict(tickmode='linear', dtick=1)
                )

                st.plotly_chart(fig, use_container_width=True)
                ###########
                ###########
                ###########
                # st.subheader('Cluster Base Maximum Rate')
                # fig = go.Figure()

                # # Add bar chart for average generation
                # fig.add_trace(
                #     go.Scatter(x=table['Months'], y=table['Cluster Base Maximum Rate'], name='Cluster Base Maximum Rate', mode='markers', marker=dict(size=12, color='lime', symbol='star'), line=dict(width=3, color='lightgray')),
                # )

                # y_max = max(table['Cluster Base Maximum Rate'])  # Find the maximum value in the table
                # y_min = min(table['Cluster Base Maximum Rate'])  # Find the maximum value in the table
                # y_axis_up_margin = y_max * 0.1  # Add a 10% margin to the y-axis
                # y_axis_down_margin = y_min * 0.1 

                # fig.update_layout(
                #     xaxis_title='Months',
                #     yaxis=dict(title='Rate [%]', range=[y_min - y_axis_down_margin, y_max + y_axis_up_margin]),
                #     legend=dict(orientation='h', x=0, y=-0.2),  # Move legend to the bottom with horizontal orientation
                #     height=570,
                #     xaxis=dict(tickmode='linear', dtick=1)
                # )

                # st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Footer
    st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f0f0;
        color: #333;
        text-align: center;
        padding: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="footer">Made with 💚 by FOTON     |     Version: 0.0.1</div>', unsafe_allow_html=True)

# Call the main function to run the Streamlit app
if __name__ == '__main__':
    main()
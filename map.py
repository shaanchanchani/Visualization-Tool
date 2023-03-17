import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium
import branca.colormap as cmp
import plotly.express as px
import json
import os

def getSenegalBounds():
    with open('senegal.geojson', 'r') as f:
        senegal_geojson = json.load(f)

    # Create a FeatureGroup from the Senegal GeoJSON data
    senegal_layer = folium.FeatureGroup(name='Senegal')

    # Add the Senegal boundary as a GeoJSON layer to the FeatureGroup
    folium.GeoJson(
        senegal_geojson,
        name='Senegal',
        style_function=lambda x: {'fillColor': 'white', 'color': 'black', 'weight': 2},
        tooltip='Senegal'
    ).add_to(senegal_layer)

    # Check if the FeatureGroup is empty before getting the bounds
    if len(senegal_layer._children) > 0:
        # Calculate the bounds of the Senegal boundary
        return senegal_layer.get_bounds()
    else:
        return None

#Returns Pandas dataframe containing JSON data 
def loadJSONData():
    json_data = []
    locs = ['Assirik','Fongoli']

    for loc in locs:
        path_to_json = f"./site_info/Additional_summary_2/{loc}/"

        for filename in os.listdir(path_to_json):
            if filename.endswith('.json'):
                with open(os.path.join(path_to_json, filename), 'r') as f:
                    json_data.append(json.load(f))

    df = pd.DataFrame(json_data)

    return df 

def options(df):
    senegal_bounds = getSenegalBounds()
    fongoli_parameters = {'location' : [13.02304, -12.67670],
    'zoom_start' : 13,
        'scrollWheelZoom' : False, 
        'tiles' : 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'attr' : 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        'max_bounds_viscosity' : 1.0,
        'max_bounds' : True,
        'max_zoom' : 20,
        'min_zoom' : 10,
        'bounds' : senegal_bounds}

    if st.sidebar.button('Zoom Fongoli', on_click = save_session):
        display_map(df, fongoli_parameters)


def display_map(df, map_parameters):

    # map = folium.Map(
    #     location = [12.90427, -12.39464],
    #     zoom_start = 10,
    #     scrollWheelZoom = False, 
    #     tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    #     attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    #     max_bounds_viscosity=1.0,
    #     max_bounds = True,
    #     max_zoom = 20,
    #     min_zoom=10,
    #     bounds = senegal_bounds
    #     )

    map = folium.Map(**map_parameters)
        
    for index, row in df.iterrows():
        folium.Marker(location = row['latlon']).add_to(map)    
    
    #type = str(st.sidebar.selectbox('Select a crop to display on US heatmap', options= ['swag', 'no swag']))

    st_map = st_folium(map, width = 1000, height = 550)



def main():
    APP_TITLE = 'Senegal Camera Trap Data'
    st.set_page_config(APP_TITLE)
    #hide Streamlit menu and ugly watermark
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    #Reduce padding above header from 6rem to 1rem
    st.write('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

    st.title(APP_TITLE)

    df_cams = loadJSONData()
    options(df_cams)    

if __name__ == "__main__":
    main()
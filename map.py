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

def handle_click(new_type):
    st.session_state.type = new_type


def options(df):
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


def handle_cam_toggle_click():
    del st.session_state['cams']
    if st.session_state.choice:
        st.session_state.show_cams = st.session_state.choice

def handle_map_view_click():
    map_view_types = {'Standard' : ['https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'],
                        'Topographical' : ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'],
                        'Satellite' : ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community']
                        }
    if st.session_state.map_choice:
        st.session_state.tile = map_view_types[st.session_state.map_choice]


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
    senegal_bounds = getSenegalBounds()
    
    if 'show_cams' not in st.session_state: st.session_state['show_cams'] = 'N'

    if 'location' not in st.session_state: st.session_state['location'] = [12.90427, -12.39464]
    
    if 'zoom' not in st.session_state: st.session_state['zoom'] = 10 

    if 'cams' not in st.session_state: st.session_state['cams'] = []

    #Format- Map_Type : [Tile, Attribution]
    if 'tile' not in st.session_state: st.session_state['tile'] = []

    toggle_cams = st.sidebar.radio("Show?", ['N','Y'], on_change=handle_cam_toggle_click, key='choice')

    toggle_map_view = st.sidebar.radio("Map View:", ['Standard','Topographical','Satellite'], on_change = handle_map_view_click, key = 'map_choice')

    if st.session_state['show_cams'] == 'N':
        cam_list = [[39.86752,126.93875]]
    elif st.session_state['show_cams'] == 'Y':
        cam_list = []
        for index, row in df_cams.iterrows():
            cam_list.append(row['latlon'])
    
    st.session_state.cams = cam_list

    map = folium.Map(location = [12.90427, -12.39464], tiles = st.session_state.tile[0], attr = st.session_state.tile[1], zoom_start = 10, max_zoom = 20, min_zoom = 10, max_bounds_viscosity = 1.0, max_bounds = True, bounds = senegal_bounds)

    fg = folium.FeatureGroup(name = "Cams")

    for cam in st.session_state["cams"]:
        fg.add_child(folium.Marker(cam))

    st_map = st_folium(
        map,
        center = st.session_state['location'],
        zoom = st.session_state['zoom'],
        feature_group_to_add = fg,
        width = 1000, 
        height = 550
        )


if __name__ == "__main__":
    main()
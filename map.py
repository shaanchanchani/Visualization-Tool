import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium
import branca.colormap as cmp
import plotly.express as px
import json
import os
import re
import glob2

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

def loadSampleImages():
    arr = []


def loadJSONData():
    json_data = []
    locs = ['Assirik','Fongoli']
    filenames = []

    for loc in locs:
        path_to_json = f"./site_info/Additional_summary_2/{loc}/"

        for filename in os.listdir(path_to_json):
            if filename.endswith('.json'):
                with open(os.path.join(path_to_json, filename), 'r') as f:
                    json_data.append(json.load(f))
                    filenames.append(str(filename).split('.')[0])

    df = pd.DataFrame(json_data)
    df['filename'] = filenames

    return df 

def calcFongoliCenter():
    json_data = []
    path_to_json = "./site_info/Additional_summary_2/Fongoli/"

    for filename in os.listdir(path_to_json):
        if filename.endswith('.json'):
            with open(os.path.join(path_to_json, filename), 'r') as f:
                json_data.append(json.load(f))
    
    df = pd.DataFrame(json_data)
    count = 0
    lat_total = 0
    lon_total = 0 

    for index, row in df.iterrows():
        count += 1
        lat_total += list(row['latlon'])[0]
        lon_total += list(row['latlon'])[1]

    return ([lat_total/count,(lon_total/count)+0.0505])

def calcAssirikCenter():
    json_data = []
    path_to_json = "./site_info/Additional_summary_2/Assirik/"

    for filename in os.listdir(path_to_json):
        if filename.endswith('.json'):
            with open(os.path.join(path_to_json, filename), 'r') as f:
                json_data.append(json.load(f))
    
    df = pd.DataFrame(json_data)
    count = 0
    lat_total = 0
    lon_total = 0 

    for index, row in df.iterrows():
        count += 1
        lat_total += list(row['latlon'])[0]
        lon_total += list(row['latlon'])[1]
        
    return ([lat_total/count,lon_total/count])

def handle_zoom_click():
    assirik_center = calcAssirikCenter()
    fongoli_center = calcFongoliCenter()

    if st.session_state.ass_button:
        st.session_state.location = assirik_center
        st.session_state.zoom = 13
    elif st.session_state.fon_button:
        st.session_state.location = fongoli_center
        st.session_state.zoom = 13

def handle_cam_toggle_click():
    #del st.session_state['cams']
    if st.session_state.choice:
        st.session_state.show_cams = 'Y'
    else: 
        st.session_state.show_cams = 'N'

def handle_map_view_click():
    map_view_types = {#'Standard' : ['https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'],
                        'Standard' : ['openstreetmap', None],
                        'Topographical' : ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'],
                        'Satellite' : ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community']
                        }
    if st.session_state.map_choice:
        st.session_state.tile = map_view_types[st.session_state.map_choice]


def main():
    APP_TITLE = 'Project HUNTRESS Visualization Tool'
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
    st.write("Data courtesy of Direction des Parcs Nationaux, Direction des Forêts et Chasses, Recherche Chimpanzé Assirik, Fongoli Savanna Chimpanzee Project, Papa Ibnou Ndiaye, and Jill Pruetz.")
    df_cams = loadJSONData()
    senegal_bounds = getSenegalBounds()
    
    if 'show_cams' not in st.session_state: st.session_state['show_cams'] = 'N'

    if 'location' not in st.session_state: st.session_state['location'] = [12.90427, -12.39464]
    
    if 'zoom' not in st.session_state: st.session_state['zoom'] = 8

    if 'cams' not in st.session_state: st.session_state['cams'] = []

    #Format- Map_Type : [Tile, Attribution]
    if 'tile' not in st.session_state: st.session_state['tile'] = ['openstreetmap',None]#['https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC']

    toggle_map_view = st.sidebar.radio("Map View:", ['Standard','Topographical','Satellite'], on_change = handle_map_view_click, key = 'map_choice')

    col1, col2 = st.sidebar.columns(2)
    st.sidebar.write('Zoom to')
    with col1:
        st.sidebar.button('Assirik', on_click = handle_zoom_click, key = 'ass_button')
    with col2:
        st.sidebar.button('Fongoli', on_click = handle_zoom_click, key = 'fon_button')

    st.sidebar.checkbox("Toggle Site Markers", on_change=handle_cam_toggle_click, key='choice', value = False)

    if st.session_state['show_cams'] == 'N':
        cam_list = [([84.86752,179.93875],0)]
    elif st.session_state['show_cams'] == 'Y':
        cam_list = []
        for index, row in df_cams.iterrows():
            cam_list.append((row['latlon'],index))
    
    st.session_state.cams = cam_list

    map = folium.Map(location = [12.90427, -12.39464], tiles = st.session_state.tile[0], attr = st.session_state.tile[1], zoom_start = 5, max_zoom = 20, min_zoom=2, max_bounds_viscosity = 1.0, max_bounds = True, bounds = senegal_bounds)

    fg = folium.FeatureGroup(name = "Cams")

    for cam in st.session_state["cams"]:
        fg.add_child(folium.Marker(location = cam[0], tooltip = f"Site {cam[1]}"))

    st_map = st_folium(
        map,
        center = st.session_state['location'],
        zoom = st.session_state['zoom'],
        feature_group_to_add = fg,
        width = 1000, 
        height = 550,
        returned_objects=["last_object_clicked_tooltip"]
        )
    
    if st_map["last_object_clicked_tooltip"]:
        #st.write(st_map["last_object_clicked_tooltip"])
        site_index = re.sub(r'[a-z]', '', st_map["last_object_clicked_tooltip"].lower())
        #st.write(df_cams['filename'].iloc[int(site_index)])

        if int(site_index) < 10:
            #Assirik
            cam_region = 'Assirik'
        elif int(site_index) > 9:
            #Fongoli 
            cam_region = 'Fongoli'
        
        folder = df_cams['filename'].iloc[int(site_index)]
        triggerHours = df_cams['hours'].iloc[int(site_index)]

        triggerHours = pd.DataFrame(triggerHours)
        triggerHours.columns = ['Hour']
        fig = px.histogram(triggerHours, x = 'Hour')

        image_path = f"./site_info/Sample_images/{cam_region}/{folder}/sample.jpg"
        #plot_path = f"./site_info/Sample_images/{cam_region}/{folder}/hist.png"        
        
        st.image(image_path)
        #st.image(plot_path)
        st.plotly_chart(fig, theme = "streamlit", use_container_width = True)








 

if __name__ == "__main__":
    main()
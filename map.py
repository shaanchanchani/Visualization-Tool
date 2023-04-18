import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium
import plotly.express as px
import json
import os
import re
import glob2
from openmeteo_py import Hourly, Daily, Options, OWmanager
import datetime

#Loads GEOJSON file containing Senegal's bounds
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

#Returns zoom location for Fongoli by averaging the lat_lon of Fongoli sites
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

#Returns zoom location for Assirik by averaging the lat_lon of Assirik sites
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

# Call-back function to change zoom location session state whenever the Assirik and Fongoli buttons are pressed
def handle_zoom_click():
    if st.session_state.ass_butt:
        st.session_state.location = calcAssirikCenter()
        st.session_state.zoom = 13
    elif st.session_state.fon_butt:
        st.session_state.location = calcFongoliCenter()
        st.session_state.zoom = 13

# Call-back function to change show_bubbles session state whenever the Toggle Baboon Bubbbles checkbox is clicked
def handle_bubble_toggle_click():
    if st.session_state.bubble:
        st.session_state.show_bubbles = 'Y'
    else:
        st.session_state.show_bubbles = 'N'

# Call-back function to change show_cams session state whenever the Toggle Site Markers checkbox is clicked
def handle_cam_toggle_click():
    if st.session_state.choice:
        st.session_state.show_cams = 'Y'
    else: 
        st.session_state.show_cams = 'N'

# Call-back function to change the map tile session state whenever the map view option is switched
def handle_map_view_click():
    map_view_types = {
                        'Standard' : ['openstreetmap', None],
                        'Topographical' : ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'],
                        'Satellite' : ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community']
                    }
    if st.session_state.map_choice:
        st.session_state.tile = map_view_types[st.session_state.map_choice]


#This function uses a Python Wrapper for Open Meteo's Weather API. The wrapper allows us to receive the JSON payload as a Pandas Dataframe
def getWeatherData(latitude,longitude):
    # Create Open Meteo API manager
    hourly = Hourly()
    daily = Daily()
    options = Options(latitude, longitude)

    mgr = OWmanager(options,
                    hourly.all()
                    )
    df = mgr.get_data(output=3)
    return df

def main():
    APP_TITLE = 'Project HUNTRESS Visualization Tool'
    st.set_page_config(APP_TITLE)
    # hides Streamlit menu and ugly watermark
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
    #Function calls to load data from JSON files and load bounds of Senegal from GEOJSON files
    df_cams = loadJSONData()
    senegal_bounds = getSenegalBounds()
    
    #Initializes session state variables 
    if 'show_cams' not in st.session_state: st.session_state['show_cams'] = 'N'
    if 'show_bubbles' not in st.session_state: st.session_state['show_bubbles'] = 'N'
    if 'location' not in st.session_state: st.session_state['location'] = [12.90427, -12.39464]
    if 'zoom' not in st.session_state: st.session_state['zoom'] = 8
    if 'cams' not in st.session_state: st.session_state['cams'] = []
    if 'tile' not in st.session_state: st.session_state['tile'] = ['openstreetmap',None] #Format- Map_Type : [Tile, Attribution]

    #Sidebar Input Widgets; Argument passed to on_click and on_change is the corresponding 
    #call back function to update session state variables
    toggle_map_view = st.sidebar.radio("Map View:", ['Standard','Topographical','Satellite'], on_change = handle_map_view_click, key = 'map_choice')
    st.sidebar.write('Zoom to')
    st.sidebar.button('Assirik', on_click = handle_zoom_click, key = 'ass_butt')
    st.sidebar.button('Fongoli', on_click = handle_zoom_click, key = 'fon_butt')
    st.sidebar.checkbox("Toggle Site Markers", on_change = handle_cam_toggle_click, key='choice', value = False)
    st.sidebar.checkbox("Toggle Baboon Bubbles", on_change = handle_bubble_toggle_click, key='bubble', value = False)

    # Updates session state for cameras based on the show_cams session state
    # Session state variable for cameras is a list of tuples containing the latitude and longtitude of each site and 
    # the index position of the site in the dataframe
    if st.session_state['show_cams'] == 'N':
        cam_list = [([84.86752,179.93875],0)] 
    elif st.session_state['show_cams'] == 'Y':
        cam_list = []
        for index, row in df_cams.iterrows():
            cam_list.append((row['latlon'],index))
    st.session_state.cams = cam_list

    if st.session_state['show_bubbles'] == 'N':
        bubble_list = [([84.86752,179.93875],0,0)] 
    elif st.session_state['show_bubbles'] == 'Y':
        bubble_list = []
        for index, row in df_cams.iterrows():
            bubble_list.append((row['latlon'],index, row['baboon_count']))
    st.session_state.bubbles = bubble_list

    #Initializes a folium map 
    map = folium.Map(location = [12.90427, -12.39464], tiles = st.session_state.tile[0], attr = st.session_state.tile[1], zoom_start = 5, max_zoom = 20, min_zoom=2, max_bounds_viscosity = 1.0, max_bounds = True, bounds = senegal_bounds)

    #Creates a folium feature group of cameras based on the session state variable for cams 
    #Sets marker location to the camera's lat-lon and hover information to site index
    fg = folium.FeatureGroup(name = "Cams")
    for cam in st.session_state["cams"]:
        fg.add_child(folium.Marker(location = cam[0], tooltip = f"Site {cam[1]}"))

    #Radius of bubbles is defined in Pixels. This allows us to size them according to Baboon count and scale them according to the map's zoom level
    for bubble in st.session_state["bubbles"]:
        fg.add_child(folium.CircleMarker(location = bubble[0], popup = f"Baboon Count: {bubble[2]}", radius = float(bubble[2])*0.5, color = 'crimson', fill = True, fill_color = 'crimson'))

    #Displays folium map based on session state variables. Configured to return the last clicked object's tool tip (hover information)
    st_map = st_folium(
        map,
        center = st.session_state['location'],
        zoom = st.session_state['zoom'],
        feature_group_to_add = fg,
        width = 1000, 
        height = 550,
        returned_objects=["last_object_clicked_tooltip"]
        )
    
    # This block of code allows us to display different components when each site marker is selected.
    # Tooltip is the information displayed whenever the mouse is hovering over the map object.
    # The tooltip for the site markers is the index position of the site in the dataframe containing every site.
    # It appears as "Site: X"
    if st_map["last_object_clicked_tooltip"]:

        # Regex the tooltip string to just an integer containing the site index 
        st.subheader(st_map["last_object_clicked_tooltip"])
        site_index = re.sub(r'[a-z]', '', st_map["last_object_clicked_tooltip"].lower())

        #Hard-coded based on the dataframe. A better way to do this would've been adding a column 
        #specifiying the site region when the data was loaded in from the JSON files.
        if int(site_index) < 10:
            #Assirik
            cam_region = 'Assirik'
        elif int(site_index) > 9:
            #Fongoli 
            cam_region = 'Fongoli'
        
        #Locates the name of the camera, lat_lon of the camera, and array of all trigger hours using the index position
        #of the site in the dataframe
        folder = df_cams['filename'].iloc[int(site_index)]
        lat_lon = df_cams['latlon'].iloc[int(site_index)]

        #Calls function to make API request based on the lat_lon coordinates of the selected site marker 
        df_weather = getWeatherData(lat_lon[0], lat_lon[1])

        #Creates 4 plots from the dataframe returned by the function that makes the API request 
        temperature_fig = px.line(df_weather, x = 'time', y = 'apparent_temperature')
        precipitation_fig = px.line(df_weather, x = 'time', y = 'precipitation')
        pressure_fig = px.line(df_weather, x = 'time', y = 'pressure_msl')
        wind_speed_fig = px.line(df_weather, x = 'time', y = 'windspeed_10m')

        # Get current time rounded to the nearest hour
        now = datetime.datetime.now().replace(second=0, microsecond=0, minute=0)
        rounded_time = now + datetime.timedelta(hours=1) if now.minute >= 30 else now

        # Format rounded time as "YYYY-MM-DDTHH:00"
        formatted_time = rounded_time.strftime('%Y-%m-%dT%H:%M')

        #Index weather data frame to get current weather data
        df_weather_current = df_weather[df_weather['time'] == formatted_time]
        df_weather_current = df_weather_current[['apparent_temperature', 'precipitation', 'pressure_msl', 'windspeed_10m']]
        arr = pd.DataFrame(df_weather_current).to_numpy()
        arr.tolist()

        #Display values
        st.write("Current Forecasted Data:") 
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", str(arr[0][0]) + " °C")
        col2.metric("Precipitation", str(arr[0][1]) + " Mm" )
        col3.metric("Pressure", str(int(arr[0][2])) + " MSL")
        col4.metric("Wind Speed ", str(arr[0][3]) + " Km/h")


        #Finds a sample image of the site based on it's region and name 
        image_path = f"./site_info/Sample_images/{cam_region}/{folder}/sample.jpg"
        
        #Displays chart and image
        st.write("Sample Frame:") 
        st.image(image_path)

        #Displays plots using tabs 
        st.write("7-Day Forecast")
        temperature_tab, precipitation_tab, pressure_tab, wind_speed_tab = st.tabs(["Temperature", "Precipiation", "Barometric Pressure", "Wind Speed"])
        with temperature_tab:
            st.plotly_chart(temperature_fig, theme = "streamlit", use_container_width = True)
        with precipitation_tab:
            st.plotly_chart(precipitation_fig, theme = "streamlit", use_container_width = True)
        with pressure_tab:
            st.plotly_chart(pressure_fig, theme = "streamlit", use_container_width = True)
        with wind_speed_tab:
            st.plotly_chart(wind_speed_fig, theme = "streamlit", use_container_width = True)

if __name__ == "__main__":
    main()
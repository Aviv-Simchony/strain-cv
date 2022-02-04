from xmlrpc.client import MAXINT
from cv2 import IMREAD_ANYCOLOR
import streamlit as st
import numpy as np
from queue import Queue
from threading import Thread
from mock_jhrecv import jh_recv
import io
from PIL import Image
from time import sleep, time
import mock_instruments
import pyvisa
import altair as alt
import cv2 as cv
import pandas as pd
import consolidated_voronoi
# Interactive Streamlit elements, like these sliders, return their value.
# This gives you an extremely simple interaction model.
with st.sidebar:
    set_T   = st.slider("Camera Temperarture",100,250,185,5)
    min_cur = st.slider("Minimum current", 0.0, 0.5, 0.19, 0.01)
    max_cur = st.slider("Maximum current", 0.0, 0.5, 0.2, 0.01)
    frame_text = st.empty()
    control_temp = st.checkbox("control temperature")
    with st.expander("marker detection settings"):
        detect_edges = st.checkbox("show edge detection")
        canny_threshold = st.slider("edge detector threshold",0,255,35,1)
        marker_threshold = st.slider("marker detection threshold",0,40,20,1)
        show_circles = st.checkbox("show radius limits")
        minimum_radius = st.slider("minimum marker radius",0,50,25,1)
        maximum_radius =  st.slider("maximum marker radius",0,50,40,1)
        show_line = st.checkbox("show minimum distance")
        min_dist = st.slider("minium distance between markers",0,300,110,1)
        dp = st.slider("Accumulator resolution",1.0,3.0,1.3,0.1)
thermometer = mock_instruments.Thermometer()

heater = mock_instruments.Heater(thermometer) 

q = Queue()
t1 = Thread(target = jh_recv, args =(q, ))    
t1.start() #TODO worry! you should do clever things here when you're sober




image = st.empty()
marker_locations = st.empty()
display_video = st.checkbox("video")
show_markers = st.checkbox("show markers")
show_voronoi = st.checkbox("show voronoi")
local_strain = st.checkbox("find local strain")

chart = st.empty()
display_temp = st.checkbox("show temperature")
home_motor = st.button("Home Motor")
source = pd.DataFrame({'time': [], 'T': []})
new_rows_df = pd.DataFrame({'time': [], 'T':[] })
start_time = time()


if display_temp:
    new_rows = [time()-start_time,thermometer.read_T()]
    source.loc[len(source.index)] = new_rows
    alt_chart = alt.Chart(source).mark_line().encode(
    alt.X("time"),
        alt.Y('T',scale=alt.Scale(zero=False)
            )
    )            
    chart.altair_chart(alt_chart,use_container_width=True)
if display_video or display_temp or control_temp:
    while True:
        # Here were setting value for these two elements.
        if display_video: 
            frame = q.get()
            im = cv.split(cv.imdecode(np.asarray(frame),cv.IMREAD_ANYCOLOR))[1]

            if show_markers:
                markers = []
                rows = im.shape[0]
                circles = cv.HoughCircles(im, cv.HOUGH_GRADIENT, dp, min_dist,
                                        param1=canny_threshold, param2=marker_threshold,
                                        minRadius=minimum_radius, maxRadius=maximum_radius)
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        center = (i[0], i[1])
                        markers.append(center)
                        # circle center
                        cv.circle(im, center, 1, 255, 3)
                        # circle outline
                        radius = i[2]
                        cv.circle(im, center, radius, (255, 0, 255), 3)
                    marker_locations.table(pd.DataFrame(markers,columns=("x","y")))
                if show_voronoi:
                    con_vor = consolidated_voronoi.ConsolidatedVoronoi(markers)
                    for ridge in con_vor.ridge_vertices:
                        if -1 not in ridge:
                            cv.line(im,np.asarray(con_vor.vertices[ridge[0]]).astype(int),np.asarray(con_vor.vertices[ridge[1]]).astype(int),(0, 100, 100), 3)
                    
                
            if detect_edges:
                im = cv.Canny(im,canny_threshold/2,canny_threshold)

            if show_circles:
                cv.circle(im, (100,100), minimum_radius, (0, 100, 100), 3)
                cv.circle(im, (100,100), maximum_radius, (0, 100, 100), 3)
            if show_line:
                cv.line(im,(100,200),(100+min_dist,200), (0, 100, 100), 3)

            image.image(im)

        
        if display_temp:
            new_rows_df.loc[0] = [time()-start_time,thermometer.read_T()]
            chart.add_rows(new_rows_df)
            sleep(0.01)

        if control_temp:
            curr_temp = thermometer.read_T()
            if curr_temp <= set_T:
                heater.heat()
            else:
                heater.chill()
            if np.random.uniform(0,1) < 0.2:
                heater.heat(np.random.uniform(-5,5))

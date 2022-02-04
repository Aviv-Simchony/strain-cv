import streamlit as st
import numpy as np
from queue import Queue
from threading import Thread
from jhrecv import jh_recv
import io
from time import sleep, time
import instruments
import pyvisa
import altair as alt
import pandas as pd
import cv2 as cv
# Interactive Streamlit elements, like these sliders, return their value.
# This gives you an extremely simple interaction model.

set_T   = st.sidebar.slider("Camera Temperarture",100,250,185,5)
min_cur = st.sidebar.slider("Minimum current", 0.0, 0.5, 0.19, 0.01)
max_cur = st.sidebar.slider("Maximum current", 0.0, 0.5, 0.2, 0.01)
rm = pyvisa.ResourceManager()
thermometer = instruments.Thermometer(rm)
heater = instruments.Heater(rm) 


frame_text = st.sidebar.empty()

q = Queue()
t1 = Thread(target = jh_recv, args =(q, ))    
t1.start() #TODO worry! you should do clever things here when you're sober

display_video = st.checkbox("video")
display_temp = st.checkbox("show temperature")
control_temp = st.sidebar.checkbox("control temperature")

image = st.empty()
chart = st.empty()

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
            im = cv.imdecode(np.asarray(frame),cv.IMREAD_GRAYSCALE)
            image.image(im)
        
        if display_temp:
            new_rows_df.loc[0] = [time()-start_time,thermometer.read_T()]
            chart.add_rows(new_rows_df)
            sleep(0.01)

        if control_temp:
            curr_temp = thermometer.read_T()
            if curr_temp <= set_T:
                heater.heat(max_cur)
            else:
                heater.heat(min_cur)
st.button("Re-run")
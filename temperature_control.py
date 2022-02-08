from gui_element import GuiElement
import mock_instruments
from time import time, sleep
import altair as alt
import pandas as pd
import numpy as np
import streamlit as st
class TemperatureControl(GuiElement):
    def __init__(self):
        self.has_loop = False
        self.thermometer = mock_instruments.Thermometer()
        self.heater = mock_instruments.Heater(self.thermometer) 
    
    def __enter__(self):
        with st.sidebar:
            self.set_T   = st.slider("Camera Temperarture",100,250,185,5)
            self.min_cur = st.slider("Minimum current", 0.0, 0.5, 0.19, 0.01)
            self.max_cur = st.slider("Maximum current", 0.0, 0.5, 0.2, 0.01)
            self.control_temp = st.checkbox("control temperature")
        self.chart = st.empty()
        self.display_temp = st.checkbox("show temperature")
        source = pd.DataFrame({'time': [], 'T': []})
        self.new_rows_df = pd.DataFrame({'time': [], 'T':[] })
        self.start_time = time()


        if self.display_temp:
            self.new_rows = [time()-self.start_time,self.thermometer.read_T()]
            source.loc[len(source.index)] = self.new_rows
            self.alt_chart = alt.Chart(source).mark_line().encode(
            alt.X("time"),
                alt.Y('T',scale=alt.Scale(zero=False)
                    )
            )            
            self.chart.altair_chart(self.alt_chart,use_container_width=True)
        self.has_loop = self.display_temp or self.control_temp
        
    def loop(self):    
        if self.display_temp:
            self.new_rows_df.loc[0] = [time()-self.start_time,self.thermometer.read_T()]
            self.chart.add_rows(self.new_rows_df)

        if self.control_temp:
            curr_temp = self.thermometer.read_T()
            if curr_temp <= self.set_T:
                self.heater.heat()
            else:
                self.heater.chill()
            if np.random.uniform(0,1) < 0.2:
                self.heater.heat(np.random.uniform(-5,5))
        sleep(0.01)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("exiting temp controller, should cleverness ensue?")
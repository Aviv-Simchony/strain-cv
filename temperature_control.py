from gui_element import GuiElement
import instruments
from time import time, sleep
import altair as alt
import pandas as pd
import numpy as np
import pyvisa
import streamlit as st

class TemperatureControl(GuiElement):
    def __init__(self,mock=False):
        self.rm = pyvisa.ResourceManager()
        self.has_loop = False
        self.thermometer = instruments.Thermometer(self.rm)
        self.heater = instruments.Heater(self.rm) 
    
    def __enter__(self):
        with st.sidebar:
            self.set_T   = st.slider("Camera Temperarture",100,320,170,5)
            self.min_cur = st.slider("Minimum current(mA)", 0, 500, 0, 2)/1000.0
            self.max_cur = st.slider("Maximum current(mA)", 0, 500, 0, 2)/1000.0
            self.control_temp = st.checkbox("control temperature")
        self.chart = st.empty()
        """
        Remember to turn set heater current to 0
        """
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
                self.heater.heat(self.max_cur)
            else:
                self.heater.heat(self.min_cur)
        sleep(0.01)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("exiting temp controller, should cleverness ensue?")
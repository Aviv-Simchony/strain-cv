from gui_elements import TemperatureControl, VideoPlayer
import streamlit as st
GUIELEMENTS = [TemperatureControl(),VideoPlayer()]

have_loop = False
for element in GUIELEMENTS:
    element.preloop()
    if element.has_loop:
        have_loop = True

if have_loop :
    while True:
        for element in GUIELEMENTS:
            element.loop()
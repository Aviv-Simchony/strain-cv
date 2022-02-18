from gui_elements import TemperatureControl, VideoPlayer
import streamlit as st
from contextlib import ExitStack
GUIELEMENTS = [VideoPlayer()]
"""
Remember to turn set heater current to 0
"""
with ExitStack() as stack:
    print("canada")
    have_loop = False
    for element in GUIELEMENTS:
        stack.enter_context(element)
        if element.has_loop:
            have_loop = True

    if have_loop :
        while True:
            for element in GUIELEMENTS:
                element.loop()
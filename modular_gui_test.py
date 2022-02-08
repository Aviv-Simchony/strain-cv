from gui_elements import TemperatureControl, VideoPlayer
import streamlit as st
from contextlib import ExitStack
GUIELEMENTS = [TemperatureControl() ,VideoPlayer()]
with ExitStack() as stack:
    have_loop = False
    for element in GUIELEMENTS:
        stack.enter_context(element)
        if element.has_loop:
            have_loop = True

    if have_loop :
        while True:
            for element in GUIELEMENTS:
                element.loop()
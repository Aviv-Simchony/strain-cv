from gui_element import GuiElement
import streamlit as st
from queue import Queue
from kthread import KThread
from jhrecv import jh_recv
import cv2 as cv
import numpy as np
import pandas as pd
from time import time
from scipy.spatial import Voronoi
from instruments import Actuatuor
class VideoPlayer(GuiElement):
    def __init__(self):
        self.has_loop = False
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("should close thread")
        if self.display_video:
            self.t1.terminate()

    def __enter__(self):
        with st.sidebar:
            with st.expander("marker detection settings"):
                self.detect_edges = st.checkbox("show edge detection")
                self.canny_threshold = st.slider("edge detector threshold",0,255,35,1)
                self.marker_threshold = st.slider("marker detection threshold",0,40,18,1)
                self.show_circles = st.checkbox("show radius limits")
                self.minimum_radius = st.slider("minimum marker radius",0,50,25,1)
                self.maximum_radius =  st.slider("maximum marker radius",0,50,34,1)
                self.show_line = st.checkbox("show minimum distance")
                self.min_dist = st.slider("minium distance between markers",0,300,110,1)
                self.dp = st.slider("accumulator resolution",1.0,3.0,1.3,0.1)

            motor_position_col, motor_homed_col = st.columns([3,1])
            with motor_position_col:
                self.motor_position = st.empty()
            with motor_homed_col:
                st.subheader("Homed")
                self.has_homed = st.empty()
            
            jog_up_col,home_col,jog_down_col = st.columns(3)
            with jog_up_col:
                self.jog_up = st.button("jog up")
            with home_col:
                self.move_home = st.button("Home")
            with jog_down_col:
                self.jog_down = st.button("jog down")
            
            with st.expander("motor settings"):
                self.save_picture = st.checkbox("Save picture on jog")
                self.picture_delay = st.slider("picture save delay",0.0,2.0,0.5,0.1)
                self.jog_size = st.slider("Jog Size",0.0,0.5,0.05,0.01)
                self.max_velocity = st.slider("maxiumum velocity",0.0,0.5,0.1,0.05)
                self.accn = st.slider("acceleration",0.0,0.5,0.1,0.05)     
        
        
        self.display_video = st.checkbox("video")
        self.show_markers = st.checkbox("show markers")
        self.show_voronoi = st.checkbox("show voronoi")
        self.local_strain = st.checkbox("find local strain")
        if self.display_video:
            self.q = Queue()
            self.t1 = KThread(target = jh_recv, args =(self.q, ))    
            self.t1.start()
            self.image = st.empty()
        self.marker_locations = st.empty()
        self.has_loop = self.display_video
        self.actuator = Actuatuor(self.accn,self.max_velocity,self.jog_size,self.move_home)
        self.start_time = time()
        if self.jog_up:
            self.actuator.jog_up()
        if self.jog_down:
            self.actuator.jog_down()
    
    def loop(self):
        if self.display_video:
             
            frame = self.q.get()
            self.q.queue.clear()
            if self.jog_up and self.save_picture:
                if time() - self.start_time > self.picture_delay:
                    with open(str(round(self.actuator.get_position(),3))+"mm.jpeg","wb") as filer:
                        filer.write(frame)
                    self.save_picture = False
            self.motor_position.metric("motor position",round(self.actuator.get_position(),3))
            #im = cv.split(cv.imdecode(np.asarray(memoryview(frame)),cv.IMREAD_ANYCOLOR))[1]
            im = cv.cvtColor(cv.imdecode(np.asarray(memoryview(frame)),cv.IMREAD_ANYCOLOR),cv.COLOR_BGR2RGB)
            #im = cv.imdecode(np.asarray(memoryview(frame)),cv.IMREAD_GRAYSCALE)
            if self.show_markers:
                im = cv.split(cv.imdecode(np.asarray(memoryview(frame)),cv.IMREAD_ANYCOLOR))[1]
                self.add_markers(im)
            if self.detect_edges:
                im = cv.Canny(im,self.canny_threshold/2,self.canny_threshold)

            if self.show_circles:
                cv.circle(im, (100,100), self.minimum_radius, (0, 100, 100), 3)
                cv.circle(im, (100,100), self.maximum_radius, (0, 100, 100), 3)
            if self.show_line:
                cv.line(im,(100,200),(100+self.min_dist,200), (0, 100, 100), 3)
            
            if self.actuator.is_homed():
                self.has_homed.image("green-led-on.png")
            else:
                self.has_homed.image("green-led-off.png")

            
            self.image.image(im)
    
    def add_voronoi(self,im,markers):
        vor = Voronoi(markers)
        for ridge in vor.ridge_vertices:
            if -1 not in ridge:
                cv.line(im,np.asarray(vor.vertices[ridge[0]]).astype(int),np.asarray(vor.vertices[ridge[1]]).astype(int),(0, 100, 100), 3)
    
    def add_markers(self,im):
        markers = []
        circles = cv.HoughCircles(im, cv.HOUGH_GRADIENT, self.dp, self.min_dist,
                                param1=self.canny_threshold, param2=self.marker_threshold,
                                minRadius=self.minimum_radius, maxRadius=self.maximum_radius)
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
            self.marker_locations.table(pd.DataFrame(markers,columns=("x","y")))
        if self.show_voronoi:
            self.add_voronoi(im,markers)
    

    def get_local_strain(polygon):
        polygon = list(set(polygon))
        if len(polygon != 4):
            return -1 # TODO somethink
        
        
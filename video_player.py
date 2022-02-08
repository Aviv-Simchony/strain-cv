from gui_element import GuiElement
import streamlit as st
from queue import Queue
from threading import Thread
from mock_jhrecv import jh_recv
import cv2 as cv
import numpy as np
import pandas as pd
from scipy.spatial import Voronoi

class VideoPlayer(GuiElement):
    def __init__(self):
        self.has_loop = False

    def preloop(self):
        with st.sidebar:
            with st.expander("marker detection settings"):
                self.image_threshold = st.slider("Image threshold",0,255,69,1)
                self.threshold_image = st.checkbox("Threshold image")
                self.detect_edges = st.checkbox("show edge detection")
                self.canny_threshold = st.slider("edge detector threshold",0,255,35,1)
                self.marker_threshold = st.slider("marker detection threshold",0,40,18,1)
                self.show_circles = st.checkbox("show radius limits")
                self.minimum_radius = st.slider("minimum marker radius",0,50,25,1)
                self.maximum_radius =  st.slider("maximum marker radius",0,50,34,1)
                self.show_line = st.checkbox("show minimum distance")
                self.min_dist = st.slider("minium distance between markers",0,300,110,1)
                self.dp = st.slider("Accumulator resolution",1.0,3.0,1.3,0.1)

        self.q = Queue()
        self.t1 = Thread(target = jh_recv, args =(self.q, ))    
        self.t1.start() #TODO worry! you should do clever things here when you're sober
        self.image = st.empty()
        self.marker_locations = st.empty()
        self.display_video = st.checkbox("video")
        self.show_markers = st.checkbox("show markers")
        self.show_voronoi = st.checkbox("show voronoi")
        self.local_strain = st.checkbox("find local strain")
        self.has_loop = self.display_video
    
    def loop(self):
        if self.display_video: 
            frame = self.q.get()
            self.q.queue.clear()
            im = cv.split(cv.imdecode(np.asarray(frame),cv.IMREAD_ANYCOLOR))[1]
            if self.threshold_image:
                  ret,im = cv.threshold(im,self.image_threshold,255,cv.THRESH_BINARY)

            if self.show_markers:
                
                self.add_markers(im)
            if self.detect_edges:
                im = cv.Canny(im,self.canny_threshold/2,self.canny_threshold)
              
            if self.show_circles:
                cv.circle(im, (100,100), self.minimum_radius, (0, 100, 100), 3)
                cv.circle(im, (100,100), self.maximum_radius, (0, 100, 100), 3)
            if self.show_line:
                cv.line(im,(100,200),(100+self.min_dist,200), (0, 100, 100), 3)

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
                cv.circle(im, center, 1, 0, 3)
                # circle outline
                radius = i[2]
                #cv.circle(im, center, radius, (255, 0, 255), 3)

            for marker in markers:
                marker_region = im[(marker[0]-self.maximum_radius):(marker[0]+self.maximum_radius)][(marker[1]-self.maximum_radius):(marker[1]+self.maximum_radius)]
                

            self.marker_locations.table(pd.DataFrame(markers,columns=("x","y")))
        if self.show_voronoi:
            self.add_voronoi(im,markers)
    

    def get_local_strain(polygon):
        polygon = list(set(polygon))
        if len(polygon != 4):
            return -1 # TODO somethink
        
        
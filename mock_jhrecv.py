from queue import Queue
import io
from PIL import Image
import numpy as np
import time
from matplotlib import cm
import cv2 as cv


def jh_recv(out_q):
    strain_counter = 0
    while True:
        im = Image.open("C:\\Users\\Aviv\\Desktop\\aiohttp_mjpeg-master\\yonghun_cropped.jpg") 
        stretched_image_np = np.asarray(im)
        stretched_image_np = cv.resize(stretched_image_np,cv.split(stretched_image_np)[1].shape+np.asarray((int(strain_counter),0)))
        stretched_image = Image.fromarray(stretched_image_np)
        xio2 = io.BytesIO()
        stretched_image.save(xio2,format="jpeg")
        time.sleep(1.0/25)
        out_q.put(xio2.getbuffer())
        strain_counter += 1
        



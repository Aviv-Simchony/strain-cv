from queue import Queue
import io
from PIL import Image
import numpy as np
import time
from matplotlib import cm
import cv2 as cv


def noisy(image):
    row,col,ch= image.shape
    mean = 0
    var = 10
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(row,col,ch))
    gauss = gauss.reshape(row,col,ch)
    noisy = image + gauss
    noisy = noisy/np.max(noisy)
    return noisy


def jh_recv(out_q):
    strain_counter = 0
    while True:
        im = Image.open("C:\\Users\\Aviv\\Desktop\\aiohttp_mjpeg-master\\yonghun_cropped.jpg") 
        noisy_image_np = np.asarray(im)
        noisy_image_np = cv.resize(noisy_image_np,cv.split(noisy_image_np)[1].shape+np.asarray((int(strain_counter),0)))
        noisy_image = Image.fromarray(noisy_image_np)
        xio2 = io.BytesIO()
        noisy_image.save(xio2,format="jpeg")
        time.sleep(1.0/25)
        out_q.put(xio2.getbuffer())
        strain_counter += 0.1
        



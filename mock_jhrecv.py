from queue import Queue
import io
from PIL import Image
import numpy as np
import time
from matplotlib import cm


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
        if strain_counter > 100:
            im = Image.open("C:\\Users\\Aviv\\Desktop\\aiohttp_mjpeg-master\\yonghun_strained.jpg") 
        else:
            im = Image.open("C:\\Users\\Aviv\\Desktop\\aiohttp_mjpeg-master\\yonghun_strained.jpg") 
        noisy_image_np = np.asarray(im)
        noisy_image = Image.fromarray(noisy_image_np)
        xio2 = io.BytesIO()
        im.save(xio2,format="jpeg")
        time.sleep(1.0/25)
        out_q.put(xio2.getbuffer())
        strain_counter += 1
        



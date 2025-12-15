from Ld06WebSocket.LD06 import LD06_WebSocket
from Ld06Vizualizer.Vizualizer import LD06_Vizualizer
import matplotlib.pyplot as plt
import cv2, math
import numpy as np

maxRange = 2
width = 700
height = 700

ldWS = LD06_WebSocket()
ldViz = LD06_Vizualizer(maxRange, width, height, ldWS)



while True:
    image, points = ldViz.getVizualizerImage()
    image2 = ldViz.getMap(points, 3)
    fig = None
    if len(points) == 360:
        arrayAngles = np.arange(1, 361)
        arrayValues = np.array([point.dist for point in ldWS.points])
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(arrayAngles, arrayValues, color='green', marker='o', markersize=3, linewidth=1, label='Исходные')
        ax.set_xlabel('Углы')
        ax.set_ylabel('Дистанции')
        ax.set_ylim(0, 1)
        ax.set_xlim(0, 360)
        ax.set_title('Лидар')
        ax.grid(True)
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(fig.canvas.renderer.buffer_rgba(), dtype=np.uint8)
        img = img.reshape(h, w, 4) 
        cv2.imshow("graph", img)


    cv2.imshow("image", image)
    cv2.imshow("image2", image2)

    cv2.waitKey(1)
    if fig:
        plt.close(fig)
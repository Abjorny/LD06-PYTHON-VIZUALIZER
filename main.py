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

def anglePoint(one, two):
    value = (one[0] * two[0] + one[1] * two[1])/ ((one[0] ** 2 + one[1] ** 2)**0.5 * (two[0] ** 2 + two[1] ** 2)**0.5)
    angle =  math.degrees(math.acos(value))
    return angle

while True:
    lines = []

    image, points = ldViz.getVizualizerImage()
    image2 = ldViz.getMap(points, 1)
    imge3 = ldViz.formatSolidImage()
    for i in range(len(points) - 1):
        startPoint = points[i]
        line = [startPoint]
        indexLine = 0
        while 1:
            i += 1
            indexLine += 1
            if i == 360:
                break
            angle = anglePoint(line[indexLine - 1], points[i])
            raz_x = abs(line[indexLine - 1][0] - points[i][0])
            raz_y = abs(line[indexLine - 1][1] - points[i][1])
            if angle < 3 and raz_x < 5 and raz_y < 5:
                line.append(points[i])
            else:
                break
        if len(line) > 2:
            lines.append(line)
    for line in lines:
        cv2.line(imge3, line[0], line[-1], (255, 0, 0), 1)
    # fig = None
    # if len(points) == 360:
    #     arrayAngles = np.arange(1, 361)
    #     arrayValues = np.array([point.dist for point in ldWS.points])
    #     fig, ax = plt.subplots(figsize=(10,4))
    #     ax.plot(arrayAngles, arrayValues, color='green', marker='o', markersize=3, linewidth=1, label='Исходные')
    #     ax.set_xlabel('Углы')
    #     ax.set_ylabel('Дистанции')
    #     ax.set_ylim(0, 1)
    #     ax.set_xlim(0, 360)
    #     ax.set_title('Лидар')
    #     ax.grid(True)
    #     fig.canvas.draw()
    #     w, h = fig.canvas.get_width_height()
    #     img = np.frombuffer(fig.canvas.renderer.buffer_rgba(), dtype=np.uint8)
    #     img = img.reshape(h, w, 4) 
    #     cv2.imshow("graph", img)


    cv2.imshow("image", image)
    cv2.imshow("image2", image2)
    cv2.imshow("image3", imge3)
    cv2.waitKey(1)
    # if fig:
    #     plt.close(fig)
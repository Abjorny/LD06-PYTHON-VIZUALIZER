import cv2, math
import numpy as np
from Ld06WebSocket.LD06 import LD06_WebSocket

class LD06_Vizualizer:
    def __init__(self, maxRange, width, height, ldWS: LD06_WebSocket):
        self.maxRange = maxRange
        self.width = width
        self.height = height
        self.ldWS = ldWS

    def formatSolidImage(self):
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        return image 
    
    def __formatStartImage(self):
        image = self.formatSolidImage()
        cx, cy = self.width // 2, self.height // 2
        color = (255, 255, 0)
        cv2.circle(image, (cx, cy), 10, color, 3)
        cv2.circle(image, (cx, cy), cx, color, 3)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.7
        cv2.line(image, (0, cy), (self.width, cy), color, 3)
        cv2.line(image, (cx, 0), (cx, self.height), color, 3)

        cv2.putText(image, "90", (cx + 10, 30), font, fontScale, color, 2)
        cv2.putText(image, "0", ( 10, cy-10), font, fontScale, color, 2)
        cv2.putText(image, "180", (self.width - 50, cy+30), font, fontScale, color, 2)
        cv2.putText(image, "270", (cx - 50, self.height - 10), font, fontScale, color, 2)

        return image

    def getVizualizerImage(self):
        pointsData = []
        image = self.__formatStartImage()
        cx, cy = self.width // 2, self.height // 2
        maxRadius = self.width // 2 - 10
        scale = maxRadius / self.maxRange

        for point in self.ldWS.points:
            distVal = point.dist
            if distVal > self.maxRange:
                distVal = self.maxRange
            
            rad = (point.angle + 90) * math.pi / 180
            dist = distVal * scale

            x = cx + int(dist * math.cos(rad))
            y = cy + int(dist * math.sin(rad))

            cv2.circle(image, (x, y), 2, (0, 0, 255), -1)
            pointsData.append([x, y])
        
        return image, pointsData, scale

    def getMap(self, points, scale = 1):
        image = self.formatSolidImage()

        contour = []
        pv = []
        cx = self.width // 2
        cy = self.height // 2

        for point in points:
            dx = point[0] - cx
            dy = point[1] - cy

            dx *= scale
            dy *= scale

            contour.append([
                int(dx + cx),
                int(dy + cy)
            ])

        
        if len(contour) > 0:
            pv = [np.array(contour, dtype=np.int32)]


        cv2.circle(image, (cx, cy), 2, (255, 255, 255), 3)

        if len(pv) > 0 :
            cv2.fillPoly(image, pv, (255, 255, 255))
        
        min_white = np.array([0, 0, 150])
        max_white = np.array([180, 255, 255])
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, min_white, max_white)

        counturs, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        x, y, w, h = 0, 0, 0, 0 
        for countur in counturs:
            area = cv2.contourArea(countur)
            x1,y1,w1,h1 = cv2.boundingRect(countur)
            if w1 * h1 > w * h:
                x,y,w,h = x1,y1,w1,h1
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)
        return image 

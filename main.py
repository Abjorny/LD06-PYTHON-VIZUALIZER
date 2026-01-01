from Ld06WebSocket.LD06 import LD06_WebSocket
from Ld06Vizualizer.Vizualizer import LD06_Vizualizer
import cv2, math
import numpy as np
from utlis import Line, LineMath

maxRange = 2
width = 700
height = 700

pcenter = (width // 2, height // 2)

ldWS = LD06_WebSocket()
ldViz = LD06_Vizualizer(maxRange, width, height, ldWS)

while True:
    lines: list[Line] = []
    perpendLines: list[tuple[Line, Line]] = []
    filterLines: list[tuple[Line, Line]] = []
    
    image, points, scale = ldViz.getVizualizerImage()
    image2, w, h = ldViz.getMap(points, 1)

    i = 0

    while 1:
        if len(points) - 1 <= i:
            break
        startPoint = points[i]
        line = [startPoint]
        indexLine = 0
        while 1:
            i += 1
            indexLine += 1
            if i == 360:
                break
            
            raz_x = abs(line[indexLine - 1][0] - points[i][0])
            raz_y = abs(line[indexLine - 1][1] - points[i][1])
            if len(line) >= 2:
                d1 = line[1][1] - line[0][1]
                d2 = line[1][0] - line[0][0]
                if d2:
                    startk = d1 / d2
                else:
                    startk = 0
                
                if raz_x:
                    newk = raz_y / raz_x
                else:
                    newk = 0
                if abs( newk - startk ) < 5:
                    if  raz_x < 7 and raz_y < 7:
                        line.append(points[i])
                    else:
                        break
                else:
                    break
            else:
                if  raz_x <  7 and raz_y < 7:
                    line.append(points[i])
                else:
                    break
        if len(line) > 15:
            lines.append(Line(line))
    

    for line1 in lines:
        for line2 in lines:
            if line2 != line1 and line2 not in perpendLines:
                if LineMath.is_perpindicular(line1, line2):
                    perpendLines.append((line1, line2))
    
    filterLines = sorted(perpendLines, key = lambda paraline: paraline[0].length + paraline[1].length)
    if filterLines:
        lineOneS, lineTwoS = filterLines[-1]
        if not LineMath.get_horizontal_line(lineOneS):
            lineOneS, lineTwoS = lineTwoS, lineOneS

        lineOneS.draw(image2, thick=2)
        lineTwoS.draw(image2, thick=2)


        dot = LineMath.get_dot_peres(lineOneS, lineTwoS)
        first = Line([dot, lineOneS.p1])
        two  = Line([dot, lineTwoS.p1])
        if w < h:
            first = LineMath.build_line(dot, first, scale, 1.8)
            two = LineMath.build_line(dot, two, scale, 2.4)
        first.draw(image2)
        two.draw(image2)

        # lineOne = LineMath.build_line(dot, lineOneS, scale, 1.8)
        # lineTwo = LineMath.build_line(dot, lineTwoS, sca-le, 1.8)
        
        # lineOne.draw(image2, thick=7)
        # lineTwo.draw(image2, thick=7)
        
        # lineOne = LineMath.build_line(dot, lineOneS, scale, 2.4)
        # lineTwo = LineMath.build_line(dot, lineTwoS, scale, 2.4)
        
        # lineOne.draw(image2, (0, 0, 255))
        # lineTwo.draw(image2, (0, 0, 255))
        cv2.circle(image2, np.astype(dot, int), 5, (255, 0, 0), 3)
    
    cv2.imshow("Vizualizer", image2)
    cv2.waitKey(1)
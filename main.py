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
    image2 = ldViz.getMap(points, 1)

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
                    if  raz_x < 6 and raz_y < 6:
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
    lineOne, lineTwo = filterLines[-1]
    
    lineOne.draw(image2)
    lineTwo.draw(image2)

    dot = LineMath.get_dot_peres(lineOne, lineTwo)

    newLine = LineMath.build_line(dot, lineTwo.k, scale, -1.8)
    newLine.draw(image2, (0, 255, 255), 2)

    newLine = LineMath.build_line(dot, lineOne.k, scale, -2.4)
    newLine.draw(image2, (0, 255, 255), 2)

    newLine = LineMath.build_line(newLine.p2, lineTwo.k, scale, -1.8)
    newLine.draw(image2, (0, 255, 255), 2)
    pointPtwo = LineMath.get_dot_perpend(pcenter, newLine)

    newLine = LineMath.build_line(newLine.p2, lineOne.k, scale, 2.4)
    newLine.draw(image2, (0, 255, 255), 2)

    pointPone = LineMath.get_dot_perpend(pcenter, newLine)
    
    linePeprendX = Line([pcenter, pointPtwo])
    linePeprendX.draw(image2, thick = 2)

    linePeprendY = Line([pcenter, pointPone])
    linePeprendY.draw(image2, thick = 2)

    cv2.putText(image2, f"X: {int(linePeprendX.length)}, Y: {int(linePeprendY.length)}", (30, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
    print(f"X: {int(linePeprendX.length)}, Y: {int(linePeprendY.length)}")
    cv2.circle(image2, pcenter, 3, (255, 0, 0), 3)
    cv2.circle(image2, (int(dot[0]), int(dot[1])), 3, (0, 0, 255), 5)
    cv2.imshow("Vizualizer", image2)
    cv2.waitKey(1)
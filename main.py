from Ld06WebSocket.LD06 import LD06_WebSocket
from Ld06Vizualizer.Vizualizer import LD06_Vizualizer
import cv2
import numpy as np
from utlis import Line, LineMath


class RobotView():
    def __init__(self):
        maxRange = 2
        width = 350
        height = 350

        self.pcenter = (width // 2, height // 2)

        ldWS = LD06_WebSocket(url="ws://0.0.0.0:8000/ws")
        self.ldViz = LD06_Vizualizer(maxRange, width, height, ldWS)

    def get_my_side(self):
        return "left"
    
    def view(self):
        x, y = 0, 0

        lines: list[Line] = []
        perpendLines: list[tuple[Line, Line]] = []
        filterLines: list[tuple[Line, Line]] = []
        
        _, points, scale = self.ldViz.getVizualizerImage()
        image2, w, h = self.ldViz.getMap(points, 1)

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

            dot = LineMath.get_dot_peres(lineOneS, lineTwoS)
            if np.linalg.norm(lineOneS.p1 - dot) > np.linalg.norm(lineOneS.p2 - dot):
                p2_first = lineOneS.p1
            else:
                p2_first = lineOneS.p2

            if np.linalg.norm(lineTwoS.p1 - dot) > np.linalg.norm(lineTwoS.p2 - dot):
                p2_two = lineTwoS.p1
            else:
                p2_two = lineTwoS.p2

            if w < h:
                first = LineMath.build_line(dot, p2_first, scale, 1.8)
                two = LineMath.build_line(dot, p2_two, scale, 2.4)
                three = LineMath.build_by_direction(two.p2, first.direction, scale, 1.8)
                four = Line([three.p2, first.p2])
            else:
                two = LineMath.build_line(dot, p2_first, scale, 2.4)
                first = LineMath.build_line(dot, p2_two, scale, 1.8)
                four = LineMath.build_by_direction(first.p2, two.direction, scale, 2.4)
                three = Line([four.p2, two.p2])

            itogLines: list[Line] = [first, three]

            two.draw(image2, (0, 255, 0))
            four.draw(image2)

            first, three = LineMath.get_my_line(itogLines, self.get_my_side())

            ft = LineMath.build_perpendicular(self.pcenter, first)
            rt = LineMath.build_perpendicular(self.pcenter, two)

            ft.draw(image2, (0, 255, 0))
            rt.draw(image2, (0, 255, 0))
            x, y = ft.length, rt.length

            first.draw(image2, (0, 255, 0))
            three.draw(image2)
            cv2.circle(image2, np.astype(dot, int), 5, (255, 0, 0), 3)

        cv2.circle(image2, self.pcenter, 5, (0, 0, 255), 3)
        return image2, f"X: {int(x)}, Y: {int(y)}"
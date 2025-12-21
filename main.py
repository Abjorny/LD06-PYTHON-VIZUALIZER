from Ld06WebSocket.LD06 import LD06_WebSocket
from Ld06Vizualizer.Vizualizer import LD06_Vizualizer
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

def line_k(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dx) < 1e-6:
        return None
    
    return dy / dx



def checkPerpendicular(l1, l2):
    if l1 == l2:
        return False

    v1 = np.array(l1[-1]) - np.array(l1[0])
    v2 = np.array(l2[-1]) - np.array(l2[0])

    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-3 or n2 < 1e-3:
        return False

    cos_angle = abs(np.dot(v1, v2) / (n1 * n2))

    return cos_angle < 0.05

def getPeres(l1, l2):
    x1, y1 = l1[0]
    x2, y2 = l1[-1]

    x3, y3 = l2[0]
    x4, y4 = l2[-1]

    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3

    det = dx1 * dy2 - dy1 * dx2
    if abs(det) < 1e-6:
        return None
    t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / det

    xi = x1 + t * dx1
    yi = y1 + t * dy1

    return np.array([xi, yi])

def getLenLine(line):
    x1, y1 = line[0][0], line[0][1]
    x2, y2 = line[-1][0], line[-1][1]
    d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return d

def direction_from_points(p1, p2):
    v = np.array(p2) - np.array(p1)
    n = np.linalg.norm(v)
    if n < 1e-6:
        return None
    return v / n

def build_line(p0, dir, length, scale):
    x0, y0 = p0
    dx, dy = dir
    length = length * scale 
    x1 = int(x0 + dx * length)
    y1 = int(y0 + dy * length)
    return (x0, y0), (x1, y1)


def dostroitLine(line, scale, target, reverse = False):
    if not reverse:
        x0, y0 = line[-1]
    else:
        x0, y0 = line[0]
    dx = line[-1][0] - line[0][0]
    dy = line[-1][1] - line[0][1]
    norm = math.hypot(dx, dy)

    if norm < 1e-6:
        return None

    dx /= norm
    dy /= norm

    length = target * scale - getLenLine(line)
    if not reverse:
        x1 = int(x0 + dx * length)
        y1 = int(y0 + dy * length)
    else:
        x1 = int(x0 - dx * length)
        y1 = int(y0 - dy * length)



    return (x0, y0), (x1, y1)

def line_direction(line):
    pts = np.array(line)
    mean = pts.mean(axis=0)
    _, _, vh = np.linalg.svd(pts - mean)
    return vh[0]


def project_point_to_line(p, line):
    p = np.array(p)
    a = np.array(line[0])
    d = line_direction(line)
    t = np.dot(p - a, d)
    return a + d * t
def dostroitLineCoords(line, x, y):
    proj = project_point_to_line((x, y), line)

    if np.dot(proj - line[0], line_direction(line)) > 0:
        return [line[0], proj.astype(int).tolist()]
    else:
        return [proj.astype(int).tolist(), line[-1]]

while True:
    lines = []
    filterLines = []
    uses = []
    perpendLines = []
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
            
            angle = anglePoint(line[indexLine - 1], points[i])
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
                    if  raz_x < 8 and raz_y < 8:
                        line.append(points[i])
                    else:
                        break
                else:
                    break
            else:
                if  raz_x < 7 and raz_y < 7:
                    line.append(points[i])
                else:
                    break
        if len(line) > 15:
            lines.append(line)
    
    for line in lines:
        for two in lines:
            if checkPerpendicular(line, two):
                perpendLines.append([line, two])

    filterLines = sorted(perpendLines, key = lambda paraLine: getLenLine(paraLine[0]) + getLenLine(paraLine[1]))
    x, y = getPeres(filterLines[-1][0], filterLines[-1][1])
    x, y = int(x), int(y)
    cv2.circle(image2, (x, y), 1, (0, 0, 255), 3)

    lineOne = filterLines[-1][0]
    lineTwo = filterLines[-1][1]
    
    lineOne = dostroitLineCoords(lineOne, x, y)
    lineTwo = dostroitLineCoords(lineTwo, x, y)

    cv2.line(image2, lineOne[0], lineOne[-1], (0,255,255), 5)
    cv2.line(image2, lineTwo[0], lineTwo[-1], (255,0,0), 5)
    

    try:
        one1, two1 = dostroitLine(lineOne, scale, 2.4)
        dir1 = direction_from_points(lineOne[0], lineOne[-1])
        cv2.line(image2, one1, two1, (0, 255, 0), 5)

        one2, two2 = dostroitLine(lineTwo, scale, 1.8, 1)
        cv2.line(image2, one2, two2, (255, 255, 0), 5)

        dir2 = direction_from_points(lineTwo[-1], lineTwo[0])

        p1, p2 = build_line(two1, dir2, 1.8, scale)
        p3, p4 = build_line(two2, dir1, 2.4, scale)
        cv2.line(image2, p1, p2, (0, 255, 0), 5)
        cv2.line(image2, p3, p4, (0, 255, 0), 5)
    except:
        pass


    cv2.imshow("image", image)
    cv2.imshow("image2", image2)
    cv2.waitKey(1)


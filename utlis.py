import cv2
import math
import numpy as np

class Line:
    def __init__(self, points):
        self.p1 = np.array(points[0])
        self.p2 = np.array(points[-1])
        self.cp = (self.p1 + self.p2) / 2

        self.points = points
        self.length = LineMath.get_len(self)
        self.pvector = self.p2 - self.p1
        norm = np.linalg.norm(self.pvector)
        self.direction = self.pvector / norm     

        self.length = norm    
        dx = self.p2[0] - self.p1[0]
        dy = self.p2[1] - self.p1[1]

        if dx == 0:
            self.k = np.inf
            self.vertical = True
            self.c = None 
        else:
            self.k = dy / dx
            self.vertical = False
            self.c = self.p1[1] - self.k * self.p1[0]

    def draw(self, image: cv2.Mat, color = (255, 0, 0), thick = 3):
        cv2.line(image, self.p1.astype(int), self.p2.astype(int), color, thick)

    def drawVector(self, image: cv2.Mat):
        cv2.circle(image, self.pvector, 3, (0, 0, 255), 5)
    
class LineMath:
    @staticmethod
    def get_len(line: Line):
        return np.linalg.norm(line.p2 - line.p1)
    
    @staticmethod
    def is_perpindicular(line1: Line, line2: Line):
        return abs(line1.k * line2.k + 1) < 0.5 if line1.k and line2.k else False
    
    @staticmethod
    def get_dot_peres(line1: Line, line2: Line):
        A = np.array([[line1.k, -1],
                    [line2.k, -1]])
        b = np.array([-line1.c, -line2.c])
        return np.linalg.solve(A, b)

    @staticmethod
    def build_line(p1, p2_ref, scale, dist):
        p1 = np.asarray(p1, dtype=float)
        p2_ref = np.asarray(p2_ref, dtype=float)

        direction = p2_ref - p1
        length = np.linalg.norm(direction)
        if length == 0:
            direction = np.array([1e-6, 0], dtype=float)
        else:
            direction /= length

        p2 = p1 + direction * dist * scale
        return Line([p1, p2])

    @staticmethod
    def build_by_direction(start_point, direction, scale, length):
        p1 = np.asarray(start_point, dtype=float)
        direction = np.asarray(direction, dtype=float)
        norm = np.linalg.norm(direction)

        direction = direction / norm  # нормализация
        p2 = p1 + direction * length * scale

        return Line([p1, p2])
   
    @staticmethod
    def get_pos_map(pcenter, dot):
        x, y = dot
        xcenter, ycenter = pcenter
        if x > xcenter:
            if y < ycenter:
                return 2
            else:
                return 3
        else:
            if y < ycenter:
                return 1
            else:
                return 4

    @staticmethod
    def get_dot_perpend(point, line: Line):
        ab = line.p2 - line.p1
        ap = point - line.p1
        t = np.dot(ap, ab) / np.dot(ab, ab)
        q = line.p1 + t * ab
        return q.astype(int)
    
    @staticmethod
    def get_horizontal_line(line: Line):
        praz = line.p2 - line.p1
        x, y = abs(praz[0]), abs(praz[1])
        return x > y
    
    @staticmethod
    def get_k_new_line(dot, line: Line):
        firstLine = Line([line.p1, dot])
        twoLine = Line([line.p2, dot])
        kresult = 1
        activeLine = None

        if firstLine.length > twoLine.length:
            activeLine = firstLine
        else:
            activeLine = twoLine

        if activeLine.k == line.k:
            kresult = -1
        
        return kresult
    
    @staticmethod
    def get_my_line_x(lines: list[Line], my: str):
        first = lines[0]
        two = lines[1]
        dx = abs(first.cp[0] - two.cp[0])
        dy = abs(first.cp[1] - two.cp[1])
        if dx > dy:
            if first.cp[0] > two.cp[0]:
                if my == "left":
                    return two, first
                else:
                    return first, two
            else:
                if my == "left":
                    return first, two
                else:
                    return two, first
        
        else:
            if first.cp[1] > two.cp[1]:
                if my == "left":
                    return two, first
                else:
                    return first, two
            else:
                if my == "left":
                    return first, two
                else:
                    return two, first


    @staticmethod
    def get_my_line_y(lines: list[Line], my: str):
        first = lines[0]
        two = lines[1]
        dx = abs(first.cp[0] - two.cp[0])
        dy = abs(first.cp[1] - two.cp[1])
        if dx > dy:
            if first.cp[0] > two.cp[0]:
                if my == "right":
                    return two, first
                else:
                    return first, two
            else:
                if my == "left":
                    return first, two
                else:
                    return two, first
        
        else:
            if first.cp[1] > two.cp[1]:
                if my == "left":
                    return two, first
                else:
                    return first, two
            else:
                if my == "right":
                    return first, two
                else:
                    return two, first

    @staticmethod
    def build_perpendicular(point, line: Line):
        point = np.asarray(point, dtype=float)
        ab = line.p2 - line.p1
        denom = np.dot(ab, ab)
        if denom == 0:
            return None

        ap = point - line.p1
        t = np.dot(ap, ab) / denom
        proj = line.p1 + t * ab

        return Line([point, proj])


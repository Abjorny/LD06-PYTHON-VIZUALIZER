import cv2
import math
import numpy as np

class Line:
    def __init__(self, points):
        self.p1 = np.array(points[0])
        self.p2 = np.array(points[-1])
        self.points = points
        self.length = LineMath.get_len(self)
        self.pvector = self.p2 - self.p1
        self.k = (self.p2[1] - self.p1[1]) / (self.p2[0] - self.p1[0])
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
        return abs(line1.k * line2.k + 1) < 0.5
    
    @staticmethod
    def get_dot_peres(line1: Line, line2: Line):
        A = np.array([[line1.k, -1],
                    [line2.k, -1]])
        b = np.array([-line1.c, -line2.c])
        return np.linalg.solve(A, b)

    @staticmethod
    def build_line(p1, line: Line, scale, dist):
        dx_original = line.p2[0] - line.p1[0]
        dy_original = line.p2[1] - line.p1[1]
        length_original = math.sqrt(dx_original**2 + dy_original**2)

        dx_normalized = dx_original / length_original
        dy_normalized = dy_original / length_original
        

        
        new_length = dist * scale
        x2 = p1[0] + dx_normalized * new_length
        y2 = p1[1] + dy_normalized * new_length
        
        return Line((p1, (x2, y2)))
    
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
    
    # @staticmethod
    # def build_line_by_spoint(p1, line: Line):
    #     return Line([p1, line.p1])

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
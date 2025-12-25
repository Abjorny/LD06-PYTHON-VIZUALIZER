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
        return abs(line1.k * line2.k + 1) < 1
    
    @staticmethod
    def get_dot_peres(line1: Line, line2: Line):
        A = np.array([[line1.k, -1],
                    [line2.k, -1]])
        b = np.array([-line1.c, -line2.c])
        return np.linalg.solve(A, b)

    @staticmethod
    def build_line(p1, k, dist, scale = 1):
        dx = dist * scale / math.sqrt(1 +  k**2)
        dy = k * dx
        return Line((p1, (p1[0] + dx, p1[1] + dy)))
    
    @staticmethod
    def get_dot_perpend(point, line: Line):
        ab = line.p2 - line.p1
        ap = point - line.p1
        t = np.dot(ap, ab) / np.dot(ab, ab)
        q = line.p1 + t * ab
        return q.astype(int)
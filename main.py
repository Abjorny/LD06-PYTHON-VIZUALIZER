from Ld06WebSocket.LD06 import LD06_WebSocket
from Ld06Vizualizer.Vizualizer import LD06_Vizualizer
from utlis import Line, LineMath
from itertools import combinations
import cv2, math
import numpy as np

porog_x = 180
porog_y = 150

_prev_angle_error = 0

def mecanum_pd(x, y, angle_cur, tx, ty,
               min_speed=50,
               max_speed=150,
               kp_angle=0.02,
               kd_angle=0.01):

    global _prev_angle_error

    dx = tx - x
    dy = ty - y

    distance = math.hypot(dx, dy)
    if distance < 1e-2:
        return [0, 0, 0, 0]

    angle_target = math.degrees(math.atan2(dx, dy))

    error = angle_target - angle_cur
    error = (error + 180) % 360 - 180

    d_error = error - _prev_angle_error
    _prev_angle_error = error

    w = kp_angle * error + kd_angle * d_error
    w = max(-1.0, min(1.0, w))

    speed = min(max_speed, distance)
    if speed > 0:
        speed = max(speed, min_speed)

    vx = speed * math.sin(math.radians(angle_target))
    vy = speed * math.cos(math.radians(angle_target))

    fl =  vy + vx + w * max_speed
    fr =  vy - vx - w * max_speed
    rl =  vy - vx + w * max_speed
    rr =  vy + vx - w * max_speed

    max_val = max(abs(fl), abs(fr), abs(rl), abs(rr), max_speed)

    return [
        int(fl / max_val * max_speed),
        int(fr / max_val * max_speed),
        int(rr / max_val * max_speed),
        int(rl / max_val * max_speed),
    ]

def get_angle(p_start, p_end, single=False, dif = 0):
    dx, dy = p_end - p_start
    angle = math.degrees(math.atan2(dy, dx))
    angle += dif

    if not single:
        if angle > 180:
            angle -= 360
        elif angle < -180:
            angle += 360
        return angle

    angle = angle % 360
    if angle > 180:
        angle -= 360

def line_from_point_angle(p_start, angle_deg, length):
    angle_rad = math.radians(angle_deg)
    x0, y0 = p_start

    x1 = x0 + length * math.sin(angle_rad)
    y1 = y0 - length * math.cos(angle_rad)

    return np.array([int(x1), int(y1)])


class RobotView():
    def __init__(self):
        maxRange = 2
        width = 350
        height = 350

        self.last_x = None
        self.last_y = None
        self.incorects = self.update_incorects()

        self.pcenter = (width // 2, height // 2)
        self.last_filter_lines = []

        ldWS = LD06_WebSocket(url="ws://0.0.0.0:8000/ws")
        self.ldViz = LD06_Vizualizer(maxRange, width, height, ldWS)

    def update_incorects(self):
        return 60

    def get_my_side(self):
        return "left"

    def view(self):
        x, y, angle = 0, 0, 0

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
                    if abs( newk - startk ) < 4:
                        if  raz_x < 4 and raz_y < 4:
                            line.append(points[i])
                        else:
                            break
                    else:
                        break
                else:
                    if  raz_x <  4 and raz_y < 4:
                        line.append(points[i])
                    else:
                        break
            if len(line) > 15:
                lines.append(Line(line))
                
        for line1, line2 in combinations(lines, 2):

            if not LineMath.is_perpindicular(line1, line2):
                continue

            result = []
            par_count = 0

            for base_line in (line1, line2):
                parallel_line = None
                for other in lines:
                    if base_line != other and LineMath.are_parallel(base_line, other):
                        parallel_line = other
                        par_count += 1
                        break

                result.append((base_line, parallel_line))
            if par_count > 0:
                perpendLines.append(result)
                
        filterLines = sorted(
            perpendLines,
            key=lambda item: item[0][0].length + item[1][0].length,
            reverse=True
        )


        if len(filterLines) == 0:
            filterLines = self.last_filter_lines
        else:
            self.last_filter_lines = filterLines
        if filterLines:
            first, two = filterLines[0]
            
            f_l, f_r = first
            b_l, b_r = two

            f_l.draw(image2)
            b_l.draw(image2)
            
            if f_r:
                f_r.draw(image2)
            if b_r:
                b_r.draw(image2)
            

            dot = LineMath.get_dot_peres(f_l, b_l)
            cv2.circle(image2, dot.astype(int), 5, (255, 0, 255), -1)
            
            if np.linalg.norm(f_l.p1 - dot) > np.linalg.norm(f_l.p2 - dot):
                p2_first = f_l.p1
            else:
                p2_first = f_l.p2

            if np.linalg.norm(b_l.p1 - dot) > np.linalg.norm(b_l.p2 - dot):
                p2_two = b_l.p1
            else:
                p2_two = b_l.p2



            if f_r:
                dist = LineMath.dist_between_lines(f_l, f_r)
                if dist < 160:
                    two = LineMath.build_line(dot, p2_first, scale, 2.4)
                    first = LineMath.build_line(dot, p2_two, scale, 1.8)
                    four = LineMath.build_by_direction(first.p2, two.direction, scale, 2.4)
                    three = Line([four.p2, two.p2])
                else:
                    first = LineMath.build_line(dot, p2_first, scale, 1.8)
                    two = LineMath.build_line(dot, p2_two, scale, 2.4)
                    three = LineMath.build_by_direction(two.p2, first.direction, scale, 1.8)
                    four = Line([three.p2, first.p2])
                
            elif b_r:
                dist = LineMath.dist_between_lines(b_l, b_r)
                if dist < 160:
                    two = LineMath.build_line(dot, p2_first, scale, 2.4)
                    first = LineMath.build_line(dot, p2_two, scale, 1.8)
                    four = LineMath.build_by_direction(first.p2, two.direction, scale, 2.4)
                    three = Line([four.p2, two.p2])
                else:
                    first = LineMath.build_line(dot, p2_first, scale, 1.8)
                    two = LineMath.build_line(dot, p2_two, scale, 2.4)
                    three = LineMath.build_by_direction(two.p2, first.direction, scale, 1.8)
                    four = Line([three.p2, first.p2])



            x_lines: list[Line] = [first, three]
            y_lines: list[Line] = [two, four]


            x_line_one, x_line_two = LineMath.get_my_line_x(x_lines, self.get_my_side())
            y_line_one, y_line_two = LineMath.get_my_line_y(y_lines, self.get_my_side())

            ft = LineMath.build_perpendicular(self.pcenter, x_line_one)
            rt= LineMath.build_perpendicular(self.pcenter, y_line_one)

            ft.draw(image2, (0, 255, 0))
            rt.draw(image2, (0, 255, 255))

            x, y = int(ft.length), int(rt.length)

            if ( self.last_x == None and self.last_y == None ) or self.incorects <= 0:
                self.last_x, self.last_y= x, y
                self.update_incorects()
            
            else:
                dx = abs(self.last_x - x)
                dy = abs(self.last_y - y)
                if dx <  5 and dy < 5:
                    self.last_x, self.last_y = x, y
                    self.update_incorects()

                else:
                    self.incorects = self.incorects - 1

            x_line_one.draw(image2, (0, 255, 0))
            y_line_one.draw(image2, (0, 255, 255 ))

            y_line_two.draw(image2)
            x_line_two.draw(image2)

            robot_line = Line([self.pcenter,[self.pcenter[0], 0]])
            robot_line.draw(image2, thick = 2, color = (255, 255, 0))
            angle = get_angle(self.pcenter, ft.p2)

            cv2.circle(image2, np.astype(dot, int), 5, (255, 0, 0), 3)
        cv2.circle(image2, self.pcenter, 5, (0, 0, 255), 3)
        if x and y:
            cv2.putText(image2, f"X: {int(x)}, Y: {int(y)}", (5, 15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0))
        return image2, x, y, angle
    
robot = RobotView()


while 1:
    image, x, y, angle = robot.view()
    cv2.imshow("test", image)
    cv2.waitKey(1)
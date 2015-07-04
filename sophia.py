from gcode import GCode
from math import sin, cos, radians
from shapely.geometry import LineString

F = 45
G0Z = 0.2

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def create_circle(cx, cy, r, a1, a2):
    points = []
    for a in range(a1, a2 + 1):
        x = cx + r * cos(radians(a))
        y = cy + r * sin(radians(a))
        points.append((x, y))
    return points

def create_s():
    c1 = create_circle(0, 1.03, 1, 20, 270-15)
    c2 = create_circle(0, -1.03, 1, 200, 450-15)
    s = LineString(c1 + list(reversed(c2)))
    s = s.buffer(0.4)
    g = GCode.from_geometry(s, 0, 0)
    g = g.scale_to_fit(6, 8)
    g = g.move(3, 4, 0.5, 0.5)
    g1 = g.depth(0.2, -0.3)
    g2 = g.depth(0.2, -0.6)
    g = HEADER + g1 + g2 + FOOTER
    g.save('sophia.nc')
    im = g.render(0, 0, 6, 8, 96)
    im.write_to_png('sophia.png')

def main():
    create_s()

if __name__ == '__main__':
    main()

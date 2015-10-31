from gcode import GCode
from math import *
from shapely.geometry import *

F = 120
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def circle(r, n):
    points = []
    for i in range(n + 1):
        p = float(i) / n
        a = radians(p * 360)
        x = cos(a) * r
        y = sin(a) * r
        points.append((x, y))
    return points

def hemisphere(r, n, bit_diameter):
    points = []
    bit_radius = bit_diameter / 2.0
    for i in range(n + 1 - 5):
        p = 1 - float(i) / n
        a = radians(p * 90)
        x = cos(a) * (r + bit_radius)
        y = r - sin(a) * (r + bit_radius)
        z = -y - bit_radius
        print x, y, z
        p = circle(x, 90)
        points.extend([(x, y, z) for x, y in p])

    lines = []
    lines.append('G0 Z%f' % G0Z)
    lines.append('G0 X%f Y%f' % points[0][:2])
    for point in points:
        lines.append('G1 X%f Y%f Z%f' % point)
    lines.append('G0 Z%f' % G0Z)
    g = GCode(lines)
    return g

def main():
    g = hemisphere(0.8125, 90, 0.125)
    g = g.origin()
    g = HEADER + g + FOOTER
    g.save('hemisphere.nc')
    im = g.render(0, 0, 6, 6, 96)
    im.write_to_png('hemisphere.png')

if __name__ == '__main__':
    main()

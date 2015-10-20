from gcode import GCode, pack_gcodes
from math import *
from shapely.geometry import *

F = 60
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def create_mount(w, h, d, bit, angle):
    a1 = radians(180 - angle)
    a2 = radians(180 - angle - 90)
    y = d - bit
    dy = h - y
    dx = dy * sin(a2) / sin(a1)
    x = w - d + dx
    points = [
        (0, 0),
        (w, 0),
        (w, h),
        (w - d, h),
        (x, y),
        (x, d),
        (0, d),
        (0, 0),
    ]
    return Polygon(points)

def create_mounts():
    a = 116.56505
    p = create_mount(5, 3.5, 1, 0.125, a)
    g = GCode.from_geometry(p, G0Z, -0.1)
    g1 = g.move(3, 0.25, 0.5, 0)
    g2 = g.origin().rotate(180).move(3, 5.5, 0.5, 1)
    g = g1 + g2
    g = g.depth(G0Z, -0.2) + g.depth(G0Z, -0.4) + g.depth(G0Z, -0.6)
    g = HEADER + g + FOOTER
    g.save('mounts.nc')
    im = g.render(0, 0, 6, 8, 96)
    im.write_to_png('mounts.png')

def create_support(d, bit, angle):
    a = radians(180 - angle)
    dx = cos(a) * d
    dy = sin(a) * d
    points = [
        (0, 0),
        (d, 0),
        (d + dx, dy),
        (0, 0),
    ]
    return Polygon(points).buffer(bit / 2)

def create_supports():
    n = 18
    a = 116.56505
    p = create_support(1, 0.125, a)
    g = GCode.from_geometry(p, G0Z, -0.1)
    g = g.origin()
    g = pack_gcodes([g] * n, 6, 8, 0.125)[0]
    g = g.depth(G0Z, -0.2) + g.depth(G0Z, -0.4) + g.depth(G0Z, -0.6)
    g = HEADER + g + FOOTER
    g.save('supports.nc')
    im = g.render(0, 0, 6, 8, 96)
    im.write_to_png('supports.png')

def main():
    create_mounts()
    create_supports()

if __name__ == '__main__':
    main()

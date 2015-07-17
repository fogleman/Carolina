from gcode import GCode
from math import radians, sin, cos
from shapely.affinity import translate, scale
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import cascaded_union

FR = 60
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2', 'F%s' % FR])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def cell(x, y):
    return translate(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), x, y)

def main():
    bit = 0.125
    r = 0.25
    steps = 8
    cells = [
        cell(0, 0),
        cell(1, 0),
        cell(1, 1),
        cell(2, 1),
        cell(2, 2),
    ]
    mp = cascaded_union(cells).buffer(-bit).buffer(bit)
    g = GCode()
    for p in cells:
        g += GCode.from_geometry(p, G0Z, -bit / 2)
    for step in range(steps):
        p = step / (steps - 1.0)
        a = radians(p * 90)
        x = sin(a) * r
        b = x + bit / 2 - r
        z = r - (r * r - x * x) ** 0.5
        print '%.3f, %.3f, %.3f, %.3f' % (p, x, b, z)
        g += GCode.from_geometry(mp.buffer(b), G0Z, -z)
    g += GCode.from_geometry(mp.buffer(bit / 2), G0Z, -0.4)
    g += GCode.from_geometry(mp.buffer(bit / 2), G0Z, -0.6)
    g = g.origin()
    g = HEADER + g + FOOTER
    p = 0.5
    im = g.render(-p, -p, 3 + p, 3 + p, 96*4)
    im.write_to_png('blokus.png')
    g.save('blokus.nc')

if __name__ == '__main__':
    main()

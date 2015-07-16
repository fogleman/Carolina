from gcode import GCode
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
    a = cell(0, 0)
    b = cell(1, 0)
    c = cell(1, 1)
    d = cell(1, 2)
    e = cell(0, 2)
    mp = cascaded_union([a, b, c, d, e])
    g = GCode()
    bit = 0.25
    r = 0.25
    steps = 8
    for step in range(steps):
        p = step / (steps - 1.0)
        x = p * r
        b = x + bit / 2
        z = r - (r * r - x * x) ** 0.5
        # print p, x, z
        g += GCode.from_geometry(mp.buffer(b), G0Z, -z)
    g = g.origin()
    g = HEADER + g + FOOTER
    p = 0.5
    im = g.render(-p, -p, 3 + p, 3 + p, 96)
    im.write_to_png('blokus.png')
    g.save('blokus.nc')

if __name__ == '__main__':
    main()

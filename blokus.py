from gcode import GCode, pack_gcodes
from math import radians, sin, cos
from shapely.affinity import translate, scale
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import cascaded_union

FR = 60
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2', 'F%s' % FR])
FOOTER = GCode(['G1 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

PIECES = [
    [(0, 0)],
    [(0, 0), (1, 0)],
    [(0, 0), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (1, 0), (1, 1), (0, 1)],
    [(0, 0), (1, 0), (2, 0), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
    [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1)],
    [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    [(0, 1), (1, 1), (2, 1), (1, 0), (0, 2)],
    [(0, 1), (1, 1), (2, 1), (1, 0), (1, 2)],
    [(0, 0), (1, 0), (2, 0), (3, 0), (1, 1)],
]

def cell(x, y):
    return translate(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), x, y)

def main():
    bit = 0.125
    r = 0.21875
    d = 0.09375
    steps = 16
    cells = [
        cell(0, 0),
        cell(1, 0),
        cell(1, 1),
        cell(2, 1),
        cell(3, 1),
    ]
    mp = cascaded_union(cells).buffer(-bit).buffer(bit)
    g = GCode()
    for p in cells:
        g += GCode.from_geometry(p, G0Z, -d)
    # for p in cells:
    #     g += GCode.from_geometry(p, G0Z, -bit)
    for step in range(steps):
        p = step / (steps - 1.0)
        a = radians(p * 90)
        x = sin(a) * r
        b = x + bit / 2 - r
        z = r - (r * r - x * x) ** 0.5
        print '%.3f, %.3f, %.3f, %.3f' % (p, x, b, z)
        g += GCode.from_geometry(mp.buffer(b), G0Z, -z)
    # g += GCode.from_geometry(mp.buffer(bit / 2), G0Z, -0.4)
    # g += GCode.from_geometry(mp.buffer(bit / 2), G0Z, -0.7)
    # g += GCode.from_geometry(mp.buffer(bit / 2), G0Z, -0.6, bit + 0.1, 3)
    g += GCode.from_geometry(mp.buffer(bit / 2), G0Z, -0.4, bit + 0.2, 3.5)
    g = g.scale(-1, 1)
    g = g.origin().translate(0, 0.5)
    g = HEADER + g + FOOTER
    p = 0#0.5
    im = g.render(-p, -p, 6 + p, 6 + p, 96*4)
    im.write_to_png('blokus.png')
    g.save('blokus.nc')

def create_piece(piece, mirror):
    bit_diameter = 0.125
    corner_radius = 0.1875
    groove_depth = 0.0625
    cells = [cell(x, y) for x, y in piece]
    mp = cascaded_union(cells).buffer(-corner_radius).buffer(corner_radius)
    g = GCode()
    for p in cells:
        g += GCode.from_geometry(p, G0Z, -groove_depth)
    g += GCode.from_geometry(mp.buffer(bit_diameter / 2), G0Z, -0.4, bit_diameter + 0.2, 3.5)
    if mirror:
        g = g.scale(-1, 1)
    g = g.origin()
    return g

def main():
    gs1 = [create_piece(piece, False) for piece in PIECES]
    gs2 = [create_piece(piece, True) for piece in PIECES]
    gs = gs1 + gs2
    gs = pack_gcodes(gs, 6, 8, 0.25, 174188068)
    for i, g in enumerate(gs):
        g = HEADER + g + FOOTER
        p = 0
        im = g.render(-p, -p, 6 + p, 8 + p, 96*4)
        im.write_to_png('blokus/%02d.png' % i)
        g.save('blokus/%02d.nc' % i)

if __name__ == '__main__':
    main()

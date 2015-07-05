from gcode import GCode
from letters import *
from math import sin, cos, radians
from shapely.geometry import LineString, MultiLineString, Polygon

FR = 45
G0Z = 0.2

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % FR])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def load_letters():
    scale = 0.0109
    shapes = [
        Polygon(A),
        Polygon(B),
        Polygon(C),
        Polygon(D),
        Polygon(E),
        Polygon(F),
        Polygon(G),
        Polygon(H),
        Polygon(I),
        Polygon(J),
        Polygon(K),
        Polygon(L),
        Polygon(M),
        Polygon(N),
        Polygon(O1, [O2]),
        Polygon(P),
        Polygon(Q),
        Polygon(R),
        Polygon(S),
        Polygon(T),
        Polygon(U),
        Polygon(V),
        Polygon(W),
        Polygon(X),
        Polygon(Y),
        Polygon(Z),
        Polygon(NUM_0),
        Polygon(NUM_1),
        Polygon(NUM_2),
        Polygon(NUM_3),
        Polygon(NUM_4),
        Polygon(NUM_5),
        Polygon(NUM_6),
        Polygon(NUM_7),
        Polygon(NUM_8),
        Polygon(NUM_9),
    ]
    result = []
    for shape in shapes:
        # shape = shape.buffer(1.0 / 16 * 90)
        g = GCode.from_geometry(shape, 0.2, -0.1875)
        g = g.scale(scale, scale).move(3, 4, 0.5, 0.5)
        result.append(g)
    return result

def main():
    gs = load_letters()
    for g0, letter in zip(gs, 'abcdefghijklmnopqrstuvwxyz0123456789'):
        g1 = g0.depth(0.2, -0.5)
        g2 = g0.depth(0.2, -0.9)
        p1 = HEADER + g0 + FOOTER
        p2 = HEADER + g1 + g2 + FOOTER
        p1.save('megan/%s1.nc' % letter)
        p2.save('megan/%s2.nc' % letter)
        im = g0.render(0, 0, 6, 8, 96)
        im.write_to_png('megan/%s.png' % letter)

if __name__ == '__main__':
    main()

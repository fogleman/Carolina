from gcode import GCode
from letters import *
from math import sin, cos, radians
from shapely.geometry import LineString, MultiLineString

FR = 45
G0Z = 0.2

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % FR])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def load_letters():
    scale = 0.011153752112
    shapes = [
        LineString(A),
        LineString(B),
        LineString(C),
        LineString(D),
        LineString(E),
        LineString(F),
        LineString(G),
        LineString(H),
        LineString(I),
        LineString(J),
        LineString(K),
        LineString(L),
        LineString(M),
        LineString(N),
        MultiLineString([LineString(O2), LineString(O1)]),
        LineString(P),
        LineString(Q),
        LineString(R),
        LineString(S),
        LineString(T),
        LineString(U),
        LineString(V),
        LineString(W),
        LineString(X),
        LineString(Y),
        LineString(Z),
        LineString(NUM_0),
        LineString(NUM_1),
        LineString(NUM_2),
        LineString(NUM_3),
        LineString(NUM_4),
        LineString(NUM_5),
        LineString(NUM_6),
        LineString(NUM_7),
        LineString(NUM_8),
        LineString(NUM_9),
    ]
    result = []
    for shape in shapes:
        # shape = shape.buffer(1.0 / 16 * 90)
        g = GCode.from_geometry(shape, 0.2, -0.1875)
        g = g.scale(scale, scale).move(3, 0, 0.5, 0)
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

from gcode import GCode
from shapely.wkt import loads
import foam

FR = 45
G0Z = 0.2

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % FR])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def load_letter(letter):
    if letter.isdigit():
        letter = 'NUM' + letter
    wkt = getattr(foam, letter)
    polygon = loads(wkt)
    g = GCode.from_geometry(polygon, 0.2, -0.1875)
    g = g.scale(6, 6).move(3, 4, 0.5, 0.5)
    return g

def main():
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
        g0 = load_letter(letter)
        g1 = g0.depth(0.2, -0.5)
        g2 = g0.depth(0.2, -0.9)
        p1 = HEADER + g0 + FOOTER
        p2 = HEADER + g1 + g2 + FOOTER
        p1.save('letters/%s-1.nc' % letter)
        p2.save('letters/%s-2.nc' % letter)
        im = g0.render(0, 0, 6, 8, 96)
        im.write_to_png('letters/%s.png' % letter)

if __name__ == '__main__':
    main()

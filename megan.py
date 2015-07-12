from gcode import GCode
from shapely.affinity import translate, scale
from shapely.geometry import MultiPolygon
from shapely.wkt import loads
import foam
import operator

FR = 45
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % FR])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def load_letter(letter):
    if letter.isdigit():
        letter = 'NUM' + letter
    wkt = getattr(foam, letter)
    return loads(wkt)

def load_letters(letters):
    x = 0.0
    s = 1.82748538
    p = 0.125
    polygons = []
    for letter in letters:
        polygon = load_letter(letter)
        polygon = scale(polygon, s, s)
        x1, y1, x2, y2 = polygon.bounds
        polygon = translate(polygon, -x1, -y1)
        polygon = translate(polygon, x)
        x += (x2 - x1) + p
        polygons.append(polygon)
        print polygon.bounds
    return MultiPolygon(polygons)

def main():
    bit = 0.25
    mp = load_letters('MEGAN')
    mp = mp.buffer(-bit / 2)
    mps = []
    while not mp.is_empty:
        mps.append(mp)
        mp = mp.buffer(-bit / 2)
    g = GCode()
    for mp in mps:
        g += GCode.from_geometry(mp, G0Z, -0.21875 * 1.0)
    g = g.rotate(90).origin().translate(2, 0)
    g = HEADER + g + FOOTER
    im = g.render(0, 0, 6, 8, 96)
    im.write_to_png('megan.png')
    g.save('megan.nc')

def main2():
    bit = 0.0625
    s = 1.82748538
    for letter in 'MEGAN':
        p = load_letter(letter)
        p = scale(p, s, s)
        p = p.buffer(bit / 2)
        g = GCode.from_geometry(p, G0Z, -bit)
        g = g.origin()
        depths = [-bit, -bit*2, -bit*3, -bit*4]
        gs = [g.depth(G0Z, d) for d in depths]
        g = reduce(operator.add, gs)
        g = HEADER + g + FOOTER
        im = g.render(0, 0, 6, 8, 96)
        im.write_to_png('megan-%s.png' % letter)
        g.save('megan-%s.nc' % letter)

if __name__ == '__main__':
    main()

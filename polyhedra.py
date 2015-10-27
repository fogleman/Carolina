from gcode import GCode
from math import *
from shapely.geometry import *

F = 120
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def create_points(sides, length, offset=0):
    x = y = 0
    rotation = 0
    margin = 0
    angle = 2 * pi / sides
    half = angle / 2
    rotation = rotation - pi / 2 + half
    angles = [angle * i + rotation for i in range(sides)]
    angles.append(angles[0])
    d = 0.5 / sin(half) - margin / cos(half)
    d *= length
    d += 1 / cos(half) * offset
    return [(x + cos(a) * d, y + sin(a) * d) for a in angles]

def create_face(dihedral, sides, length, depth, iterations):
    angle = radians((180 - dihedral) / 2)
    hyp = 1 / cos(angle) * depth
    max_offset = sin(angle) * hyp
    points = []
    for i in range(iterations):
        p = i / float(iterations - 1)
        offset = sin(angle) * p * hyp
        z = -cos(angle) * p * hyp
        p = create_points(sides, length, offset - max_offset)
        p = [(x, y, z) for x, y in p]
        points.extend(p)
    lines = []
    lines.append('G0 Z%f' % G0Z)
    lines.append('G0 X%f Y%f' % points[0][:2])
    for point in points:
        lines.append('G1 X%f Y%f Z%f' % point)
    lines.append('G0 Z%f' % G0Z)
    g = GCode(lines)
    g = g.origin()
    g = HEADER + g + FOOTER
    g.save('polyhedra.nc')
    im = g.render(0, 0, 6, 8, 96)
    im.write_to_png('polyhedra.png')

def main():
    create_face(70.528779, 3, 6, 0.5, 20) # tetrahedron
    # create_face(90.000000, 4, 6, 0.5, 10) # hexahedron
    # create_face(109.47122, 3, 6, 0.5, 10) # octahedron
    # create_face(116.56505, 5, 6, 0.5, 10) # dodecahedron
    # create_face(138.18969, 3, 6, 0.5, 10) # dodecahedron

if __name__ == '__main__':
    main()

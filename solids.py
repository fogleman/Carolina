from gcode import GCode
from math import *
from shapely.geometry import *

F = 60
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def create_points(sides, length):
    x = y = 0
    rotation = 0
    margin = 0
    angle = 2 * pi / sides
    rotation = rotation - pi / 2
    if sides % 2 == 0:
        rotation += angle / 2
    angles = [angle * i + rotation for i in range(sides)]
    angles.append(angles[0])
    d = 0.5 / sin(angle / 2) - margin / cos(angle / 2)
    d *= length
    return [(x + cos(a) * d, y + sin(a) * d) for a in angles]

def add_notches(points, size, offset, directions):
    result = []
    for (x1, y1), (x2, y2), direction in zip(points, points[1:], directions):
        dx = x2 - x1
        dy = y2 - y1
        a = atan2(dy, dx)
        d = hypot(dx, dy)
        if direction:
            s = -size
            p = offset / d
        else:
            s = size * 0.4
            p = 0
        px = x1 + dx * (0.25 + p)
        py = y1 + dy * (0.25 + p)
        qx = x1 + dx * (0.75 - p)
        qy = y1 + dy * (0.75 - p)
        Px = px + cos(a + pi / 2) * s
        Py = py + sin(a + pi / 2) * s
        Qx = qx + cos(a + pi / 2) * s
        Qy = qy + sin(a + pi / 2) * s
        result.extend([
            (x1, y1),
            (px, py),
            (Px, Py),
            (Qx, Qy),
            (qx, qy),
            (x2, y2),
        ])
    return result

def create_shape(sides, length):
    bit = 0.125
    size = 0.25
    offset = bit / 5
    data = [
        [0] * 5,
        # [1] * 5,
        # [0, 1, 0, 0, 1],
        # [1, 0, 1, 1, 0],
    ]
    # gs = GCode()
    for index, directions in enumerate(data):
        p = create_points(sides, length)
        # p = add_notches(p, size, offset, directions)
        # p = LineString(p).buffer(bit / 2).exterior.coords
        g = GCode()
        g += GCode.from_points(p, G0Z, -0.15)
        g += GCode.from_points(p, G0Z, -0.275)
        # g = g.move(3, 0, 0.5, 0)
        # gs += g
        g = HEADER + g + FOOTER
        g.save('solids%d.nc' % index)
        im = g.render(0, 0, 6, 8, 96)
        im.write_to_png('solids%d.png' % index)
    # im = gs.render(0, 0, 6, 8, 96)
    # im.write_to_png('solids.png')

def create_shape(sides, length):
    p = create_points(sides, length)
    g = GCode()
    g += GCode.from_points(p, G0Z, -0.24)
    # g += GCode.from_points(p, G0Z, -0.4)
    # g += GCode.from_points(p, G0Z, -0.5)
    # g = g.rotate_and_scale_to_fit(6.5, 8)
    # g = g.rotate(180)
    g = g + g.translate(0, 4)
    g = g.origin()
    g = HEADER + g + FOOTER
    g.save('solids.nc')
    im = g.render(0, 0, 6.5, 8, 96)
    im.write_to_png('solids.png')

def main():
    create_shape(4, 3.75)

if __name__ == '__main__':
    main()

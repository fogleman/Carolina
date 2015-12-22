from gcode import GCode
from math import *
from shapely.geometry import *

F = 120
G0Z = 0.5

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def polygon(sides, radius):
    angle = 2 * pi / sides
    rotation = -pi / 2
    if sides % 2 == 0:
        rotation += angle / 2
    angles = [angle * i + rotation for i in range(sides)]
    angles.append(angles[0])
    return [(cos(a) * radius, sin(a) * radius) for a in angles]

def rounded_polygon(sides, pradius, radius):
    points = polygon(sides, pradius - radius)
    return Polygon(points).buffer(radius).exterior.coords

def circle(r, n):
    points = []
    for i in range(n + 1):
        p = float(i) / n
        a = radians(p * 360)
        x = cos(a) * r
        y = sin(a) * r
        points.append((x, y))
    return points

def filled_circle(r, n, max_step):
    points = []
    outer = Polygon(circle(r, n))
    steps = int(ceil(r / max_step))
    for i in range(steps):
        p = 1 - float(i) / (steps - 1)
        shape = outer.buffer(-p * r)
        if shape.exterior:
            points.extend(shape.exterior.coords)
    return points

def wavy_circle(r, n, amplitude, frequency):
    points = []
    for i in range(n + 1):
        p = float(i) / n
        a = radians(p * 360)
        s = r + sin(p * 2 * pi * frequency) * amplitude
        x = cos(a) * s
        y = sin(a) * s
        points.append((x, y))
    return points

def square(side):
    n = side / 2.0
    return [
        (-n, -n),
        (-n, n),
        (n, n),
        (n, -n),
        (-n, -n),
    ]

def rounded_square(side, radius):
    points = square(side - radius * 2)
    return Polygon(points).buffer(radius).exterior.coords

def coaster(style, side, corner_radius, circle_diameter, circle_depth, depth, bit):
    n = 120
    points = filled_circle(circle_diameter / 2.0 - bit / 2.0, n, bit / 4.0)
    g = GCode.from_points(points, G0Z, -circle_depth)
    if style == 1:
        points = rounded_square(side + bit, corner_radius)
    elif style == 2:
        points = circle(side / 2.0, n)
    elif style == 3:
        points = rounded_polygon(6, side / 2.0, corner_radius)
    elif style == 4:
        points = wavy_circle(side / 2.0, 360, 0.2, 7)
    else:
        raise Exception('invalid style')
    g += GCode.from_points(points, G0Z, -depth).multipass(G0Z, -depth, bit)
    return g.origin()

def main():
    for style in range(1, 5):
        g = coaster(style, 5, 0.5, 4, 0.40625, 0.8, 0.125)
        g = HEADER + g + FOOTER
        g.save('coaster%d.nc' % style)
        im = g.render(0, 0, 6, 8, 96)
        im.write_to_png('coaster%d.png' % style)

if __name__ == '__main__':
    main()

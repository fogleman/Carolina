from gcode import GCode

PLANETS = [
    ('Sun', 0.000, 695800),
    ('Mercury', 0.387, 2439.64),
    ('Venus', 0.723, 6051.59),
    ('Earth', 1.000, 6378.1),
    ('Mars', 1.524, 3397.00),
    # ('Ceres', 2.766, 471),
    ('Jupiter', 5.203, 71492.68),
    ('Saturn', 9.537, 60267.14),
    ('Uranus', 19.191, 25557.25),
    ('Neptune', 30.069, 24766.36),
    # ('Pluto', 39.482, 1184),
    # ('Haumea', 43.335, 650),
    # ('Makemake', 45.792, 715),
    # ('Eris', 67.668, 1163),
]

def main():
    g0z = 0.2
    g1z = -0.01
    w = 32
    h = 6
    g = GCode()
    for i, (name, au, radius) in enumerate(PLANETS):
        p = (au + 0.25) / (PLANETS[-1][1] + 1)
        x = w * p
        t = GCode.from_file('text/%s.nc' % name)
        t = t.depth(0.2, -0.01)
        t = t.rotate(90).scale(0.2, 0.2)
        t = t.move(x, 0.75, 0.5, 0.5)
        _, ty1, _, ty2 = t.bounds
        g += t
        if i > 0:
            r = 1.2 * radius / 71492.68
            y1 = h / 2 - r
            y2 = h / 2 + r
            g += GCode(['G0 X%f Y%f' % (x, y1), 'G3 X%f Y%f I%f J%f' % (x, y2, 0, r), 'G3 X%f Y%f I%f J%f' % (x, y1, 0, -r)])
            g += GCode.from_points([(x, 0), (x, ty1 - 0.1)], g0z, g1z)
            g += GCode.from_points([(x, ty2 + 0.1), (x, y1-0.1)], g0z, g1z)
            g += GCode.from_points([(x, y2+0.1), (x, h)], g0z, g1z)
        else:
            g += GCode.from_points([(x, 0), (x, ty1 - 0.1)], g0z, g1z)
            g += GCode.from_points([(x, ty2 + 0.1), (x, h)], g0z, g1z)
    im = g.render(0, 0, 32, 6, 96)
    im.write_to_png('planets.png')

if __name__ == '__main__':
    main()

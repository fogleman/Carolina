from gcode import GCode

F = 45
G0Z = 0.2

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def main():
    sep = GCode.from_points([(3, 0), (3, 8)], 0.2, -0.05)

    t1 = GCode.from_file('text/Planet Earth.nc')
    t2 = GCode.from_file('text/Lambert Azimuthal Equal-Area.nc')
    t3 = GCode.from_file('text/0 N 110 W.nc')
    t4 = GCode.from_file('text/Michael Fogleman.nc')
    t5 = GCode.from_file('text/July 2015.nc')

    t1 = t1.scale(1.25, 1.25)
    t2 = t2.scale(0.55, 0.55)
    t3 = t3.scale(0.55, 0.55)

    t1 = t1.move(0, 0, 0.5, 0.5).depth(0.2, -0.07)
    t2 = t2.move(0, 0, 0.5, 0.5).depth(0.2, -0.03)
    t3 = t3.move(0, 0, 0.5, 0.5).depth(0.2, -0.03)
    t4 = t4.move(0, 0, 0.5, 0.5).depth(0.2, -0.05)
    t5 = t5.move(0, 0, 0.5, 0.5).depth(0.2, -0.05)

    t1 = t1.translate(0, 6.5)
    t2 = t2.translate(0, 5)
    t3 = t3.translate(0, 4)
    t4 = t4.translate(0, 2)
    t5 = t5.translate(0, 0)

    t = t1 + t2 + t3
    b = t4 + t5
    s = 2.0 / 3.0
    t = t.scale(s, s)
    b = b.scale(s, s)
    t = t.rotate(90)
    b = b.rotate(90)
    t = t.move(1.5, 4, 0.5, 0.5)
    b = b.move(4.5, 4, 0.5, 0.5)
    t = t + b
    t = t + sep
    t = HEADER + t + FOOTER
    p = 0.25
    im = t.render(0-p, 0-p, 6+p, 8+p, 96)
    im.write_to_png('engrave.png')
    t.save('engrave.nc')

if __name__ == '__main__':
    main()

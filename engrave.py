from gcode import GCode

F = 45
G0Z = 0.2

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def main():
    sep = GCode.from_points([(3, 0), (3, 8)], 0.2, -0.05)
    t1 = GCode.from_file('text/Counties of.nc')
    t2 = GCode.from_file('text/North Carolina.nc')
    t3 = GCode.from_file('text/Michael Fogleman.nc')
    t4 = GCode.from_file('text/June 2015.nc')
    t1 = t1.move(0, 0, 0.5, 0.5)
    t2 = t2.move(0, 0, 0.5, 0.5)
    t3 = t3.move(0, 0, 0.5, 0.5)
    t4 = t4.move(0, 0, 0.5, 0.5)
    t1 = t1.translate(0, 6.5)
    t2 = t2.translate(0, 5)
    t3 = t3.translate(0, 1.5)
    t4 = t4.translate(0, 0)
    t = t1 + t2 + t3 + t4
    s = 2.0 / 3.0
    t = t.scale(s, s)
    t = t.rotate(90)
    t = t.move(3, 4, 0.5, 0.5)
    t = t.depth(0.2, -0.05)
    t = t + sep
    t = HEADER + t + FOOTER
    p = 0.25
    im = t.render(0-p, 0-p, 6+p, 8+p, 96)
    im.write_to_png('engrave.png')
    t.save('engrave.nc')

if __name__ == '__main__':
    main()

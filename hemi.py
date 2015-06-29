from gcode import GCode
from math import sin, cos, radians, hypot, atan2
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
from shapely.affinity import translate, scale
import shapefile

SHAPEFILE = 'shapefiles/ne_110m_land/ne_110m_land.shp'

F = 60
G0Z = 0.2
G1Z = -1 / 8.0 / 8

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

R = 2 ** 0.5

def laea(pt):
    lng, lat = pt
    p = 0.1
    ok = lng > -180+p and lng < 180-p
    lng, lat = radians(lng), radians(lat)
    clat = radians(0)
    clng = radians(-110+180)
    k = (2 / (1 + sin(clat) * sin(lat) + cos(clat) * cos(lat) * cos(lng - clng))) ** 0.5
    x = k * cos(lat) * sin(lng - clng)
    y = k * (cos(clat) * sin(lat) - sin(clat) * cos(lat) * cos(lng - clng))
    return (x, y, ok)

def circle(r):
    points = []
    for i in range(361):
        a = radians(i)
        x = cos(a) * r
        y = sin(a) * r
        points.append((x, y))
    return LineString(points)

def shape_to_polygons(shape):
    def inside(pt):
        return hypot(*pt) <= R
    def adjust(pt):
        x, y = pt
        a = atan2(y, x)
        x = cos(a) * R
        y = sin(a) * R
        return (x, y)
    result = []
    parts = list(shape.parts) + [len(shape.points)]
    for i1, i2 in zip(parts, parts[1:]):
        points = map(tuple, shape.points[i1:i2])
        points = map(laea, points)
        points = filter(None, points)
        for a, b in zip(points, points[1:]):
            if not a[-1] and not b[-1]:
                continue
            a = a[:2]
            b = b[:2]
            in1 = inside(a)
            in2 = inside(b)
            if not in1 and not in2:
                continue
            if in1 and not in2:
                b = adjust(b)
            if in2 and not in1:
                a = adjust(a)
            result.append(LineString([a, b]))
    return result

def load_shapes():
    result = []
    sf = shapefile.Reader(SHAPEFILE)
    for item in sf.shapeRecords():
        result.extend(shape_to_polygons(item.shape))
    return result

def fit_shape(shape, width, height, padding=0):
    width -= padding * 2
    height -= padding * 2
    x1, y1, x2, y2 = shape.bounds
    w, h = x2 - x1, y2 - y1
    s = min(width / w, height / h)
    shape = translate(shape, -x1, -y1)
    shape = scale(shape, s, s, origin=(0, 0, 0))
    shape = translate(shape, padding, padding)
    return shape

def create_tile(i, j, w, h):
    x1, y1 = i * w, j * h
    x2, y2 = x1 + w, y1 + h
    return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

def intersection(mp, tile):
    result = []
    for shape in mp:
        line = shape.intersection(tile)
        if not line.is_empty:
            if isinstance(line, MultiLineString):
                result.extend(list(line.geoms))
            else:
                result.append(line)
    return MultiLineString(result)

def main():
    tw, th = 6, 8
    w, h = 24-2, 24-2
    p = 0
    shapes = load_shapes()
    shapes.append(circle(R))
    shapes.append(circle(R * 1.05))
    mp = MultiLineString(shapes)
    mp = fit_shape(mp, w, h, p)
    g = GCode.from_geometry(mp, G0Z, G1Z)
    im = g.render(0, 0, w, h, 96)
    im.write_to_png('hemi.png')
    for i in range(4):
        for j in range(3):
            print i, j
            tile = create_tile(i, j, tw, th)
            tmp = intersection(mp, tile)
            g = GCode.from_geometry(tmp, G0Z, G1Z)
            g = g.translate(-i * tw, -j * th)
            g = HEADER + g + FOOTER
            im = g.render(0, 0, tw, th, 96)
            im.write_to_png('hemi-tiles/%d.%d.png' % (j, i))
            g.save('hemi-tiles/%d.%d.nc' % (j, i))

if __name__ == '__main__':
    main()

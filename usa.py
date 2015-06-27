from gcode import GCode
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
from shapely.affinity import translate, scale
import shapefile

SHAPEFILES = [
    'shapefiles/cb_2014_us_state_20m/mercator.shp',
]

F = 60
G0Z = 0.2
G1Z = -1 / 8.0 / 4

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

def shape_to_polygons(shape):
    result = []
    parts = list(shape.parts) + [len(shape.points)]
    for i1, i2 in zip(parts, parts[1:]):
        points = map(tuple, shape.points[i1:i2])
        result.append(Polygon(points))
    return result

def load_shapes():
    skip = set(['AK', 'HI', 'AS', 'GU', 'MP', 'VI', 'PR'])
    result = []
    for i, path in enumerate(SHAPEFILES):
        sf = shapefile.Reader(path)
        for j, item in enumerate(sf.shapeRecords()):
            if item.record[4] in skip:
                continue
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

def intersection(mp, tile, offset=None):
    result = []
    for shape in mp:
        if offset:
            shape = shape.buffer(offset)
        if shape.is_empty:
            continue
        if isinstance(shape, Polygon):
            shape = [shape]
        for polygon in shape:
            line = LineString(list(polygon.exterior.coords)).intersection(tile)
            if not line.is_empty:
                if isinstance(line, MultiLineString):
                    result.extend(list(line.geoms))
                else:
                    result.append(line)
    return MultiLineString(result)

def main():
    # 8x3
    i, j = 5, 1
    tw, th = 6, 8
    w, h = 48-2, 24-2
    p = 0
    shapes = load_shapes()
    mp = MultiPolygon(shapes)
    mp = fit_shape(mp, w, h, p)
    for i in range(7):
        for j in range(3):
            print i, j
            tile = create_tile(i, j, tw, th)
            tmp = intersection(mp, tile)
            g = GCode.from_geometry(tmp, G0Z, G1Z)
            g = g.translate(-i * tw, -j * th)
            g = HEADER + g + FOOTER
            im = g.render(0, 0, tw, th, 96)
            im.write_to_png('usa-tiles/%d.%d.png' % (j, i))
            g.save('usa-tiles/%d.%d.nc' % (j, i))

if __name__ == '__main__':
    main()

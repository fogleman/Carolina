from gcode import GCode
from math import radians, asinh, tan
from shapely.geometry import Polygon, LineString
from shapely.affinity import translate
import shapefile

SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'
SCALE = 525
X = -772.6394788798026
Y = 329.90359819959644

# 81.21 x 30.78 inches
# 6.77 x 2.56 feet
# 14 x 4 tiles

def mercator(lat, lng):
    x = radians(lng) * SCALE - X
    y = asinh(tan(radians(lat))) * SCALE - Y
    return (x, y)

def get_shapes(shape, tile):
    result = []
    parts = list(shape.parts) + [len(shape.points)]
    for i1, i2 in zip(parts, parts[1:]):
        points = [mercator(y, x) for x, y in shape.points[i1:i2]]
        p = LineString(points).intersection(tile)
        if not p.is_empty:
            result.append(p)
    return result

def load_counties(statefp, tile):
    result = []
    sf = shapefile.Reader(SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[0] != statefp:
            continue
        result.extend(get_shapes(item.shape, tile))
    return result

def tile_polygon(i, j):
    w, h = 6, 8
    w, h = 6, 8
    minx = i * w
    miny = j * h
    maxx = minx + w
    maxy = miny + h
    return Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])

def main():
    for y in range(4):
        for x in range(14):
            tile = tile_polygon(x, y)
            shapes = load_counties('37', tile)
            if not shapes:
                continue
            print x, y, len(shapes)
            g = GCode()
            for shape in shapes:
                g += GCode.from_geometry(shape, 0.2, -0.05)
            g = g.translate(-tile.bounds[0], -tile.bounds[1])
            p = 0.1
            surface = g.render(0 - p, 0 - p, 6 + p, 8 + p, 96)
            surface.write_to_png('tiles/%02d.%02d.png' % (y, x))

if __name__ == '__main__':
    main()

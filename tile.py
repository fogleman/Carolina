from gcode import GCode
from math import radians, asinh, tan
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.affinity import translate
import shapefile

COUNTY_SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'
STATE_SHAPEFILE = 'shapefiles/cb_2014_us_state_5m/cb_2014_us_state_5m.shp'

SCALE = 525
X = -772.6394788798026
Y = 329.90359819959644

F = 60
G0Z = 0.2
G1Z_COUNTY = -1/16.0
G1Z_STATE1 = -0.3
G1Z_STATE2 = -0.6

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8', 'G0 X3 Y6'])

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

def get_state_shapes(shape, tile):
    result = []
    parts = list(shape.parts) + [len(shape.points)]
    for i1, i2 in zip(parts, parts[1:]):
        points = [mercator(y, x) for x, y in shape.points[i1:i2]]
        mp = Polygon(points).buffer(-0.25)
        if mp.is_empty:
            continue
        if isinstance(mp, Polygon):
            polygons = [mp]
        else:
            polygons = mp
        for polygon in polygons:
            line = LineString(list(polygon.exterior.coords)).intersection(tile)
            if not line.is_empty:
                result.append(line)
    return result

def load_counties(statefp, tile):
    result = []
    sf = shapefile.Reader(COUNTY_SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[0] != statefp:
            continue
        result.extend(get_shapes(item.shape, tile))
    return result

def load_state(statefp, tile):
    result = []
    sf = shapefile.Reader(STATE_SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[0] != statefp:
            continue
        result.extend(get_state_shapes(item.shape, tile))
    return result

def tile_polygon(i, j):
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
            county_shapes = load_counties('37', tile)
            state_shapes = load_state('37', tile)
            if not county_shapes and not state_shapes:
                continue
            print x, y, len(county_shapes), len(state_shapes)
            g = GCode()
            for shape in county_shapes:
                g += GCode.from_geometry(shape, G0Z, G1Z_COUNTY)
            for shape in state_shapes:
                g += GCode.from_geometry(shape, G0Z, G1Z_STATE1)
            for shape in state_shapes:
                g += GCode.from_geometry(shape, G0Z, G1Z_STATE2)
            g = g.translate(-tile.bounds[0], -tile.bounds[1])
            g = HEADER + g + FOOTER
            g.save('tiles/%02d.%02d.nc' % (y, x))
            p = 0.1
            surface = g.render(0 - p, 0 - p, 6 + p, 8 + p, 96)
            surface.write_to_png('tiles/%02d.%02d.png' % (y, x))

if __name__ == '__main__':
    main()

from counties import COUNTIES
from gcode import GCode
from math import radians, asinh, tan, sin, cos
from operator import attrgetter
from shapely.geometry import Polygon
from shapely.affinity import translate
import pack
import shapefile

SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'
# SCALE = 400
SCALE = 525

F = 50
G0Z = 0.2
G1Z = -0.04
G1Z_TEXT = -0.035

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8'])

def mercator(lat, lng, scale):
    x = radians(lng) * scale
    y = asinh(tan(radians(lat))) * scale
    return (x, y)

def load_county_shapes(statefp):
    result = {}
    sf = shapefile.Reader(SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[0] != statefp:
            continue
        result[item.record[5]] = item.shape
    return result

def get_polygons(shape, scale):
    result = []
    parts = list(shape.parts) + [len(shape.points)]
    for i1, i2 in zip(parts, parts[1:]):
        points = [mercator(y, x, scale) for x, y in shape.points[i1:i2]]
        polygon = Polygon(points)
        bounds = polygon.bounds
        polygon = translate(polygon, -bounds[0], -bounds[1])
        result.append(polygon)
    return result

def best_scale(width, height):
    result = None
    shapes = load_county_shapes('37')
    for county in COUNTIES:
        shape = shapes[county.name]
        polygons = get_polygons(shape, 1)
        for polygon in polygons:
            sizes = []
            g = GCode.from_polygon(polygon, 0, 0)
            for angle in range(0, 180, 5):
                w, h = g.rotate(angle).size
                size = min(width / w, height / h)
                sizes.append((size, angle))
            size = max(sizes)
            print county.name, size
            if result is None or size < result:
                result = size
    print result
    return result

def generate_text(name, x, y):
    g = GCode.from_file('text/%s.nc' % name)
    g = g.depth(G0Z, G1Z_TEXT)
    g = g.scale(0.25, 0.25)
    g = g.translate(x - g.width / 2, y - g.height / 2)
    return g

def generate_county(shapes, name):
    g = GCode()
    shape = shapes[name]
    polygons = get_polygons(shape, SCALE)
    for polygon in polygons:
        g += GCode.from_polygon(polygon, G0Z, G1Z)
    polygon = max(polygons, key=attrgetter('area'))
    x, y = polygon.centroid.coords[0]
    g += generate_text(name, x, y)
    g = min([g.rotate(a) for a in range(0, 180, 5)], key=attrgetter('width'))
    g = g.origin()
    g = HEADER + g + FOOTER
    return g

def generate_counties(shapes):
    result = {}
    for name, shape in shapes.items():
        result[name] = generate_county(shapes, name)
    return result

def pack_counties(counties, padding):
    counties = counties.values()
    sizes = [county.size for county in counties]
    sizes = [(w + padding, h + padding) for w, h in sizes]
    bins = pack.pack_bins(6, 8, sizes)
    result = GCode()
    for i, b in enumerate(bins):
        for item in b:
            index, rotated, (x, y, _, _) = item
            g = counties[index]
            if rotated:
                g = g.rotate(90).origin()
            g = g.translate(x, y)
            g = g.translate(i * 30, 0)
            result += g
    result = result.scale(0.1, 0.1)
    print result

if __name__ == '__main__':
    shapes = load_county_shapes('37')
    counties = generate_counties(shapes)
    bins = pack_counties(counties, 0.25)
    # counties = generate_counties(shapes)
    # print counties
    # best_scale(6, 8)
    # result = GCode()
    # x = 0
    # for county in COUNTIES[:10]:
    #     g = generate_county(county.name)
    #     g = g.translate(x, 0)
    #     x += g.width + 0.5
    #     result += g
    # print result
    # print generate_county(shapes, 'Wake')

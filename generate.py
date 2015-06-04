from counties import COUNTIES
from gcode import GCode
from math import radians, asinh, tan, sin, cos
from operator import attrgetter
from shapely.geometry import Polygon
from shapely.affinity import translate
import shapefile

SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'
SCALE = 400

F = 50
G0Z = 0.2
G1Z = -0.04

def mercator(lat, lng, scale):
    x = radians(lng) * scale
    y = asinh(tan(radians(lat))) * scale
    return (x, y)

def load_county_shape(statefp, name):
    sf = shapefile.Reader(SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[0] != statefp:
            continue
        if item.record[5] != name:
            continue
        return item.shape
    return None

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
    for county in COUNTIES:
        shape = load_county_shape('37', county.name)
        polygons = get_polygons(shape, 1)
        for polygon in polygons:
            minx, miny, maxx, maxy = polygon.bounds
            w = maxx - minx
            h = maxy - miny
            s1 = min(width / w, height / h)
            s2 = min(width / h, height / w)
            s = max(s1, s2)
            print county.name, s
            if result is None or s < result:
                result = s
    print result
    return result

def generate_text(name, x, y):
    g = GCode.from_file('text/%s.nc' % name)
    g = g.scale(0.25, 0.25)
    g = g.translate(x - g.size.w / 2, y - g.size.h / 2)
    return g

def generate_county(name):
    g = GCode()
    shape = load_county_shape('37', name)
    polygons = get_polygons(shape, SCALE)
    for polygon in polygons:
        g += GCode.from_polygon(polygon, G0Z, G1Z)
    polygon = max(polygons, key=attrgetter('area'))
    x, y = polygon.centroid.coords[0]
    g += generate_text(name, x, y)
    return g

if __name__ == '__main__':
    g = generate_county('Wake')
    g = g.scale(10, 10)
    g = g.rotate(45)
    g = g.move(0, 0, 0, 0)
    print g

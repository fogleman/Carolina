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

def generate_county(name):
    lines = []
    shape = load_county_shape('37', name)
    polygons = get_polygons(shape, SCALE)
    for polygon in polygons:
        points = list(polygon.exterior.coords)
        lines.append('G0 Z%f' % G0Z)
        lines.append('G0 X%f Y%f' % points[0])
        lines.append('G1 Z%f' % G1Z)
        for point in points:
            lines.append('G1 X%f Y%f' % point)
    g = GCode.from_file('text/%s.nc' % name)
    g = g.scale(0.25, 0.25)
    w, h = g.size
    polygon = max(polygons, key=attrgetter('area'))
    cx, cy = polygon.centroid.coords[0]
    g = g.translate(cx - w / 2, cy - h / 2)
    return GCode(lines) + g

if __name__ == '__main__':
    g = generate_county('Wake')
    g = g.scale(10, 10)
    print g
    # for i, county in enumerate(COUNTIES):
    #     x = i % 10
    #     y = i / 10
    #     print '(%s)' % county.name
    #     g = generate_county(county.name)
    #     g = g.translate(x * 6, y * 8)
    #     g = g.scale(10, 10)
    #     print g

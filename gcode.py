from counties import COUNTIES
from math import radians, asinh, tan
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

def nc_load_text(text):
    with open('text/%s.nc' % text, 'r') as fp:
        return fp.read()

def nc_bounds(nc):
    x = []
    y = []
    for line in nc.split('\n'):
        for token in line.split():
            if token[0] == 'X':
                x.append(float(token[1:]))
            if token[0] == 'Y':
                y.append(float(token[1:]))
    return (min(x), min(y), max(x), max(y))

def nc_scale(nc, sx, sy):
    lines = []
    for line in nc.split('\n'):
        tokens = []
        for token in line.split():
            if token[0] == 'X':
                token = 'X' + str(float(token[1:]) * sx)
            elif token[0] == 'Y':
                token = 'Y' + str(float(token[1:]) * sy)
            elif token[0] == 'I':
                token = 'I' + str(float(token[1:]) * sx)
            elif token[0] == 'J':
                token = 'J' + str(float(token[1:]) * sy)
            tokens.append(token)
        lines.append(' '.join(tokens))
    return '\n'.join(lines)

def nc_translate(nc, dx, dy):
    lines = []
    for line in nc.split('\n'):
        tokens = []
        for token in line.split():
            if token[0] == 'X':
                token = 'X' + str(float(token[1:]) + dx)
            elif token[0] == 'Y':
                token = 'Y' + str(float(token[1:]) + dy)
            tokens.append(token)
        lines.append(' '.join(tokens))
    return '\n'.join(lines)

def nc_swap(nc):
    lines = []
    for line in nc.split('\n'):
        tokens = []
        for token in line.split():
            if token[0] == 'X':
                token = 'Y' + str(float(token[1:]))
            elif token[0] == 'Y':
                token = 'X' + str(-float(token[1:]))
            elif token[0] == 'I':
                token = 'J' + str(float(token[1:]))
            elif token[0] == 'J':
                token = 'I' + str(-float(token[1:]))
            tokens.append(token)
        lines.append(' '.join(tokens))
    nc = '\n'.join(lines)
    x, y, _, _ = nc_bounds(nc)
    nc = nc_translate(nc, -x, -y)
    return nc

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
    nc = nc_load_text(name)
    nc = nc_scale(nc, 0.25, 0.25)
    polygon = max(polygons, key=attrgetter('area'))
    _, _, w, h = nc_bounds(nc)
    cx, cy = polygon.centroid.coords[0]
    nc = nc_translate(nc, cx - w / 2, cy - h / 2)
    lines.extend(nc.split('\n'))
    return '\n'.join(lines)

if __name__ == '__main__':
    for i, county in enumerate(COUNTIES):
        x = i % 10
        y = i / 10
        print '(%s)' % county.name
        nc = generate_county(county.name)
        nc = nc_translate(nc, x * 6, y * 8)
        nc = nc_scale(nc, 10, 10)
        print nc

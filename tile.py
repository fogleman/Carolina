from gcode import GCode
from itertools import groupby
from math import radians, asinh, tan
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.affinity import translate
import shapefile

COUNTY_SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'
STATE_SHAPEFILE = 'shapefiles/cb_2014_us_state_5m/cb_2014_us_state_5m.shp'

SCALE = 525
X = -772.6394788798026
Y = 329.90359819959644

F = 60
G0Z = 0.2
G1Z_COUNTY = -1 / 8.0
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

def shapes_to_polygons(shapes):
    result = []
    for shape in shapes:
        parts = list(shape.parts) + [len(shape.points)]
        for i1, i2 in zip(parts, parts[1:]):
            points = [mercator(y, x) for x, y in shape.points[i1:i2]]
            result.append(Polygon(points))
    return result

def load_polygons(path):
    result = []
    sf = shapefile.Reader(path)
    for item in sf.shapeRecords():
        if item.record[0] != '37':
            continue
        result.append(item.shape)
    return shapes_to_polygons(result)

def intersection(shapes, tile, offset=None):
    result = []
    for shape in shapes:
        if offset:
            shape = shape.buffer(offset)
        if shape.is_empty:
            continue
        if isinstance(shape, Polygon):
            shape = [shape]
        for polygon in shape:
            line = LineString(list(polygon.exterior.coords)).intersection(tile)
            if not line.is_empty:
                line = line.simplify(0.01)
                if isinstance(line, MultiLineString):
                    result.extend(list(line.geoms))
                else:
                    result.append(line)
    result = simplify(result)
    return result

def simplify(lines):
    result = []
    seen = set()
    for line in lines:
        line = list(line.coords)
        edges = []
        for a, b in zip(line, line[1:]):
            edge = (a, b)
            repeat = edge in seen
            edges.append((edge, repeat))
            seen.add((a, b))
            seen.add((b, a))
        for repeat, group in groupby(edges, key=lambda x: x[1]):
            group = list(group)
            points = [group[0][0][0]]
            for item in group:
                points.append(item[0][1])
            segment = LineString(points)
            if repeat and segment.length >= 1:
                continue
            result.append(segment)
    return result

def create_tile(i, j, w, h):
    minx, miny = i * w, j * h
    maxx, maxy = minx + w, miny + h
    return Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])

def main():
    counties = load_polygons(COUNTY_SHAPEFILE)
    state = load_polygons(STATE_SHAPEFILE)
    for y in range(4):
        for x in range(14):
            tile = create_tile(x, y, 6, 8)
            county_shapes = intersection(counties, tile)
            state_shapes = intersection(state, tile, -0.25)
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

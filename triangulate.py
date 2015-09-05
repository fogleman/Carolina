from math import radians, asinh, tan
from p2t import Point, CDT
from shapely.geometry import Polygon, MultiPolygon
import shapefile

SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'

def mercator(lat, lng, scale):
    x = radians(lng) * scale
    y = asinh(tan(radians(lat))) * scale
    return (x, y)

def load_county_shapes(statefp):
    result = []
    sf = shapefile.Reader(SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[0] != statefp:
            continue
        result.append((item.record[5], item.shape))
    return result

def triangulate(name, shape):
    result = []
    parts = list(shape.parts) + [len(shape.points)]
    for i1, i2 in zip(parts, parts[1:]):
        points = shape.points[i1:i2]
        points = [mercator(y, x, 1000) for x, y in points]
        polygon = Polygon(points).buffer(-0.3).simplify(0.05)
        if isinstance(polygon, MultiPolygon):
            polygons = polygon.geoms
        else:
            polygons = [polygon]
        for polygon in polygons:
            if polygon.is_empty:
                continue
            if polygon.area < 1:
                continue
            points = list(polygon.exterior.coords[:-1])
            points = [Point(x, y) for x, y in points]
            cdt = CDT(points)
            triangles = cdt.triangulate()
            for t in triangles:
                p = [name]
                for a in [t.a, t.b, t.c]:
                    p.append(a.x)
                    p.append(a.y)
                    p.append(0.0)
                print ','.join(map(str, p))
            z1 = 0
            z2 = -5
            points = list(polygon.exterior.coords)
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                p = [name, x1, y1, z1, x2, y2, z1, x1, y1, z2]
                print ','.join(map(str, p))
                p = [name, x1, y1, z2, x2, y2, z1, x2, y2, z2]
                print ','.join(map(str, p))
    return result

def create_graph():
    shapes = load_county_shapes('37')
    for name, shape in shapes:
        triangulate(name, shape)

if __name__ == '__main__':
    graph = create_graph()

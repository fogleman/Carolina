from counties import COUNTIES
from gcode import GCode, pack_gcodes
from math import radians, asinh, tan, sin, cos
from operator import attrgetter
from shapely.geometry import Polygon
from shapely.affinity import translate
import shapefile

SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'
SCALE = 525

F = 45
G0Z = 0.2
G1Z_BEVEL = -0.125
G1Z_TEXT = -0.05
G1Z_THRU1 = -0.4
G1Z_THRU2 = -0.65

HEADER = GCode(['G90', 'G20', 'G0 Z%s' % G0Z, 'M4', 'G4 P2.0', 'F%s' % F])
FOOTER = GCode(['G0 Z%s' % G0Z, 'M8'])

TEXT_SIZE = 0.375

TEXT_SIZES = {
    'Transylvania': 0.3,
}

TEXT_OFFSETS = {
    'Alleghany': (0, 0.125),
    'Beaufort': (0, 1),
    'Cabarrus': (0, 0.25),
    'Camden': (-0.5, 0.625),
    'Carteret': (-1.5, -0.75),
    'Cherokee': (-0.25, 0),
    'Chowan': (-0.25, 0),
    'Cleveland': (0, -0.25),
    'Currituck': (-0.75, 0.5),
    'Cumberland': (-0.375, 0),
    'Davidson': (-0.125, 0),
    'Durham': (0.25, -0.5),
    'Edgecombe': (0.125, 0),
    'Henderson': (0, 0.375),
    'Hertford': (0, -0.25),
    'Jackson': (0, 0.25),
    'Lenoir': (-0.25, 0),
    'Mitchell': (0, 0.25),
    'Mecklenburg': (0.25, -0.5),
    'Martin': (0, -0.25),
    'Montgomery': (0, -0.75),
    'New Hanover': (0.25, 0),
    'Northampton': (0.375, 0.375),
    'Perquimans': (0.15, 0.45),
    'Richmond': (0.25, 0.25),
    'Rutherford': (0, 0.25),
    'Scotland': (-0.075, 0),
    'Transylvania': (0.25, 0),
}

TEXT_ANGLES = {
    'Camden': -45,
    'Chowan': -90,
    'Currituck': -45,
    'Mitchell': -45,
    'New Hanover': 60,
    'Pasquotank': -45,
    'Perquimans': -45,
}

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

def fit_text(polygon, x, y, w, h):
    result = scale = 0.1
    while True:
        x1 = x - w * scale / 2
        y1 = y - h * scale / 2
        x2 = x + w * scale / 2
        y2 = y + h * scale / 2
        box = Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)])
        if not polygon.contains(box):
            return result
        result = scale
        scale += 0.1

def position_text(polygon, w, h, n):
    items = []
    minx, miny, maxx, maxy = polygon.bounds
    for i in range(n):
        for j in range(n):
            x = minx + (maxx - minx) * (float(i) / (n - 1))
            y = miny + (maxy - miny) * (float(j) / (n - 1))
            s = fit_text(polygon, x, y, w, h)
            items.append((s, x, y))
    return max(items)

def generate_text(name, x, y, scale, angle):
    g = GCode.from_file('text/%s.nc' % name)
    g = g.depth(G0Z, G1Z_TEXT)
    g = g.scale(scale, scale)
    g = g.rotate(angle)
    g = g.move(x, y, 0.5, 0.5)
    return g

def generate_county(shape, name, text):
    result = []
    polygons = get_polygons(shape, SCALE)
    max_polygon = max(polygons, key=attrgetter('area'))
    for i, polygon in enumerate(polygons):
        g = GCode.from_polygon(polygon, G0Z, G1Z_BEVEL)
        if text and polygon == max_polygon:
            x, y = polygon.centroid.coords[0]
            dx, dy = TEXT_OFFSETS.get(name, (0, 0))
            scale = TEXT_SIZES.get(name, TEXT_SIZE)
            angle = TEXT_ANGLES.get(name, 0)
            g += generate_text(name, x + dx, y + dy, scale, angle)
        g = g.origin()
        g.name = ('%s %d' % (name, i)) if i else name
        result.append(g)
    return result

def generate_counties(shapes, text):
    result = []
    for name, shape in shapes:
        result.extend(generate_county(shape, name, text))
    return result

def render_counties(counties):
    for g in counties:
        name = g.name
        g = g.move(5, 5, 0.5, 0.5)
        surface = g.render(0, 0, 10, 10, 96)
        surface.write_to_png('pngs/%s.png' % name)

if __name__ == '__main__':
    seed = 44654645
    shapes = load_county_shapes('37')

    big = [
        'Northampton', 'Halifax', 'Pitt', 'Beaufort', 'Craven', 'Carteret',
        'Wake', 'Johnston', 'Sampson', 'Robeson', 'Columbus', 'Brunswick',
    ]
    shapes = [(k, v) for k, v in shapes if k in big]

    counties = generate_counties(shapes, True)

    for i, g in enumerate(counties):
        if g.name == 'Carteret':
            g = g.rotate(35).origin()
            g = g.clamp(0, 0, 6, 8)
            counties[i] = g

    bins = pack_gcodes(counties, 6, 8, 0.0, seed)
    for i, g in enumerate(bins):
        g = HEADER + g + FOOTER
        g.save('pass1/bin%02d.nc' % i)
        surface = g.render(0, 0, 6, 8, 96)
        surface.write_to_png('bins/%02d.png' % i)

    counties = generate_counties(shapes, False)

    for i, g in enumerate(counties):
        if g.name == 'Carteret':
            g = g.rotate(35).origin()
            g = g.clamp(0, 0, 6, 8)
            counties[i] = g

    bins = pack_gcodes(counties, 6, 8, 0.0, seed)
    for i, g in enumerate(bins):
        g1 = g.depth(G0Z, G1Z_THRU1)
        g2 = g.depth(G0Z, G1Z_THRU2)
        g = HEADER + g1 + g2 + FOOTER
        g.save('pass2/bin%02d.nc' % i)

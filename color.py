from collections import defaultdict
from gcode import GCode
from shapely.geometry import Polygon
import random
import shapefile

SHAPEFILE = 'shapefiles/cb_2013_us_county_5m/cb_2013_us_county_5m.shp'

def load_county_shapes(statefp):
    result = []
    sf = shapefile.Reader(SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[0] != statefp:
            continue
        result.append((item.record[5], item.shape))
    return result

def get_polygons(shape):
    result = []
    parts = list(shape.parts) + [len(shape.points)]
    for i1, i2 in zip(parts, parts[1:]):
        polygon = Polygon(shape.points[i1:i2])
        result.append(polygon)
    return result

def create_graph():
    result = Graph()
    shapes = load_county_shapes('37')
    polygons = [(name, get_polygons(shape)) for name, shape in shapes]
    for name1, polygons1 in polygons:
        for name2, polygons2 in polygons:
            if name1 == name2:
                continue
            for p1 in polygons1:
                for p2 in polygons2:
                    if p1.intersects(p2):
                        result.add(name1, name2)
    return result

class Graph(object):
    def __init__(self):
        self.edges = defaultdict(set)
    def add(self, a, b):
        self.edges[a].add(b)
        self.edges[b].add(a)
    def add_all(self, name, names):
        for other in names:
            self.add(name, other)
    def remove(self, a, b):
        self.edges[a].discard(b)
        self.edges[b].discard(a)
    def remove_all(self, name):
        result = set(self.edges[name])
        for x in result:
            self.remove(name, x)
        return result
    def choice(self, items, n):
        items = [x for x in items if len(self.edges[x]) < n]
        return random.choice(items)
    def color(self, n):
        result = {}
        stack = []
        items = list(self.edges)
        while items:
            name = self.choice(items, n)
            items.remove(name)
            names = self.remove_all(name)
            stack.append((name, names))
        colors = set(range(n))
        for name, names in reversed(stack):
            self.add_all(name, names)
            used = set(result[x] for x in self.edges[name])
            available = list(colors - used)
            color = random.choice(available)
            result[name] = color
        return result

if __name__ == '__main__':
    graph = create_graph()
    colors = graph.color(4)
    for name, names in graph.edges.items():
        for other in names:
            if colors[name] == colors[other]:
                raise Exception('invalid coloring!')
    for name in sorted(colors):
        print name, colors[name]

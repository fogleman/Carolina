from collections import namedtuple
from math import radians, sin, cos, hypot, atan2, ceil
from operator import attrgetter
from pack import pack, best_seed
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, LinearRing
import cairo

DECIMALS = 6

Bounds = namedtuple('Bounds', ['x1', 'y1', 'x2', 'y2'])
Size = namedtuple('Size', ['width', 'height'])

def pack_gcodes(gcodes, width, height, padding, seed=None):
    gcodes = filter(None, [g.rotate_to_fit(width, height) for g in gcodes])
    result = []
    sizes = [g.size for g in gcodes]
    sizes = [(w + padding * 2, h + padding * 2) for w, h in sizes]
    # print best_seed(width, height, sizes, 1000)
    bins = pack(width, height, sizes, seed)
    for b in bins:
        bg = GCode()
        for item in b:
            index, rotated, (x, y, _, _) = item
            g = gcodes[index]
            if rotated:
                g = g.rotate(-90).origin()
            g = g.translate(x + padding, y + padding)
            bg += g
        result.append(bg)
    return result

def interpolate(a, b, d):
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    t = d / hypot(dx, dy)
    x = x1 + dx * t
    y = y1 + dy * t
    return (x, y)

def tab(points, tab_size, tab_spacing):
    points.append(points[0])
    px, py = points[0]
    length = 0
    thresholds = (tab_spacing, tab_size)
    index = 0
    group = [(px, py)]
    groups = []
    for x, y in points:
        while length + hypot(x - px, y - py) > thresholds[index % 2]:
            ix, iy = interpolate((px, py), (x, y), thresholds[index % 2] - length)
            group.append((ix, iy))
            # print group
            length = 0
            px, py = ix, iy
            groups.append(group)
            group = [(px, py)]
            index += 1
        group.append((x, y))
        length += hypot(x - px, y - py)
        px, py = x, y
    if group:
        groups.append(group)
    return groups[::2]

class GCode(object):

    @staticmethod
    def from_file(path):
        with open(path, 'r') as fp:
            return GCode(fp.read())

    @staticmethod
    def from_points(points, g0z, g1z):
        lines = []
        lines.append('G0 Z%f' % g0z)
        lines.append('G0 X%f Y%f' % points[0])
        lines.append('G1 Z%f' % g1z)
        for point in points:
            lines.append('G1 X%f Y%f' % point)
        lines.append('G0 Z%f' % g0z)
        return GCode(lines)

    @staticmethod
    def from_points_tabbed(points, g0z, g1z, tab_size, tab_spacing):
        g = GCode()
        for points in tab(points, tab_size, tab_spacing):
            g += GCode.from_points(points, g0z, g1z)
        return g

    @staticmethod
    def from_geometry(geometry, g0z, g1z, tab_size=None, tab_spacing=None):
        t = type(geometry)
        if t == Polygon:
            g = GCode()
            for x in geometry.interiors:
                g += GCode.from_geometry(x, g0z, g1z, tab_size, tab_spacing)
            g += GCode.from_geometry(geometry.exterior, g0z, g1z, tab_size, tab_spacing)
            return g
        if t == LineString or t == LinearRing:
            points = list(geometry.coords)
            if tab_size and tab_spacing:
                return GCode.from_points_tabbed(points, g0z, g1z, tab_size, tab_spacing)
            else:
                return GCode.from_points(points, g0z, g1z)
        if t in (MultiPolygon, MultiLineString):
            g = GCode()
            for x in geometry:
                g += GCode.from_geometry(x, g0z, g1z, tab_size, tab_spacing)
            return g
        raise Exception('unrecognized geometry type')

    @staticmethod
    def from_geometries(geometries, g0z, g1z):
        g = GCode()
        for geometry in geometries:
            g += GCode.from_geometry(geometry, g0z, g1z)
        return g

    @staticmethod
    def from_shape(shape, g0z, g1z):
        g = GCode()
        parts = list(shape.parts) + [len(shape.points)]
        for i1, i2 in zip(parts, parts[1:]):
            points = map(tuple, shape.points[i1:i2])
            g += GCode.from_points(points, g0z, g1z)
        return g

    @staticmethod
    def from_shapes(shapes, g0z, g1z):
        g = GCode()
        for shape in shapes:
            g += GCode.from_shape(shape, g0z, g1z)
        return g

    def __init__(self, code=None):
        if code is None:
            self.code = ''
        elif isinstance(code, basestring):
            self.code = code
        elif isinstance(code, GCode):
            self.code = code.code
        else:
            self.code = '\n'.join(map(str, code))

    def __str__(self):
        return self.code

    def __add__(self, other):
        return GCode(self.lines + GCode(other).lines)

    @property
    def lines(self):
        return self.code.split('\n')

    @property
    def bounds(self):
        x = []
        y = []
        for line in self.lines:
            for token in line.split():
                if token[0] == 'X':
                    x.append(float(token[1:]))
                if token[0] == 'Y':
                    y.append(float(token[1:]))
        return Bounds(min(x), min(y), max(x), max(y))

    @property
    def size(self):
        b = self.bounds
        return Size(b.x2 - b.x1, b.y2 - b.y1)

    @property
    def width(self):
        return self.size.width

    @property
    def height(self):
        return self.size.height

    @property
    def area(self):
        w, h = self.size
        return w * h

    def save(self, path):
        with open(path, 'w') as fp:
            fp.write(self.code)

    def origin(self):
        return self.move(0, 0, 0, 0)

    def move(self, x, y, ax, ay):
        x1, y1, x2, y2 = self.bounds
        dx = x1 + (x2 - x1) * ax - x
        dy = y1 + (y2 - y1) * ay - y
        return self.translate(-dx, -dy)

    def translate(self, dx, dy):
        lines = []
        for line in self.lines:
            tokens = []
            for token in line.split():
                if token[0] == 'X':
                    token = 'X' + str(float(token[1:]) + dx)
                elif token[0] == 'Y':
                    token = 'Y' + str(float(token[1:]) + dy)
                tokens.append(token)
            lines.append(' '.join(tokens))
        return GCode(lines)

    def scale(self, sx, sy):
        lines = []
        for line in self.lines:
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
        return GCode(lines)

    def rotate(self, angle):
        c = cos(radians(angle))
        s = sin(radians(angle))
        lines = []
        x = y = i = j = 0
        for line in self.lines:
            for token in line.split():
                if token[0] == 'X':
                    x = float(token[1:])
                elif token[0] == 'Y':
                    y = float(token[1:])
                elif token[0] == 'I':
                    i = float(token[1:])
                elif token[0] == 'J':
                    j = float(token[1:])
            rx = round(x * c - y * s, DECIMALS)
            ry = round(y * c + x * s, DECIMALS)
            ri = round(i * c - j * s, DECIMALS)
            rj = round(j * c + i * s, DECIMALS)
            tokens = []
            for token in line.split():
                if token[0] == 'X':
                    token = 'X' + str(rx)
                elif token[0] == 'Y':
                    token = 'Y' + str(ry)
                elif token[0] == 'I':
                    token = 'I' + str(ri)
                elif token[0] == 'J':
                    token = 'J' + str(rj)
                tokens.append(token)
            lines.append(' '.join(tokens))
        return GCode(lines)

    def rotate_to_fit(self, width, height):
        for a in range(0, 180, 5):
            g = self.rotate(a).origin()
            if g.width <= width and g.height <= height:
                return g
        return None

    def scale_to_fit(self, width, height, padding=0):
        width -= padding * 2
        height -= padding * 2
        s = min(width / self.width, height / self.height)
        return self.scale(s, s).origin()

    def rotate_and_scale_to_fit(self, width, height, padding=0):
        gs = []
        width -= padding * 2
        height -= padding * 2
        for a in range(0, 180, 5):
            g = self.rotate(a)
            s = min(width / g.width, height / g.height)
            g = g.scale(s, s).origin()
            gs.append((s, g))
        g = max(gs, key=lambda x: x[0])[1]
        return g

    def clamp(self, minx, miny, maxx, maxy):
        lines = []
        for line in self.lines:
            tokens = []
            for token in line.split():
                if token[0] == 'X':
                    token = 'X' + str(max(float(token[1:]), minx))
                    token = 'X' + str(min(float(token[1:]), maxx))
                elif token[0] == 'Y':
                    token = 'Y' + str(max(float(token[1:]), miny))
                    token = 'Y' + str(min(float(token[1:]), maxy))
                tokens.append(token)
            lines.append(' '.join(tokens))
        return GCode(lines)

    def depth(self, g0z, g1z):
        lines = []
        for line in self.lines:
            tokens = []
            for token in line.split():
                if token[0] == 'Z':
                    z = float(token[1:])
                    z = g0z if z > 0 else g1z
                    token = 'Z' + str(z)
                tokens.append(token)
            lines.append(' '.join(tokens))
        return GCode(lines)

    def multipass(self, g0z, g1z, max_step):
        passes = int(ceil(abs(g1z / max_step)))
        step = g1z / passes
        g = GCode()
        for i in range(passes):
            depth = (i + 1) * step
            print depth
            g += self.depth(g0z, depth)
        return g

    def crop(self, x1, y1, x2, y2):
        def inside(x, y):
            return x >= x1 and y >= y1 and x <= x2 and y <= y2
        lines = []
        x = y = z = 0
        for line in self.lines:
            tokens = line.split()
            if not tokens:
                continue
            px, py, pz = x, y, z
            for token in tokens:
                if token[0] == 'X':
                    x = float(token[1:])
                elif token[0] == 'Y':
                    y = float(token[1:])
                elif token[0] == 'Z':
                    z = float(token[1:])
            in1 = inside(px, py)
            in2 = inside(x, y)
            if in1 and in2:
                lines.append(line)
            elif in1 and not in2:
                pass
            elif not in1 and in2:
                pass
            else:
                pass
        return GCode(lines)

    def render(self, x1, y1, x2, y2, scale):
        width = int(round((x2 - x1) * scale))
        height = int(round((y2 - y1) * scale))
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        dc = cairo.Context(surface)
        dc.set_source_rgb(0, 0, 0)
        dc.paint()
        dc.scale(scale, -scale)
        dc.translate(0, y1 - y2)
        dc.translate(-x1, -y1)
        dc.set_line_cap(cairo.LINE_CAP_ROUND)
        dc.set_line_join(cairo.LINE_JOIN_ROUND)
        dc.set_source_rgb(1, 1, 1)
        x = y = z = i = j = 0
        px = py = 0
        for line in self.lines:
            tokens = line.split()
            if not tokens:
                continue
            if tokens[0][0] == 'N':
                tokens.pop(0)
            for token in tokens:
                if token[0] == 'X':
                    x = float(token[1:])
                elif token[0] == 'Y':
                    y = float(token[1:])
                elif token[0] == 'Z':
                    z = float(token[1:])
                elif token[0] == 'I':
                    i = float(token[1:])
                elif token[0] == 'J':
                    j = float(token[1:])
            if tokens[0] == 'G0':
                dc.move_to(x, y)
            elif tokens[0] == 'G1':
                dc.line_to(x, y)
            elif tokens[0] in ['G2', 'G3']:
                cx = px + i
                cy = py + j
                r = hypot(i, j)
                a1 = atan2(py - cy, px - cx)
                a2 = atan2(y - cy, x - cx)
                dc.new_sub_path()
                if tokens[0] == 'G3':
                    dc.arc(cx, cy, r, a1, a2)
                else:
                    dc.arc_negative(cx, cy, r, a1, a2)
            dc.set_line_width(-z * 2 / 20)
            dc.stroke()
            dc.move_to(x, y)
            px, py = x, y
        return surface

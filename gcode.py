from collections import namedtuple
from math import radians, sin, cos, hypot, atan2
from operator import attrgetter
from pack import pack
import cairo

DECIMALS = 6

Bounds = namedtuple('Bounds', ['x1', 'y1', 'x2', 'y2'])
Size = namedtuple('Size', ['width', 'height'])

def pack_gcodes(gcodes, width, height, padding, seed=None):
    gcodes = filter(None, [g.rotate_to_fit(width, height) for g in gcodes])
    result = []
    sizes = [g.size for g in gcodes]
    sizes = [(w + padding * 2, h + padding * 2) for w, h in sizes]
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

class GCode(object):

    @staticmethod
    def from_file(path):
        with open(path, 'r') as fp:
            return GCode(fp.read())

    @staticmethod
    def from_polygon(polygon, g0z, g1z):
        lines = []
        points = list(polygon.exterior.coords)
        lines.append('G0 Z%f' % g0z)
        lines.append('G0 X%f Y%f' % points[0])
        lines.append('G1 Z%f' % g1z)
        for point in points:
            lines.append('G1 X%f Y%f' % point)
        lines.append('G0 Z%f' % g0z)
        return GCode(lines)

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

    def render(self, x1, y1, x2, y2, scale):
        width = int(round((x2 - x1) * scale))
        height = int(round((y2 - y1) * scale))
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        dc = cairo.Context(surface)
        dc.set_source_rgb(0, 0, 0)
        dc.paint()
        dc.scale(scale, -scale)
        dc.translate(0, y1 - y2)
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
            dc.set_line_width(-z * 2)
            dc.stroke()
            dc.move_to(x, y)
            px, py = x, y
        return surface

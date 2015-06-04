from collections import namedtuple
from math import radians, sin, cos

Bounds = namedtuple('Bounds', ['x1', 'y1', 'x2', 'y2'])
Size = namedtuple('Size', ['w', 'h'])

class GCode(object):
    @staticmethod
    def from_file(path):
        with open(path, 'r') as fp:
            return GCode(fp.read())
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
    def move(self, x, y, ax, ay):
        minx, miny, maxx, maxy = self.bounds
        w = maxx - minx
        h = maxy - miny
        dx = minx + w * ax - x
        dy = miny + h * ay - y
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
            rx = x * c - y * s
            ry = y * c + x * s
            ri = i * c - j * s
            rj = j * c + i * s
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

# def nc_swap(nc):
#     lines = []
#     for line in nc.split('\n'):
#         tokens = []
#         for token in line.split():
#             if token[0] == 'X':
#                 token = 'Y' + str(float(token[1:]))
#             elif token[0] == 'Y':
#                 token = 'X' + str(-float(token[1:]))
#             elif token[0] == 'I':
#                 token = 'J' + str(float(token[1:]))
#             elif token[0] == 'J':
#                 token = 'I' + str(-float(token[1:]))
#             tokens.append(token)
#         lines.append(' '.join(tokens))
#     nc = '\n'.join(lines)
#     x, y, _, _ = nc_bounds(nc)
#     nc = nc_translate(nc, -x, -y)
#     return nc

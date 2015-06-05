import random

class Node(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.right = None
        self.down = None
    def insert(self, w, h):
        if self.right:
            result = self.right.insert(w, h)
            if result:
                return result
            result = self.down.insert(w, h)
            if result:
                return result
            return None
        elif w <= self.w and h <= self.h:
            self.right = Node(self.x + w, self.y, self.w - w, h)
            self.down = Node(self.x, self.y + h, self.w, self.h - h)
            return (self.x, self.y, w, h)
        else:
            return None

def try_pack(tw, th, items):
    result = []
    node = Node(0, 0, tw, th)
    for index, (w, h) in items:
        rotated = False
        position = node.insert(w, h)
        if position is None:
            rotated = True
            position = node.insert(h, w)
            if position is None:
                return None
        result.append((index, rotated, position))
    return result

class Bin(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.items = []
    def add(self, item):
        layout = try_pack(self.width, self.height, self.items + [item])
        if layout is None:
            return False
        self.items.append(item)
        return True
    def layout(self):
        return try_pack(self.width, self.height, self.items)

def pack_bins(width, height, sizes, seed=None):
    bins = []
    items = list(enumerate(sizes))
    if seed is not None:
        r = random.Random(seed)
        r.shuffle(items)
    for item in items:
        for b in bins:
            if b.add(item):
                break
        else:
            b = Bin(width, height)
            b.add(item)
            bins.append(b)
    result = [b.layout() for b in bins]
    return result

def best_seed(width, height, sizes, iterations):
    best = (len(sizes) + 1, None)
    for i in xrange(iterations):
        print i, iterations
        seed = int(random.getrandbits(31))
        result = pack_bins(width, height, sizes, seed)
        best = min(best, (len(result), seed))
    return best[1]
